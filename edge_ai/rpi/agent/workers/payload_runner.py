"""P4wnP1-style HID payload execution with trigger engine."""

from __future__ import annotations

import logging
import threading
from pathlib import Path
from typing import Any, Dict, Optional

from agent.offensive.ducky import DuckyRunner
from agent.offensive.hid_keyboard import HidKeyboard
from agent.offensive.payload_triggers import PayloadTriggerEngine
from agent.state import AgentState, Mode

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]
PAYLOAD_DIR = ROOT / "payloads"


class PayloadRunner:
    """Run DuckyScript payloads on events, gadget connect, or manual trigger."""

    def __init__(
        self,
        state: AgentState,
        payload_path: Optional[Path] = None,
        auto_run: bool = False,
        wait_for_hid_s: float = 30.0,
        cfg: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.state = state
        self.payload_path = payload_path
        self.auto_run = auto_run
        self.wait_for_hid_s = wait_for_hid_s
        self._stop = False
        self.keyboard = HidKeyboard()
        self.ducky = DuckyRunner(keyboard=self.keyboard)
        self.triggers = PayloadTriggerEngine(run_fn=self.run_once)
        if cfg:
            self.triggers.load_from_config(cfg)
        self.state.set_trigger_handler(self._on_trigger_event)
        self._listener_thread: Optional[threading.Thread] = None

    def stop(self) -> None:
        self._stop = True
        self.triggers.stop()
        self.state.set_trigger_handler(None)

    def start_listener(self) -> Optional[threading.Thread]:
        if not self.triggers.rules and not self.auto_run:
            return None
        self._listener_thread = threading.Thread(
            target=self._listener_loop,
            name="payload-triggers",
            daemon=True,
        )
        self._listener_thread.start()
        return self._listener_thread

    def _listener_loop(self) -> None:
        if self.auto_run and self.payload_path:
            self.triggers.on_boot()
            if self._wait_hid():
                self.run_once(self.payload_path)
        self.triggers.run_listener_loop(poll_s=2.0, gadget_poll_s=1.0)

    def _on_trigger_event(self, event: str, context: Dict[str, Any]) -> None:
        self.triggers.handle_event(event, context)

    def run_once(self, path: Optional[Path] = None) -> bool:
        payload = path or self.payload_path
        if payload is None:
            payload = self._default_payload()
        if not payload or not payload.exists():
            self.state.push_log("no payload file")
            self.state.record_payload("", False)
            return False

        if not self._wait_hid():
            self.state.push_log("HID not ready")
            self.state.record_payload(payload.name, False)
            return False

        self.state.set_mode(Mode.PAYLOAD)
        self.state.set_payload(True, payload.name)
        ok = False
        try:
            self.ducky.run_file(payload)
            self.state.push_log(f"payload done {payload.name}")
            ok = True
        except Exception as exc:  # noqa: BLE001
            logger.exception("payload failed")
            self.state.push_log(f"payload err {exc}")
        finally:
            self.state.set_payload(False)
            self.state.record_payload(payload.name, ok)
        return ok

    def _wait_hid(self) -> bool:
        import time

        deadline = time.monotonic() + self.wait_for_hid_s
        while not self._stop and time.monotonic() < deadline:
            if self.state.hid_ready or self.keyboard.available():
                self.state.hid_ready = True
                return True
            time.sleep(0.5)
        return self.keyboard.available()

    def _default_payload(self) -> Optional[Path]:
        if not PAYLOAD_DIR.exists():
            return None
        for ext in ("*.ducky", "*.txt"):
            matches = sorted(PAYLOAD_DIR.glob(ext))
            if matches:
                return matches[0]
        return None
