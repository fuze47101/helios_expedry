#!/bin/bash
# ═══════════════════════════════════════════════════
# ExpeDRY FeatherV2 — Deploy Rebuilt Modules to Pi
# ═══════════════════════════════════════════════════
# Pushes all reconstructed modules to the Pi.
# Run from Mac terminal (NOT from Pi SSH session).
#
# Pi: allied2@alliedV2.local  password: Allied2025
# App: /home/allied2/FeatherV2/
# ═══════════════════════════════════════════════════

PI="allied2@alliedV2.local"
APP="/home/allied2/FeatherV2"
DIR="$(cd "$(dirname "$0")" && pwd)"

echo "══════════════════════════════════════"
echo "  ExpeDRY — Deploy Rebuilt Modules"
echo "══════════════════════════════════════"

# Ensure remote directories exist
echo "[1/5] Creating directories on Pi..."
ssh $PI "mkdir -p $APP/utils $APP/components $APP/camera $APP/assets"

# Deploy utils
echo "[2/5] Deploying utils/..."
scp "$DIR/utils/Relay.py"    $PI:$APP/utils/Relay.py
scp "$DIR/utils/RS485.py"    $PI:$APP/utils/RS485.py
scp "$DIR/utils/__init__.py" $PI:$APP/utils/__init__.py

# Deploy components
echo "[3/5] Deploying components/..."
scp "$DIR/components/Controls.py"       $PI:$APP/components/Controls.py
scp "$DIR/components/Controls.kv"       $PI:$APP/components/Controls.kv
scp "$DIR/components/SaveDialog.py"     $PI:$APP/components/SaveDialog.py
scp "$DIR/components/SaveDialog.kv"     $PI:$APP/components/SaveDialog.kv
scp "$DIR/components/Test_Settings.py"  $PI:$APP/components/Test_Settings.py
scp "$DIR/components/Test_Settings.kv"  $PI:$APP/components/Test_Settings.kv
scp "$DIR/components/WarningDialog.py"  $PI:$APP/components/WarningDialog.py
scp "$DIR/components/WarningDialog.kv"  $PI:$APP/components/WarningDialog.kv
scp "$DIR/components/__init__.py"       $PI:$APP/components/__init__.py

# Deploy camera
echo "[4/5] Deploying camera/..."
scp "$DIR/camera/thermalcameraController.py" $PI:$APP/camera/thermalcameraController.py
scp "$DIR/camera/guiController.py"           $PI:$APP/camera/guiController.py
scp "$DIR/camera/ColormapEnum.py"            $PI:$APP/camera/ColormapEnum.py
scp "$DIR/camera/values.py"                  $PI:$APP/camera/values.py
scp "$DIR/camera/__init__.py"                $PI:$APP/camera/__init__.py

# Install dependencies
echo "[5/5] Installing Python dependencies..."
ssh $PI "pip install --break-system-packages smbus2 pyserial kivy neukivy kivy-garden opencv-python-headless numpy pyudev"
ssh $PI "pip install --break-system-packages kivy_garden.graph || python3 -m garden install graph"

echo ""
echo "══════════════════════════════════════"
echo "  Deploy complete!"
echo ""
echo "  Files deployed:"
echo "    utils/Relay.py, RS485.py"
echo "    components/Controls, SaveDialog,"
echo "      Test_Settings, WarningDialog"
echo "    camera/thermalcameraController,"
echo "      guiController, ColormapEnum, values"
echo ""
echo "  To launch:"
echo "    ssh $PI"
echo "    cd $APP"
echo "    python3 main.py"
echo ""
echo "  To kill existing:"
echo "    ssh $PI 'pkill -f main.py'"
echo "══════════════════════════════════════"
