#!/bin/bash
# ═══════════════════════════════════════════════════
# ExpeDRY FeatherV2 v3 — Full Deploy to Raspberry Pi
# Dual graphs + Scale + WiFi + CSV export
# ═══════════════════════════════════════════════════
#
# Usage:  chmod +x deploy.sh && ./deploy.sh
#
# Pi: alliedV2@<IP>  password: Allied2025
# App: /home/alliedV2/FeatherV2/
# ═══════════════════════════════════════════════════

# ── Config ──
PI_USER="alliedV2"
PI_HOST="${1:-192.168.1.178}"  # pass IP as arg or use default
PI="$PI_USER@$PI_HOST"
APP="/home/$PI_USER/FeatherV2"
DIR="$(cd "$(dirname "$0")" && pwd)"

echo "══════════════════════════════════════"
echo "  ExpeDRY v3 — Full Deploy"
echo "  Target: $PI:$APP"
echo "══════════════════════════════════════"

# Test SSH connection
echo "[0/8] Testing SSH connection..."
ssh -o ConnectTimeout=5 $PI "echo 'Connected!'" || {
    echo ""
    echo "  FAILED to reach $PI"
    echo "  Make sure Pi is on the same network."
    echo "  Usage: ./deploy.sh <pi-ip-address>"
    echo ""
    exit 1
}

# Backup
echo "[1/8] Backing up current files on Pi..."
BACKUP="backup_$(date +%Y%m%d_%H%M%S)"
ssh $PI "cd $APP && mkdir -p $BACKUP && cp main.py tester.kv $BACKUP/ 2>/dev/null; cp -r utils components $BACKUP/ 2>/dev/null"

# Ensure directories
echo "[2/8] Creating directories..."
ssh $PI "mkdir -p $APP/utils $APP/components $APP/camera $APP/assets"

# Deploy core files
echo "[3/8] Deploying main.py + tester.kv..."
scp "$DIR/main.py"    $PI:$APP/main.py
scp "$DIR/tester.kv"  $PI:$APP/tester.kv

# Deploy utils
echo "[4/8] Deploying utils/..."
scp "$DIR/utils/theme.py"      $PI:$APP/utils/theme.py
scp "$DIR/utils/Scale.py"      $PI:$APP/utils/Scale.py
scp "$DIR/utils/RS485.py"      $PI:$APP/utils/RS485.py
scp "$DIR/utils/Relay.py"      $PI:$APP/utils/Relay.py
scp "$DIR/utils/__init__.py"   $PI:$APP/utils/__init__.py

# Deploy components
echo "[5/8] Deploying components/..."
scp "$DIR/components/Controls.py"        $PI:$APP/components/Controls.py
scp "$DIR/components/Controls.kv"        $PI:$APP/components/Controls.kv
scp "$DIR/components/SaveDialog.py"      $PI:$APP/components/SaveDialog.py
scp "$DIR/components/SaveDialog.kv"      $PI:$APP/components/SaveDialog.kv
scp "$DIR/components/Test_Settings.py"   $PI:$APP/components/Test_Settings.py
scp "$DIR/components/Test_Settings.kv"   $PI:$APP/components/Test_Settings.kv
scp "$DIR/components/WarningDialog.py"   $PI:$APP/components/WarningDialog.py
scp "$DIR/components/WarningDialog.kv"   $PI:$APP/components/WarningDialog.kv
scp "$DIR/components/WeighDialog.py"     $PI:$APP/components/WeighDialog.py
scp "$DIR/components/WeighDialog.kv"     $PI:$APP/components/WeighDialog.kv
scp "$DIR/components/WifiDialog.py"      $PI:$APP/components/WifiDialog.py
scp "$DIR/components/WifiDialog.kv"      $PI:$APP/components/WifiDialog.kv
scp "$DIR/components/__init__.py"        $PI:$APP/components/__init__.py

# Deploy camera
echo "[6/8] Deploying camera/..."
scp "$DIR/camera/thermalcameraController.py"  $PI:$APP/camera/thermalcameraController.py
scp "$DIR/camera/guiController.py"            $PI:$APP/camera/guiController.py
scp "$DIR/camera/ColormapEnum.py"             $PI:$APP/camera/ColormapEnum.py
scp "$DIR/camera/values.py"                   $PI:$APP/camera/values.py
scp "$DIR/camera/__init__.py"                 $PI:$APP/camera/__init__.py

# Deploy assets
echo "[7/8] Deploying assets/..."
scp "$DIR/assets/ExpeDRY_logo.png"  $PI:$APP/assets/ExpeDRY_logo.png
scp "$DIR/assets/save-24.png"       $PI:$APP/assets/save-24.png

# Install/verify dependencies
echo "[8/8] Verifying Python dependencies..."
ssh $PI "pip install --break-system-packages pyserial smbus2 2>/dev/null"

echo ""
echo "══════════════════════════════════════"
echo "  Deploy complete!"
echo ""
echo "  v3 features:"
echo "    - Dual graphs (humidity + weight)"
echo "    - Live scale integration"
echo "    - WiFi settings from touchscreen"
echo "    - CSV export with weight data"
echo ""
echo "  To kill existing & relaunch:"
echo "    ssh $PI 'pkill -f main.py; sleep 1; cd $APP && python3 main.py &'"
echo ""
echo "  Or SSH in and run manually:"
echo "    ssh $PI"
echo "    cd $APP"
echo "    python3 main.py"
echo "══════════════════════════════════════"
