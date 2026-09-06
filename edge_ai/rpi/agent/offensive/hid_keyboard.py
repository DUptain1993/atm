"""Linux USB HID gadget keyboard driver (/dev/hidg0)."""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Sequence

logger = logging.getLogger(__name__)

HID_DEVICE = Path("/dev/hidg0")

# Modifier bit masks
MOD = {"CTRL": 0x01, "SHIFT": 0x02, "ALT": 0x04, "GUI": 0x08}

# HID usage IDs (USB HID spec) for common keys
KEYS: Dict[str, int] = {
    "A": 0x04, "B": 0x05, "C": 0x06, "D": 0x07, "E": 0x08, "F": 0x09,
    "G": 0x0a, "H": 0x0b, "I": 0x0c, "J": 0x0d, "K": 0x0e, "L": 0x0f,
    "M": 0x10, "N": 0x11, "O": 0x12, "P": 0x13, "Q": 0x14, "R": 0x15,
    "S": 0x16, "T": 0x17, "U": 0x18, "V": 0x19, "W": 0x1a, "X": 0x1b,
    "Y": 0x1c, "Z": 0x1d,
    "1": 0x1e, "2": 0x1f, "3": 0x20, "4": 0x21, "5": 0x22, "6": 0x23,
    "7": 0x24, "8": 0x25, "9": 0x26, "0": 0x27,
    "ENTER": 0x28, "ESC": 0x29, "SPACE": 0x2c, "TAB": 0x2b,
    "-": 0x2d, "=": 0x2e, "[": 0x2f, "]": 0x30, "\\": 0x31,
    ";": 0x33, "'": 0x34, "`": 0x35, ",": 0x36, ".": 0x37, "/": 0x38,
}

SHIFT_CHARS = {
    "!": "1", "@": "2", "#": "3", "$": "4", "%": "5", "^": "6",
    "&": "7", "*": "8", "(": "9", ")": "0",
}


class HidKeyboard:
    """Write 8-byte HID keyboard reports to the gadget device."""

    def __init__(self, device: Path = HID_DEVICE, mock: bool = False) -> None:
        self.device = device
        self.mock = mock or not device.exists()

    def available(self) -> bool:
        return not self.mock

    def _write_report(self, modifiers: int, keys: Sequence[int]) -> None:
        report = bytes([modifiers, 0x00] + list(keys[:6]) + [0x00] * (6 - min(len(keys), 6)))
        if self.mock:
            logger.debug("HID mock report: %s", report.hex())
            return
        with open(self.device, "wb", buffering=0) as hid:
            hid.write(report)
            # Release keys
            hid.write(bytes(8))

    def press_key(self, key: str, modifiers: int = 0) -> None:
        usage = KEYS.get(key.upper())
        if usage is None:
            logger.debug("unknown key: %s", key)
            return
        self._write_report(modifiers, [usage])
        time.sleep(0.02)

    def press_combo(self, keys: List[str]) -> None:
        mods = 0
        usages: List[int] = []
        for k in keys:
            ku = k.upper()
            if ku in MOD:
                mods |= MOD[ku]
            elif ku in KEYS:
                usages.append(KEYS[ku])
        self._write_report(mods, usages)
        time.sleep(0.02)

    def type_string(self, text: str) -> None:
        for ch in text:
            if ch == "\n":
                self.press_key("ENTER")
                continue
            if ch in SHIFT_CHARS:
                base = SHIFT_CHARS[ch]
                self.press_key(base, MOD["SHIFT"])
                continue
            if ch == " ":
                self.press_key("SPACE")
                continue
            if ch.isupper():
                self.press_key(ch, MOD["SHIFT"])
            elif ch in KEYS:
                self.press_key(ch)
            else:
                logger.debug("skip char: %r", ch)
            time.sleep(0.01)
