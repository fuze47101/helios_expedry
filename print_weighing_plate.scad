$fn = 160;

// ============================================================
// HELIOS — Weighing Plate (Rev V4 — integral 70 mm posts)
// ============================================================
// Material: Polycarbonate (PC)
// Printer:  Bambu H2D, enclosed
// Date:     2026-05-12
// Rev:      V4.1 (fixed disc carve-out bug from broken bottom chamfer)
// ============================================================
// WHY INTEGRAL
//   Load-cell readings are only as accurate as the geometry of
//   the post that delivers the load to the receiver.  Separate
//   posts glued into sockets have three error modes that all
//   show up at the scale:
//     1. Glue depth variation → posts protrude different amounts
//     2. Perpendicularity drift → posts tip slightly off-axis
//     3. Post-to-post length mismatch → uneven load transfer
//   Integral posts eliminate ALL THREE.  They're geometrically
//   guaranteed to be the same length, parallel, perpendicular
//   to the plate, and dead-flush at the top.
// ============================================================
// PRINT NOTES (PC, integral 70 mm × Ø6.5 posts)
//   These are tall thin features but they grow from a Ø170 disc
//   base — maximum anchor area, zero detachment risk.  Print
//   orientation: plate top face on the bed, posts standing UP.
//   The SCAD layout is pre-flipped for this — just hit slice.
//   Recommended slicer settings:
//     • Walls: 3 (Ø6.5 post becomes 100% solid at 3 perimeters)
//     • Outer wall speed: 30 mm/s (clean post sidewalls)
//     • Inner wall:       100 mm/s
//     • Infill:           30% gyroid
//     • Brim:             8 mm outer (extra adhesion for the
//                          plate edge — keeps post bases planted)
//     • Min layer time:   15 s (force cool between layers so PC sets)
//     • Fan:              0% first 3 layers, then 10–20%
//     • Z-hop:            0.4 mm Auto Lift
//     • Detect thin walls: ON
//     • Avoid crossing walls: ON
//   Posts at R=65 with 120° spacing → 113 mm between adjacent
//   posts.  Plenty of airflow, no stringing risk.
// ============================================================
// BUSHINGS REMINDER
//   Posts went from Ø8 → Ø6.5.  Reprint the labyrinth bushings
//   at Ø7.0 bore (0.5 mm radial clearance) to match.
// ============================================================

// ============================================================
// PARAMETERS
// ============================================================

// --- Column (heated Al with silicone tape wrap) ---
column_od             = 80.0;
column_clearance      = 5.0;
plate_center_hole     = column_od + 2*column_clearance;   // 90 mm

// --- Plate disc ---
plate_od              = 170.0;
plate_thickness       = 6.0;
plate_chamfer         = 1.5;

// --- Posts (INTEGRAL — printed as part of the plate) ---
post_count            = 3;
post_od               = 6.5;     // diameter
post_length           = 70.0;    // total length, top flush with plate top
bolt_circle_r         = 65.0;

// --- Floor & assembly geometry (reference only — for the math echo) ---
floor_t               = 2.5;
above_floor_gap       = 40.0;    // plate hovers high — clears column top

// ============================================================
// COMPUTED Z STACK (in-use, z=0 at chamber floor top)
// ============================================================
z_floor_top           = 0;
z_floor_bottom        = -floor_t;
z_plate_bottom        = above_floor_gap;
z_plate_top           = z_plate_bottom + plate_thickness;
z_post_top            = z_plate_top;                        // posts flush w/ plate top
z_post_tip            = z_post_top - post_length;           // -24

z_receiver_top        = z_post_tip + 9.0;                   // 9 mm engagement
z_pan_top             = z_receiver_top - 15.0;              // -30
z_pan_bottom          = z_pan_top - 5.0;                    // -35 → standoff top here

// ============================================================
// MATH VERIFICATION
// ============================================================
echo("");
echo("=========================================");
echo("HELIOS WEIGHING PLATE — V4 (integral 70 mm posts)");
echo("=========================================");
echo("Plate OD              :", plate_od, "mm");
echo("Plate thickness       :", plate_thickness, "mm");
echo("Center hole D         :", plate_center_hole, "mm (clears Ø",column_od,"column)");
echo("");
echo("Posts (integral):");
echo("  Count               :", post_count, "at R=", bolt_circle_r, "mm");
echo("  Post OD             :", post_od, "mm");
echo("  Post length         :", post_length, "mm");
echo("  Spacing             :", round(2*bolt_circle_r*sin(60)), "mm between adjacent posts");
echo("");
echo("Vertical stack (in use, z=0 at floor top):");
echo("  Plate top           : z =", z_plate_top);
echo("  Plate bottom        : z =", z_plate_bottom);
echo("  Floor top           : z =", z_floor_top);
echo("  Floor bottom        : z =", z_floor_bottom);
echo("  Post tip            : z =", z_post_tip);
echo("  Receiver TOP        : z =", z_receiver_top);
echo("  Pan TOP             : z =", z_pan_top);
echo("  Pan BOTTOM (= standoff top) : z =", z_pan_bottom);
echo("");
echo("PRINT ORIENTATION (after flip in layout):");
echo("  z = 0      → plate top face (bed)");
echo("  z = 0..6   → plate body Ø170 (rests on bed)");
echo("  z = 6..70  → 3 integral posts Ø6.5 standing UP");
echo("=========================================");
echo("");

// ============================================================
// MODULE (drawn in IN-USE orientation: plate body z=0..6, posts hang in -z)
// ============================================================
module weighing_plate() {
    difference() {
        union() {
            // Plate disc
            cylinder(d = plate_od, h = plate_thickness);

            // Integral posts — extend DOWN from plate top, length = post_length.
            // Translate them so their TOP is flush with plate top (z=plate_thickness).
            for (i = [0 : post_count - 1]) {
                rotate([0, 0, i * (360 / post_count)])
                    translate([bolt_circle_r, 0, -(post_length - plate_thickness)])
                        cylinder(d = post_od, h = post_length);
            }
        }

        // Center hole — clears the column
        translate([0, 0, -1])
            cylinder(d = plate_center_hole, h = plate_thickness + 2);

        // Edge chamfer — ONE chamfer on the in-use top edge of the disc.
        // (After the print-orientation flip, this ends up adjacent to the
        // bed, giving a clean bevel.  The in-use bottom edge stays sharp;
        // it doesn't matter — it faces the chamber floor and isn't seen.
        //
        // V4-bug history: an earlier "bottom chamfer" block had a malformed
        // inner subtractor (straight Ø170 × 0.05mm cylinder) that left the
        // outer Ø172 × 1.6mm solid intact, carving a slab out of the disc
        // bottom.  After flipping, that hole became an "empty layer" between
        // z=4.4–6 in print coords.  Removed in V4.1.)
        if (plate_chamfer > 0) {
            translate([0, 0, plate_thickness - plate_chamfer])
                difference() {
                    cylinder(d = plate_od + 2, h = plate_chamfer + 0.1);
                    cylinder(d1 = plate_od - 2*plate_chamfer,
                             d2 = plate_od,
                             h  = plate_chamfer + 0.1);
                }
        }
    }
}

// ============================================================
// LAYOUT — pre-flipped for print (plate TOP on bed, posts UP)
// ============================================================
translate([0, 0, plate_thickness])
    rotate([180, 0, 0])
        weighing_plate();
