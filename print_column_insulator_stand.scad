$fn = 160;

// ============================================================
// HELIOS — Aluminum Column Insulator Stand
// Material: Polycarbonate (PC) — straight, dry filament only
// Printer:  Bambu H2D, enclosed
// Date:     2026-05-11
// Rev:      V2 — hollow through-bore for cartridge heater cables,
//               internal lip seat for the column
// ============================================================
// PURPOSE
//   The aluminum steam generator column carries 12V cartridge
//   heaters in its puck. The heater leads exit the underside of
//   the column and must drop straight through the stand and into
//   the lower equipment bay. So:
//     • The stand is a TUBE — fully open from top to bottom.
//     • The column drops in from above and rests on an INTERNAL
//       LIP that projects inward from the tube wall.
//     • Below the lip the bore opens up wide for the cable bundle.
//     • Above the lip the bore is a slip-fit to the column OD so
//       the column is registered concentric.
// ============================================================
// CROSS-SECTION (radial cut, axis on left)
//                                        outer wall ─→│
//          axis                                       │
//           │                                         │
//   z=29.5 ┤  ░░░░ upper bore (ID 75.8) ░░░░          │  top
//           │  ░  ← column slip-fits here              │
//           │  ░░░ 10 mm of side-wrap ░░░░░░░░░░       │
//   z=19.5 ┤━━━━ LIP TOP — column rests here ━━━━━━━━ │  ← annular shoulder
//           │  ████ lip vertical wall (ID 65) ████    │
//   z=16.5 ┤━━━━ LIP BOTTOM ━━━━━━━━━━━━━━━━━━━━━━━━━ │
//           ╲                                          │
//           ╲   45° chamfer (printable overhang)      │
//           ╲                                          │
//   z=2    ╲___ chamfer ends, lower bore begins ____╲ │
//           │                                         │
//           │  lower bore (ID 94) — cable passthrough │
//   z=0    ─┤   (perimeter feet at corners)           │  bottom
//           ╰─────────────────────────────────────────╯
// ============================================================
// PRINT SETTINGS (Bambu H2D + PC)
//   Nozzle 270 °C   |   Bed 100 °C   |   Chamber heater ON
//   Print STANDING (open end up).  The lip's underside is a 45°
//   conical chamfer — no supports needed.
//   Walls: 4   |   Infill: 30% gyroid   |   Top/bottom: 5 layers
//   Brim: 5 mm   |   Fan 0% layers 1-3, then 10–20%
//   Filament: DRY (dehydrate 4 hrs @ 80°C if it sat out)
// ============================================================
// THERMAL NOTE
//   PC HDT ≈ 110°C. The column base contacts the lip top — an
//   annulus from r=32.5 to r=37.9, area ≈ 1194 mm².
//   That's ~3.8× less than a flat column-base contact (4514 mm²),
//   not as aggressive as V1's 3-pad design (192 mm², 23×) but
//   matches what Andrew asked for ("sits on a lip easily").
//   If thermal soak ever softens the lip in operation, V3 can
//   break the annulus into 3 raised bumps.
// ============================================================

// === COLUMN — VERIFY WITH CALIPERS ===
column_od            = 75.0;     // CLAUDE.md tube OD — [TODO calipered?]
column_clearance     = 0.4;      // slip fit
bore_upper_d         = column_od + 2*column_clearance;   // = 75.8 mm

// === STAND ENVELOPE ===
stand_od             = 110.0;    // outer wall OD
wall_t               = 8.0;      // wall thickness (firm)
bore_lower_d         = stand_od - 2*wall_t;              // = 94.0 mm (cable cavity)

// === LIP ===
lip_id               = 65.0;     // inner diameter of the lip (cable opening at lip)
                                 // column rests on annulus r=lip_id/2 → r=bore_upper_d/2
                                 // = r=32.5 → r=37.9 → lip width = 5.4 mm
lip_vertical_h       = 3.0;      // straight cylindrical lip wall above chamfer

// === FEET (perimeter contact with chamber floor) ===
foot_count           = 4;
foot_arc_deg         = 25;       // angular width of each foot
foot_h               = 2.0;      // how far the feet stand off the floor relief
                                 // (effectively: floor relief is foot_h tall)

// === FLOOR-MOUNT THROUGH-HOLES ===
// 4 holes pass through the wall (top to bottom) so the stand bolts down to
// the bulkhead. Centered radially in the wall, aligned with the 4 feet so
// each bolt clamps a foot to the floor.
mount_hole_count        = 4;
mount_hole_d            = 5.2;   // M5 clearance ( use 4.5 for M4, 6.5 for M6 )
mount_hole_r            = (bore_lower_d/2 + stand_od/2) / 2;   // mid-wall radius
mount_hole_angle_offset = 0;     // 0° = on the feet; 45° = between feet

