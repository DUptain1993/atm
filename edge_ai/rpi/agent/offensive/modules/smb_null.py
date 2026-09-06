"""SMB null session / open share probe."""

from __future__ import annotations

import socket
import subprocess

from agent.offensive.modules.base import ExploitModule
from agent.state import HostHit


class SmbNullModule(ExploitModule):
    name = "smb_null"
    ports = (445, 139)

    def run(self, host: HostHit) -> bool:
        if not any(p in host.open_ports for p in self.ports):
            return False
        if self._try_smbclient(host.ip):
            return True
        return self._try_socket(host.ip)

    def _try_smbclient(self, ip: str) -> bool:
        try:
            result = subprocess.run(
                ["smbclient", "-L", ip, "-N", "-g"],
                capture_output=True,
                text=True,
                timeout=8,
                check=False,
            )
            return result.returncode == 0 and "Disk" in result.stdout
        except (OSError, subprocess.SubprocessError):
            return False

    def _try_socket(self, ip: str) -> bool:
        for port in (445, 139):
            try:
                with socket.create_connection((ip, port), timeout=2.0) as sock:
                    sock.send(b"\x00\x00\x00\x85\xffSMB\x72\x00")
                    resp = sock.recv(128)
                    if resp and len(resp) > 4:
                        return True
            except OSError:
                continue
        return False
