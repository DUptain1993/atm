"""VNC RFB handshake probe."""

from __future__ import annotations

import socket

from agent.offensive.modules.base import ExploitModule
from agent.state import HostHit


class VncProbeModule(ExploitModule):
    name = "vnc_probe"
    ports = (5900, 5901)

    def run(self, host: HostHit) -> bool:
        ports = [p for p in host.open_ports if p in self.ports]
        if not ports:
            return False
        for port in ports:
            try:
                with socket.create_connection((host.ip, port), timeout=3.0) as sock:
                    banner = sock.recv(12)
                    if banner.startswith(b"RFB"):
                        return True
            except OSError:
                continue
        return False
