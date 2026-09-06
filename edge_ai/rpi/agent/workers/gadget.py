"""USB gadget helpers via ConfigFS (RNDIS/ECM + optional HID keyboard)."""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional

from agent.state import AgentState

logger = logging.getLogger(__name__)

CONFIGFS_ROOT = Path("/sys/kernel/config/usb_gadget")
GADGET_NAME = "rpi_agent"
SCRIPT_PATH = Path(__file__).resolve().parents[2] / "scripts" / "usb_gadget.sh"
HID_DEVICE = Path("/dev/hidg0")


class GadgetManager:
    """
    P4wnP1-inspired composite USB gadget: ethernet tether + HID keyboard.

    Requires root and dwc2/libcomposite on the Pi Zero USB port.
    """

    def __init__(
        self,
        state: AgentState,
        enable_on_start: bool = False,
        enable_hid: bool = True,
    ) -> None:
        self.state = state
        self.enable_on_start = enable_on_start
        self.enable_hid = enable_hid

    def available(self) -> bool:
        return CONFIGFS_ROOT.exists() and os.geteuid() == 0

    def start(self) -> bool:
        if not self.enable_on_start:
            self.state.push_log("gadget skipped")
            return False
        if SCRIPT_PATH.exists():
            return self._run_script("start")
        return self._start_inline()

    def stop(self) -> None:
        if SCRIPT_PATH.exists():
            self._run_script("stop")
        else:
            self._stop_inline()
        self.state.set_gadget(False, hid=False)

    def _run_script(self, action: str) -> bool:
        hid_arg = "hid" if self.enable_hid else "nohid"
        try:
            subprocess.run(
                ["bash", str(SCRIPT_PATH), action, hid_arg],
                check=True,
                timeout=30,
                capture_output=True,
                text=True,
            )
            iface = self._detect_iface()
            hid = self.enable_hid and HID_DEVICE.exists()
            self.state.set_gadget(action == "start", iface or "usb0", hid=hid)
            return action == "start"
        except (OSError, subprocess.SubprocessError) as exc:
            logger.warning("gadget script %s failed: %s", action, exc)
            self.state.push_log(f"gadget {action} fail")
            return False

    def _start_inline(self) -> bool:
        if not self.available():
            self.state.push_log("gadget unavailable")
            logger.info("ConfigFS gadget unavailable (need root + libcomposite)")
            return False
        try:
            g = CONFIGFS_ROOT / GADGET_NAME
            g.mkdir(parents=True, exist_ok=True)
            (g / "idVendor").write_text("0x1d6b\n")
            (g / "idProduct").write_text("0x0104\n")
            (g / "bcdDevice").write_text("0x0100\n")
            (g / "bcdUSB").write_text("0x0200\n")

            strings = g / "strings" / "0x409"
            strings.mkdir(parents=True, exist_ok=True)
            (strings / "serialnumber").write_text("rpi-agent-001\n")
            (strings / "manufacturer").write_text("RPiAgent\n")
            (strings / "product").write_text("RPi USB Attack\n")

            funcs = g / "functions"
            rndis = funcs / "rndis.usb0"
            ecm = funcs / "ecm.usb0"
            rndis.mkdir(parents=True, exist_ok=True)
            ecm.mkdir(parents=True, exist_ok=True)

            links = [rndis, ecm]
            if self.enable_hid:
                hid = funcs / "hid.usb0"
                hid.mkdir(parents=True, exist_ok=True)
                (hid / "protocol").write_text("1\n")
                (hid / "subclass").write_text("1\n")
                (hid / "report_length").write_text("8\n")
                report = bytes([
                    0x05, 0x01, 0x09, 0x06, 0xa1, 0x01, 0x05, 0x07,
                    0x19, 0xe0, 0x29, 0xe7, 0x15, 0x00, 0x25, 0x01,
                    0x75, 0x01, 0x95, 0x08, 0x81, 0x02, 0x95, 0x01,
                    0x75, 0x08, 0x81, 0x03, 0x95, 0x05, 0x75, 0x01,
                    0x05, 0x08, 0x19, 0x01, 0x29, 0x05, 0x91, 0x02,
                    0x95, 0x01, 0x75, 0x03, 0x91, 0x03, 0x95, 0x06,
                    0x75, 0x08, 0x15, 0x00, 0x25, 0x65, 0x05, 0x07,
                    0x19, 0x00, 0x29, 0x65, 0x81, 0x00, 0xc0,
                ])
                (hid / "report_desc").write_bytes(report)
                links.append(hid)

            cfg = g / "configs" / "c.1"
            cfg.mkdir(parents=True, exist_ok=True)
            (cfg / "strings" / "0x409").mkdir(parents=True, exist_ok=True)
            (cfg / "strings" / "0x409" / "configuration").write_text("RNDIS+ECM+HID\n")
            (cfg / "MaxPower").write_text("250\n")

            for fn in links:
                link = cfg / fn.name
                if not link.exists():
                    link.symlink_to(fn)

            udc_dir = Path("/sys/class/udc")
            udcs = list(udc_dir.iterdir()) if udc_dir.exists() else []
            if not udcs:
                raise RuntimeError("no UDC controller found")
            (g / "UDC").write_text(udcs[0].name + "\n")

            iface = self._detect_iface() or "usb0"
            hid_ok = self.enable_hid and HID_DEVICE.exists()
            self.state.set_gadget(True, iface, hid=hid_ok)
            return True
        except OSError as exc:
            logger.warning("inline gadget start failed: %s", exc)
            self.state.push_log("gadget start fail")
            return False

    def _stop_inline(self) -> None:
        g = CONFIGFS_ROOT / GADGET_NAME
        if not g.exists():
            return
        try:
            (g / "UDC").write_text("\n")
        except OSError:
            pass
        cfg = g / "configs" / "c.1"
        if cfg.exists():
            for child in cfg.iterdir():
                if child.is_symlink():
                    child.unlink()
            strings = cfg / "strings" / "0x409"
            if strings.exists():
                shutil.rmtree(strings, ignore_errors=True)
            try:
                cfg.rmdir()
            except OSError:
                pass
        funcs = g / "functions"
        if funcs.exists():
            for child in funcs.iterdir():
                shutil.rmtree(child, ignore_errors=True)
        strings = g / "strings" / "0x409"
        if strings.exists():
            shutil.rmtree(strings, ignore_errors=True)
        try:
            g.rmdir()
        except OSError:
            pass

    @staticmethod
    def _detect_iface() -> Optional[str]:
        for name in ("usb0", "usb1"):
            if Path(f"/sys/class/net/{name}").exists():
                return name
        return None
