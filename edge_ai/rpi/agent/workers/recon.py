"""Lightweight local-subnet discovery worker (authorized networks only)."""

from __future__ import annotations

import concurrent.futures
import ipaddress
import logging
import socket
import subprocess
import time
from datetime import datetime, timezone
from typing import Iterable, List, Optional, Sequence

from agent.state import AgentState, HostHit, Mode

logger = logging.getLogger(__name__)

# Common service ports for Bjorn-style offensive sweep.
DEFAULT_PORTS: Sequence[int] = (
    21, 22, 23, 53, 80, 139, 161, 443, 445, 3306, 3389, 5900, 6379, 8080, 27017,
)


def _default_cidr() -> str:
    """Best-effort local IPv4 /24 from the default route interface."""
    try:
        out = subprocess.check_output(
            ["ip", "-4", "route", "get", "1.1.1.1"],
            text=True,
            timeout=3,
        )
        parts = out.split()
        if "src" in parts:
            src = parts[parts.index("src") + 1]
            net = ipaddress.ip_network(f"{src}/24", strict=False)
            return str(net)
    except (OSError, subprocess.SubprocessError, ValueError) as exc:
        logger.debug("cidr detect failed: %s", exc)
    return "192.168.1.0/24"


def _ping_rtt(ip: str, timeout_s: float = 1.0) -> Optional[float]:
    """Return RTT in seconds, or None if unreachable."""
    try:
        start = time.monotonic()
        result = subprocess.run(
            ["ping", "-c", "1", "-W", str(max(1, int(timeout_s))), ip],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=timeout_s + 1.0,
            check=False,
        )
        if result.returncode == 0:
            return time.monotonic() - start
    except (OSError, subprocess.SubprocessError):
        pass
    return None


def _probe_port(ip: str, port: int, timeout_s: float = 0.35) -> bool:
    try:
        with socket.create_connection((ip, port), timeout=timeout_s):
            return True
    except OSError:
        return False


def _resolve_hostname(ip: str) -> str:
    try:
        name, _, _ = socket.gethostbyaddr(ip)
        return name
    except OSError:
        return ""


def scan_host(ip: str, ports: Sequence[int] = DEFAULT_PORTS) -> Optional[HostHit]:
    rtt = _ping_rtt(ip)
    if rtt is None:
        return None
    # Adaptive timeout: base 0.3s + 2 * RTT, but at least 0.3s
    port_timeout = max(0.3, rtt * 2)
    open_ports = [p for p in ports if _probe_port(ip, p, timeout_s=port_timeout)]
    return HostHit(
        ip=ip,
        hostname=_resolve_hostname(ip),
        open_ports=open_ports,
        last_seen=datetime.now(timezone.utc).isoformat(),
    )


def iter_hosts(cidr: str) -> Iterable[str]:
    network = ipaddress.ip_network(cidr, strict=False)
    for host in network.hosts():
        yield str(host)


class ReconWorker:
    """Periodic subnet sweep; updates AgentState with live hosts."""

    def __init__(
        self,
        state: AgentState,
        cidr: Optional[str] = None,
        interval_s: float = 60.0,
        max_workers: int = 32,
        ports: Sequence[int] = DEFAULT_PORTS,
    ) -> None:
        self.state = state
        self.cidr = cidr or _default_cidr()
        self.interval_s = interval_s
        self.max_workers = max_workers
        self.ports = ports
        self._stop = False

    def stop(self) -> None:
        self._stop = True

    def run_once(self) -> List[HostHit]:
        self.state.set_mode(Mode.SCANNING)
        self.state.push_log(f"scan {self.cidr}")
        targets = list(iter_hosts(self.cidr))
        hits: List[HostHit] = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as pool:
            futures = {pool.submit(scan_host, ip, self.ports): ip for ip in targets}
            for fut in concurrent.futures.as_completed(futures):
                if self._stop:
                    break
                try:
                    hit = fut.result()
                except Exception as exc:  # noqa: BLE001 — keep worker alive
                    logger.debug("host scan error: %s", exc)
                    continue
                if hit:
                    hits.append(hit)

        hits.sort(key=lambda h: tuple(int(x) for x in h.ip.split(".")))
        self.state.set_hosts(hits)
        self.state.record_scan_complete(len(hits))
        self.state.push_log(f"found {len(hits)} hosts")
        if not self._stop:
            self.state.set_mode(Mode.ACTIVE if hits else Mode.IDLE)
        return hits

    def run_loop(self) -> None:
        while not self._stop:
            try:
                self.run_once()
            except Exception as exc:  # noqa: BLE001
                logger.exception("recon cycle failed")
                self.state.set_error(str(exc))
            deadline = time.monotonic() + self.interval_s
            while not self._stop and time.monotonic() < deadline:
                time.sleep(0.25)
