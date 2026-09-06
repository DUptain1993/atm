#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "=========================================================="
echo "🛠️  EDGE AI SYSTEM - DEPLOYMENT SETUP"
echo "=========================================================="

# Create the data folder
echo "📁 Creating data directory..."
mkdir -p data

# Check Python 3 installation
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

echo "🐍 Python version:"
python3 --version

# Detect OS to guide package installation
OS_NAME=$(uname -s)
echo "💻 Operating System: $OS_NAME"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "📥 Installing pip3..."
    if [ "$OS_NAME" = "Linux" ]; then
        sudo apt-get update && sudo apt-get install -y python3-pip python3-venv espeak
    else
        echo "Please install pip3 for your OS manually."
        exit 1
    fi
fi

# Set up virtual environment (optional but recommended)
echo "📦 Setting up Python virtual environment (venv)..."
python3 -m venv venv
source venv/bin/activate

# Install requirements
echo "📥 Installing python packages..."
pip install --upgrade pip
pip install -r requirements.txt

echo "=========================================================="
echo "✅ SETUP COMPLETE!"
echo "=========================================================="
echo "To activate the environment:"
echo "  source venv/bin/activate"
echo ""
echo "To compile the FAISS index & optimize models for the Pi:"
echo "  python3 build_faiss.py"
echo ""
echo "To run the interactive agent loop:"
echo "  python3 run.py"
echo "=========================================================="
