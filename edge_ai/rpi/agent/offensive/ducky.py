"""P4wnP1-style DuckyScript interpreter for HID payloads."""

from __future__ import annotations

import re
import time
from pathlib import Path
from typing import Callable, List, Optional

from agent.offensive.hid_keyboard import HidKeyboard

DelayFn = Callable[[int], None]


class DuckyRunner:
    """Execute DuckyScript payloads via USB HID keyboard gadget."""

    def __init__(
        self,
        keyboard: Optional[HidKeyboard] = None,
        delay_fn: Optional[DelayFn] = None,
    ) -> None:
        self.keyboard = keyboard or HidKeyboard()
        self._delay = delay_fn or (lambda ms: time.sleep(ms / 1000.0))

    def run_file(self, path: Path) -> None:
        lines = path.read_text().splitlines()
        self.run_lines(lines)

    def run_lines(self, lines: List[str]) -> None:
        for raw in lines:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            self._exec(line)

    def _exec(self, line: str) -> None:
        upper = line.upper()
        if upper.startswith("DELAY "):
            ms = int(upper.split()[1])
            self._delay(ms)
        elif upper.startswith("STRING "):
            text = line[7:]
            self.keyboard.type_string(text)
        elif upper == "ENTER":
            self.keyboard.press_key("ENTER")
        elif upper.startswith("REPEAT "):
            count = int(upper.split()[1])
            for _ in range(count):
                self.keyboard.press_key("ENTER")
        elif upper.startswith("ALT "):
            key = upper.split()[1]
            self.keyboard.press_combo(["ALT", key])
        elif upper.startswith("GUI "):
            key = upper.split()[1]
            self.keyboard.press_combo(["GUI", key])
        elif re.match(r"^[A-Z0-9]$", upper):
            self.keyboard.press_key(upper)
