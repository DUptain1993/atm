# CyberAgent — Pwnagotchi + Bjorn + P4wnP1 Offensive Blend

Headless Raspberry Pi Zero W attack agent with Waveshare 2.13" tri-color e-ink telemetry.

## What each project contributes

| Source | Capability in this repo |
|--------|-------------------------|
| **Pwnagotchi** | WiFi handshake hunting (monitor mode, deauth, cap capture), telemetry grid UI |
| **Bjorn** | Subnet recon, port sweep, exploit chain runner (`ssh_defaults`, `ftp_anon`, `http_defaults`) |
| **P4wnP1** | USB composite gadget (RNDIS/ECM + HID keyboard), DuckyScript payload runner |

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     Raspberry Pi Zero W                      │
│  backend_worker (orchestrator)                               │
│    ├─ recon        Bjorn subnet scan + port probe             │
│    ├─ wifi         Pwnagotchi handshake hunt                  │
│    ├─ exploits     Bjorn module chain on open services        │
│    ├─ gadget       P4wnP1 ConfigFS RNDIS/ECM + HID           │
│    └─ payloads     P4wnP1 DuckyScript → /dev/hidg0          │
│                          │                                    │
│                          ▼ AgentState                         │
│  display_manager   Pwnagotchi-style 250×122 offensive grid   │
└──────────────────────────────────────────────────────────────┘
```

## E-ink display layout

```
┌──────────────────────────────────────────────┐
│ RPi-Agent                 HANDSHAKE  HS:1   │  mode + handshakes (red)
├──────────────────────────────────────────────┤
│ PEERS:1  DEAUTH:5           PWN:2            │  Pwnagotchi session stats
│ APs:12 HOSTS:5    EXP:2/8         CH:6       │
│ CPU 45% RAM 62%           UP 01:23:45        │
├──────────────────────────────────────────────┤
│ GAD:ON+HID PLD:1/2          TestNet          │  payload stats + WiFi target
├──────────────────────────────────────────────┤
│ 08:01 exp ssh_defaults 10.0.0.1 WIN          │
│ 08:01 HS! TestNet                            │
└──────────────────────────────────────────────┘
```


## Bjorn modules (12)

`ssh_defaults`, `ftp_anon`, `http_defaults`, `http_sensitive`, `telnet_defaults`,
`redis_unauth`, `mongo_unauth`, `mysql_defaults`, `smb_null`, `snmp_public`,
`rdp_probe`, `vnc_probe`

## P4wnP1 payload triggers

Rules in `payloads/manifest.yaml` (+ `config payload_triggers`):

| Event | When fired |
|-------|------------|
| `boot` | Agent start (optional) |
| `gadget_host` | USB host connects (UDC configured) |
| `handshake` | WPA handshake captured |
| `exploit_success` | Bjorn module wins (optional `module` filter) |
| `scan_complete` | Recon sweep finished |
| `interval` | Periodic (`interval_s` on rule) |
| manual | Write payload name to `payloads/trigger.request` |

Example manual trigger: `echo on_pwn.ducky > payloads/trigger.request`

## Deployment

```bash
# On Pi — system tools for WiFi/offense
sudo apt install aircrack-ng iw sshpass

pip install -r requirements.txt

# Waveshare library + SPI (see docs/hardware-pinout.md)
sudo raspi-config  # enable SPI

# Run full offensive stack (mock display for dev)
python3 agent/main.py --mock-display

# On device with HAT + root for gadget/WiFi
sudo python3 agent/main.py --enable-gadget --payload-auto
```

Config: `config/default.yaml` or gitignored `config/local.yaml`.

## Payloads

Place DuckyScript files in `payloads/`. Set `payload_file` in config or use `--payload-auto` to run when HID connects.

## Captures

WiFi handshakes saved under `captures/handshakes/` when `aircrack-ng` is available.
