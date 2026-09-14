README.md — Autonomous ATM Jackpotting Device

```markdown
# 🎰 Autonomous ATM Jackpotting Device

**A self-directing, edge-optimized XFS attack platform for Raspberry Pi Zero W.**

This device fuses three independently-powerful offensive security frameworks into a single autonomous unit:

| Layer | Source | Role |
|-------|--------|------|
| **Bjorn** | Network attack platform | Discovery, brute-force, credential harvesting |
| **Edge AI** | RAG brain + XFS tooling | Pattern selection, XFS jackpotting, autonomy |
| **RPi Agent** | P4wnP1-style payloads | USB HID injection, e-ink telemetry, WiFi capture |

Boot it on a network. It discovers ATMs, cracks adjacent services, selects the optimal XFS attack pattern from a trained knowledge base, and dispenses cash — all without human intervention.

---

## ⚠️ Legal & Ethical Notice

This software is a **weapons-grade offensive security tool**. It is intended **exclusively** for:

- Authorized penetration testing against ATMs you **own or have written permission to test**
- Red-team engagements with signed Rules of Engagement
- Security research in isolated lab environments
- Academic study of XFS protocol weaknesses

**Unauthorized use is a felony** under the Computer Fraud and Abuse Act (US), Computer Misuse Act (UK), and equivalent laws worldwide. Cash theft via XFS exploitation carries mandatory sentencing guidelines in most jurisdictions.

The authors assume **zero liability** for misuse. If you do not have explicit written authorization for every target, **stop now**.

---

## 🏗 Architecture

```

┌─────────────────────────────────────────────────────────────────┐
│                    AUTONOMOUS JACKPOT BRAIN                      │
│  (edge_ai/agent.py + watchdog.py + RAG)                          │
│  Decides: WHEN to attack, WHICH pattern, HOW MUCH               │
└────────────────────────┬────────────────────────────────────────┘
│
┌────────────────┼────────────────┐
▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ BJORN LAYER  │  │  XFS LAYER   │  │ PAYLOAD LAYER│
│              │  │              │  │              │
│ Network      │  │ RemoteXFS    │  │ USB HID      │
│ Discovery    │  │ Exploit      │  │ DuckyScript  │
│              │  │              │  │              │
│ SSH/SMB/FTP  │  │ cdm dispense │  │ Physical     │
│ SQL/RDP/Tel  │  │ cdm reset    │  │ ATM access   │
│ brute-force  │  │ cdm confirm  │  │              │
└──────────────┘  └──────────────┘  └──────────────┘
│                │                │
└────────────────┼────────────────┘
▼
┌─────────────────────┐
│  UNIFIED KB         │
│  netkb.csv +        │
│  brain.db           │
└─────────────────────┘
│
▼
┌─────────────────────┐
│  E-INK TELEMETRY    │
│  250×122 tri-color  │
│  Field-visible      │
└─────────────────────┘

```

### What Each Layer Contributes

**Bjorn (Layer 1)** — Network reconnaissance and credential acquisition
- Full subnet discovery with MAC/hostname resolution
- Port scanning across 40+ common service ports
- Parallel brute-force against SSH, SMB, FTP, SQL, RDP, Telnet
- Automatic file exfiltration from compromised shares
- Central knowledge base (`netkb.csv`) tracking every target

**Edge AI (Layer 2)** — Decision-making and XFS exploitation
- RAG brain trained on 100+ ATM attack chains (`ei_dataset/`)
- Pattern selection: `classic_dispense`, `denial_bypass`, `state_overflow`, `rapid`, `stealth`
- XFS protocol client (`RemoteXFSExploit`) for dispenser control
- Autonomous watchdog that triggers on detection threshold
- Persistent SQLite brain (`brain.db`) for full attack history

**RPi Agent (Layer 3)** — Physical access and field telemetry
- P4wnP1-style USB composite gadget (RNDIS/ECM + HID keyboard)
- DuckyScript interpreter for HID payload delivery
- Waveshare 2.13" tri-color e-ink display
- WiFi handshake capture (Pwnagotchi-style, optional)

---

## 📋 Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **SBC** | Raspberry Pi Zero W | Raspberry Pi Zero 2 W |
| **RAM** | 512 MB | 512 MB |
| **Storage** | 8 GB microSD | 16 GB Class 10 |
| **Display** | Waveshare 2.13" e-Paper HAT (B) | Same |
| **USB** | OTG cable to target | USB-A breakout cable |
| **Power** | 5V 2A micro-USB | Battery pack for field use |
| **Network** | wlan0 (built-in) | + USB Ethernet for air-gapped ATMs |

**Optional attack accessories:**
- Proxmark3 or ACR122U (NFC/EMV contactless testing)
- Facedancer21 or GreatFET (USB emulation research)
- Alfa AWUS036NHA (long-range WiFi for standoff attacks)

---

## 🚀 Quick Start

### Dev / Testing (Laptop or Pi with mock display)

```bash
# Clone
git clone https://github.com/<your-org>/jackpot-device.git
cd jackpot-device

# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r edge_ai/requirements.txt

# Build RAG index from ei_dataset/
cd edge_ai
python3 build_faiss.py
cd ..

# Run in safe mock mode (no HID, no display, verbose)
python3 jackpot_daemon.py --no-hid --no-display -v
```

Expected output after ~60 seconds:

```
[INFO] jackpot_daemon: ============ AUTONOMOUS ATM JACKPOT DAEMON STARTING ============
[INFO] jackpot_daemon:   Subnet:           192.168.1.0/24
[INFO] jackpot_daemon:   Bjorn:            ON
[INFO] jackpot_daemon:   RAG Brain:        ON
[INFO] jackpot_daemon:   Watchdog:         ON
[INFO] jackpot_daemon:   Jackpot Drone:    ON
[INFO] jackpot_daemon:   USB HID:          OFF
[INFO] jackpot_daemon:   E-ink Display:    OFF
[INFO] jackpot_daemon: RAG brain loaded (127 entries)
[INFO] jackpot_daemon: Bjorn orchestrator running
[INFO] jackpot_daemon: Watchdog thread started
[INFO] jackpot_daemon: [STATUS] bjorn=NetworkScanner | detections=0/2 | hv_targets=0 | creds=0
...
```

Production Deployment (Pi Zero W)

One-shot install — copies the repo, sets up systemd, enables SPI/USB gadget, builds the FAISS index:

```bash
cd jackpot-device
sudo ./edge_ai/rpi/scripts/install_jackpot.sh
sudo reboot
```

After reboot, the device auto-starts. Monitor with:

```bash
sudo journalctl -u jackpot -f
```

Manual run for first-time verification:

```bash
cd /home/pi/jackpot
sudo ./venv/bin/python jackpot_daemon.py \
    --enable-hid \
    --subnet 192.168.1.0/24
```

---

🎛 Command-Line Reference

```
python3 jackpot_daemon.py [OPTIONS]

Autonomy Controls:
  --enable-hid                Enable USB HID gadget for physical payload delivery
  --no-rag                    Disable RAG reasoning (faster boot, lower RAM)
  --no-bjorn                  Disable Bjorn orchestrator (XFS-only mode)
  --no-watchdog               Disable autonomous trigger
  --no-drone                  Disable the edge_ai scan+exploit drone
  --no-display                Disable e-ink telemetry

Targeting:
  --subnet CIDR               Override scan subnet (default: 192.168.1.0/24)
  --kb-sync-interval SECONDS  UnifiedKB sync frequency (default: 30)

Diagnostics:
  -v, --verbose               Debug-level logging
```

Common Invocations

```bash
# Full autonomous device, HID enabled, on a /24 network
sudo python3 jackpot_daemon.py --enable-hid --subnet 10.0.0.0/24

# Lab test: no hardware, no Bjorn, pure XFS drone
python3 jackpot_daemon.py --no-bjorn --no-hid --no-display -v

# Stealth: minimal footprint, slower KB sync
sudo python3 jackpot_daemon.py --enable-hid --kb-sync-interval 120

