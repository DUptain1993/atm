#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
atm_full_realistic_enriched.py - Generate enriched ATM vulnerability dataset
Combines realistic scenarios with enriched vulnerability data
"""

import json
import csv
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any

class ATMRealisticEnrichedGenerator:
    """Generate realistic enriched ATM vulnerability dataset"""
    
    def __init__(self):
        self.atm_manufacturers = [
            "Diebold Nixdorf", "NCR", "Hyosung", "GRG Banking",
            "Wincor Nixdorf", "Fujitsu", "Hitachi", "OKI"
        ]
        
        self.atm_models = [
            "Serie 2000", "Serie 5000", "Serie 7000", "SelfServ 34",
            "SelfServ 36", "SelfServ 80", "SelfServ 90", "Hyosung 1500",
            "Hyosung 2100", "GRG Wytron", "Wincor Cineo", "Wincor ProCash"
        ]
        
        self.software_versions = [
            "XFS 2.0", "XFS 3.0", "XFS 3.10", "XFS 3.20",
            "XFS 4.0", "Windows 7 SP1", "Windows 10 IoT", "Windows Embedded"
        ]
        
        self.vulnerability_categories = [
            "Remote Code Execution",
            "Privilege Escalation",
            "Information Disclosure",
            "Denial of Service",
            "Authentication Bypass",
            "SQL Injection",
            "Command Injection",
            "Buffer Overflow",
            "Race Condition"
        ]
        
        self.exploit_difficulty = ["Low", "Medium", "High", "Very High"]
        self.impact_levels = ["Low", "Medium", "High", "Critical"]
        
        self.locations = [
            "Bank Branch", "Shopping Mall", "Gas Station", "Convenience Store",
            "Casino", "Airport", "Train Station", "Hotel", "Restaurant"
        ]
    
    def generate_vulnerability(self) -> Dict:
        """Generate a single vulnerability entry"""
        return {
            "cve_id": f"CVE-2024-{random.randint(1000, 9999)}",
            "category": random.choice(self.vulnerability_categories),
            "difficulty": random.choice(self.exploit_difficulty),
            "impact": random.choice(self.impact_levels),
            "exploit_public": random.choice([True, False]),
            "patch_available": random.choice([True, False])
        }
    
    def generate_atm_entry(self, index: int) -> Dict:
        """Generate a single ATM entry with enriched data"""
        manufacturer = random.choice(self.atm_manufacturers)
        model = random.choice(self.atm_models)
        location = random.choice(self.locations)
        software = random.choice(self.software_versions)
        
        # Generate vulnerabilities
        num_vulns = random.randint(1, 5)
        vulnerabilities = [self.generate_vulnerability() for _ in range(num_vulns)]
        
        # Generate commands
        attack_commands = [
            f"open CashDispenser_{random.randint(1, 5)}",
            "cdm caps",
            "cdm status",
            "cdm reset",
            f"cdm dispense {random.randint(50, 500)} {random.randint(1, 20)}",
            "cdm close"
        ]
        random.shuffle(attack_commands)
        attack_commands = attack_commands[:random.randint(3, 6)]
        
        return {
            "id": f"ATM_{index:04d}",
            "manufacturer": manufacturer,
            "model": model,
            "software_version": software,
            "location": location,
            "vulnerabilities": vulnerabilities,
            "vulnerability_count": len(vulnerabilities),
            "critical_vulnerabilities": sum(1 for v in vulnerabilities if v["impact"] == "Critical"),
            "attack_commands": attack_commands,
            "command_count": len(attack_commands),
            "exploit_probability": random.uniform(0.1, 0.9),
            "cves": [v["cve_id"] for v in vulnerabilities],
            "last_audit": (datetime.now() - timedelta(days=random.randint(30, 365))).strftime("%Y-%m-%d"),
            "has_physical_access": random.choice([True, False]),
            "network_accessible": random.choice([True, False])
        }
    
    def generate_dataset(self, count: int = 50) -> List[Dict]:
        """Generate full dataset"""
        return [self.generate_atm_entry(i) for i in range(count)]
    
    def save_csv(self, dataset: List[Dict], filename: str = "atm_full_realistic_enriched.csv"):
        """Save to CSV"""
        if not dataset:
            return
        
        # Flatten structure for CSV
        rows = []
        for entry in dataset:
            base = {
                "id": entry["id"],
                "manufacturer": entry["manufacturer"],
                "model": entry["model"],
                "software_version": entry["software_version"],
                "location": entry["location"],
                "vulnerability_count": entry["vulnerability_count"],
                "critical_vulnerabilities": entry["critical_vulnerabilities"],
                "command_count": entry["command_count"],
                "exploit_probability": round(entry["exploit_probability"], 3),
                "has_physical_access": entry["has_physical_access"],
                "network_accessible": entry["network_accessible"],
                "last_audit": entry["last_audit"],
                "cves": "|".join(entry["cves"]),
                "attack_commands": "|".join(entry["attack_commands"])
            }
            
            # Add vulnerability details as JSON string
            base["vulnerabilities"] = json.dumps(entry["vulnerabilities"])
            rows.append(base)
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            if rows:
                writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows(rows)
        
        print(f"âœ… Saved {len(rows)} ATM entries to {filename}")
    
    def save_json(self, dataset: List[Dict], filename: str = "atm_full_realistic_enriched.json"):
        """Save to JSON"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, indent=2)
        
        print(f"âœ… Saved {len(dataset)} ATM entries to {filename}")


def main():
    """Generate enriched dataset"""
    print("=" * 60)
    print("ðŸ¦ ATM Full Realistic Enriched Dataset Generator")
    print("=" * 60)
    
    generator = ATMRealisticEnrichedGenerator()
    
    print("\nðŸ“Š Generating enriched ATM data...")
    dataset = generator.generate_dataset(50)
    
    generator.save_csv(dataset, "atm_full_realistic_enriched.csv")
    generator.save_json(dataset, "atm_full_realistic_enriched.json")
    
    print("\n" + "=" * 60)
    print("ðŸ“Š Dataset Summary")
    print("=" * 60)
    print(f"Total ATM entries: {len(dataset)}")
    
    # Stats
    total_vulns = sum(entry["vulnerability_count"] for entry in dataset)
    total_critical = sum(entry["critical_vulnerabilities"] for entry in dataset)
    
    print(f"Total vulnerabilities: {total_vulns}")
    print(f"Critical vulnerabilities: {total_critical}")
    print(f"Average vulnerabilities per ATM: {total_vulns / len(dataset):.1f}")
    
    # Manufacturers
    manufacturers = {}
    for entry in dataset:
        mfg = entry["manufacturer"]
        manufacturers[mfg] = manufacturers.get(mfg, 0) + 1
    
    print("\nManufacturer distribution:")
    for mfg, count in sorted(manufacturers.items(), key=lambda x: -x[1]):
        print(f"  {mfg}: {count}")
    
    print("=" * 60)


if __name__ == "__main__":
    main()
