#!/usr/bin/env python3
"""Root-level shim for agent.ui.display_manager."""
import argparse
import logging

from agent.state import AgentState, Mode
from agent.ui.display_manager import DisplayManager

__all__ = ["DisplayManager"]


def run_display(mock: bool = False, refresh_s: float = 12.0) -> None:
    """Standalone display test loop with a dummy shared state."""
    logging.basicConfig(level=logging.INFO)
    state = AgentState()
    state.set_mode(Mode.ACTIVE)
    state.push_log("display standalone")
    state.update_metrics(12.3, 45.6, 1024.0, 2048.0)

    display = DisplayManager(state=state, refresh_s=refresh_s, use_hardware=not mock)
    display.start()
    try:
        while True:
            import time

            time.sleep(1.0)
    except KeyboardInterrupt:
        display.stop()


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="E-ink display loop")
    p.add_argument("--mock", action="store_true", help="PNG preview instead of SPI hardware")
    p.add_argument("--refresh", type=float, default=12.0, help="Seconds between refreshes")
    args = p.parse_args()
    run_display(mock=args.mock, refresh_s=args.refresh)
