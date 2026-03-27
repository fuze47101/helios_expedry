# AGENTS — Helios (Expedry Capsule) Operational Procedures

## Session Startup
1. Read CLAUDE.md for project context, dimensions, revision history, printing lessons
2. Check which .scad file revision is current (header comment shows rev)
3. Verify key dimensions before any geometry changes

## Design Workflow
1. All parametric geometry lives in a single .scad file (OpenSCAD)
2. Changes must be mathematically verified BEFORE telling Andrew to print
3. Use Python scripts to validate stack-up heights, clearances, overlaps
4. When modifying joint/section geometry, always check:
   - Assembled height = sum of section contributions (NOT print heights)
   - Collar overlap doesn't add net height
   - Boundary rings fully capture post inner edges
   - No air gaps between collar and cage body (collar_bridge)

## Verification Checklist (Before Any Print)
- [ ] Outer assembled height = 228.6mm
- [ ] Inner assembled height = 231.6mm
- [ ] Inner protrudes exactly 3mm above outer
- [ ] Lid sits flush on outer cage top
- [ ] Both cages seat 2mm into base grooves
- [ ] Section print heights match expected (76.2/84.2 for outer, 77.2/85.2 for inner)
- [ ] Boundary rings extend past post inner edge by ≥1.5mm
- [ ] Collar_bridge connects collar to cage body with overlap

## 3mf Verification
When Andrew uploads .3mf files for checking:
1. Unzip (3mf = zip file)
2. Parse XML mesh data for vertex bounding boxes
3. Compare height/diameter against expected values
4. Check for scrambled numbering (sections may not match filenames)

## OpenSCAD Export Gotcha
OpenSCAD caches geometry. If exported files show wrong dimensions:
- F4 (force reload and recompile)
- F6 (full CGAL render — NOT F5 preview)
- Then export

## Printing Protocol (Bambu H2D / PLA)
- Brim 8mm (not anchors)
- Outer wall 60 mm/s, inner 80 mm/s
- Nozzle 215°C, first layer 220°C
- Fan 0% first 3 layers, 70% after
- Min layer time 15s
- ONE section per plate
- Wall count 3, detect thin walls ON
- Z-hop 0.4mm, avoid crossing walls ON

## DO NOT
- Change joint_h, joint_gap, or socket_wall without recalculating ALL section heights
- Modify boundary ring dimensions without checking post capture overlap
- Assume 3mf files are from current revision — always verify heights
- Skip mathematical verification before recommending a print
