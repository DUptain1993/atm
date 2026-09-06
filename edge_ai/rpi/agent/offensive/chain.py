"""Bjorn-style exploit chain runner."""

from __future__ import annotations

import logging
from typing import List

from agent.offensive.modules import MODULES, PORT_MAP
from agent.state import AgentState, HostHit, Mode

logger = logging.getLogger(__name__)


class ExploitChain:
    """Run port-matched modules against recon results."""

    def __init__(self, state: AgentState, modules: List | None = None) -> None:
        self.state = state
        self.modules = modules or MODULES

    def run_chain(self, hosts: List[HostHit]) -> int:
        wins = 0
        self.state.set_mode(Mode.ATTACKING)
        for host in hosts:
            modules_to_run: list = []
            for port in host.open_ports:
                modules_to_run.extend(PORT_MAP.get(port, []))
            for mod in self.modules:
                if mod.name == "snmp_public":
                    modules_to_run.append(mod)
            seen = set()
            for mod in modules_to_run:
                if mod.name in seen:
                    continue
                seen.add(mod.name)
                try:
                    result = mod.run(host)
                    self.state.record_exploit(
                        mod.name,
                        host.ip,
                        result.success,
                        result.credentials,
                    )
                    if result.success:
                        wins += 1
                        # Additional logging for credentials
                        if result.credentials and result.credentials != ("", ""):
                            logger.info("Credentials found: %s@%s", result.credentials[0], host.ip)
                except Exception as exc:  # noqa: BLE001
                    logger.debug("module %s failed: %s", mod.name, exc)
                    self.state.record_exploit(mod.name, host.ip, False)
        return wins
