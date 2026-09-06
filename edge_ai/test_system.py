# test_system.py - Run this after deployment

import os
import sys
import subprocess

def test_imports():
    """Test all imports"""
    print("Testing imports...")
    try:
        import numpy as np
        import faiss
        import onnxruntime
        import flask
        import sklearn
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_files():
    """Test required files exist"""
    required = [
        'config.py',
        'run.py',
        'agent.py',
        'executor.py',
        'tools.py',
        'memory.py',
        'sqlite_db.py',
        'embedder.py',
        'reranker.py',
        'rag.py',
        'build_faiss.py',
        'network_xfs.py',
        'web_interface.py',
        'remote_trigger.py',
        'watchdog.py',
        'startup.sh',
        'requirements.txt'
    ]
    
    print("Testing required files...")
    missing = [f for f in required if not os.path.exists(f)]
    if missing:
        print(f"❌ Missing files: {missing}")
        return False
    print("✅ All files present")
    return True

def test_data_files():
    """Test data files exist and are valid"""
    print("Testing data files...")
    data_dir = 'data'
    if not os.path.exists(data_dir):
        print("⚠️ data/ directory missing (will be created at runtime)")
        os.makedirs(data_dir, exist_ok=True)
        return True
    
    # Check if index exists
    if os.path.exists(os.path.join(data_dir, 'faiss_index.bin')):
        import faiss
        try:
            index = faiss.read_index(os.path.join(data_dir, 'faiss_index.bin'))
            print(f"✅ FAISS index loaded: {index.ntotal} vectors, dimension {index.d}")
        except Exception as e:
            print(f"⚠️ Could not load FAISS index: {e}")
    else:
        print("⚠️ FAISS index not found (run build_faiss.py first)")
    
    return True

def test_network():
    """Test network connectivity"""
    print("Testing network...")
    try:
        import socket
        socket.gethostbyname('google.com')
        print("✅ Internet connectivity OK")
    except:
        print("⚠️ No internet connectivity (will use local network only)")
    
    # Check WiFi
    try:
        subprocess.run(['ifconfig', 'wlan0'], capture_output=True, check=True)
        print("✅ WiFi interface found")
    except:
        print("⚠️ WiFi interface not found (may be using Ethernet)")

def test_xfs():
    """Test XFS exploration tool"""
    print("Testing XFS tools...")
    if os.path.exists('xfsc.exe'):
        print("✅ xfsc.exe found")
        try:
            result = subprocess.run(['./xfsc.exe', '--help'], capture_output=True, text=True)
            if 'XFS' in result.stdout:
                print("✅ xfsc.exe works")
            else:
                print("⚠️ xfsc.exe may not be working correctly")
        except:
            print("⚠️ xfsc.exe execution failed")
    else:
        print("⚠️ xfsc.exe not found (will be compiled or transferred)")
    
    # Check XFS Python module
    try:
        import xfs
        print("✅ xfs Python module found")
    except:
        print("⚠️ xfs Python module not found (install via pip or copy from SDK)")

def main():
    print("="*60)
    print("🧪 SYSTEM TEST SUITE")
    print("="*60)
    
    tests = [
        ("Imports", test_imports),
        ("Files", test_files),
        ("Data Files", test_data_files),
        ("Network", test_network),
        ("XFS", test_xfs),
    ]
    
    results = []
    for name, test_fn in tests:
        print(f"\n--- {name} ---")
        try:
            result = test_fn()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Test {name} crashed: {e}")
            results.append((name, False))
    
    print("\n" + "="*60)
    print("RESULTS SUMMARY")
    print("="*60)
    passed = sum(1 for _, r in results if r)
    total = len(results)
    for name, result in results:
        print(f"  {'✅' if result else '❌'} {name}")
    print(f"\nPassed: {passed}/{total} ({passed/total*100:.1f}%)")

if __name__ == '__main__':
    main()
