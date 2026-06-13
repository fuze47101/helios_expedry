#!/usr/bin/env bash
# =====================================================================
# Helios -> Dropbox auto-sync  (run ON THE PI)
# Pushes ~/helios/data/*.csv (+ *.png) to Dropbox every 2 min via a
# systemd timer. DECOUPLED from the helios service — installing/running
# this never restarts helios, so it can't interrupt a running test.
#
# ONE-TIME SETUP (do this part interactively first):
#   1) Install rclone:           curl https://rclone.org/install.sh | sudo bash
#   2) Configure Dropbox remote:  rclone config
#        n) new remote
#        name> dropbox
#        Storage> dropbox
#        client_id / secret> (leave blank, press enter)
#        Edit advanced config> n
#        Use web browser to auto config> n   (headless Pi)
#        -> it prints a command; run that on a machine WITH a browser
#           (your Mac:  rclone authorize "dropbox"), sign in, paste the
#           token back into the Pi prompt.
#        y) yes this is OK   ->  q) quit
#   3) Test it:   rclone lsd dropbox:
#   4) Then run THIS script:   bash ~/setup_helios_dropbox.sh
# =====================================================================
set -e
REMOTE="dropbox:Helios/data"          # change "Helios/data" if you want a different folder
SRC="$HOME/helios/data"

mkdir -p "$SRC"

# --- the sync script ---
cat > "$HOME/helios_sync.sh" <<SYNC
#!/usr/bin/env bash
/usr/bin/rclone copy "$SRC" "$REMOTE" \
  --include "*.csv" --include "*.png" \
  --log-file "$HOME/helios/sync.log" --log-level INFO
SYNC
chmod +x "$HOME/helios_sync.sh"

# --- systemd oneshot service ---
sudo tee /etc/systemd/system/helios-sync.service >/dev/null <<UNIT
[Unit]
Description=Helios data -> Dropbox sync
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
User=$USER
ExecStart=$HOME/helios_sync.sh
UNIT

# --- systemd timer: every 2 min ---
sudo tee /etc/systemd/system/helios-sync.timer >/dev/null <<TIMER
[Unit]
Description=Run Helios Dropbox sync every 2 minutes

[Timer]
OnBootSec=2min
OnUnitActiveSec=2min
Unit=helios-sync.service

[Install]
WantedBy=timers.target
TIMER

sudo systemctl daemon-reload
sudo systemctl enable --now helios-sync.timer

echo "== DONE =="
echo "Syncing $SRC  ->  $REMOTE  every 2 min."
echo "Check:   systemctl status helios-sync.timer"
echo "         rclone ls $REMOTE | tail"
echo "         tail ~/helios/sync.log"
echo "Run once now:   systemctl start helios-sync.service"
