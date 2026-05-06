#!/bin/bash
# ═══════════════════════════════════════════════════
# ExpeDRY GUI v2 Deployment Script
# Push updated files to Raspberry Pi via SSH
# ═══════════════════════════════════════════════════
#
# Usage:  ./deploy.sh
# Or run individual scp commands below manually.
#
# Pi: alliedV2@192.168.1.178  password: Allied2025
# App: /home/alliedV2/FeatherV2/
# ═══════════════════════════════════════════════════

PI="alliedV2@192.168.1.178"
APP="/home/alliedV2/FeatherV2"

echo "══════════════════════════════════════"
echo "  ExpeDRY GUI v2 — Deploying to Pi"
echo "══════════════════════════════════════"

# Backup current files first
echo "[1/7] Backing up current files on Pi..."
ssh $PI "cd $APP && mkdir -p backup_$(date +%Y%m%d) && cp main.py tester.kv utils/theme.py components/WeighDialog.py components/WeighDialog.kv backup_$(date +%Y%m%d)/ 2>/dev/null"

# Deploy files
echo "[2/7] Deploying main.py..."
scp ./main.py $PI:$APP/main.py

echo "[3/7] Deploying tester.kv..."
scp ./tester.kv $PI:$APP/tester.kv

echo "[4/7] Deploying utils/theme.py..."
scp ./theme.py $PI:$APP/utils/theme.py

echo "[5/7] Deploying components/WeighDialog.py..."
scp ./WeighDialog.py $PI:$APP/components/WeighDialog.py

echo "[6/7] Deploying components/WeighDialog.kv..."
scp ./WeighDialog.kv $PI:$APP/components/WeighDialog.kv

echo "[7/7] Deploying utils/Scale.py (if not present)..."
scp ../mnt/Desktop/helios/Scale.py $PI:$APP/utils/Scale.py

echo ""
echo "══════════════════════════════════════"
echo "  Deployment complete!"
echo ""
echo "  To launch:"
echo "    ssh $PI"
echo "    cd $APP"
echo "    source FeatherV2/bin/activate"
echo "    python3 main.py"
echo ""
echo "  To kill existing GUI first:"
echo "    ssh $PI 'pkill -f main.py'"
echo "══════════════════════════════════════"
