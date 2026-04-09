#!/bin/bash
# ExpeDRY — Install systemd service + WiFi permissions
# Run on Pi: sudo bash ~/FeatherV2/setup_service.sh

set -e

echo "=== ExpeDRY Service Setup ==="

# 1. Install the systemd service
echo "[1/4] Installing systemd service..."
cp /home/allied2/FeatherV2/expedry.service /etc/systemd/system/expedry.service
systemctl daemon-reload
systemctl enable expedry.service
echo "  Service installed and enabled"

# 2. Allow allied2 to manage WiFi without sudo
echo "[2/4] Setting up WiFi permissions..."
cat > /etc/polkit-1/localauthority/50-local.d/10-network-manager.pkla << 'POLKIT'
[Allow allied2 to manage NetworkManager]
Identity=unix-user:allied2
Action=org.freedesktop.NetworkManager.*
ResultAny=yes
ResultInactive=yes
ResultActive=yes
POLKIT
echo "  WiFi permissions set"

# 3. Ensure allied2 is in the right groups
echo "[3/4] Checking user groups..."
usermod -aG netdev,dialout,i2c,video,input allied2 2>/dev/null || true
echo "  User groups updated"

# 4. Create log file
echo "[4/4] Setting up log..."
touch /home/allied2/FeatherV2/expedry.log
chown allied2:allied2 /home/allied2/FeatherV2/expedry.log
echo "  Log at /home/allied2/FeatherV2/expedry.log"

echo ""
echo "=== Done! ==="
echo "Start now:    sudo systemctl start expedry"
echo "Check status: sudo systemctl status expedry"
echo "View log:     tail -f /home/allied2/FeatherV2/expedry.log"
echo "Reboot:       sudo reboot  (app will auto-start)"
