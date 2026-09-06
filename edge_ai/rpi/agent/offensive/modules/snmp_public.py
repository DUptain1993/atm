"""SNMP public community string probe."""

from __future__ import annotations

import subprocess

from agent.offensive.modules.base import ExploitModule
from agent.state import HostHit


class SnmpPublicModule(ExploitModule):
    name = "snmp_public"
    ports = (161,)  # UDP — module probes even if TCP sweep missed it

    def run(self, host: HostHit) -> bool:
        try:
            result = subprocess.run(
                ["snmpwalk", "-v2c", "-c", "public", host.ip, "1.3.6.1.2.1.1.1.0"],
                capture_output=True,
                text=True,
                timeout=6,
                check=False,
            )
            return result.returncode == 0 and "Timeout" not in result.stderr
        except (OSError, subprocess.SubprocessError):
            return False
