# CyberAgent

Pwnagotchi + Bjorn + P4wnP1 offensive agent for Raspberry Pi Zero W with Waveshare 2.13" tri-color e-ink.

## Quick start

```bash
sudo apt install aircrack-ng iw sshpass   # on Pi
pip install -r requirements.txt
sudo raspi-config   # enable SPI

python3 agent/main.py --mock-display              # dev preview
sudo python3 agent/main.py --enable-gadget        # full stack on device
```

Config: `config/default.yaml` → copy to `config/local.yaml` to override.

## Layout

```
agent/           Python package (orchestrator, workers, UI, offensive modules)
config/          YAML defaults
docs/            Architecture + hardware notes
payloads/        DuckyScript payloads + trigger manifest
scripts/         USB gadget setup
backend_worker.py / display_manager.py   Root shims
```

## Docs

- [Architecture & display layout](docs/architecture.md)
- [E-ink HAT pinout & SPI](docs/hardware-pinout.md)

## Manual payload trigger

```bash
echo on_pwn.ducky > payloads/trigger.request
```
