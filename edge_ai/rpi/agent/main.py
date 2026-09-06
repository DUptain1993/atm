#!/usr/bin/env python3
"""Entry point: offensive blend — Pwnagotchi + Bjorn + P4wnP1 + Jackpot."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent.backend_worker import BackendOrchestrator, load_config
from agent.state import AgentState
from agent.ui.display_manager import DisplayManager


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="RPi offensive e-ink agent with jackpot extensions")
    p.add_argument("--cidr", default=None, help="Subnet to scan, e.g. 192.168.1.0/24")
    p.add_argument("--scan-interval", type=float, default=90.0)
    p.add_argument("--display-interval", type=float, default=12.0)
    p.add_argument(
        "--enable-gadget",
        action="store_true",
        help="USB RNDIS/ECM + HID composite gadget",
    )
    p.add_argument(
        "--no-gadget",
        action="store_true",
        help="Disable USB gadget at startup",
    )
    p.add_argument(
        "--payload-auto",
        action="store_true",
        help="Auto-run first payload when HID is ready",
    )
    p.add_argument(
        "--no-wifi",
        action="store_true",
        help="Disable WiFi handshake hunting",
    )
    p.add_argument(
        "--no-exploits",
        action="store_true",
        help="Disable Bjorn-style exploit chains",
    )
    p.add_argument(
        "--mock-display",
        action="store_true",
        help="PNG preview instead of Waveshare SPI",
    )
    p.add_argument(
        "--enable-network-delivery",
        action="store_true",
        help="Use TCP socket delivery instead of USB gadget",
    )
    p.add_argument(
        "--enable-jackpot",
        action="store_true",
        help="Enable XFS jackpot watchdog and autonomous drone",
    )
    p.add_argument(
        "--enable-web",
        action="store_true",
        help="Enable web interface dashboard",
    )
    p.add_argument(
        "--web-port",
        type=int,
        default=8080,
        help="Port for web interface",
    )
    p.add_argument("-v", "--verbose", action="store_true")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    cfg = load_config()
    display_interval = args.display_interval
    if display_interval == 12.0 and cfg.get("display_interval"):
        display_interval = float(cfg["display_interval"])

    enable_gadget = cfg.get("enable_gadget", True)
    if args.enable_gadget:
        enable_gadget = True
    if args.no_gadget:
        enable_gadget = False

    state = AgentState()
    orch = BackendOrchestrator(
        state=state,
        cidr=args.cidr,
        scan_interval_s=args.scan_interval,
        enable_gadget=enable_gadget,
        enable_wifi_hunt=not args.no_wifi,
        enable_exploits=not args.no_exploits,
        payload_auto_run=args.payload_auto or bool(cfg.get("payload_auto_run", False)),
        enable_network_delivery=args.enable_network_delivery or bool(cfg.get("enable_network_delivery", False)),
        enable_jackpot=args.enable_jackpot or bool(cfg.get("enable_jackpot", False)),
        enable_web_interface=args.enable_web or bool(cfg.get("enable_web_interface", False)),
        web_port=args.web_port,
    )
    display = DisplayManager(
        state=state,
        refresh_s=display_interval,
        use_hardware=not args.mock_display,
    )

    display.start()
    orch.start()
    try:
        orch.wait()
    finally:
        display.stop()
        orch.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
