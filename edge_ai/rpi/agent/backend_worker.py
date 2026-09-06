"""Background orchestrator: offensive workers, gadget, network delivery, metrics, signals, and jackpot."""

from __future__ import annotations

import logging
import signal
import threading
import time
from pathlib import Path
from typing import Any, Dict, Optional

import psutil
import yaml

from agent.state import AgentState, Mode
from agent.workers.exploit_worker import ExploitWorker
from agent.workers.gadget import GadgetManager
from agent.workers.payload_runner import PayloadRunner
from agent.workers.recon import ReconWorker
from agent.workers.wifi_handshake import WifiHandshakeWorker
from agent.workers.network_delivery import NetworkDelivery

# Optionally import jackpot components if they exist in the root
try:
    from network_xfs import NetworkJackpotDrone, RemoteXFSExploit
    from watchdog import JackpotWatchdog
    from web_interface import run_web_server
except ImportError:
    NetworkJackpotDrone = None
    RemoteXFSExploit = None
    JackpotWatchdog = None
    run_web_server = None

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "config" / "default.yaml"
LOCAL_CONFIG = ROOT / "config" / "local.yaml"


def load_config(path: Optional[Path] = None) -> Dict[str, Any]:
    """Merge default.yaml with optional local.yaml overrides."""
    merged: Dict[str, Any] = {}
    for cfg in (DEFAULT_CONFIG, LOCAL_CONFIG):
        if cfg.exists():
            with open(cfg) as f:
                data = yaml.safe_load(f) or {}
                merged.update(data)
    if path and path.exists():
        with open(path) as f:
            data = yaml.safe_load(f) or {}
            merged.update(data)
    return merged


