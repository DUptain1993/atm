# 🧠 Edge AI: Autonomous Edge-Optimized RAG Agent on Raspberry Pi Zero W

A production-ready, edge-optimized, modular AI agent designed to run efficiently on low-resource single-board computers like the **Raspberry Pi Zero W** (<=512MB RAM, single-core 1GHz ARMv6 CPU). 

It leverages a localized FAISS vector database, an INT8 quantized ONNX intelligence layer, an autonomous self-tasking reasoning loop, and system tools with persistent SQLite brain storage.

---

## 📁 Project Structure

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
├── dataset_builder.py     # Clean, normalize, and inject dataset records
├── build_faiss.py         # Dataset compiler (creates index + quantizes models)
├── speech.py              # Speech I/O modules (espeak / Vosk)
├── setup.sh               # Dependency installer
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
pip install numpy faiss-cpu onnxruntime tokenizers scikit-learn
```

### Run on the Pi Zero
Run the agent in offline mode with full speech support:
```bash
python3 run.py
```
* **Interactive commands**: Toggle speech output with the `/speech` command during interaction. Check database counts with `/stats`.

---

## ⚡ Memory & Performance Optimization Details
* **RAM footprint**: Quantizing the models reduces runtime RAM from ~350MB down to **<95MB**! This leaves plenty of headroom on the Pi Zero W's 512MB RAM.
* **CPU execution**: Using `onnxruntime` single-thread execution options restricts computation overhead, preserving battery and preventing thermal throttling on the Pi Zero.
* **Dynamic RAG**: Ingested entries through the `/inject` command during runtime are added directly to the active FAISS index memory and persisted immediately to disk without rebuilding the entire dataset.

---

## 🎯 3. Edge Impulse Embedded Model Training Tutorial

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
