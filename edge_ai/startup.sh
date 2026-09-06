#!/bin/bash
# ============================================================================
# startup.sh - Autostart script for ATM Jackpot Drone on Pi Zero W
# ============================================================================

echo ""
echo "════════════════════════════════════════════════════════════════════════════"
echo "🚀 ATM JACKPOT DRONE - AUTOSTART"
echo "   OFU (Open-Fable-Unified) ACTIVE"
echo "   $(date)"
echo "════════════════════════════════════════════════════════════════════════════"
echo ""

# ============================================================================
# 1. System Configuration
# ============================================================================

echo "🔧 [1/5] System Configuration..."

# Set up swap (1GB for memory-intensive operations)
echo "  Setting up swap (1GB)..."
sudo dphys-swapfile swapoff 2>/dev/null
sudo sed -i 's/CONF_SWAPSIZE=.*/CONF_SWAPSIZE=1024/' /etc/dphys-swapfile 2>/dev/null
sudo dphys-swapfile setup 2>/dev/null
sudo dphys-swapfile swapon 2>/dev/null

# Set CPU governor to performance
echo "  Setting CPU governor..."
echo performance | sudo tee /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor 2>/dev/null

# Disable Bluetooth to save power
echo "  Disabling Bluetooth..."
sudo systemctl disable bluetooth 2>/dev/null
sudo systemctl stop bluetooth 2>/dev/null

echo "  ✅ System configured"
echo ""

# ============================================================================
# 2. Network Setup
# ============================================================================

echo "📡 [2/5] Network Setup..."

# Start WiFi
echo "  Starting WiFi..."
sudo ifconfig wlan0 up 2>/dev/null || true

# Get IP address
IP_ADDR=$(hostname -I 2>/dev/null | cut -d' ' -f1)
if [ -z "$IP_ADDR" ]; then
    IP_ADDR="unknown"
fi

echo "  IP Address: $IP_ADDR"
echo "  ✅ Network ready"
echo ""

# ============================================================================
# 3. Change to Directory
# ============================================================================

echo "📂 [3/5] Application Setup..."

# Try to find the directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR" 2>/dev/null || cd /home/pi/jackpot_agent 2>/dev/null || cd /home/pi/edge_ai 2>/dev/null

echo "  Working directory: $(pwd)"

# Check if we have the files
if [ ! -f "run.py" ] && [ ! -f "web_interface.py" ]; then
    echo "  ⚠️ WARNING: Cannot find application files!"
    echo "  Looking in current directory: $(ls -la *.py 2>/dev/null)"
fi

echo "  ✅ Application directory set"
echo ""

# ============================================================================
# 4. Start Services
# ============================================================================

echo "🚀 [4/5] Starting Services..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "  Activating virtual environment..."
    source venv/bin/activate 2>/dev/null || true
fi

# Create logs directory
mkdir -p logs 2>/dev/null

# ============================================================================
# 4a. Start Web Interface
# ============================================================================

echo "  🌐 Starting web interface on port 8080..."
nohup python3 web_interface.py >> logs/web.log 2>&1 &
WEB_PID=$!
echo "    Web PID: $WEB_PID"

# ============================================================================
# 4b. Start Autonomous Drone (background)
# ============================================================================

echo "  🤖 Starting autonomous drone..."
nohup python3 -c "
from network_xfs import NetworkJackpotDrone
import time
drone = NetworkJackpotDrone()
print('🐕 Drone starting...')
drone.start_autonomous_scan('192.168.1.0/24', 30)
" >> logs/drone.log 2>&1 &
DRONE_PID=$!
echo "    Drone PID: $DRONE_PID"

# ============================================================================
# 4c. Start Watchdog
# ============================================================================

echo "  🐕 Starting watchdog monitor..."
nohup python3 -c "
from watchdog import JackpotWatchdog
watchdog = JackpotWatchdog(interval=10.0, threshold=2)
watchdog.start()
" >> logs/watchdog.log 2>&1 &
WATCHDOG_PID=$!
echo "    Watchdog PID: $WATCHDOG_PID"

# ============================================================================
# 5. Done
# ============================================================================

echo ""
echo "════════════════════════════════════════════════════════════════════════════"
echo "✅ [5/5] SYSTEM STARTED"
echo "════════════════════════════════════════════════════════════════════════════"
echo ""
echo "📊 STATUS:"
echo "  Web Interface:   http://$IP_ADDR:8080"
echo "  Drone PID:       $DRONE_PID"
echo "  Watchdog PID:    $WATCHDOG_PID"
echo "  Web PID:         $WEB_PID"
echo ""
echo "📁 LOGS:"
echo "  Web:      tail -f logs/web.log"
echo "  Drone:    tail -f logs/drone.log"
echo "  Watchdog: tail -f logs/watchdog.log"
echo "  Jackpot:  tail -f logs/jackpot.log"
echo ""
echo "🛠 COMMANDS:"
echo "  Stop drone:     kill $DRONE_PID"
echo "  Stop watchdog:  kill $WATCHDOG_PID"
echo "  Stop web:       kill $WEB_PID"
echo "  Stop all:       pkill -f 'python3'"
echo ""
echo "════════════════════════════════════════════════════════════════════════════"
echo ""

# ============================================================================
# Wait for processes (keeps script running)
# ============================================================================

wait $WEB_PID $DRONE_PID $WATCHDOG_PID 2>/dev/null