class BackendOrchestrator:
    """
    Owns long-running offensive worker threads and process lifecycle.

    Blends Pwnagotchi (WiFi handshakes), Bjorn (exploit chains),
    network delivery (instead of P4wnP1 USB gadget), and optionally
    jackpot drone capabilities.
    """

    def __init__(
        self,
        state: Optional[AgentState] = None,
        cidr: Optional[str] = None,
        scan_interval_s: Optional[float] = None,
        metrics_interval_s: Optional[float] = None,
        enable_gadget: Optional[bool] = None,
        enable_hid: Optional[bool] = None,
        enable_wifi_hunt: Optional[bool] = None,
        enable_exploits: Optional[bool] = None,
        payload_auto_run: Optional[bool] = None,
        config_path: Optional[Path] = None,
        # Network delivery settings
        enable_network_delivery: Optional[bool] = None,
        net_mode: str = "server",
        net_port: int = 4444,
        net_reverse_host: Optional[str] = None,
        # Jackpot settings
        enable_jackpot: Optional[bool] = None,
        jackpot_subnet: str = "192.168.1.0/24",
        jackpot_interval: int = 60,
        enable_web_interface: Optional[bool] = None,
        web_port: int = 8080,
    ) -> None:
        cfg = load_config(config_path)
        networks = cfg.get("networks") or ["192.168.1.0/24"]
        resolved_cidr = cidr or networks[0]
        resolved_scan = scan_interval_s if scan_interval_s is not None else float(
            cfg.get("scan_interval", 90.0)
        )
        resolved_metrics = metrics_interval_s if metrics_interval_s is not None else float(
            cfg.get("metrics_interval", 5.0)
        )
        resolved_gadget = (
            enable_gadget if enable_gadget is not None else bool(cfg.get("enable_gadget", True))
        )
        resolved_hid = (
            enable_hid if enable_hid is not None else bool(cfg.get("enable_hid", True))
        )
        resolved_wifi = (
            enable_wifi_hunt
            if enable_wifi_hunt is not None
            else bool(cfg.get("enable_wifi_hunt", True))
        )
        resolved_exploits = (
            enable_exploits if enable_exploits is not None else bool(cfg.get("enable_exploits", True))
        )
        resolved_payload_auto = (
            payload_auto_run
            if payload_auto_run is not None
            else bool(cfg.get("payload_auto_run", False))
        )
        resolved_net_delivery = (
            enable_network_delivery
            if enable_network_delivery is not None
            else bool(cfg.get("enable_network_delivery", False))
        )
        resolved_jackpot = (
            enable_jackpot if enable_jackpot is not None else bool(cfg.get("enable_jackpot", False))
        )
        resolved_web = (
            enable_web_interface if enable_web_interface is not None else bool(cfg.get("enable_web_interface", False))
        )

        self.state = state or AgentState()
        self.metrics_interval_s = resolved_metrics
        self.cfg = cfg
        self.recon = ReconWorker(self.state, cidr=resolved_cidr, interval_s=resolved_scan)
        self.gadget = GadgetManager(
            self.state,
            enable_on_start=resolved_gadget and not resolved_net_delivery,
            enable_hid=resolved_hid,
        )
        self.wifi = WifiHandshakeWorker(
            self.state,
            interface=str(cfg.get("wifi_interface", "wlan0")),
            interval_s=float(cfg.get("wifi_interval", 120.0)),
            deauth_count=int(cfg.get("handshake_deauth_count", 5)),
        )
        self.exploits = ExploitWorker(
            self.state,
            interval_s=float(cfg.get("exploit_interval", 180.0)),
        )
        payload_file = cfg.get("payload_file")
        payload_path = Path(payload_file) if payload_file else None
        if payload_path and not payload_path.is_absolute():
            payload_path = ROOT / payload_path
        self.payloads = PayloadRunner(
            self.state,
            payload_path=payload_path,
            auto_run=resolved_payload_auto,
            cfg=cfg,
        )
        # Network delivery (replaces USB gadget for payload transport)
        self.net_delivery: Optional[NetworkDelivery] = None
        if resolved_net_delivery:
            net_cfg = cfg.get("network_delivery", {})
            self.net_delivery = NetworkDelivery(
                self.state,
                mode=net_mode if net_mode else net_cfg.get("mode", "server"),
                port=net_port if net_port else int(net_cfg.get("port", 4444)),
                server_host=net_cfg.get("server_host", "0.0.0.0"),
                reverse_host=net_reverse_host or net_cfg.get("reverse_host"),
            )

        # Jackpot drone and watchdog
        self.jackpot_drone = None
        self.jackpot_watchdog = None
        self.web_thread = None
        self._enable_jackpot = resolved_jackpot
        self._enable_web = resolved_web
        self._jackpot_subnet = jackpot_subnet or cfg.get("jackpot_subnet", "192.168.1.0/24")
        self._jackpot_interval = jackpot_interval or int(cfg.get("jackpot_interval", 60))
        self._web_port = web_port or int(cfg.get("web_port", 8080))

        if self._enable_jackpot and JackpotWatchdog is not None:
            self.jackpot_watchdog = JackpotWatchdog(
                state=self.state,
                interval=5.0,
                threshold=2,
                subnet=self._jackpot_subnet,
            )
        if self._enable_web and run_web_server is not None:
            self.web_thread = threading.Thread(
                target=run_web_server,
                kwargs={"host": "0.0.0.0", "port": self._web_port, "debug": False},
                daemon=True,
            )

        self._enable_wifi = resolved_wifi
        self._enable_exploits = resolved_exploits
        self._enable_payload_triggers = bool(cfg.get("enable_payload_triggers", True))
        self._stop = threading.Event()
        self._threads: list[threading.Thread] = []

    def start(self) -> None:
        self._install_signals()
        self.state.push_log("daemon start")
        self.state.set_mode(Mode.IDLE)

        # Start gadget if enabled (and not using network delivery)
        if self.gadget.enable_on_start:
            self.state.set_mode(Mode.GADGET)
            try:
                self.gadget.start()
            except Exception as exc:
                logger.warning("gadget start error: %s", exc)
                self.state.push_log("gadget error")

        # Start network delivery if enabled
        if self.net_delivery:
            self.net_delivery.start()
            self.state.push_log("network delivery started")

        # Start jackpot watchdog if enabled
        if self.jackpot_watchdog:
            self.jackpot_watchdog.start()
            self.state.push_log("jackpot watchdog started")
            self.state.set_jackpot_armed(True)

        # Start web interface if enabled
        if self.web_thread:
            self.web_thread.start()
            self.state.push_log(f"web interface started on port {self._web_port}")

        self._threads = [
            threading.Thread(target=self._metrics_loop, name="metrics", daemon=True),
            threading.Thread(target=self.recon.run_loop, name="recon", daemon=True),
        ]
        if self._enable_wifi:
            self._threads.append(
                threading.Thread(target=self.wifi.run_loop, name="wifi", daemon=True)
            )
        if self._enable_exploits:
            self._threads.append(
                threading.Thread(target=self.exploits.run_loop, name="exploits", daemon=True)
            )
        if self._enable_payload_triggers or self.payloads.auto_run:
            listener = self.payloads.start_listener()
            if listener is not None:
                self._threads.append(listener)

        for t in self._threads:
            t.start()
        logger.info("orchestrator started (%d threads)", len(self._threads))

    def wait(self) -> None:
        while not self._stop.is_set():
            self._stop.wait(timeout=0.5)

    def shutdown(self) -> None:
        if self._stop.is_set():
            return
        logger.info("shutting down")
        self.state.set_mode(Mode.SHUTDOWN)
        self.state.push_log("shutdown")
        self._stop.set()
        self.recon.stop()
        self.wifi.stop()
        self.exploits.stop()
        self.payloads.stop()
        if self.net_delivery:
            self.net_delivery.stop()
        if self.jackpot_watchdog:
            self.jackpot_watchdog.stop()
        try:
            self.gadget.stop()
        except Exception as exc:
            logger.debug("gadget stop: %s", exc)
        # Stop session logger
        self.state.logger.stop()
        for t in self._threads:
            t.join(timeout=5.0)

    def _metrics_loop(self) -> None:
        psutil.cpu_percent(interval=None)
        while not self._stop.is_set():
            try:
                cpu = psutil.cpu_percent(interval=None)
                mem = psutil.virtual_memory()
                net = psutil.net_io_counters()
                self.state.update_metrics(
                    cpu,
                    mem.percent,
                    net.bytes_recv / 1024,
                    net.bytes_sent / 1024,
                )
            except Exception as exc:
                logger.debug("metrics error: %s", exc)
            self._stop.wait(timeout=self.metrics_interval_s)

    def _install_signals(self) -> None:
        def _handler(signum, _frame) -> None:
            logger.info("signal %s received", signum)
            self.shutdown()

        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                signal.signal(sig, _handler)
            except ValueError:
                logger.debug("could not install signal %s", sig)


def run_backend(
    cidr: Optional[str] = None,
    enable_gadget: bool = True,
    state: Optional[AgentState] = None,
    enable_network_delivery: bool = False,
    enable_jackpot: bool = False,
    enable_web: bool = False,
) -> AgentState:
    """Convenience entry used by main.py."""
    orch = BackendOrchestrator(
        state=state,
        cidr=cidr,
        enable_gadget=enable_gadget,
        enable_network_delivery=enable_network_delivery,
        enable_jackpot=enable_jackpot,
        enable_web_interface=enable_web,
    )
    orch.start()
    try:
        orch.wait()
    finally:
        orch.shutdown()
    return orch.state


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    run_backend()
