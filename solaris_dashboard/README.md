# Solaris FZ-500 Dashboard

Live sensor dashboard + test control + WiFi switcher for the Solaris IR Heat Deflection / Sweat Egress test rig.

## Features

- Real-time charts for TC-A, TC-B (MAX31855 via SPI), and air-gap temp (DS18B20 via OneWire)
- Large readout numbers for each sensor
- IR lamp state + elapsed timer, manual ON/OFF toggle
- Automated test sequence: warmup → lamp on → cooldown, with configurable durations
- CSV export per test, downloadable from the UI
- WiFi switcher: one-click toggle between ISEEYOU2 (home) and FX4 (hotspot)
- Auto-launch in Chromium kiosk mode on the Pi's HDMI output
- Accessible from any device on the same network: `http://solaris.local:5000/`

## Install on the Pi

Copy this directory to `/home/fuze/solaris_dashboard/` on the Pi:

```bash
# From your laptop
scp -r solaris_dashboard fuze@solaris.local:/home/fuze/
```

Then SSH in and run the setup:

```bash
ssh fuze@solaris.local
cd ~/solaris_dashboard
./setup_kiosk.sh
sudo reboot
```

After reboot, the dashboard launches automatically on the HDMI monitor and is accessible at `http://solaris.local:5000/` from your laptop.

## Files

- `app.py` — Flask + Socket.IO backend. Polls sensors at 1 Hz, controls SSR on GPIO 17, runs test automation, handles WiFi switching
- `templates/index.html` — dashboard markup
- `static/dashboard.js` — Plotly charts, Socket.IO client, button handlers
- `setup_kiosk.sh` — one-shot installer: system deps, systemd services, sudoers config, kiosk auto-launch
- `kiosk.xinitrc` — created by setup script; starts Chromium in kiosk mode

## Hardware map (as wired 2026-04-21)

| Sensor | Interface | Pi pin | Notes |
|---|---|---|---|
| TC-A (plate) | SPI CE0 | Pin 24 | MAX31855 #1 |
| TC-B (plate) | SPI CE1 | Pin 26 | MAX31855 #2 |
| Air gap | OneWire | Pin 7 (GPIO 4) | DS18B20 + 4.7kΩ pull-up |
| IR lamp SSR | GPIO out | Pin 11 (GPIO 17) | DIWD SSR-25 DA |

## Runtime behavior

- Flask backend runs as `solaris-dashboard.service` (systemd), auto-starts on boot
- Chromium kiosk runs as `solaris-kiosk.service` on tty1, auto-starts on boot
- Test CSVs saved to `~/solaris_logs/solaris_YYYYMMDD_HHMMSS.csv`
- If a sensor is unavailable at startup, the backend logs a warning and returns fake data so the UI still works for development

## Security

- Passwordless sudo is granted **only** for `/usr/bin/nmcli`, scoped via `/etc/sudoers.d/solaris-nmcli`
- No other sudo escalation from the Flask app
- Flask binds to 0.0.0.0:5000 — assumed trusted LAN. For public deployment, add a reverse proxy with auth

## Stopping / restarting

```bash
sudo systemctl stop solaris-kiosk       # close Chromium
sudo systemctl stop solaris-dashboard   # stop Flask
sudo systemctl restart solaris-dashboard
sudo journalctl -u solaris-dashboard -f # tail logs
```
