"""Thread-safe shared state for workers and the display loop."""

from __future__ import annotations

import threading
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Callable, Deque, Dict, List, Optional, Set

from agent.persistence import SessionLogger


class Mode(str, Enum):
    IDLE = "Idle"
    SCANNING = "Scanning"
    ACTIVE = "Active"
    HANDSHAKE = "Handshake"
    ATTACKING = "Attacking"
    PAYLOAD = "Payload"
    GADGET = "Gadget"
    JACKPOT = "Jackpot"          # New jackpot mode
    ERROR = "Error"
    SHUTDOWN = "Shutdown"


@dataclass
class HostHit:
    ip: str
    hostname: str = ""
    open_ports: List[int] = field(default_factory=list)
    last_seen: str = ""


@dataclass
class SessionStats:
    """Pwnagotchi-style cumulative session counters."""

    scans_completed: int = 0
    deauths_sent: int = 0
    peers_seen: int = 0
    networks_seen: int = 0
    handshakes_total: int = 0
    exploits_pwned: int = 0
    payloads_run: int = 0
    payloads_ok: int = 0
    last_channel: str = ""
    # Jackpot specific
    jackpot_attempts: int = 0
    jackpot_success: int = 0
    total_dispensed: int = 0


TriggerFn = Callable[[str, Dict], None]


