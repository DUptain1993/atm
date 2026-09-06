"""HTTP sensitive path discovery."""

from __future__ import annotations

import urllib.error
import urllib.request

from agent.offensive.modules.base import ExploitModule
from agent.state import HostHit

SENSITIVE_PATHS = (
    "/.env",
    "/admin",
    "/phpmyadmin/",
    "/server-status",
    "/.git/HEAD",
)


class HttpSensitiveModule(ExploitModule):
    name = "http_sensitive"
    ports = (80, 8080, 443)

    def run(self, host: HostHit) -> bool:
        ports = [p for p in host.open_ports if p in self.ports]
        if not ports:
            return False
        for port in ports:
            scheme = "https" if port == 443 else "http"
            for path in SENSITIVE_PATHS:
                url = f"{scheme}://{host.ip}:{port}{path}"
                try:
                    with urllib.request.urlopen(url, timeout=4.0) as resp:
                        if resp.status < 400:
                            return True
                except urllib.error.HTTPError as exc:
                    if exc.code in (401, 403):
                        return True
                except Exception:
                    continue
        return False
