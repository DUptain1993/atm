#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
atm_attack_chain_dataset.py - Generate ATM attack chain dataset for RAG training
Creates structured attack patterns for XFS exploitation
"""

import json
import csv
import random
from datetime import datetime
from typing import List, Dict, Any

class ATMAttackChainGenerator:
    """Generate ATM attack chain datasets"""
    
    def __init__(self):
        self.attack_patterns = {
            "classic_dispense": [
                ("Open XFS connection", "open CashDispenser_1"),
                ("Get capabilities", "cdm caps"),
                ("Check status", "cdm status"),
                ("Reset device", "cdm reset"),
                ("Dispense cash", "cdm dispense 100 20"),
                ("Close connection", "close CashDispenser_1")
            ],
            "bypass_reset": [
                ("Open XFS connection", "open CashDispenser_1"),
                ("Reset device", "cdm reset"),
                ("Dispense cash", "cdm dispense 100 20"),
                ("Dispense more", "cdm dispense 100 20"),
                ("Close connection", "close CashDispenser_1")
            ],
            "rapid_dispense": [
                ("Open XFS connection", "open CashDispenser_1"),
                ("Dispense cash", "cdm dispense 100 20"),
                ("Dispense cash", "cdm dispense 100 20"),
                ("Dispense cash", "cdm dispense 100 20"),
                ("Close connection", "close CashDispenser_1")
            ],
            "stealth_mode": [
                ("Open XFS connection", "open CashDispenser_1"),
                ("Check status", "cdm status"),
                ("Dispense small", "cdm dispense 50 10"),
                ("Check status", "cdm status"),
                ("Dispense small", "cdm dispense 50 10"),
                ("Close connection", "close CashDispenser_1")
            ],
            "denial_bypass": [
                ("Open XFS connection", "open CashDispenser_1"),
                ("Deny transaction", "cdm deny"),
                ("Confirm transaction", "cdm confirm"),
                ("Dispense cash", "cdm dispense 100 20"),
                ("Close connection", "close CashDispenser_1")
            ],
            "state_overflow": [
                ("Open XFS connection", "open CashDispenser_1"),
                ("Close connection", "close CashDispenser_1"),
                ("Open connection", "open CashDispenser_1"),
                ("Dispense cash", "cdm dispense 100 20"),
                ("Close connection", "close CashDispenser_1")
            ]
        }
        
        self.vulnerability_types = [
            "Authentication Bypass",
            "Command Injection",
            "Buffer Overflow",
            "Race Condition",
            "State Confusion",
            "Session Replay",
            "Parameter Manipulation",
            "Denial of Service"
        ]
        
        self.attack_vectors = [
            "Network-based remote exploitation",
            "Physical USB injection",
            "Software vulnerability exploitation",
            "Protocol manipulation",
            "Firmware corruption"
        ]
    
    def generate_command_sequence(self, pattern_name: str) -> List[Dict]:
        """Generate a single command sequence"""
        pattern = self.attack_patterns.get(pattern_name, self.attack_patterns["classic_dispense"])
        commands = []
        
        for step_name, command in pattern:
            commands.append({
                "step": step_name,
                "command": command,
                "success_criteria": "No error returned",
                "expected_output": "Command executed successfully"
            })
        
        return commands
    
    def generate_attack_entry(self, pattern_name: str, target_type: str = "ATM") -> Dict:
        """Generate a single attack entry"""
        commands = self.generate_command_sequence(pattern_name)
        
        return {
            "id": f"atm_attack_{pattern_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "target": target_type,
            "pattern": pattern_name,
            "vulnerability": random.choice(self.vulnerability_types),
            "vector": random.choice(self.attack_vectors),
            "severity": random.choice(["High", "Critical", "Medium"]),
            "commands": commands,
            "command_count": len(commands),
            "success_rate": random.uniform(0.7, 0.95),
            "complexity": random.choice(["Low", "Medium", "High"]),
            "detection_risk": random.choice(["Low", "Medium", "High"])
        }
    
    def generate_dataset(self, count: int = 100) -> List[Dict]:
        """Generate full dataset"""
        dataset = []
        pattern_names = list(self.attack_patterns.keys())
        
        for i in range(count):
            pattern_name = random.choice(pattern_names)
            entry = self.generate_attack_entry(pattern_name)
            dataset.append(entry)
        
        return dataset
    
    def save_csv(self, dataset: List[Dict], filename: str = "atm_attack_chain_dataset.csv"):
        """Save dataset to CSV"""
        if not dataset:
            return
        
        # Flatten for CSV
        rows = []
        for entry in dataset:
            base = {
                "id": entry["id"],
                "target": entry["target"],
                "pattern": entry["pattern"],
                "vulnerability": entry["vulnerability"],
                "vector": entry["vector"],
                "severity": entry["severity"],
                "command_count": entry["command_count"],
                "success_rate": entry["success_rate"],
                "complexity": entry["complexity"],
                "detection_risk": entry["detection_risk"]
            }
            
            # Add commands as JSON string
            base["commands"] = json.dumps(entry["commands"])
            rows.append(base)
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            if rows:
                writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows(rows)
        
        print(f"âœ… Saved {len(rows)} attack chains to {filename}")
    
    def save_json(self, dataset: List[Dict], filename: str = "atm_attack_chain_dataset.json"):
        """Save dataset to JSON"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, indent=2)
        
        print(f"âœ… Saved {len(dataset)} attack chains to {filename}")


def main():
    """Generate attack chain datasets"""
    print("=" * 60)
    print("ðŸ”§ ATM Attack Chain Dataset Generator")
    print("=" * 60)
    
    generator = ATMAttackChainGenerator()
    
    # Generate 100 attack chains
    print("\nðŸ“Š Generating attack chains...")
    dataset = generator.generate_dataset(100)
    
    # Save in both formats
    generator.save_csv(dataset, "atm_attack_chain_dataset.csv")
    generator.save_json(dataset, "atm_attack_chain_dataset.json")
    
    print("\n" + "=" * 60)
    print("ðŸ“Š Dataset Summary")
    print("=" * 60)
    print(f"Total attack chains: {len(dataset)}")
    print(f"Patterns used: {len(generator.attack_patterns)}")
    
    # Count by pattern
    pattern_counts = {}
    for entry in dataset:
        pattern = entry["pattern"]
        pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
    
    print("\nPattern distribution:")
    for pattern, count in sorted(pattern_counts.items(), key=lambda x: -x[1]):
        print(f"  {pattern}: {count}")
    
    print("=" * 60)


if __name__ == "__main__":
    main()