// === DERIVED HEIGHTS ===
chamfer_h            = (bore_lower_d - lip_id) / 2;   // 45° chamfer height
                                                       // = (94 - 65)/2 = 14.5 mm

upper_bore_h         = 10.0;     // depth column descends into upper bore (registering)
lip_top_z            = foot_h + chamfer_h + lip_vertical_h;     // column rests here
stand_h              = lip_top_z + upper_bore_h;                // = 25.0 mm

// === MATH VERIFICATION ===
echo("");
echo("=========================================");
echo("HELIOS COLUMN INSULATOR STAND — V2");
echo("=========================================");
echo("Column OD         :", column_od, "mm");
echo("Upper bore (slip) :", bore_upper_d, "mm   (clearance",
       bore_upper_d - column_od, "mm)");
echo("Lip ID            :", lip_id, "mm");
echo("Lip width         :", (bore_upper_d - lip_id)/2, "mm");
echo("Lower bore (cable):", bore_lower_d, "mm");
echo("Stand OD          :", stand_od, "mm");
echo("Stand total height:", stand_h, "mm");
echo("");
echo("Vertical stack:");
echo("  z=0 .. ",      foot_h,                     "→ feet / floor-relief zone");
echo("  z=",foot_h," .. ",foot_h+chamfer_h,        "→ 45° chamfer (",chamfer_h,"mm)");
echo("  z=",foot_h+chamfer_h," .. ",lip_top_z,     "→ lip vertical");
echo("  z=",lip_top_z," .. ",stand_h,              "→ upper bore (column slip-fit)");
echo("");
echo("Column-lip contact area: ~",
       round(PI*((bore_upper_d/2)*(bore_upper_d/2) - (lip_id/2)*(lip_id/2))),
       "mm^2");
echo("");
echo("Floor mounting (bulkhead):");
echo("  Bolts          :", mount_hole_count, "x M5 (clearance D =", mount_hole_d, "mm)");
echo("  Bolt circle R  :", mount_hole_r, "mm   (D =", 2*mount_hole_r, "mm)");
echo("  Bolt angles    : 0°, 90°, 180°, 270°  (aligned with feet)");
echo("  TODO: drill matching holes in chamber floor at R =",
       mount_hole_r, "mm");
echo("=========================================");
echo("");

// ============================================================
// MODULE
// ============================================================
module column_insulator_stand() {

    difference() {
        // ── outer body (solid cylinder)
        cylinder(d=stand_od, h=stand_h);

        // ── UPPER BORE: column drops into this
        translate([0, 0, lip_top_z])
            cylinder(d=bore_upper_d, h=upper_bore_h + 1);

        // ── LIP VERTICAL CYLINDER: straight wall, ID = lip_id
        translate([0, 0, foot_h + chamfer_h])
            cylinder(d=lip_id, h=lip_vertical_h + 0.01);

        // ── CHAMFER: 45° cone from lower bore (large) to lip ID (small)
        //    Cone: at z=foot_h diameter = bore_lower_d, at z=foot_h+chamfer_h diameter = lip_id
        translate([0, 0, foot_h])
            cylinder(d1=bore_lower_d, d2=lip_id, h=chamfer_h + 0.01);

        // ── LOWER BORE: full inner cavity below chamfer (cable passthrough)
        translate([0, 0, -0.5])
            cylinder(d=bore_lower_d, h=foot_h + 0.5 + 0.01);

        // ── FLOOR RELIEF (between feet)
        //    Recess the entire bottom face (z < foot_h) so only the 4 wedge feet
        //    touch the chamber floor.  The wedges PRESERVE material in their slice.
        difference() {
            translate([0, 0, -0.5])
                cylinder(d=stand_od + 1, h=foot_h + 0.5);
            // wedge feet — material here is preserved (NOT cut from main body)
            for (i = [0 : foot_count - 1]) {
                rotate([0, 0, (360/foot_count)*i])
                    rotate([0, 0, -foot_arc_deg/2])
                        linear_extrude(foot_h + 2)
                            polygon([
                                [0, 0],
                                [stand_od, 0],
                                [stand_od*cos(foot_arc_deg), stand_od*sin(foot_arc_deg)],
                                [0, 0]
                            ]);
            }
        }

        // ── FLOOR-MOUNT THROUGH-HOLES
        //    4 equidistant M5 clearance holes, top to bottom, through the wall.
        for (i = [0 : mount_hole_count - 1]) {
            rotate([0, 0, mount_hole_angle_offset + (360/mount_hole_count)*i])
                translate([mount_hole_r, 0, -1])
                    cylinder(d=mount_hole_d, h=stand_h + 2);
        }
    }
}

column_insulator_stand();
