#!/bin/bash
# ============================================================================
# ATM JACKPOT DRONE - COMPLETE INSTALLATION SCRIPT
# ============================================================================

echo "═══════════════════════════════════════════════════════════════════════════"
echo "🚀 ATM JACKPOT DRONE - COMPLETE INSTALLATION"
echo "═══════════════════════════════════════════════════════════════════════════"

# Detect platform
ARCH=$(uname -m)
IS_PI=false
if [[ "$ARCH" == "armv6l" ]] || [[ "$ARCH" == "armv7l" ]]; then
    IS_PI=true
    echo "📡 Detected Raspberry Pi (ARM) - using minimal requirements"
else
    echo "💻 Detected x86_64 - using full requirements"
fi

# Create virtual environment
echo "🔧 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install dependencies based on platform
if [ "$IS_PI" = true ]; then
    echo "📦 Installing Pi Zero W optimized requirements..."
    pip install -r requirements_pi.txt
else
    echo "📦 Installing full development requirements..."
    pip install -r requirements.txt
    pip install -r requirements_dev.txt
fi

echo "✅ Installation complete!"

# Verify installation
echo "🔍 Verifying installation..."
python3 -c "
import sys
import numpy
import faiss
import onnxruntime
import flask
import pandas
print('✅ All core imports successful')
print(f'Python: {sys.version}')
print(f'NumPy: {numpy.__version__}')
print(f'FAISS: {faiss.__version__}')
print(f'ONNX Runtime: {onnxruntime.__version__}')
print(f'Flask: {flask.__version__}')
"

echo "═══════════════════════════════════════════════════════════════════════════"
echo "✅ ATM JACKPOT DRONE - INSTALLATION COMPLETE"
echo "═══════════════════════════════════════════════════════════════════════════"