class AgentState:
    """Central status object shared across threads."""

    def __init__(self, log_capacity: int = 8) -> None:
        self._lock = threading.RLock()
        self.mode: Mode = Mode.IDLE
        self.uptime_start = datetime.now(timezone.utc)
        self.cpu_percent: float = 0.0
        self.ram_percent: float = 0.0
        self.network_rx_kb: float = 0.0
        self.network_tx_kb: float = 0.0
        self.hosts_found: int = 0
        self.last_scan_hosts: List[HostHit] = []
        self.gadget_active: bool = False
        self.gadget_iface: str = ""
        self.hid_ready: bool = False
        self.payload_active: bool = False
        self.payload_name: str = ""
        self.wifi_aps_seen: int = 0
        self.handshakes_captured: int = 0
        self.wifi_target_essid: str = ""
        self.wifi_target_bssid: str = ""
        self.exploits_run: int = 0
        self.exploits_success: int = 0
        self.last_exploit: str = ""
        self.error_message: str = ""
        self.session = SessionStats()
        self._peers: Set[str] = set()
        self._networks: Set[str] = set()
        self._log: Deque[str] = deque(maxlen=log_capacity)
        self._trigger_fn: Optional[TriggerFn] = None
        # Module stats for conditional triggers
        self._module_stats: Dict[str, Dict[str, int]] = {}
        # Persistent logger
        self.logger = SessionLogger()
        # Jackpot specific
        self.jackpot_armed: bool = False
        self.jackpot_targets: List[Dict] = []
        self.last_jackpot_result: Optional[Dict] = None
        self.xfs_devices_found: int = 0

    def set_trigger_handler(self, handler: Optional[TriggerFn]) -> None:
        with self._lock:
            self._trigger_fn = handler

    def _emit_trigger(self, event: str, context: Dict) -> None:
        fn = self._trigger_fn
        if fn is None:
            return
        try:
            fn(event, context)
        except Exception:  # noqa: BLE001 — triggers must not break workers
            pass

    def set_mode(self, mode: Mode) -> None:
        with self._lock:
            self.mode = mode
            msg = f"mode -> {mode.value}"
            self.push_log(msg)
            self.logger.log("mode_change", {"mode": mode.value})

    def update_metrics(
        self,
        cpu: float,
        ram: float,
        network_rx_kb: float = 0.0,
        network_tx_kb: float = 0.0,
    ) -> None:
        with self._lock:
            self.cpu_percent = cpu
            self.ram_percent = ram
            self.network_rx_kb = network_rx_kb
            self.network_tx_kb = network_tx_kb

    def set_hosts(self, hosts: List[HostHit]) -> None:
        with self._lock:
            self.last_scan_hosts = list(hosts)
            self.hosts_found = len(hosts)

    def record_scan_complete(self, host_count: int) -> None:
        with self._lock:
            self.session.scans_completed += 1
        self._emit_trigger("scan_complete", {"hosts": host_count})
        self.logger.log("scan_complete", {"hosts": host_count})

    def set_gadget(self, active: bool, iface: str = "", hid: bool = False) -> None:
        with self._lock:
            self.gadget_active = active
            self.gadget_iface = iface
            self.hid_ready = hid if active else False
            state = "up" if active else "down"
            hid_tag = "+HID" if hid and active else ""
            self.push_log(f"gadget {state}{hid_tag} {iface}".strip())
        if active:
            self._emit_trigger("gadget_up", {"iface": iface, "hid": hid})
            self.logger.log("gadget_up", {"iface": iface, "hid": hid})

    def set_wifi_status(
        self,
        aps_seen: int,
        handshakes: int,
        target_essid: str = "",
        target_bssid: str = "",
        channel: str = "",
    ) -> None:
        with self._lock:
            self.wifi_aps_seen = aps_seen
            self.handshakes_captured = handshakes
            if target_essid:
                self.wifi_target_essid = target_essid
                if target_essid not in self._networks:
                    self._networks.add(target_essid)
                    self.session.networks_seen = len(self._networks)
            if target_bssid:
                self.wifi_target_bssid = target_bssid
                if target_bssid not in self._peers:
                    self._peers.add(target_bssid)
                    self.session.peers_seen = len(self._peers)
            if channel:
                self.session.last_channel = channel

    def record_deauth(self, count: int = 1, bssid: str = "") -> None:
        with self._lock:
            self.session.deauths_sent += count
            if bssid and bssid not in self._peers:
                self._peers.add(bssid)
                self.session.peers_seen = len(self._peers)
        self.logger.log("deauth", {"count": count, "bssid": bssid})

    def record_handshake(self, essid: str, bssid: str) -> None:
        with self._lock:
            self.handshakes_captured += 1
            self.session.handshakes_total += 1
            self.wifi_target_essid = essid
            self.wifi_target_bssid = bssid
            self.push_log(f"HS! {essid or bssid}")
        self._emit_trigger(
            "handshake",
            {"essid": essid, "bssid": bssid, "count": self.handshakes_captured},
        )
        self.logger.log("handshake", {"essid": essid, "bssid": bssid})

    def record_exploit(self, module: str, target: str, success: bool, credentials: tuple = ("", "")) -> None:
        with self._lock:
            self.exploits_run += 1
            if success:
                self.exploits_success += 1
                self.session.exploits_pwned += 1
            self.last_exploit = f"{module}@{target}"
            tag = "WIN" if success else "fail"
            self.push_log(f"exp {module} {target} {tag}")
        self._record_module_attempt(module, success)
        self._emit_trigger(
            "exploit_success" if success else "exploit_fail",
            {"module": module, "ip": target, "credentials": credentials},
        )
        self.logger.log(
            "exploit",
            {"module": module, "target": target, "success": success, "credentials": credentials},
        )

    def _record_module_attempt(self, module: str, success: bool) -> None:
        with self._lock:
            stats = self._module_stats.setdefault(module, {"attempts": 0, "success": 0})
            stats["attempts"] += 1
            if success:
                stats["success"] += 1

    def get_module_stats(self, module: str) -> Dict[str, int]:
        with self._lock:
            return self._module_stats.get(module, {"attempts": 0, "success": 0}).copy()

    def record_payload(self, name: str, success: bool) -> None:
        with self._lock:
            self.session.payloads_run += 1
            if success:
                self.session.payloads_ok += 1
        self.logger.log("payload", {"name": name, "success": success})

    def set_payload(self, active: bool, name: str = "") -> None:
        with self._lock:
            self.payload_active = active
            self.payload_name = name
            if active and name:
                self.push_log(f"payload {name}")

    def set_error(self, message: str) -> None:
        with self._lock:
            self.error_message = message
            self.mode = Mode.ERROR
            self.push_log(f"ERR: {message}")
        self.logger.log("error", {"message": message})

    def push_log(self, message: str) -> None:
        ts = datetime.now().strftime("%H:%M:%S")
        with self._lock:
            self._log.appendleft(f"{ts} {message}")
        self.logger.log("log", {"message": message})

    # ========== Jackpot-specific methods ==========
    def record_jackpot_attempt(self, target_ip: str, port: int, success: bool, amount: int = 0) -> None:
        with self._lock:
            self.session.jackpot_attempts += 1
            if success:
                self.session.jackpot_success += 1
                self.session.total_dispensed += amount
            self.push_log(f"jackpot {target_ip}:{port} {'WIN' if success else 'fail'} amt={amount}")
        self._emit_trigger(
            "jackpot" if success else "jackpot_fail",
            {"target": target_ip, "port": port, "amount": amount, "success": success},
        )
        self.logger.log("jackpot", {"target": target_ip, "port": port, "success": success, "amount": amount})

    def set_jackpot_targets(self, targets: List[Dict]) -> None:
        with self._lock:
            self.jackpot_targets = targets
            self.xfs_devices_found = len(targets)

    def set_jackpot_armed(self, armed: bool) -> None:
        with self._lock:
            self.jackpot_armed = armed
            self.push_log(f"jackpot {'armed' if armed else 'disarmed'}")

    def set_last_jackpot_result(self, result: Dict) -> None:
        with self._lock:
            self.last_jackpot_result = result

    # ========== Snapshot ==========
    def snapshot(self) -> dict:
        with self._lock:
            uptime = datetime.now(timezone.utc) - self.uptime_start
            sess = self.session
            return {
                "mode": self.mode,
                "uptime_s": int(uptime.total_seconds()),
                "cpu_percent": self.cpu_percent,
                "ram_percent": self.ram_percent,
                "network_rx_kb": self.network_rx_kb,
                "network_tx_kb": self.network_tx_kb,
                "hosts_found": self.hosts_found,
                "last_scan_hosts": list(self.last_scan_hosts),
                "gadget_active": self.gadget_active,
                "gadget_iface": self.gadget_iface,
                "hid_ready": self.hid_ready,
                "payload_active": self.payload_active,
                "payload_name": self.payload_name,
                "wifi_aps_seen": self.wifi_aps_seen,
                "handshakes_captured": self.handshakes_captured,
                "wifi_target_essid": self.wifi_target_essid,
                "wifi_target_bssid": self.wifi_target_bssid,
                "exploits_run": self.exploits_run,
                "exploits_success": self.exploits_success,
                "last_exploit": self.last_exploit,
                "error_message": self.error_message,
                "session_scans": sess.scans_completed,
                "session_deauths": sess.deauths_sent,
                "session_peers": sess.peers_seen,
                "session_networks": sess.networks_seen,
                "session_pwned": sess.exploits_pwned + sess.handshakes_total,
                "session_payloads_run": sess.payloads_run,
                "session_payloads_ok": sess.payloads_ok,
                "session_channel": sess.last_channel,
                "log_lines": list(self._log),
                # Jackpot additions
                "jackpot_armed": self.jackpot_armed,
                "jackpot_targets": len(self.jackpot_targets),
                "jackpot_attempts": sess.jackpot_attempts,
                "jackpot_success": sess.jackpot_success,
                "total_dispensed": sess.total_dispensed,
                "last_jackpot": self.last_jackpot_result,
            }
