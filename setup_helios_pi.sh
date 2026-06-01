#!/usr/bin/env bash
# =====================================================================
# Helios Pi provisioning — restores the wine-fridge controller
# (helios_control.py Flask dashboard) onto a freshly flashed SD card.
#
# RUN THIS *ON THE PI* after first boot, from the folder that contains
# both this script AND helios_control.py.  e.g.:
#   scp helios_control.py setup_helios_pi.sh <user>@<pi-ip>:~/
#   ssh <user>@<pi-ip>
#   bash ~/setup_helios_pi.sh
# =====================================================================
set -e
APP_DIR="$HOME/helios"
VENV="$HOME/helios-env"
# config.txt location differs Bookworm (/boot/firmware) vs older (/boot)
CFG=/boot/firmware/config.txt; [ -f "$CFG" ] || CFG=/boot/config.txt
CMD=/boot/firmware/cmdline.txt; [ -f "$CMD" ] || CMD=/boot/cmdline.txt

echo "== 1/6  system packages =="
sudo apt-get update
sudo apt-get install -y python3-venv python3-pip i2c-tools python3-lgpio liblgpio-dev

echo "== 2/6  enable SPI + hardware I2C(bus1) + UART(ttyAMA0 for Modbus) =="
sudo raspi-config nonint do_spi 0      # SPI on  (MAX31855, CE1)
sudo raspi-config nonint do_i2c 0      # I2C bus 1 on (SDP810 0x25)
# Free up the PL011 UART on GPIO14/15 for /dev/ttyAMA0 (Waveshare Modbus relay):
grep -q "^enable_uart=1"        "$CFG" || echo "enable_uart=1"        | sudo tee -a "$CFG"
grep -q "^dtoverlay=disable-bt" "$CFG" || echo "dtoverlay=disable-bt" | sudo tee -a "$CFG"
sudo systemctl disable hciuart 2>/dev/null || true
# Remove the serial login console so it doesn't fight the relay:
sudo sed -i 's/console=serial0,[0-9]* //' "$CMD" || true
sudo systemctl disable serial-getty@ttyAMA0.service 2>/dev/null || true

echo "== 3/6  software I2C bus 15 (SHT41 on GPIO22=SDA / GPIO25=SCL) =="
grep -q "i2c_gpio_sda=22" "$CFG" || \
  echo "dtoverlay=i2c-gpio,bus=15,i2c_gpio_sda=22,i2c_gpio_scl=25" | sudo tee -a "$CFG"

echo "== 4/6  python venv + deps =="
python3 -m venv "$VENV"
"$VENV/bin/pip" install --upgrade pip
# pymodbus>=3.7 required for the write_coil(device_id=...) signature used in the code.
# rpi-lgpio is the Pi 5 drop-in for RPi.GPIO (legacy RPi.GPIO crashes on Pi 5: "Cannot determine SOC peripheral base address").
"$VENV/bin/pip" install flask smbus2 spidev "pymodbus>=3.7" pyserial rpi-lgpio

echo "== 5/6  install app =="
mkdir -p "$APP_DIR"
cp "$(dirname "$0")/helios_control.py" "$APP_DIR/"

echo "== 6/6  systemd autostart service =="
sudo tee /etc/systemd/system/helios.service >/dev/null <<UNIT
[Unit]
Description=Helios wine-fridge controller (Flask dashboard :5000)
After=network-online.target
Wants=network-online.target

[Service]
User=$USER
WorkingDirectory=$APP_DIR
ExecStart=$VENV/bin/python $APP_DIR/helios_control.py
Restart=on-failure
RestartSec=3

[Install]
WantedBy=multi-user.target
UNIT
sudo systemctl daemon-reload
sudo systemctl enable helios.service

echo "== 7/7  touchscreen Chromium kiosk -> dashboard =="
# NOTE: needs the Raspberry Pi OS *Desktop* image (not Lite) and Desktop Autologin
#       (raspi-config > 1 System Options > S5 Boot/Auto Login > Desktop Autologin).
CHROME=$(command -v chromium-browser || command -v chromium || echo chromium-browser)
mkdir -p "$HOME/.config/autostart"
cat > "$HOME/.config/autostart/helios-kiosk.desktop" <<KIOSK
[Desktop Entry]
Type=Application
Name=Helios Kiosk
Exec=bash -c 'sleep 8; $CHROME --noerrdialogs --disable-infobars --touch-events=enabled --enable-features=TouchpadAndWheelScrollLatching --kiosk http://localhost:5000'
X-GNOME-Autostart-enabled=true
KIOSK
echo "  kiosk autostart written. Old touchscreen ran rotated 270 deg —"
echo "  set rotation in raspi-config > Display, or the Screen Configuration app, if needed."

echo
echo "== DONE — reboot to apply interface + UART changes:  sudo reboot =="
echo "After reboot:"
echo "  sudo systemctl status helios       # should be active (running)"
echo "  i2cdetect -y 1                     # expect 0x25 (SDP810) and 0x44 (SHT41 on bus 15: -y 15)"
echo "  browse to  http://<pi-ip>:5000"
