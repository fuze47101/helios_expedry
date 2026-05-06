#!/usr/bin/env bash
# Solaris FZ-500 kiosk setup
# Run as the 'fuze' user on the Solaris Pi. Idempotent — safe to re-run.
set -euo pipefail

USER_NAME="fuze"
APP_DIR="/home/${USER_NAME}/solaris_dashboard"
VENV="/home/${USER_NAME}/solaris-env"

if [[ "${USER}" != "${USER_NAME}" ]]; then
  echo "Run as user '${USER_NAME}' (current: ${USER})" >&2
  exit 1
fi

echo "==> Installing X stack + Chromium + helpers"
sudo apt update
sudo apt install -y chromium xserver-xorg xinit openbox unclutter \
  liblgpio-dev python3-lgpio python3-dev

echo "==> Python deps in venv"
source "${VENV}/bin/activate"
pip install flask flask-socketio eventlet spidev gpiozero lgpio matplotlib

echo "==> Passwordless sudo for nmcli (narrow scope)"
sudo tee /etc/sudoers.d/solaris-nmcli >/dev/null <<SUDO
${USER_NAME} ALL=(ALL) NOPASSWD: /usr/bin/nmcli
SUDO
sudo chmod 0440 /etc/sudoers.d/solaris-nmcli
sudo visudo -c -f /etc/sudoers.d/solaris-nmcli

echo "==> OneWire (DS18B20) overlay in /boot/firmware/config.txt"
CONFIG_TXT="/boot/firmware/config.txt"
if [[ ! -f "${CONFIG_TXT}" ]]; then
  # Fall back to legacy path (pre-Bookworm)
  CONFIG_TXT="/boot/config.txt"
fi
echo "  config.txt path: ${CONFIG_TXT}"
if ! sudo grep -q "^dtoverlay=w1-gpio" "${CONFIG_TXT}"; then
  echo "  (not present — appending)"
  echo "dtoverlay=w1-gpio" | sudo tee -a "${CONFIG_TXT}" >/dev/null
  # Verify the write actually landed
  if ! sudo grep -q "^dtoverlay=w1-gpio" "${CONFIG_TXT}"; then
    echo "  ERROR: failed to persist dtoverlay=w1-gpio to ${CONFIG_TXT}" >&2
    exit 1
  fi
  echo "  (added — reboot required for OneWire to activate at boot)"
else
  echo "  (already present)"
fi
# Also activate at runtime so you don't have to reboot right now
if ! lsmod | grep -q "^w1_gpio"; then
  echo "  activating overlay at runtime via dtovertay w1-gpio"
  sudo dtoverlay w1-gpio || true
fi
sudo modprobe w1-gpio w1-therm 2>/dev/null || true

echo "==> Enable SPI + I2C (needed for sensors)"
sudo raspi-config nonint do_spi 0
sudo raspi-config nonint do_i2c 0

echo "==> systemd service: solaris-dashboard (Flask backend)"
sudo tee /etc/systemd/system/solaris-dashboard.service >/dev/null <<UNIT
[Unit]
Description=Solaris FZ-500 Dashboard (Flask)
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=${USER_NAME}
WorkingDirectory=${APP_DIR}
ExecStart=${VENV}/bin/python ${APP_DIR}/app.py
Restart=on-failure
RestartSec=3

[Install]
WantedBy=multi-user.target
UNIT

echo "==> systemd service: solaris-kiosk (Chromium kiosk on HDMI)"
sudo tee /etc/systemd/system/solaris-kiosk.service >/dev/null <<UNIT
[Unit]
Description=Solaris FZ-500 Kiosk (Chromium on HDMI)
After=solaris-dashboard.service graphical.target
Wants=solaris-dashboard.service

[Service]
Type=simple
User=${USER_NAME}
PAMName=login
Environment=XDG_RUNTIME_DIR=/run/user/1000
Environment=DISPLAY=:0
TTYPath=/dev/tty1
ExecStart=/usr/bin/startx ${APP_DIR}/kiosk.xinitrc -- :0 vt1 -nolisten tcp
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
UNIT

echo "==> kiosk.xinitrc (starts openbox + chromium)"
cat > "${APP_DIR}/kiosk.xinitrc" <<'XINIT'
#!/usr/bin/env bash
xset -dpms
xset s off
xset s noblank
unclutter -idle 0.1 -root &
openbox-session &
sleep 3
# Wait for dashboard to come up (up to 30s)
for i in $(seq 1 30); do
  if curl -sf http://localhost:5000/ >/dev/null; then break; fi
  sleep 1
done
exec chromium \
  --kiosk \
  --no-first-run \
  --noerrdialogs \
  --disable-infobars \
  --disable-translate \
  --disable-features=TranslateUI \
  --check-for-update-interval=31536000 \
  --overscroll-history-navigation=0 \
  --password-store=basic \
  --app=http://localhost:5000/
XINIT
chmod +x "${APP_DIR}/kiosk.xinitrc"

echo "==> Allowing console user to start X on tty1"
# Xwrapper.config should allow 'anybody' for startx from service
if ! grep -q "^allowed_users" /etc/X11/Xwrapper.config 2>/dev/null; then
  sudo tee /etc/X11/Xwrapper.config >/dev/null <<XWRAP
allowed_users=anybody
needs_root_rights=yes
XWRAP
fi

echo "==> Enable + start services"
sudo systemctl daemon-reload
sudo systemctl enable solaris-dashboard.service
sudo systemctl enable solaris-kiosk.service
sudo systemctl restart solaris-dashboard.service

echo ""
echo "=========================================="
echo "Setup complete."
echo "  Dashboard: http://$(hostname -I | awk '{print $1}'):5000/"
echo "  Local URL: http://localhost:5000/"
echo ""
echo "Next steps:"
echo "  1. Reboot so the OneWire overlay activates: sudo reboot"
echo "  2. On next boot the monitor will auto-launch the dashboard full-screen"
echo "  3. From laptop, open http://solaris.local:5000/"
echo "=========================================="
