"""RDP service reachability (Bjorn-style service pwn marker)."""

from __future__ import annotations

import socket

from agent.offensive.modules.base import ExploitModule
from agent.state import HostHit


class RdpProbeModule(ExploitModule):
    name = "rdp_probe"
    ports = (3389,)

    def run(self, host: HostHit) -> bool:
        if 3389 not in host.open_ports:
            return False
        try:
            with socket.create_connection((host.ip, 3389), timeout=3.0) as sock:
                banner = sock.recv(16)
                return banner.startswith(b"\x03\x00")
        except OSError:
            return False
