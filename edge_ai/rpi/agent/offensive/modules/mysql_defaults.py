"""MySQL default / empty password check."""

from __future__ import annotations

import socket
import struct

from agent.offensive.modules.base import ExploitModule
from agent.state import HostHit


class MySqlDefaultsModule(ExploitModule):
    name = "mysql_defaults"
    ports = (3306,)

    def run(self, host: HostHit) -> bool:
        if 3306 not in host.open_ports:
            return False
        for user, password in (("root", ""), ("root", "root"), ("mysql", "")):
            if self._try_auth(host.ip, user, password):
                return True
        return False

    def _try_auth(self, ip: str, user: str, password: str) -> bool:
        try:
            with socket.create_connection((ip, 3306), timeout=3.0) as sock:
                greeting = sock.recv(256)
                if not greeting or greeting[0] != 0x0a:
                    return False
                # Minimal handshake response — server may accept empty auth on misconfigs.
                user_b = user.encode() + b"\x00"
                payload = struct.pack("<I", len(user_b) + 33)[:3] + bytes([0x01]) + user_b
                sock.send(payload[:4] + payload[4:])
                resp = sock.recv(64)
                return resp and resp[0] == 0x00
        except OSError:
            return False
