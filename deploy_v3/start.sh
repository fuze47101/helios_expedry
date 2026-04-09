#!/bin/bash
# ExpeDRY FeatherV2 — Launch script
# Rotates screen and starts the app

# Rotate display (try both possible output names)
wlr-randr --output HDMI-A-1 --transform 270 2>/dev/null || \
wlr-randr --output HDMI-A-2 --transform 270 2>/dev/null || \
echo "wlr-randr rotation failed — may need manual rotation"

sleep 1

# Launch app
export DISPLAY=:0
cd /home/allied2/FeatherV2
exec python3 main.py
