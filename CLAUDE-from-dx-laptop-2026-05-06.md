# DX LAPTOP CLAUDE.md (snapshot from origin/main on 2026-05-06)

This file was created during the pre-Mac-transfer cleanup.
It contains the version of CLAUDE.md that was on origin/main at the time
(commit `0ec83e6` — "Sync CLAUDE.md from dx laptop").

It was a 39-line stripped-down version that REPLACED a 772-line
comprehensive CLAUDE.md when the dx laptop synced.

Below is the content. The Mesh_Frames_v1.scad design notes here are
REAL WORK that should be hand-merged into the main CLAUDE.md when convenient.
After merging, delete this holding file.

---

# ExpeDRY Capsule — Working Memory

## Printer
- **Bambu H2D** (dual-head / H-bot)
- Build volume: **350 × 320 × 325 mm** (single extruder mode)
- Diagonal bed reach: ~474 mm — large parts can be oriented diagonally
- Direct drive extruder, handles TPU 95A well

## Materials on hand
- **TPU 95A** — Overture brand, flexible filament for mesh frames
  - Print 30–45 mm/s, bed 50 °C, nozzle 230 °C, no supports, flat orientation
- **Mesh**: 0.2 mm wedding veil / tulle (sandwiched in laminate frames)

## Current design: Mesh_Frames_v1.scad
- Replaces outer + inner cages with laminate mesh frames
- **Laminate stackup**
  - Outer: 1.4 + 0.2 + 1.4 = 3.0 mm (into 3.2 mm groove)
  - Inner: 0.8 + 0.2 + 0.8 = 1.8 mm (into 2.0 mm groove)
- **Outer split into 2 halves** (~231 mm each, fits H2D bed)
- **Seam overlap**: 15 mm single-sheet tongue on A-sheet, lap joint heat-pressed
- **PLA support posts**: 4 inner + 4 outer, 6 × 3 mm cross-section, full height
  - TPU laminate too floppy for vertical structure; PLA posts provide column rigidity
  - Posts sit inside the TPU cylinder, pinched between base plate and ring cap
- **Part count**: 6 TPU sheets + 8 PLA posts + 2 PLA ring caps = 16 parts
- Alignment bosses/holes at every rib × band intersection (2 mm × 0.6 mm press-fit)

## Assembly
1. Lay sheet A bosses-up, drape mesh, press sheet B down onto bosses
2. Heat-weld with iron through parchment paper, OR flex CA on bands/ribs only
3. Trim mesh flush to outer edges
4. Roll into cylinder, seat bottom edge into base groove
5. Install ring cap to capture top edge

## Rev D4.1 dimensions (reference)
- Base outer seat: OD 150.2 / ID 143.8 / depth 2.0 (groove width 3.2)
- Base inner seat: OD 86.2 / ID 82.2 / depth 2.0 (groove width 2.0)
- Outer cage OD 150.0, height 228.6
- Inner cage OD 86.0, height 231.6
- Lid has 6 snap nubs to be removed in D4.2
