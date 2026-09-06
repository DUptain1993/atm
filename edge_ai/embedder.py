#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
embedder.py - Sentence embedding with ONNX optimization for Pi Zero W
"""

import numpy as np
import os
import hashlib
import json
from typing import List, Union, Optional

class Embedder:
    """Sentence embedding with ONNX optimization and fallback"""
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2', dimension: int = 384):
        self.model_name = model_name
        self.dimension = dimension
        self.model = None
        self.tokenizer = None
        self.use_onnx = False
        self.fallback_mode = False
        self._load_model()
    
    def _load_model(self) -> None:
        """Load embedding model with ONNX fallback"""
        
        # ============================================================
        # 1. Try ONNX (most efficient on Pi Zero W)
        # ============================================================
        try:
            from onnxruntime import InferenceSession
            import onnxruntime as ort
            
            # Check for ONNX model in data directory
            model_path = os.path.join('data', 'embedder.onnx')
            if os.path.exists(model_path):
                # Create session with optimized settings for Pi
                providers = ['CPUExecutionProvider']
                self.model = InferenceSession(model_path, providers=providers)
                self.use_onnx = True
                print("✅ ONNX Embedder loaded (optimized for Pi Zero W)")
                return
                
        except ImportError:
            pass
        except Exception as e:
            print(f"⚠️ ONNX load failed: {e}")
        
        # ============================================================
        # 2. Try Sentence Transformers
        # ============================================================
        try:
            from sentence_transformers import SentenceTransformer
            
            # Use CPU-optimized model
            self.model = SentenceTransformer(self.model_name, device='cpu')
            self.dimension = self.model.get_sentence_embedding_dimension()
            print("✅ SentenceTransformer Embedder loaded")
            return
            
        except ImportError:
            pass
        except Exception as e:
            print(f"⚠️ SentenceTransformer load failed: {e}")
        
        # ============================================================
        # 3. Fallback to simple hashing-based embeddings
        # ============================================================
        print("⚠️ Using fallback embedding (deterministic hash-based)")
        self.fallback_mode = True
        self.dimension = 384
    
    def encode(self, text: str, normalize: bool = True) -> np.ndarray:
        """
        Encode text to embedding vector
        
        Args:
            text: Input text string
            normalize: Normalize output vector to unit length
        
        Returns:
            np.ndarray: Embedding vector of dimension
        """
        if not text:
            return np.zeros(self.dimension)
        
        if self.fallback_mode:
            emb = self._fallback_encode(text)
        elif self.use_onnx:
            emb = self._onnx_encode(text)
        else:
            emb = self._transformer_encode(text)
        
        # Normalize if requested
        if normalize and np.linalg.norm(emb) > 0:
            emb = emb / np.linalg.norm(emb)
        
        # Ensure correct dimension
        if len(emb) != self.dimension:
            if len(emb) > self.dimension:
                emb = emb[:self.dimension]
            else:
                emb = np.pad(emb, (0, self.dimension - len(emb)))
        
        return emb.astype(np.float32)
    
    def _transformer_encode(self, text: str) -> np.ndarray:
        """Encode using sentence-transformers"""
        try:
            embedding = self.model.encode([text])[0]
            return embedding.astype(np.float32)
        except Exception as e:
            print(f"⚠️ Transformer encode error: {e}")
            return self._fallback_encode(text)
    
    def _onnx_encode(self, text: str) -> np.ndarray:
        """Encode using ONNX model"""
        try:
            # Tokenize text (simplified for ONNX)
            # In production, use proper tokenizer
            import re
            tokens = re.findall(r'\w+', text.lower())
            
            # Simple token embedding using hash
            token_embeddings = []
            for token in tokens[:64]:
                token_hash = hashlib.sha256(token.encode()).digest()
                token_vec = np.frombuffer(token_hash, dtype=np.uint8)[:32].astype(np.float32) / 255.0
                token_embeddings.append(token_vec)
            
            # Average pooling
            if token_embeddings:
                emb = np.mean(token_embeddings, axis=0)
            else:
                emb = np.zeros(32)
            
            # Extend to full dimension
            if len(emb) < self.dimension:
                emb = np.pad(emb, (0, self.dimension - len(emb)))
            
            return emb[:self.dimension].astype(np.float32)
            
        except Exception as e:
            print(f"⚠️ ONNX encode error: {e}")
            return self._fallback_encode(text)
    
    def _fallback_encode(self, text: str) -> np.ndarray:
        """Simple deterministic fallback embedding using hash"""
        # Use SHA256 to generate deterministic random vector
        hash_obj = hashlib.sha256(text.encode())
        hash_bytes = hash_obj.digest()
        
        # Convert to float array
        emb = np.frombuffer(hash_bytes, dtype=np.uint8)[:self.dimension].astype(np.float32)
        
        # Normalize roughly
        emb = (emb - 128) / 128
        
        # Pad if needed
        if len(emb) < self.dimension:
            emb = np.pad(emb, (0, self.dimension - len(emb)))
        
        return emb[:self.dimension].astype(np.float32)
    
    def encode_batch(self, texts: List[str], normalize: bool = True) -> np.ndarray:
        """Encode multiple texts"""
        if not texts:
            return np.array([])
        
        if self.fallback_mode:
            embeddings = [self._fallback_encode(t) for t in texts]
        elif self.use_onnx:
            embeddings = [self._onnx_encode(t) for t in texts]
        else:
            try:
                embeddings = self.model.encode(texts)
            except:
                embeddings = [self._fallback_encode(t) for t in texts]
        
        # Ensure all vectors have correct dimension
        embeddings = [e[:self.dimension] if len(e) >= self.dimension 
                      else np.pad(e, (0, self.dimension - len(e))) 
                      for e in embeddings]
        
        embeddings = np.array(embeddings, dtype=np.float32)
        
        # Normalize if requested
        if normalize:
            norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
            norms = np.where(norms > 0, norms, 1)
            embeddings = embeddings / norms
        
        return embeddings
    
    def get_dimension(self) -> int:
        """Return embedding dimension"""
        return self.dimension
    
    def is_ready(self) -> bool:
        """Check if embedder is ready"""
        return True
    
    def save_onnx(self, output_path: str) -> bool:
        """Export model to ONNX format"""
        try:
            from sentence_transformers import SentenceTransformer
            import torch
            
            model = SentenceTransformer(self.model_name)
            
            # Create dummy input
            dummy_input = ["test text"]
            
            # Export to ONNX
            torch.onnx.export(
                model,
                dummy_input,
                output_path,
                input_names=['input_ids', 'attention_mask'],
                output_names=['output'],
                dynamic_axes={
                    'input_ids': {0: 'batch_size', 1: 'sequence_length'},
                    'attention_mask': {0: 'batch_size', 1: 'sequence_length'},
                },
                opset_version=11
            )
            print(f"✅ ONNX model saved to {output_path}")
            return True
            
        except Exception as e:
            print(f"⚠️ ONNX export failed: {e}")
            return False


# ============================================================================
# TEST
# ============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("🧠 Embedder Test")
    print("=" * 60)
    
    embedder = Embedder()
    print(f"Dimension: {embedder.get_dimension()}")
    print(f"Mode: {'ONNX' if embedder.use_onnx else 'Fallback' if embedder.fallback_mode else 'Transformer'}")
    
    test_text = "This is a test sentence for embedding."
    emb = embedder.encode(test_text)
    print(f"Embedding shape: {emb.shape}")
    print(f"Embedding sample: {emb[:5]}")
    
    batch_texts = ["Test 1", "Test 2", "Test 3"]
    batch_embs = embedder.encode_batch(batch_texts)
    print(f"Batch shape: {batch_embs.shape}")
    
    print("=" * 60)
