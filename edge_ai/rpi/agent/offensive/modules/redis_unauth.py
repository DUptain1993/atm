"""Redis unauthenticated instance check."""

from __future__ import annotations

import socket

from agent.offensive.modules.base import ExploitModule
from agent.state import HostHit


class RedisUnauthModule(ExploitModule):
    name = "redis_unauth"
    ports = (6379,)

    def run(self, host: HostHit) -> bool:
        if 6379 not in host.open_ports:
            return False
        try:
            with socket.create_connection((host.ip, 6379), timeout=3.0) as sock:
                sock.sendall(b"PING\r\n")
                resp = sock.recv(128)
                return b"PONG" in resp.upper()
        except OSError:
            return False
