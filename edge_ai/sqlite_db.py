#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sqlite_db.py - SQLite database manager with full jackpot logging
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Any, Tuple

class BrainDB:
    """SQLite database manager for agent memory and jackpot logging"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._initialize_db()
    
    def _connect(self) -> sqlite3.Connection:
        """Create database connection with row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _initialize_db(self) -> None:
        """Initialize all database tables"""
        conn = self._connect()
        c = conn.cursor()
        
        # ============================================================
        # 1. Conversation Memory
        # ============================================================
        c.execute('''
            CREATE TABLE IF NOT EXISTS memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_input TEXT,
                ai_response TEXT,
                timestamp TEXT,
                context_hash TEXT,
                session_id TEXT
            )
        ''')
        
        # Index for faster retrieval
        c.execute('CREATE INDEX IF NOT EXISTS idx_memory_session ON memory(session_id)')
        
        # ============================================================
        # 2. Feedback / Reinforcement Learning
        # ============================================================
        c.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_input TEXT,
                ai_response TEXT,
                is_good INTEGER,
                timestamp TEXT,
                session_id TEXT
            )
        ''')
        
        # ============================================================
        # 3. XFS Command Execution Log
        # ============================================================
        c.execute('''
            CREATE TABLE IF NOT EXISTS xfs_commands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                command TEXT,
                args TEXT,
                target_ip TEXT,
                target_port INTEGER,
                result TEXT,
                success INTEGER,
                response_time_ms INTEGER,
                timestamp TEXT
            )
        ''')
        
        c.execute('CREATE INDEX IF NOT EXISTS idx_xfs_target ON xfs_commands(target_ip)')
        
        # ============================================================
        # 4. Jackpot Attempts
        # ============================================================
        c.execute('''
            CREATE TABLE IF NOT EXISTS jackpot_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                attempt_type TEXT,
                target_ip TEXT,
                target_port INTEGER,
                commands TEXT,
                results TEXT,
                success INTEGER,
                amount_dispensed INTEGER,
                timestamp TEXT
            )
        ''')
        
        c.execute('CREATE INDEX IF NOT EXISTS idx_jackpot_ip ON jackpot_attempts(target_ip)')
        
        # ============================================================
        # 5. Device Scans
        # ============================================================
        c.execute('''
            CREATE TABLE IF NOT EXISTS device_scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_results TEXT,
                devices_found TEXT,
                target_count INTEGER,
                timestamp TEXT
            )
        ''')
        
        # ============================================================
        # 6. Execution History (All Tool Calls)
        # ============================================================
        c.execute('''
            CREATE TABLE IF NOT EXISTS execution_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tool TEXT,
                args TEXT,
                result TEXT,
                error TEXT,
                execution_time_ms INTEGER,
                timestamp TEXT
            )
        ''')
        
        # ============================================================
        # 7. Detected Targets
        # ============================================================
        c.execute('''
            CREATE TABLE IF NOT EXISTS targets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip TEXT,
                port INTEGER,
                device_type TEXT,
                first_seen TEXT,
                last_seen TEXT,
                scan_count INTEGER DEFAULT 1,
                is_active INTEGER DEFAULT 1
            )
        ''')
        
        c.execute('CREATE INDEX IF NOT EXISTS idx_targets_ip ON targets(ip)')
        
        # ============================================================
        # 8. Command Templates (for RAG injection)
        # ============================================================
        c.execute('''
            CREATE TABLE IF NOT EXISTS command_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trigger_phrase TEXT,
                command TEXT,
                description TEXT,
                use_count INTEGER DEFAULT 0,
                created_at TEXT
            )
        ''')
        
        # ============================================================
        # 9. Session Management
        # ============================================================
        c.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE,
                started_at TEXT,
                ended_at TEXT,
                command_count INTEGER DEFAULT 0,
                jackpot_attempts INTEGER DEFAULT 0
            )
        ''')
        
        # ============================================================
        # 10. Network Activity Log
        # ============================================================
        c.execute('''
            CREATE TABLE IF NOT EXISTS network_activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target_ip TEXT,
                target_port INTEGER,
                activity_type TEXT,
                payload_size INTEGER,
                response_time_ms INTEGER,
                timestamp TEXT
            )
        ''')
        
        c.execute('CREATE INDEX IF NOT EXISTS idx_network_ip ON network_activity(target_ip)')
        
        # ============================================================
        # Commit and close
        # ============================================================
        conn.commit()
        conn.close()
    
    # ========================================================================
    # MEMORY OPERATIONS
    # ========================================================================
    
    def add_memory(self, user_input: str, ai_response: str, session_id: str = None) -> int:
        """Add conversation to memory, returns ID"""
        conn = self._connect()
        c = conn.cursor()
        c.execute(
            "INSERT INTO memory (user_input, ai_response, timestamp, session_id) VALUES (?, ?, ?, ?)",
            (user_input, ai_response, datetime.now().isoformat(), session_id)
        )
        conn.commit()
        row_id = c.lastrowid
        conn.close()
        return row_id
    
    def get_recent(self, limit: int = 50, session_id: str = None) -> List[Tuple]:
        """Get recent conversations"""
        conn = self._connect()
        c = conn.cursor()
        
        if session_id:
            c.execute(
                "SELECT user_input, ai_response, timestamp FROM memory WHERE session_id = ? ORDER BY id DESC LIMIT ?",
                (session_id, limit)
            )
        else:
            c.execute(
                "SELECT user_input, ai_response, timestamp FROM memory ORDER BY id DESC LIMIT ?",
                (limit,)
            )
        
        results = c.fetchall()
        conn.close()
        return [(r['user_input'], r['ai_response'], r['timestamp']) for r in results]
    
    def get_memory_count(self, session_id: str = None) -> int:
        """Get total memory count"""
        conn = self._connect()
        c = conn.cursor()
        
        if session_id:
            c.execute("SELECT COUNT(*) FROM memory WHERE session_id = ?", (session_id,))
        else:
            c.execute("SELECT COUNT(*) FROM memory")
        
        count = c.fetchone()[0]
        conn.close()
        return count
    
    # ========================================================================
    # FEEDBACK OPERATIONS
    # ========================================================================
    
    def save_feedback(self, user_input: str, ai_response: str, is_good: bool, session_id: str = None) -> int:
        """Save reinforcement feedback"""
        conn = self._connect()
        c = conn.cursor()
        c.execute(
            "INSERT INTO feedback (user_input, ai_response, is_good, timestamp, session_id) VALUES (?, ?, ?, ?, ?)",
            (user_input, ai_response, 1 if is_good else 0, datetime.now().isoformat(), session_id)
        )
        conn.commit()
        row_id = c.lastrowid
        conn.close()
        return row_id
    
    def get_feedback_count(self) -> int:
        """Get total feedback records"""
        conn = self._connect()
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM feedback")
        count = c.fetchone()[0]
        conn.close()
        return count
    
    def get_feedback_ratio(self) -> float:
        """Get ratio of good to total feedback"""
        conn = self._connect()
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM feedback WHERE is_good = 1")
        good = c.fetchone()[0] or 0
        c.execute("SELECT COUNT(*) FROM feedback")
        total = c.fetchone()[0] or 1
        conn.close()
        return good / total
    
    # ========================================================================
    # XFS COMMAND LOGGING
    # ========================================================================
    
    def log_xfs_command(self, command: str, args: str, target_ip: str, target_port: int, 
                         result: str, response_time_ms: int = 0) -> int:
        """Log XFS command execution"""
        success = 1 if result and "error" not in result.lower() else 0
        
        conn = self._connect()
        c = conn.cursor()
        c.execute(
            """INSERT INTO xfs_commands 
               (command, args, target_ip, target_port, result, success, response_time_ms, timestamp) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (command, args, target_ip, target_port, result[:500], success, response_time_ms, datetime.now().isoformat())
        )
        conn.commit()
        row_id = c.lastrowid
        conn.close()
        return row_id
    
    def get_xfs_stats(self, target_ip: str = None) -> Dict:
        """Get XFS command statistics"""
        conn = self._connect()
        c = conn.cursor()
        
        if target_ip:
            c.execute("SELECT COUNT(*) FROM xfs_commands WHERE target_ip = ?", (target_ip,))
            total = c.fetchone()[0] or 0
            c.execute("SELECT COUNT(*) FROM xfs_commands WHERE target_ip = ? AND success = 1", (target_ip,))
            success = c.fetchone()[0] or 0
        else:
            c.execute("SELECT COUNT(*) FROM xfs_commands")
            total = c.fetchone()[0] or 0
            c.execute("SELECT COUNT(*) FROM xfs_commands WHERE success = 1")
            success = c.fetchone()[0] or 0
        
        conn.close()
        return {
            'total': total,
            'success': success,
            'failure': total - success,
            'success_rate': success / total if total > 0 else 0
        }
    
    # ========================================================================
    # JACKPOT ATTEMPT LOGGING
    # ========================================================================
    
    def log_jackpot_attempt(self, attempt_type: str, target_ip: str, target_port: int,
                             commands: List[str], results: List[str], success: bool,
                             amount_dispensed: int = 0) -> int:
        """Log a jackpot attempt"""
        conn = self._connect()
        c = conn.cursor()
        c.execute(
            """INSERT INTO jackpot_attempts 
               (attempt_type, target_ip, target_port, commands, results, success, amount_dispensed, timestamp) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (attempt_type, target_ip, target_port, json.dumps(commands), json.dumps(results), 
             1 if success else 0, amount_dispensed, datetime.now().isoformat())
        )
        conn.commit()
        row_id = c.lastrowid
        conn.close()
        return row_id
    
    def get_jackpot_summary(self) -> Dict:
        """Get jackpot attempt summary"""
        conn = self._connect()
        c = conn.cursor()
        
        c.execute("SELECT COUNT(*) FROM jackpot_attempts")
        total = c.fetchone()[0] or 0
        c.execute("SELECT COUNT(*) FROM jackpot_attempts WHERE success = 1")
        successful = c.fetchone()[0] or 0
        c.execute("SELECT SUM(amount_dispensed) FROM jackpot_attempts")
        total_dispensed = c.fetchone()[0] or 0
        
        conn.close()
        return {
            'total_attempts': total,
            'successful': successful,
            'failed': total - successful,
            'total_dispensed': total_dispensed,
            'success_rate': successful / total if total > 0 else 0
        }
    
    # ========================================================================
    # TARGET MANAGEMENT
    # ========================================================================
    
    def add_target(self, ip: str, port: int, device_type: str = "XFS") -> int:
        """Add or update a discovered target"""
        conn = self._connect()
        c = conn.cursor()
        
        # Check if target exists
        c.execute("SELECT id, scan_count FROM targets WHERE ip = ? AND port = ?", (ip, port))
        existing = c.fetchone()
        
        if existing:
            c.execute(
                "UPDATE targets SET last_seen = ?, scan_count = scan_count + 1, is_active = 1 WHERE id = ?",
                (datetime.now().isoformat(), existing['id'])
            )
            row_id = existing['id']
        else:
            c.execute(
                "INSERT INTO targets (ip, port, device_type, first_seen, last_seen) VALUES (?, ?, ?, ?, ?)",
                (ip, port, device_type, datetime.now().isoformat(), datetime.now().isoformat())
            )
            row_id = c.lastrowid
        
        conn.commit()
        conn.close()
        return row_id
    
    def get_targets(self, active_only: bool = True) -> List[Dict]:
        """Get discovered targets"""
        conn = self._connect()
        c = conn.cursor()
        
        if active_only:
            c.execute("SELECT * FROM targets WHERE is_active = 1 ORDER BY last_seen DESC")
        else:
            c.execute("SELECT * FROM targets ORDER BY last_seen DESC")
        
        results = [dict(r) for r in c.fetchall()]
        conn.close()
        return results
    
    def mark_target_inactive(self, ip: str, port: int) -> None:
        """Mark target as inactive"""
        conn = self._connect()
        c = conn.cursor()
        c.execute("UPDATE targets SET is_active = 0 WHERE ip = ? AND port = ?", (ip, port))
        conn.commit()
        conn.close()
    
    # ========================================================================
    # EXECUTION HISTORY
    # ========================================================================
    
    def log_execution(self, tool: str, args: str, result: str, error: str = None, 
                       execution_time_ms: int = 0) -> int:
        """Log tool execution"""
        conn = self._connect()
        c = conn.cursor()
        c.execute(
            "INSERT INTO execution_history (tool, args, result, error, execution_time_ms, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
            (tool, args, result[:1000], error, execution_time_ms, datetime.now().isoformat())
        )
        conn.commit()
        row_id = c.lastrowid
        conn.close()
        return row_id
    
    def get_execution_history(self, limit: int = 20, tool: str = None) -> List[Dict]:
        """Get execution history"""
        conn = self._connect()
        c = conn.cursor()
        
        if tool:
            c.execute(
                "SELECT tool, args, result, timestamp FROM execution_history WHERE tool = ? ORDER BY id DESC LIMIT ?",
                (tool, limit)
            )
        else:
            c.execute(
                "SELECT tool, args, result, timestamp FROM execution_history ORDER BY id DESC LIMIT ?",
                (limit,)
            )
        
        results = [dict(r) for r in c.fetchall()]
        conn.close()
        return results
    
    # ========================================================================
    # NETWORK ACTIVITY
    # ========================================================================
    
    def log_network_activity(self, target_ip: str, target_port: int, activity_type: str,
                               payload_size: int = 0, response_time_ms: int = 0) -> int:
        """Log network activity"""
        conn = self._connect()
        c = conn.cursor()
        c.execute(
            "INSERT INTO network_activity (target_ip, target_port, activity_type, payload_size, response_time_ms, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
            (target_ip, target_port, activity_type, payload_size, response_time_ms, datetime.now().isoformat())
        )
        conn.commit()
        row_id = c.lastrowid
        conn.close()
        return row_id
    
    # ========================================================================
    # COMMAND TEMPLATES (RAG Injection)
    # ========================================================================
    
    def add_command_template(self, trigger_phrase: str, command: str, description: str = "") -> int:
        """Add a command template for RAG injection"""
        conn = self._connect()
        c = conn.cursor()
        c.execute(
            "INSERT INTO command_templates (trigger_phrase, command, description, created_at) VALUES (?, ?, ?, ?)",
            (trigger_phrase, command, description, datetime.now().isoformat())
        )
        conn.commit()
        row_id = c.lastrowid
        conn.close()
        return row_id
    
    def get_command_templates(self) -> List[Dict]:
        """Get all command templates"""
        conn = self._connect()
        c = conn.cursor()
        c.execute("SELECT * FROM command_templates ORDER BY use_count DESC")
        results = [dict(r) for r in c.fetchall()]
        conn.close()
        return results
    
    # ========================================================================
    # SESSION MANAGEMENT
    # ========================================================================
    
    def create_session(self) -> str:
        """Create a new session ID"""
        import uuid
        session_id = str(uuid.uuid4())
        conn = self._connect()
        c = conn.cursor()
        c.execute(
            "INSERT INTO sessions (session_id, started_at) VALUES (?, ?)",
            (session_id, datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
        return session_id
    
    def update_session(self, session_id: str, command_count: int = None, jackpot_attempts: int = None) -> None:
        """Update session statistics"""
        conn = self._connect()
        c = conn.cursor()
        
        updates = []
        params = []
        if command_count is not None:
            updates.append("command_count = ?")
            params.append(command_count)
        if jackpot_attempts is not None:
            updates.append("jackpot_attempts = ?")
            params.append(jackpot_attempts)
        
        if updates:
            params.append(session_id)
            c.execute(
                f"UPDATE sessions SET {', '.join(updates)} WHERE session_id = ?",
                params
            )
            conn.commit()
        
        conn.close()
    
    # ========================================================================
    # CLEANUP
    # ========================================================================
    
    def cleanup_old_records(self, days: int = 30) -> Dict:
        """Delete records older than specified days"""
        conn = self._connect()
        c = conn.cursor()
        
        cutoff = (datetime.now().timestamp() - days * 24 * 3600)
        cutoff_str = datetime.fromtimestamp(cutoff).isoformat()
        
        results = {}
        tables = ['memory', 'feedback', 'xfs_commands', 'jackpot_attempts', 
                  'device_scans', 'execution_history', 'network_activity']
        
        for table in tables:
            c.execute(f"DELETE FROM {table} WHERE timestamp < ?", (cutoff_str,))
            results[table] = c.rowcount
        
        conn.commit()
        conn.close()
        return results
    
    # ========================================================================
    # BACKUP
    # ========================================================================
    
    def backup(self, backup_path: str = None) -> str:
        """Create database backup"""
        import shutil
        if backup_path is None:
            backup_path = self.db_path + '.backup'
        shutil.copy2(self.db_path, backup_path)
        return backup_path
    
    def log_device_scan(self, scan_results: str) -> None:
        """Log device scan results"""
        conn = self._connect()
        c = conn.cursor()
        c.execute(
            "INSERT INTO device_scans (scan_results, timestamp) VALUES (?, ?)",
            (scan_results[:1000], datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
