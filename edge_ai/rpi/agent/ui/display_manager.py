"""Waveshare 2.13\" tri-color e-ink UI (Pwnagotchi-style offensive telemetry)."""

from __future__ import annotations

import logging
import threading
from pathlib import Path
from typing import Optional, Tuple

from PIL import Image, ImageDraw, ImageFont

from agent.state import AgentState, Mode

logger = logging.getLogger(__name__)

EPD_WIDTH = 250
EPD_HEIGHT = 122


def _load_font(size: int) -> ImageFont.ImageFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    return ImageFont.load_default()


class DisplayManager:
    """Independent refresh loop for offensive telemetry on e-ink."""

    def __init__(
        self,
        state: AgentState,
        refresh_s: float = 12.0,
        mock_dir: Optional[Path] = None,
        use_hardware: bool = True,
    ) -> None:
        self.state = state
        self.refresh_s = refresh_s
        self.mock_dir = mock_dir or Path(__file__).resolve().parents[2] / "logs"
        self.use_hardware = use_hardware
        self._stop = threading.Event()
        self._epd = None
        self._font_md = _load_font(11)
        self._font_sm = _load_font(9)
        self._refresh_count = 0

    def start(self) -> threading.Thread:
        t = threading.Thread(target=self.run_loop, name="display", daemon=True)
        t.start()
        return t

    def stop(self) -> None:
        self._stop.set()

    def run_loop(self) -> None:
        try:
            self._init_epd()
        except Exception as exc:
            logger.warning("display init failed, using mock frames: %s", exc)
            self.state.push_log("display mock")
            self._epd = None

        while not self._stop.is_set():
            try:
                self.render_once()
                self._refresh_count += 1
            except Exception as exc:
                logger.warning("display refresh error: %s", exc)
                self.state.push_log("display err")
            self._stop.wait(timeout=self.refresh_s)

        self._sleep_epd()

    def render_once(self) -> None:
        snap = self.state.snapshot()
        black, red = self._compose(snap)

        if self._epd is not None:
            self._push_hardware(black, red)
        else:
            self.mock_dir.mkdir(parents=True, exist_ok=True)
            out = self.mock_dir / "eink_preview.png"
            preview = black.convert("RGB")
            red_overlay = Image.new("RGB", (EPD_WIDTH, EPD_HEIGHT), (180, 0, 0))
            mask = red.point(lambda p: 255 if p < 128 else 0).convert("L")
            preview.paste(red_overlay, (0, 0), mask)
            preview.save(out)

    def _compose(self, snap: dict) -> Tuple[Image.Image, Image.Image]:
        black = Image.new("1", (EPD_WIDTH, EPD_HEIGHT), 255)
        red = Image.new("1", (EPD_WIDTH, EPD_HEIGHT), 255)
        db = ImageDraw.Draw(black)
        dr = ImageDraw.Draw(red)

        mode: Mode = snap["mode"]
        uptime = snap["uptime_s"]
        hh, rem = divmod(uptime, 3600)
        mm, ss = divmod(rem, 60)

        db.rectangle((0, 0, EPD_WIDTH - 1, EPD_HEIGHT - 1), outline=0, width=1)
        db.rectangle((0, 0, EPD_WIDTH - 1, 18), outline=0, width=1)

        db.text((4, 3), "RPi-Agent", font=self._font_md, fill=0)
        mode_label = mode.value.upper()
        hs = snap.get("handshakes_captured", 0)
        header_right = f"{mode_label}  HS:{hs}"
        accent_modes = (
            Mode.SCANNING,
            Mode.ACTIVE,
            Mode.HANDSHAKE,
            Mode.ATTACKING,
            Mode.PAYLOAD,
            Mode.ERROR,
        )
        accent = dr if mode in accent_modes else db
        accent.text(
            (max(4, EPD_WIDTH - 4 - len(header_right) * 6), 3),
            header_right,
            font=self._font_md,
            fill=0,
        )

        db.line((0, 18, EPD_WIDTH, 18), fill=0)
        peers = snap.get("session_peers", 0)
        deauths = snap.get("session_deauths", 0)
        pwned = snap.get("session_pwned", 0)
        pl_ok = snap.get("session_payloads_ok", 0)
        pl_run = snap.get("session_payloads_run", 0)
        ch = snap.get("session_channel", "") or "-"
        db.text((4, 22), f"PEERS:{peers}", font=self._font_sm, fill=0)
        db.text((70, 22), f"DEAUTH:{deauths}", font=self._font_sm, fill=0)
        dr.text((145, 22), f"PWN:{pwned}", font=self._font_sm, fill=0)

        db.line((0, 36, EPD_WIDTH, 36), fill=0)
        aps = snap.get("wifi_aps_seen", 0)
        exp_run = snap.get("exploits_run", 0)
        exp_ok = snap.get("exploits_success", 0)
        db.text((4, 40), f"APs:{aps} HOSTS:{snap['hosts_found']}", font=self._font_sm, fill=0)
        db.text((130, 40), f"EXP:{exp_ok}/{exp_run}", font=self._font_sm, fill=0)
        db.text((200, 40), f"CH:{ch}", font=self._font_sm, fill=0)

        db.line((0, 52, EPD_WIDTH, 52), fill=0)
        db.text(
            (4, 56),
            f"CPU {snap['cpu_percent']:.0f}% RAM {snap['ram_percent']:.0f}%",
            font=self._font_sm,
            fill=0,
        )
        db.text((140, 56), f"UP {hh:02d}:{mm:02d}:{ss:02d}", font=self._font_sm, fill=0)

        db.line((0, 70, EPD_WIDTH, 70), fill=0)
        if snap.get("payload_active"):
            dr.text(
                (4, 74),
                f"RUN {snap.get('payload_name', '')[:22]}",
                font=self._font_sm,
                fill=0,
            )
        else:
            gadget = "ON" if snap["gadget_active"] else "OFF"
            hid = "HID" if snap.get("hid_ready") else "---"
            db.text((4, 74), f"GAD:{gadget}+{hid} PLD:{pl_ok}/{pl_run}", font=self._font_sm, fill=0)
            target = snap.get("wifi_target_essid") or snap.get("wifi_target_bssid") or "-"
            target_short = target[:12] if len(target) <= 12 else target[:9] + "..."
            accent_target = dr if mode == Mode.HANDSHAKE else db
            accent_target.text((130, 74), target_short, font=self._font_sm, fill=0)

        db.line((0, 86, EPD_WIDTH, 86), fill=0)
        y = 90
        for line in snap["log_lines"][:2]:
            text = line if len(line) <= 38 else line[:35] + "..."
            db.text((4, y), text, font=self._font_sm, fill=0)
            y += 10

        return black, red

    def _init_epd(self) -> None:
        if not self.use_hardware:
            self._epd = None
            return
        try:
            try:
                from waveshare_epd import epd2in13b_V4 as epd_mod
            except ImportError:
                from waveshare_epd import epd2in13_V4 as epd_mod

            epd = epd_mod.EPD()
            epd.init()
            try:
                epd.Clear()
            except Exception:
                pass
            self._epd = epd
            self.state.push_log("display ready")
            logger.info("e-ink initialized (%sx%s)", EPD_WIDTH, EPD_HEIGHT)
        except ImportError:
            logger.info("waveshare_epd not installed — mock display")
            self._epd = None

    def _push_hardware(self, black: Image.Image, red: Image.Image) -> None:
        epd = self._epd
        assert epd is not None
        try:
            # Schedule full refresh every 5 iterations (approx every 60s) to prevent ghosting
            if self._refresh_count % 5 == 0:
                # Full refresh
                epd.display(epd.getbuffer(black), epd.getbuffer(red))
            else:
                # Partial refresh (if supported) – but many e-papers only have global refresh.
                # We'll use the same method but could add a partial update if API exists.
                epd.display(epd.getbuffer(black), epd.getbuffer(red))
        except TypeError:
            epd.display(epd.getbuffer(black))

    def _sleep_epd(self) -> None:
        if self._epd is None:
            return
        try:
            self._epd.sleep()
        except Exception as exc:
            logger.debug("epd sleep: %s", exc)
