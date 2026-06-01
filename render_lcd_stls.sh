#!/bin/bash
# ============================================================
# Render LCD enclosure STLs — front + back as separate files
# Andrew 2026-05-29
# ============================================================
# Usage: bash render_lcd_stls.sh
#
# Outputs (in same directory as the .scad):
#   lcd_enclosure_FRONT.stl   — the LCD-window side (smaller, prints first)
#   lcd_enclosure_BACK.stl    — the deep box with all the back-face cutouts
# ============================================================

set -e

SCAD_FILE="$(dirname "$0")/lcd_enclosure.scad"
OUT_DIR="$(dirname "$0")"

# Find OpenSCAD binary on macOS
OPENSCAD="/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD"
if [ ! -x "$OPENSCAD" ]; then
    # Fallback to PATH
    OPENSCAD="$(command -v openscad || echo "")"
fi

if [ -z "$OPENSCAD" ] || [ ! -x "$OPENSCAD" ]; then
    echo "ERROR: OpenSCAD not found."
    echo "  Looked at: /Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD"
    echo "  Looked at: \$(which openscad)"
    echo ""
    echo "Install OpenSCAD from https://openscad.org/downloads.html"
    exit 1
fi

echo "Using OpenSCAD: $OPENSCAD"
echo ""

echo "Rendering FRONT half..."
"$OPENSCAD" -o "$OUT_DIR/lcd_enclosure_FRONT.stl" \
    -D 'PART="front"' \
    "$SCAD_FILE"

echo "Rendering BACK half..."
"$OPENSCAD" -o "$OUT_DIR/lcd_enclosure_BACK.stl" \
    -D 'PART="back"' \
    "$SCAD_FILE"

echo ""
echo "Done. STL files written to:"
echo "  $OUT_DIR/lcd_enclosure_FRONT.stl"
echo "  $OUT_DIR/lcd_enclosure_BACK.stl"
