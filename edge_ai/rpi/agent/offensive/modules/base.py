"""Base class for Bjorn-style offensive modules."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Sequence, Tuple

from agent.state import HostHit


@dataclass
class ExploitResult:
    success: bool
    credentials: Tuple[str, str] = ("", "")
    extra: Dict[str, Any] = field(default_factory=dict)


class ExploitModule(ABC):
    name: str = "base"
    ports: Sequence[int] = ()

    @abstractmethod
    def run(self, host: HostHit) -> ExploitResult:
        """Attempt exploit; return ExploitResult with success and optional credentials."""

    def applicable(self, host: HostHit) -> bool:
        return any(p in host.open_ports for p in self.ports)
