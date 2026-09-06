"""MongoDB open instance probe."""

from __future__ import annotations

import socket

from agent.offensive.modules.base import ExploitModule
from agent.state import HostHit


class MongoUnauthModule(ExploitModule):
    name = "mongo_unauth"
    ports = (27017,)

    def run(self, host: HostHit) -> bool:
        if 27017 not in host.open_ports:
            return False
        try:
            with socket.create_connection((host.ip, 27017), timeout=3.0) as sock:
                greeting = sock.recv(512)
                return len(greeting) > 0
        except OSError:
            return False
