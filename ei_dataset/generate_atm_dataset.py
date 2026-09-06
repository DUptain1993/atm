#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_atm_dataset.py - Master dataset generation script
Runs all dataset generators and combines them
"""

import os
import json
import csv
import subprocess
import sys
from pathlib import Path
from typing import List  # ADD THIS LINE


def run_generator(script_name: str) -> bool:
    """Run a generator script"""
    print(f"\n📦 Running {script_name}...")
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=True,
            text=True,
            timeout=60
        )
        print(result.stdout)
        if result.stderr:
            print(f"⚠️ Stderr: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Failed to run {script_name}: {e}")
        return False


def combine_datasets(input_files: List[str], output_file: str) -> None:  # Now List is defined
    """Combine multiple CSV datasets into one"""
    combined_data = []
    
    for file in input_files:
        if not os.path.exists(file):
            print(f"⚠️ File not found: {file}")
            continue
        
        try:
            with open(file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    combined_data.append(row)
            print(f"✅ Loaded {len(combined_data)} rows from {file}")
        except Exception as e:
            print(f"⚠️ Error loading {file}: {e}")
    
    if combined_data:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=combined_data[0].keys())
            writer.writeheader()
            writer.writerows(combined_data)
        print(f"✅ Saved {len(combined_data)} combined rows to {output_file}")
    else:
        print("❌ No data to combine")


def main():
    """Main execution"""
    print("=" * 60)
    print("🏦 ATM Dataset Master Generator")
    print("=" * 60)
    
    # Check if generators exist
    generators = [
        "atm_attack_chain_dataset.py",
        "atm_full_realistic_enriched.py",
        "atm_vulnerability_complete.py"
    ]
    
    existing = []
    for gen in generators:
        if os.path.exists(gen):
            existing.append(gen)
            print(f"✅ Found generator: {gen}")
        else:
            print(f"⚠️ Generator not found: {gen}")
    
    if not existing:
        print("\n❌ No generators found!")
        return
    
    print("\n" + "=" * 60)
    print("📊 Running generators...")
    print("=" * 60)
    
    # Run each generator
    for gen in existing:
        run_generator(gen)
    
    # Check outputs
    print("\n" + "=" * 60)
    print("📁 Output files:")
    print("=" * 60)
    
    output_files = [
        "atm_attack_chain_dataset.csv",
        "atm_attack_chain_dataset.json",
        "atm_full_realistic_enriched.csv",
        "atm_full_realistic_enriched.json",
        "atm_vulnerability_complete.csv",
        "atm_vulnerability_complete.json"
    ]
    
    for file in output_files:
        if os.path.exists(file):
            size = os.path.getsize(file) / 1024
            print(f"  ✅ {file} ({size:.1f} KB)")
        else:
            print(f"  ⚠️ {file} (not found)")
    
    # Try to build embeddings
    print("\n" + "=" * 60)
    print("🔢 Building embeddings...")
    print("=" * 60)
    
    if os.path.exists("atm_vulnerability_embeddings.py"):
        run_generator("atm_vulnerability_embeddings.py")
    
    # Also try standalone build
    if os.path.exists("standalone_build_faiss.py"):
        run_generator("standalone_build_faiss.py")
    
    print("\n" + "=" * 60)
    print("✅ Dataset generation complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
