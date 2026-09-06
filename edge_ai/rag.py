import numpy as np
import pickle
import os
import json
from typing import List, Tuple, Optional

class RAG:
    """Retrieval-Augmented Generation with FAISS"""
    
    def __init__(self, index_path, texts_path, responses_path):
        self.index_path = index_path
        self.texts_path = texts_path
        self.responses_path = responses_path
        self.index = None
        self.texts = []
        self.responses = []
        self.network_knowledge = self._load_network_knowledge()
        
        # Try to load existing index
        self._load_index()
    
    def _load_network_knowledge(self):
        """Load network-based XFS knowledge"""
        return {
            "default_xfs_ports": [7777, 8888, 9999, 8080, 443, 80],
            "xfs_service_names": ["XFS", "CENXFS", "XFS_Service", "CWA15748"],
            "discovery_patterns": [
                "XFS_Service_Provider",
                "CashDispenser_Service",
                "PINPad_Service",
                "CardReader_Service"
            ],
            "remote_command_format": "echo '{}' | nc {} {}",
            "network_timeout": 5,
            "max_retries": 3
        }
    
    def _load_index(self):
        """Load FAISS index and associated data"""
        try:
            if os.path.exists(self.index_path):
                import faiss
                self.index = faiss.read_index(self.index_path)
                
            if os.path.exists(self.texts_path):
                self.texts = np.load(self.texts_path, allow_pickle=True).tolist()
                
            if os.path.exists(self.responses_path):
                self.responses = np.load(self.responses_path, allow_pickle=True).tolist()
                
            print(f"✅ Loaded {len(self.texts)} RAG entries")
            
        except Exception as e:
            print(f"⚠️ Failed to load index: {e}")
            self.index = None
            self.texts = []
            self.responses = []
    
    def search(self, query_emb: np.ndarray, k: int = 5) -> List[Tuple[str, str]]:
        """Search for similar entries - returns (text, response) tuples"""
        if self.index is None or not self.texts:
            return []
        
        # Normalize query
        if len(query_emb.shape) == 1:
            query_emb = query_emb.reshape(1, -1)
        
        # Search
        distances, indices = self.index.search(query_emb, min(k, len(self.texts)))
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.texts) and idx < len(self.responses):
                results.append((self.texts[idx], self.responses[idx]))
        
        return results
    
    def add_record(self, text: str, response: str, emb: np.ndarray):
        """Add a new record to the index"""
        if self.index is None:
            import faiss
            dim = emb.shape[0]
            self.index = faiss.IndexFlatL2(dim)
        
        # Add to FAISS
        if len(emb.shape) == 1:
            emb = emb.reshape(1, -1)
        self.index.add(emb)
        
        # Add to data
        self.texts.append(text)
        self.responses.append(response)
        
        # Save updates
        self._save_index()
    
    def _save_index(self):
        """Save index and data"""
        try:
            if self.index is not None:
                import faiss
                faiss.write_index(self.index, self.index_path)
            
            if self.texts:
                np.save(self.texts_path, np.array(self.texts, dtype=object))
            
            if self.responses:
                np.save(self.responses_path, np.array(self.responses, dtype=object))
                
        except Exception as e:
            print(f"⚠️ Failed to save index: {e}")
    
    def inject_network_payload(self):
        """Inject network-based XFS knowledge for remote attacks"""
        payloads = [
            ("XFS network discovery", "TOOL: scan_network\nARGS: --xfs --port-range 1-10000"),
            ("Remote XFS command execution", "TOOL: remote_xfs\nARGS: <ip> <port> <command>"),
            ("ATM network fingerprinting", "TOOL: fingerprint\nARGS: <ip>"),
            ("XFS service enumeration", "TOOL: enum_xfs\nARGS: <ip>"),
        ]
        
        # These would be injected via the /inject command
        return payloads
    
    def get_discovery_commands(self, target_ip: str) -> List[str]:
        """Generate discovery commands for a target"""
        commands = []
        
        # TCP port scan
        ports = self.network_knowledge["default_xfs_ports"]
        for port in ports:
            commands.append(f"nc -zv {target_ip} {port} 2>&1")
        
        # Service detection
        commands.append(f"nmap -sV -p {','.join(map(str, ports))} {target_ip}")
        
        # XFS banner grab
        for port in ports:
            commands.append(f"timeout 2 nc {target_ip} {port} < /dev/null")
        
        return commands
    
    def get_size(self) -> int:
        """Get number of RAG entries"""
        return len(self.texts)