# Raspberry Pi Zero (no RAG, saves ~60MB RAM)
sudo python3 jackpot_daemon.py --enable-hid --no-rag
```

---

🔬 How the Autonomy Works

The daemon has no user-facing prompts. Once started, it runs the following loop forever:

Phase 1 — Discovery (0-60s)

Bjorn's NetworkScanner (loaded automatically by the Bjorn orchestrator) sweeps the subnet, records every live host and its open ports to netkb.csv. Meanwhile, Edge AI's NetworkJackpotDrone independently scans for XFS service banners.

Phase 2 — Credential Acquisition (60s-30min)

Bjorn's action modules fire against discovered hosts:

· ssh_connector.py → SSH brute-force
· smb_connector.py → SMB brute-force + share enumeration
· ftp_connector.py, sql_connector.py, rdp_connector.py, telnet_connector.py
· Child actions trigger on parent success: steal_files_ssh.py, steal_files_smb.py, etc.

All results stream into Bjorn/data/output/crackedpwd/*.csv.

Phase 3 — KB Sync (every 30s)

The UnifiedKB background thread imports Bjorn's findings into brain.db, tagging any host with an XFS port (7777/8888/9999/8080) as a high-value target.

Phase 4 — Detection (continuous)

Edge AI's JackpotWatchdog polls four signals per cycle:

1. XFS service on subnet
2. Bjorn netkb targets with XFS ports
3. Local XFS loopback
4. Jackpot log patterns

When two signals fire, the watchdog triggers.

Phase 5 — Autonomous Trigger (event-driven)

On trigger, the watchdog:

1. Queries the RAG brain: "best attack pattern for ATM <ip> XFS jackpot"
2. RAG returns one of: classic_dispense, denial_bypass, state_overflow, rapid, stealth
3. Calls RemoteXFSExploit.exploit_sequence(ip, port) with the selected pattern
4. Executes the XFS command chain via xfsc or raw socket
5. Persists result to brain.db.jackpot_attempts and Bjorn's netkb.csv
6. Pushes telemetry to the e-ink display
7. Enters 300s cooldown before re-arming

Phase 6 — Payload Delivery (optional, HID-enabled)

If --enable-hid is set and the USB gadget is plugged into an ATM's service port:

· GadgetManager enumerates RNDIS/ECM + HID keyboard
· PayloadTriggerEngine detects the gadget_host event
· DuckyRunner executes the configured DuckyScript payload
· For offline ATMs where XFS-over-network fails, this provides direct input injection

Phase 7 — Loop

After cooldown, the watchdog re-arms. Bjorn continues running its own scan/brute-force cycle. The drone keeps probing. The device runs indefinitely.

---

📁 Project Layout

```
jackpot-device/
├── jackpot_daemon.py              ← MAIN ENTRY POINT
├── requirements.txt               ← Top-level Python deps
│
├── Bjorn/                         ← Layer 1: Offensive tooling
│   ├── orchestrator.py            ← Heuristic action scheduler
│   ├── shared.py                  ← Config, paths, KB management
│   ├── init_shared.py             ← Singleton shared_data
│   ├── actions/
│   │   ├── scanning.py            ← NetworkScanner
│   │   ├── ssh_connector.py       ← SSH brute-force
│   │   ├── smb_connector.py       ← SMB brute-force
│   │   ├── ftp_connector.py       ← FTP brute-force
│   │   ├── sql_connector.py       ← MySQL brute-force
│   │   ├── rdp_connector.py       ← RDP brute-force
│   │   ├── telnet_connector.py    ← Telnet brute-force
│   │   ├── xfs_connector.py       ← ★ NEW: XFS jackpot action
│   │   ├── steal_files_*.py       ← File exfiltration
│   │   └── nmap_vuln_scanner.py   ← Vulnerability scanning
│   ├── config/                    ← actions.json, shared_config.json
│   └── data/                      ← netkb.csv, output/crackedpwd/*.csv
│
├── edge_ai/                       ← Layer 2: RAG brain + XFS
│   ├── config.py                  ← Paths, XFS tuning, JACKPOT_CONFIG
│   ├── agent.py                   ← RAG reasoning + jackpot detection
│   ├── rag.py                     ← FAISS vector search
│   ├── embedder.py                ← ONNX sentence embeddings
│   ├── reranker.py                ← Cross-encoder reranking
│   ├── network_xfs.py             ← RemoteXFSExploit, NetworkJackpotDrone
│   ├── watchdog.py                ← ★ REWRITTEN: autonomous trigger
│   ├── unified_kb.py              ← ★ NEW: Bjorn ↔ edge_ai bridge
│   ├── sqlite_db.py               ← BrainDB persistence
│   ├── executor.py                ← Tool router
│   ├── web_interface.py           ← Flask dashboard
│   ├── build_faiss.py             ← Index builder
│   ├── data/                      ← brain.db, faiss_index.bin, *.onnx
│   └── rpi/                       ← Layer 3: Hardware payloads
│       ├── agent/
│       │   ├── offensive/
│       │   │   ├── ducky.py       ← DuckyScript interpreter
│       │   │   ├── hid_keyboard.py
│       │   │   ├── payload_triggers.py
│       │   │   └── modules/       ← 12 exploit modules
│       │   ├── workers/
│       │   │   ├── gadget.py      ← USB composite gadget
│       │   │   ├── payload_runner.py
│       │   │   ├── recon.py
│       │   │   └── wifi_handshake.py
│       │   └── ui/
│       │       └── display_manager.py
│       ├── payloads/              ← DuckyScript files
│       └── scripts/
│           ├── jackpot.service    ← systemd unit
│           ├── install_jackpot.sh ← One-shot installer
│           └── usb_gadget.sh
│
└── ei_dataset/                    ← Training data (RAG knowledge)
    ├── atm_attack_chain_dataset.csv
    ├── atm_vulnerability_complete.csv
    ├── atm_full_realistic_enriched.csv
    └── build_faiss.py
```

---

🧠 The RAG Brain

The device's decision-making comes from a FAISS-indexed knowledge base built from ei_dataset/. This corpus contains:

· 100+ ATM attack chains with success rates, complexity, and detection risk
· XFS vulnerability profiles (CVE-adjacent) for common ATM models
· Enriched device data — manufacturer, model, firmware version, location type
· Exploit command sequences — verified cdm dispense, cdm reset, cdm confirm chains

When the watchdog triggers, it asks the brain: "best XFS attack pattern for ATM 10.0.0.5 jackpot cash dispense". The RAG system:

1. Embeds the query via Embedder (ONNX, quantized, ~15MB RAM)
2. Searches faiss_index.bin for the top-K most similar attack records
3. Reranks results with Reranker (cross-encoder)
4. Returns the highest-scoring pattern name to the watchdog

This means the device learns from the corpus, not from hardcoded rules. Adding new rows to ei_dataset/*.csv and rebuilding (python3 edge_ai/build_faiss.py) immediately expands the device's tactical vocabulary.

Extending the Brain

To teach the device a new attack pattern:

```bash
# 1. Add a row to ei_dataset/atm_attack_chain_dataset.csv
#    Required columns: pattern, commands, success_rate, complexity, detection_risk

# 2. Rebuild the index
cd edge_ai
python3 build_faiss.py

# 3. Restart the daemon — the new pattern is now available
sudo systemctl restart jackpot
```

---

🖥 E-ink Telemetry

The Waveshare 2.13" HAT (B) renders a live dashboard in the field:

```
┌──────────────────────────────────────────────┐
│ RPi-Agent                 HANDSHAKE  HS:1   │  mode + handshake count
├──────────────────────────────────────────────┤
│ PEERS:1  DEAUTH:5           PWN:2            │  Pwnagotchi-style stats
│ APs:12 HOSTS:5    EXP:2/8         CH:6       │
│ CPU 45% RAM 62%           UP 01:23:45        │
├──────────────────────────────────────────────┤
│ GAD:ON+HID PLD:1/2          TestNet          │  gadget + payload status
├──────────────────────────────────────────────┤
│ 08:01 exp ssh_defaults 10.0.0.1 WIN          │  recent activity log
│ 08:01 HS! TestNet                            │
└──────────────────────────────────────────────┘
```

Refreshes every 12 seconds. Tri-color (black/white/red) for emphasis on wins and alerts.

For headless testing, the display can write a PNG preview instead:

```bash
python3 jackpot_daemon.py --no-hid    # mock display, writes logs/eink_preview.png
```

---

🔍 Verification & Debugging

Is each layer alive?

```bash
# Check Bjorn is discovering hosts
sqlite3 edge_ai/data/brain.db "SELECT COUNT(*) FROM bjorn_hosts;"

# Check credentials are being cracked
sqlite3 edge_ai/data/brain.db "SELECT COUNT(*) FROM bjorn_credentials;"

# Check high-value (XFS-adjacent) targets
sqlite3 edge_ai/data/brain.db \
    "SELECT ips, ports FROM bjorn_hosts WHERE is_xfs_candidate = 1;"

# Check jackpot attempts
sqlite3 edge_ai/data/brain.db \
    "SELECT target_ip, success, amount_dispensed, attempt_type \
     FROM jackpot_attempts ORDER BY id DESC LIMIT 10;"

# Check watchdog is detecting
journalctl -u jackpot | grep "Detection signals fired"

# Check RAG brain is loaded
journalctl -u jackpot | grep "RAG brain loaded"

# Check USB gadget enumerated
ls -la /dev/hidg0
ip link show usb0
```

Manual layer testing

```bash
# Test Bjorn standalone
cd Bjorn && python3 Bjorn.py

# Test edge_ai interactive REPL
cd edge_ai && python3 run.py
# Then type: /arm    (arms jackpot)
#            /trigger (manual trigger)
#            /scan   (scan for XFS)

# Test XFS exploit against a lab target
cd edge_ai
python3 -c "
from network_xfs import RemoteXFSExploit
e = RemoteXFSExploit()
print(e.exploit_sequence('192.168.1.100', 7777))
"

# Test UnifiedKB
cd edge_ai
python3 unified_kb.py --sync --summary

# Test display standalone
cd edge_ai/rpi
python3 display_manager.py --mock     # PNG output
python3 display_manager.py            # real HAT
```

---

⚙ Configuration

Bjorn Config (Bjorn/config/shared_config.json)

Controls network scanning and offensive module behavior:

```json
{
    "scan_interval": 180,
    "portlist": [20, 21, 22, 23, 25, 53, 69, 80, 110, 111, 135,
                 137, 139, 143, 161, 162, 389, 443, 445, 512, 513,
                 514, 587, 636, 993, 995, 1080, 1433, 1521, 2049,
                 3306, 3389, 5000, 5001, 5432, 5900, 8080, 8443,
                 9090, 10000, 7777, 8888, 9999],
    "mac_scan_blacklist": [],
    "ip_scan_blacklist": [],
    "failed_retry_delay": 600,
    "success_retry_delay": 900,
    "retry_failed_actions": true,
    "retry_success_actions": false,
    "scan_vuln_running": false
}
```

Edge AI Config (edge_ai/config.py)

Controls XFS behavior and jackpot parameters:

```python
JACKPOT_CONFIG = {
    'enabled': True,
    'auto_arm': False,
    'max_dispense': 2000,
    'retry_count': 3,
    'watchdog_interval': 5.0,
    'command_timeout': 10,
    'stealth_mode': True,
    'remote_trigger_enabled': True,
}

XFS_CONFIG = {
    'executable': 'xfsc.exe',
    'default_device': 'CashDispenser_1',
    'ports': [7777, 8888, 9999, 8080, 443, 80, 22, 23],
    'network_timeout': 5,
    'session_timeout': 30,
}

NETWORK_CONFIG = {
    'discovery_subnet': '192.168.1.0/24',
    'scan_interval': 60,
    'max_targets': 100,
    'stealth_mode': True,
}
```

Runtime Overrides

```bash
# Override subnet
python3 jackpot_daemon.py --subnet 10.0.0.0/24

# Faster KB sync (more DB pressure)
python3 jackpot_daemon.py --kb-sync-interval 10
```

---

🛠 Troubleshooting

Symptom Cause Fix
edge_ai import failed Missing edge_ai/data/*.npy Run python3 edge_ai/build_faiss.py
RAG brain loaded (0 entries) FAISS index empty Verify ei_dataset/*.csv are present, rebuild
Bjorn import failed Wrong working dir Run from repo root; Bjorn path auto-detected
no UDC controller found dwc2 not loaded Add dtoverlay=dwc2 to /boot/firmware/config.txt
Waveshare install failed Library not available Mock display will auto-activate; or pip install . from Waveshare repo
OOM killed on Pi Zero RAG + Bjorn + display exceed RAM Run with --no-rag or --no-display
Watchdog never triggers Threshold too high, no XFS found Lower --subnet scope; verify XFS ATMs on network
brain.db locked Multiple daemon instances pkill -f jackpot_daemon; only run one
Service crash-looping Missing deps journalctl -u jackpot -n 100 --no-pager

---

🔒 Security Hardening (for defense)

If you deploy ATMs and want to defend against tools like this:

1. Disable XFS debug ports — 7777/8888/9999 should never be exposed
2. Network segmentation — ATMs on isolated VLANs, no inter-ATM routing
3. Dispenser authentication — enforce Level 3 dispenser encryption per NCR spec
4. BIOS locking — prevent boot-to-USB, disable unused USB ports
5. Application whitelisting — AppLocker or equivalent; block all unsigned binaries
6. USB port sealing — physical tamper-evident covers on service ports
7. Mutual TLS — ATM ↔ host communication must be authenticated both ways
8. Monitoring — alert on any XFS command outside business hours
9. Cabinet lock upgrade — replace stock keys with unique, registered locks
10. Egress filtering — ATMs should never initiate outbound connections to arbitrary hosts

See docs/hardware-pinout.md and ei_dataset/atm_vulnerability_complete.csv for a full defensive playbook.

---

📚 Further Documentation

Document Content
docs/architecture.md Deep-dive on the integration architecture
docs/hardware-pinout.md Waveshare HAT wiring + SPI enablement
ei_dataset/atm_attack_chain_dataset.csv The RAG training corpus (attack patterns)
ei_dataset/atm_vulnerability_complete.csv XFS vulnerability catalog
Bjorn/orchestrator.py How Bjorn schedules actions
edge_ai/agent.py How the RAG brain reasons about jackpots
edge_ai/network_xfs.py XFS protocol client implementation
edge_ai/rpi/payloads/manifest.yaml HID payload trigger rules

---

🧩 Extending the Device

Add a new XFS attack pattern

1. Add a row to ei_dataset/atm_attack_chain_dataset.csv with the new pattern name and its command list.
2. Rebuild: cd edge_ai && python3 build_faiss.py
3. The watchdog will now be able to select it via RAG.

Add a new Bjorn offensive module

1. Create Bjorn/actions/your_module.py following the Bjorn action contract (b_class, b_module, b_status, b_port, b_parent).
2. Bjorn auto-discovers it on next boot (shared.generate_actions_json()).
3. The orchestrator will schedule it against matching targets.

Add a new HID payload

1. Drop a .ducky file in edge_ai/rpi/payloads/.
2. Add a trigger rule to edge_ai/rpi/payloads/manifest.yaml:
   ```yaml
   - event: exploit_success
     module: xfs_jackpot
     payload: payloads/on_jackpot_win.ducky
     cooldown_s: 60
   ```
3. On the next successful XFS jackpot, the payload fires automatically.

Add a new hardware target (NFC, EMV, etc.)

1. Create a module in edge_ai/rpi/agent/offensive/modules/.
2. Subclass ExploitModule from base.py.
3. Register it in modules/__init__.py.
4. It will be scheduled by ExploitChain on any host with matching open ports.

---

🤝 Attribution

This device integrates work from three independent offensive security projects:

· Bjorn by infinition — MIT License
· Edge AI (this repo) — MIT License
· P4wnP1 by RoganDawes — GPL-3.0
· Pwnagotchi by evilsocket — GPL-3.0

XFS protocol specifications referenced from CEN/CWA 16926 (public).

---

📜 License

MIT — see LICENSE.

Use responsibly. Use legally. Use only where you have written authorization.

```
