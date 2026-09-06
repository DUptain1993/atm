#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
standalone_build_faiss.py - Standalone FAISS index builder for ATM dataset
Can be run independently without the main edge_ai directory
"""

import os
import sys
import json
import pickle
import hashlib
import numpy as np
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

# Auto-detect paths
BASE_DIR = Path(__file__).parent.absolute()
DATA_DIR = BASE_DIR / 'data'
DATASETS_DIR = BASE_DIR

# Create directories
DATA_DIR.mkdir(exist_ok=True, parents=True)

# File paths
FAISS_INDEX_PATH = DATA_DIR / 'faiss_index.bin'
TEXTS_PATH = DATA_DIR / 'texts.npy'
RESPONSES_PATH = DATA_DIR / 'responses.npy'
METADATA_PATH = DATA_DIR / 'metadata.pkl'

# Try to import FAISS
try:
    import faiss
    HAS_FAISS = True
except ImportError:
    HAS_FAISS = False
    print("⚠️ FAISS not installed. Install with: pip install faiss-cpu")


def load_training_data() -> Tuple[List[str], List[str], List[Dict]]:
    """Load training data from CSV files"""
    print("📊 Loading training data...")
    training_texts = []
    training_responses = []
    training_metadata = []
    
    # Look for CSV files
    csv_files = [
        'atm_vulnerability_complete.csv',
        'atm_full_realistic_enriched.csv',
        'atm_attack_chain_dataset.csv'
    ]
    
    for csv_file in csv_files:
        file_path = DATASETS_DIR / csv_file
        if not file_path.exists():
            print(f"  ⚠️ {csv_file} not found, skipping...")
            continue
        
        try:
            df = pd.read_csv(file_path)
            print(f"  ✅ Loaded {len(df)} rows from {csv_file}")
            
            # Determine column structure
            text_col = None
            response_col = None
            metadata_cols = []
            
            # Find columns that look like text/response
            for col in df.columns:
                col_lower = col.lower()
                if 'instruction' in col_lower or 'prompt' in col_lower or 'name' in col_lower or 'text' in col_lower:
                    text_col = col
                elif 'response' in col_lower or 'output' in col_lower or 'description' in col_lower or 'commands' in col_lower:
                    response_col = col
                else:
                    metadata_cols.append(col)
            
            # If no explicit text/response, create them
            if text_col is None:
                # Create text from all columns
                df['_text'] = df.apply(lambda row: ' '.join(str(v) for v in row.values if pd.notna(v)), axis=1)
                text_col = '_text'
            
            if response_col is None:
                # Use 'id' or first column as response
                response_col = df.columns[0] if len(df.columns) > 0 else 'id'
            
            # Extract data
            for idx, row in df.iterrows():
                # Build text
                text_parts = []
                for col in df.columns:
                    if col != text_col and col != response_col and col != '_text':
                        val = row[col]
                        if pd.notna(val) and str(val).strip():
                            text_parts.append(f"{col}: {val}")
                text = str(row[text_col]) if pd.notna(row[text_col]) else ' '.join(text_parts)
                text = text[:500] if len(text) > 500 else text  # Truncate
                
                # Build response
                response = str(row[response_col]) if pd.notna(row[response_col]) else ''
                
                # Build metadata
                metadata = {}
                for col in df.columns:
                    if col not in [text_col, response_col, '_text'] and pd.notna(row[col]):
                        metadata[col] = str(row[col])
                metadata['source_file'] = csv_file
                metadata['row_index'] = idx
                
                training_texts.append(text)
                training_responses.append(response)
                training_metadata.append(metadata)
                
        except Exception as e:
            print(f"  ❌ Error loading {csv_file}: {e}")
    
    # Also try loading from JSON files
    json_files = [
        'atm_vulnerability_complete.json',
        'atm_full_realistic_enriched.json',
        'atm_attack_chain_dataset.json'
    ]
    
    for json_file in json_files:
        file_path = DATASETS_DIR / json_file
        if not file_path.exists():
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, list):
                print(f"  ✅ Loaded {len(data)} rows from {json_file}")
                
                for idx, item in enumerate(data):
                    if isinstance(item, dict):
                        # Build text from all fields
                        text_parts = []
                        response = ''
                        metadata = {'source_file': json_file, 'row_index': idx}
                        
                        for key, value in item.items():
                            if key.lower() in ['commands', 'attack_commands', 'exploit_commands']:
                                # Use this as response
                                if isinstance(value, list):
                                    response = '\n'.join(str(v) for v in value)
                                else:
                                    response = str(value)
                            elif key.lower() in ['name', 'id', 'pattern', 'description']:
                                # Use as text
                                text_parts.append(f"{key}: {value}")
                                metadata[key] = str(value)
                            else:
                                metadata[key] = str(value) if not isinstance(value, (list, dict)) else json.dumps(value)
                        
                        text = ' '.join(text_parts) if text_parts else str(item)
                        text = text[:500] if len(text) > 500 else text
                        
                        if not response:
                            response = item.get('id', '') or item.get('name', '')
                        
                        training_texts.append(text)
                        training_responses.append(response)
                        training_metadata.append(metadata)
                        
        except Exception as e:
            print(f"  ❌ Error loading {json_file}: {e}")
    
    print(f"📊 Total training samples: {len(training_texts)}")
    return training_texts, training_responses, training_metadata


def generate_embedding(text: str, dimension: int = 384) -> np.ndarray:
    """Generate deterministic embedding from text using SHA256"""
    # Use SHA256 to generate deterministic vector
    hash_obj = hashlib.sha256(text.encode('utf-8'))
    hash_bytes = hash_obj.digest()
    
    # Convert to float array
    emb = np.frombuffer(hash_bytes, dtype=np.uint8)[:dimension].astype(np.float32)
    
    # Normalize roughly to [-1, 1]
    emb = (emb - 128) / 128
    
    # Pad if needed
    if len(emb) < dimension:
        emb = np.pad(emb, (0, dimension - len(emb)))
    
    return emb[:dimension].astype(np.float32)


def build_faiss_index(texts: List[str], dimension: int = 384) -> Tuple[np.ndarray, Any]:
    """Build FAISS index from texts"""
    if not HAS_FAISS:
        print("❌ FAISS not available. Install with: pip install faiss-cpu")
        return None, None
    
    if not texts:
        print("❌ No texts to embed")
        return None, None
    
    print(f"🔢 Generating {len(texts)} embeddings (dim={dimension})...")
    
    # Generate embeddings one by one (memory efficient for small datasets)
    embeddings = []
    for i, text in enumerate(texts):
        if i % 50 == 0:
            print(f"  Progress: {i}/{len(texts)}")
        emb = generate_embedding(text, dimension)
        embeddings.append(emb)
    
    embeddings_array = np.array(embeddings).astype(np.float32)
    
    # Normalize for cosine similarity
    faiss.normalize_L2(embeddings_array)
    
    # Build index
    print("🏗️ Building FAISS index...")
    index = faiss.IndexFlatIP(dimension)  # Inner product = cosine after normalization
    index.add(embeddings_array)
    
    print(f"✅ FAISS index built with {index.ntotal} vectors")
    return embeddings_array, index


def save_index(index: Any, texts: List[str], responses: List[str], 
               metadata: List[Dict], embeddings: np.ndarray):
    """Save FAISS index and associated data"""
    # Save FAISS index
    if HAS_FAISS and index is not None:
        faiss.write_index(index, str(FAISS_INDEX_PATH))
        print(f"✅ Saved FAISS index to {FAISS_INDEX_PATH}")
    
    # Save texts
    np.save(TEXTS_PATH, np.array(texts, dtype=object))
    print(f"✅ Saved texts to {TEXTS_PATH}")
    
    # Save responses
    np.save(RESPONSES_PATH, np.array(responses, dtype=object))
    print(f"✅ Saved responses to {RESPONSES_PATH}")
    
    # Save metadata
    with open(METADATA_PATH, 'wb') as f:
        pickle.dump(metadata, f)
    print(f"✅ Saved metadata to {METADATA_PATH}")
    
    # Also save embeddings if available
    if embeddings is not None:
        embeddings_path = DATA_DIR / 'embeddings.npy'
        np.save(embeddings_path, embeddings)
        print(f"✅ Saved embeddings to {embeddings_path}")


def load_index() -> Tuple[Optional[Any], Optional[np.ndarray], Optional[List[str]], Optional[List[str]], Optional[List[Dict]]]:
    """Load saved FAISS index and data"""
    if not HAS_FAISS:
        print("❌ FAISS not available")
        return None, None, None, None, None
    
    index = None
    embeddings = None
    texts = None
    responses = None
    metadata = None
    
    # Load FAISS index
    if FAISS_INDEX_PATH.exists():
        try:
            index = faiss.read_index(str(FAISS_INDEX_PATH))
            print(f"✅ Loaded FAISS index with {index.ntotal} vectors")
        except Exception as e:
            print(f"❌ Failed to load FAISS index: {e}")
    
    # Load texts
    if TEXTS_PATH.exists():
        texts = np.load(TEXTS_PATH, allow_pickle=True).tolist()
        print(f"✅ Loaded {len(texts)} texts")
    
    # Load responses
    if RESPONSES_PATH.exists():
        responses = np.load(RESPONSES_PATH, allow_pickle=True).tolist()
        print(f"✅ Loaded {len(responses)} responses")
    
    # Load metadata
    if METADATA_PATH.exists():
        with open(METADATA_PATH, 'rb') as f:
            metadata = pickle.load(f)
        print(f"✅ Loaded {len(metadata)} metadata entries")
    
    # Load embeddings
    embeddings_path = DATA_DIR / 'embeddings.npy'
    if embeddings_path.exists():
        embeddings = np.load(embeddings_path)
        print(f"✅ Loaded embeddings with shape {embeddings.shape}")
    
    return index, embeddings, texts, responses, metadata


def search_index(query: str, index: Any, texts: List[str], 
                 responses: List[str], k: int = 5) -> List[Dict]:
    """Search the FAISS index"""
    if not HAS_FAISS or index is None:
        print("❌ FAISS index not available")
        return []
    
    if not texts:
        print("❌ No texts available")
        return []
    
    # Generate query embedding
    query_emb = generate_embedding(query, index.d)
    query_emb = query_emb.reshape(1, -1).astype(np.float32)
    faiss.normalize_L2(query_emb)
    
    # Search
    distances, indices = index.search(query_emb, min(k, len(texts)))
    
    results = []
    for i, idx in enumerate(indices[0]):
        if idx < len(texts) and idx >= 0:
            results.append({
                'index': int(idx),
                'text': texts[idx],
                'response': responses[idx] if idx < len(responses) else '',
                'score': float(distances[0][i]),
                'metadata': metadata[idx] if idx < len(metadata) else {}
            })
    
    return results


def print_search_results(results: List[Dict]):
    """Pretty print search results"""
    print("\n" + "=" * 60)
    print("🔍 Search Results")
    print("=" * 60)
    
    for i, result in enumerate(results):
        print(f"\n[{i+1}] Score: {result['score']:.4f}")
        print(f"    Text: {result['text'][:100]}...")
        print(f"    Response: {result['response'][:100]}...")
        if result.get('metadata'):
            print(f"    Metadata: {json.dumps(result['metadata'], indent=2)[:200]}...")


def interactive_search():
    """Interactive search mode"""
    index, embeddings, texts, responses, metadata = load_index()
    
    if index is None or texts is None:
        print("❌ No index loaded. Run build first.")
        return
    
    print("\n" + "=" * 60)
    print("🔍 Interactive Search Mode")
    print("Type 'quit' to exit")
    print("=" * 60)
    
    while True:
        query = input("\n🔎 Query: ").strip()
        if query.lower() in ['quit', 'exit', 'q']:
            break
        
        if not query:
            continue
        
        results = search_index(query, index, texts, responses, k=5)
        print_search_results(results)


def main():
    """Main execution"""
    print("=" * 60)
    print("🔧 Standalone FAISS Index Builder for ATM Dataset")
    print("=" * 60)
    
    # Parse arguments
    import argparse
    parser = argparse.ArgumentParser(description='Build FAISS index for ATM dataset')
    parser.add_argument('--build', action='store_true', help='Build FAISS index')
    parser.add_argument('--search', action='store_true', help='Interactive search mode')
    parser.add_argument('--load', action='store_true', help='Load and display index info')
    parser.add_argument('--dimension', type=int, default=384, help='Embedding dimension (default: 384)')
    args = parser.parse_args()
    
    # If no args, show help
    if not any([args.build, args.search, args.load]):
        print("\nUsage:")
        print("  python standalone_build_faiss.py --build    # Build FAISS index")
        print("  python standalone_build_faiss.py --search   # Interactive search")
        print("  python standalone_build_faiss.py --load     # Load and display index info")
        return
    
    if args.build:
        # Load training data
        texts, responses, metadata = load_training_data()
        
        if not texts:
            print("❌ No training data found")
            return
        
        # Build FAISS index
        embeddings, index = build_faiss_index(texts, args.dimension)
        
        if index is not None:
            save_index(index, texts, responses, metadata, embeddings)
            print("\n✅ FAISS index built successfully!")
        else:
            print("\n❌ Failed to build FAISS index")
    
    elif args.search:
        interactive_search()
    
    elif args.load:
        index, embeddings, texts, responses, metadata = load_index()
        
        if index is None:
            print("❌ No index found. Run --build first.")
        else:
            print("\n" + "=" * 60)
            print("📊 Index Information")
            print("=" * 60)
            print(f"  Number of vectors: {index.ntotal}")
            print(f"  Embedding dimension: {index.d}")
            print(f"  Index type: {type(index).__name__}")
            
            if texts:
                print(f"  Number of texts: {len(texts)}")
            if responses:
                print(f"  Number of responses: {len(responses)}")
            if metadata:
                print(f"  Number of metadata entries: {len(metadata)}")
            
            # Show sample
            if texts and len(texts) > 0:
                print("\n📝 Sample text:")
                print(f"  {texts[0][:150]}...")
                if responses and len(responses) > 0:
                    print(f"  Response: {responses[0][:100]}...")


if __name__ == "__main__":
    main()
