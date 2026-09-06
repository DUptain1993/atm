"""P4wnP1-style payload trigger rules and event dispatch."""

from __future__ import annotations

import logging
import re
import time
from dataclasses import dataclass, field
from datetime import datetime, time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import yaml

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]
PAYLOAD_DIR = ROOT / "payloads"
MANIFEST_PATH = PAYLOAD_DIR / "manifest.yaml"
MANUAL_TRIGGER_FILE = PAYLOAD_DIR / "trigger.request"

RunFn = Callable[[Path], bool]


@dataclass
class TriggerRule:
    event: str
    payload: Path
    cooldown_s: float = 60.0
    module_filter: str = ""
    last_fired: float = 0.0
    interval_s: float = 0.0
    enabled: bool = True
    condition: Optional[Dict[str, Any]] = None
    fired_count: int = 0  # for count_ge condition


class PayloadTriggerEngine:
    """
    Maps offensive events to HID payloads (P4wnP1 trigger profiles).

    Events: boot, handshake, exploit_success, gadget_host, scan_complete,
    interval, manual.
    Supports advanced conditions: success_rate, ssid_regex, time_window, count_ge.
    """

    def __init__(
        self,
        state: Optional[Any] = None,  # AgentState (avoid circular import)
        rules: Optional[List[TriggerRule]] = None,
        run_fn: Optional[RunFn] = None,
    ) -> None:
        self.state = state
        self.rules = rules or []
        self._run_fn = run_fn
        self._stop = False
        self._host_was_connected = False
        self._boot_done = False

    def set_runner(self, run_fn: RunFn) -> None:
        self._run_fn = run_fn

    def load_from_config(self, cfg: Dict[str, Any]) -> None:
        merged: List[TriggerRule] = list(self.rules)
        if MANIFEST_PATH.exists():
            with open(MANIFEST_PATH) as f:
                manifest = yaml.safe_load(f) or {}
            for item in manifest.get("triggers", []):
                merged.append(self._rule_from_dict(item))

        for item in cfg.get("payload_triggers", []):
            merged.append(self._rule_from_dict(item))

        self.rules = merged
        logger.info("loaded %d payload trigger rules", len(self.rules))

    def _rule_from_dict(self, item: Dict[str, Any]) -> TriggerRule:
        payload = item.get("payload") or item.get("file") or ""
        path = Path(payload)
        if not path.is_absolute():
            path = ROOT / payload
        return TriggerRule(
            event=str(item.get("event", "")),
            payload=path,
            cooldown_s=float(item.get("cooldown_s", item.get("cooldown", 60))),
            module_filter=str(item.get("module", item.get("module_filter", ""))),
            interval_s=float(item.get("interval_s", 0)),
            enabled=bool(item.get("enabled", True)),
            condition=item.get("condition"),  # new
        )

    def stop(self) -> None:
        self._stop = True

    def handle_event(self, event: str, context: Dict[str, Any]) -> int:
        fired = 0
        for rule in self.rules:
            if not rule.enabled or rule.event != event:
                continue
            if rule.module_filter and context.get("module") != rule.module_filter:
                continue
            if not self._evaluate_condition(rule, context):
                continue
            if self._fire_rule(rule, context):
                fired += 1
        return fired

    def _evaluate_condition(self, rule: TriggerRule, context: Dict) -> bool:
        cond = rule.condition
        if not cond:
            return True

        # success_rate
        if "success_rate" in cond:
            module = cond.get("module") or rule.module_filter
            if module and self.state:
                stats = self.state.get_module_stats(module)
                attempts = stats.get("attempts", 0)
                if attempts == 0:
                    return False
                if stats.get("success", 0) / attempts < cond["success_rate"]:
                    return False

        # ssid_regex
        if "ssid_regex" in cond:
            essid = context.get("essid", "")
            if not re.search(cond["ssid_regex"], essid, re.I):
                return False

        # time_window (format "HH:MM-HH:MM")
        if "time_window" in cond:
            try:
                start_str, end_str = cond["time_window"].split("-")
                start_t = time.fromisoformat(start_str)
                end_t = time.fromisoformat(end_str)
                now = datetime.now().time()
                if not (start_t <= now <= end_t):
                    return False
            except (ValueError, TypeError):
                return False

        # count_ge (number of times this rule has already fired)
        if "count_ge" in cond:
            if rule.fired_count < cond["count_ge"]:
                return False

        return True

    def on_boot(self) -> None:
        if self._boot_done:
            return
        self._boot_done = True
        self.handle_event("boot", {})

    def run_listener_loop(
        self,
        poll_s: float = 2.0,
        gadget_poll_s: float = 1.0,
    ) -> None:
        """Poll gadget host + manual trigger file + interval rules."""
        last_gadget_poll = 0.0
        last_interval_check = 0.0
        self.on_boot()

        while not self._stop:
            now = time.monotonic()

            if now - last_gadget_poll >= gadget_poll_s:
                last_gadget_poll = now
                self._poll_gadget_host()

            if MANUAL_TRIGGER_FILE.exists():
                self._poll_manual_trigger()

            if now - last_interval_check >= 5.0:
                last_interval_check = now
                self._poll_interval_rules()

            time.sleep(poll_s)

    def _poll_gadget_host(self) -> None:
        connected = self._gadget_host_connected()
        if connected and not self._host_was_connected:
            self._host_was_connected = True
            self.handle_event("gadget_host", {})
        elif not connected:
            self._host_was_connected = False

    def _gadget_host_connected(self) -> bool:
        udc = Path("/sys/class/udc")
        if not udc.exists():
            return False
        for entry in udc.iterdir():
            state_file = entry / "state"
            if state_file.exists():
                try:
                    state = state_file.read_text().strip().lower()
                    if state in ("configured", "active"):
                        return True
                except OSError:
                    continue
        return False

    def _poll_manual_trigger(self) -> None:
        try:
            raw = MANUAL_TRIGGER_FILE.read_text().strip()
            MANUAL_TRIGGER_FILE.unlink(missing_ok=True)
        except OSError:
            return
        if not raw:
            return
        path = Path(raw)
        if not path.is_absolute():
            path = PAYLOAD_DIR / raw
        if path.exists() and self._run_fn:
            logger.info("manual trigger -> %s", path.name)
            self._run_fn(path)

    def _poll_interval_rules(self) -> None:
        now = time.monotonic()
        for rule in self.rules:
            if rule.event != "interval" or not rule.enabled or rule.interval_s <= 0:
                continue
            if now - rule.last_fired >= rule.interval_s:
                self._fire_rule(rule, {})

    def _fire_rule(self, rule: TriggerRule, context: Dict[str, Any]) -> bool:
        now = time.monotonic()
        if now - rule.last_fired < rule.cooldown_s:
            return False
        path = rule.payload
        if context.get("path"):
            path = Path(context["path"])
        if not path.exists():
            logger.debug("trigger payload missing: %s", path)
            return False
        if self._run_fn is None:
            return False
        rule.last_fired = now
        rule.fired_count += 1
        logger.info("trigger %s -> %s", rule.event, path.name)
        try:
            return bool(self._run_fn(path))
        except Exception as exc:  # noqa: BLE001
            logger.warning("trigger run failed: %s", exc)
            return False
