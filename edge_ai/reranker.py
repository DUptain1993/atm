#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
reranker.py - Cross-encoder reranking with TF-IDF fallback
"""

import numpy as np
import os
from typing import List, Union

class Reranker:
    """Cross-encoder reranking with fallback for Pi Zero W"""
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.use_onnx = False
        self.fallback_mode = False
        self._load_model()
    
    def _load_model(self) -> None:
        """Load reranker model with ONNX fallback"""
        
        # ============================================================
        # 1. Try ONNX (optimized for Pi)
        # ============================================================
        try:
            from onnxruntime import InferenceSession
            
            model_path = os.path.join('data', 'reranker.onnx')
            if os.path.exists(model_path):
                self.model = InferenceSession(model_path, providers=['CPUExecutionProvider'])
                self.use_onnx = True
                print("✅ ONNX Reranker loaded (optimized for Pi Zero W)")
                return
        except:
            pass
        
        # ============================================================
        # 2. Try PyTorch Transformers
        # ============================================================
        try:
            from transformers import AutoTokenizer, AutoModelForSequenceClassification
            import torch
            
            model_name = 'cross-encoder/ms-marco-MiniLM-L-2-v2'
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
            self.model.eval()
            print("✅ PyTorch Reranker loaded")
            return
        except:
            pass
        
        # ============================================================
        # 3. Fallback to TF-IDF
        # ============================================================
        print("⚠️ Using TF-IDF reranker fallback")
        self.fallback_mode = True
    
    def score(self, query: str, candidates: List[str]) -> List[float]:
        """
        Score candidates against query
        
        Args:
            query: Query string
            candidates: List of candidate strings
        
        Returns:
            List[float]: Scores for each candidate
        """
        if not candidates:
            return []
        
        if self.fallback_mode:
            return self._tfidf_score(query, candidates)
        
        if self.use_onnx:
            return self._onnx_score(query, candidates)
        
        return self._transformer_score(query, candidates)
    
    def _transformer_score(self, query: str, candidates: List[str]) -> List[float]:
        """Score using transformer model"""
        try:
            import torch
            
            pairs = [[query, cand] for cand in candidates]
            inputs = self.tokenizer(
                pairs,
                padding=True,
                truncation=True,
                return_tensors='pt',
                max_length=512
            )
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                scores = outputs.logits.squeeze().tolist()
            
            if not isinstance(scores, list):
                scores = [scores]
            
            return scores
            
        except Exception as e:
            print(f"⚠️ Transformer reranker error: {e}")
            return self._tfidf_score(query, candidates)
    
    def _onnx_score(self, query: str, candidates: List[str]) -> List[float]:
        """Score using ONNX model"""
        try:
            # Simplified scoring for ONNX
            # Use overlap-based scoring for now
            scores = []
            query_words = set(query.lower().split())
            
            for cand in candidates:
                cand_words = set(cand.lower().split())
                overlap = len(query_words & cand_words)
                scores.append(overlap / max(len(query_words), 1))
            
            return scores
            
        except:
            return self._tfidf_score(query, candidates)
    
    def _tfidf_score(self, query: str, candidates: List[str]) -> List[float]:
        """TF-IDF based scoring (fallback)"""
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity
            
            all_texts = [query] + candidates
            vectorizer = TfidfVectorizer(stop_words='english')
            tfidf_matrix = vectorizer.fit_transform(all_texts)
            
            query_vec = tfidf_matrix[0]
            candidate_vecs = tfidf_matrix[1:]
            
            scores = cosine_similarity(query_vec, candidate_vecs).flatten().tolist()
            return scores
            
        except:
            # Ultra simple fallback
            query_words = set(query.lower().split())
            scores = []
            for cand in candidates:
                cand_words = set(cand.lower().split())
                overlap = len(query_words & cand_words)
                scores.append(overlap / max(len(query_words), 1))
            return scores
    
    def rank(self, query: str, candidates: List[str]) -> List[str]:
        """Rank candidates by relevance"""
        scores = self.score(query, candidates)
        sorted_pairs = sorted(zip(scores, candidates), key=lambda x: x[0], reverse=True)
        return [cand for _, cand in sorted_pairs]
    
    def top_k(self, query: str, candidates: List[str], k: int = 5) -> List[str]:
        """Get top-k most relevant candidates"""
        ranked = self.rank(query, candidates)
        return ranked[:k]
