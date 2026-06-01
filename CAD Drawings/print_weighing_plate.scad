$fn = 160;

// ============================================================
// HELIOS — Weighing Plate (Rev V2 — PC, flat top, integral posts)
// ============================================================
// Material: Polycarbonate (PC)
// Printer:  Bambu H2D, enclosed
// Date:     2026-05-12
// Rev:      V2
// ============================================================
// CHANGES FROM V1
//   • Top is FLAT — no rim, no cage seat grooves.  New flat
//     capsule caps register against the flat top by gravity.
//   • Center hole grew Ø80 → Ø90 (column is now ~Ø80 with the
//     silicone tape wrap; old hole was tight).
//   • Posts shrank from 65.5 mm to ~22 mm because the load cell
//     now sits on a 4" PC stand only 1 inch (25.4 mm) below the
//     chamber floor — much closer than the Bonvoisin scale was.
//   • Posts are INTEGRAL to the plate (no separate press-fit).
//     PC + 22 mm length means warping is no longer a concern.
//   • All key heights parametric — change live_end_below_floor
//     or receiver_h to retune post length without touching the
//     post geometry.
// ============================================================
// PRINT ORIENTATION
//   FLIP the plate UPSIDE-DOWN in the slicer so the posts point
//   UP during printing.  Bed face = the plate's top face (where
//   the capsule sits) — gets a smooth bed-finish surface.  Posts
//   print as ~22 mm vertical stubs, fully supported by the plate
//   beneath them.  No internal supports needed.
// ============================================================

// ============================================================
// PARAMETERS — change these to retune the design
// ============================================================

// --- Column (now wrapped in silicone tape) ---
column_od             = 80.0;     // [TODO verify] ~Ø80 with tape
column_clearance      = 5.0;      // per side
plate_center_hole     = column_od + 2*column_clearance;   // 90 mm

// --- Plate ---
plate_od              = 170.0;
plate_thickness       = 6.0;
plate_chamfer         = 1.5;      // cosmetic edge ease

// --- Floor & assembly ---
floor_t               = 2.5;      // chamber floor thickness
above_floor_gap       = 2.0;      // plate hovers above floor

// --- Load cell / pan adapter (must match pan adapter SCAD) ---
live_end_below_floor  = 25.4;     // [TODO verify] 1 inch = button below floor top
pan_thickness         = 5.0;      // pan adapter disc thickness
receiver_h            = 15.0;     // height of receiver post above pan top
receiver_engagement   = 9.0;      // how deep post tip sits in receiver bore

// --- Posts (integral) ---
post_count            = 3;
post_od               = 8.0;
bolt_circle_r         = 65.0;     // matches floor labyrinth bushings

// ============================================================
// COMPUTED HEIGHTS
// z-frame: z=0 at chamber floor TOP.
// ============================================================
z_floor_top           = 0;
z_floor_bottom        = -floor_t;                                // -2.5
z_pan_bottom          = -live_end_below_floor;                   // -25.4
z_pan_top             = z_pan_bottom + pan_thickness;            // -20.4
z_receiver_top        = z_pan_top + receiver_h;                  //  -5.4
z_post_tip            = z_receiver_top - receiver_engagement;    // -14.4

z_plate_bottom        = above_floor_gap;                         //  +2.0
z_plate_top           = z_plate_bottom + plate_thickness;        //  +8.0

post_length           = z_plate_top - z_post_tip;                //  22.4

// ============================================================
// MATH VERIFICATION
// ============================================================
echo("");
echo("=========================================");
echo("HELIOS WEIGHING PLATE — V2");
echo("=========================================");
echo("Plate OD          :", plate_od, "mm");
echo("Plate thickness   :", plate_thickness, "mm");
echo("Center hole D     :", plate_center_hole, "mm (clearance",
       (plate_center_hole - column_od)/2, "mm/side from Ø",column_od,"column)");
echo("");
echo("Post:");
echo("  OD              :", post_od, "mm");
echo("  Count           :", post_count, "at 120° (R =", bolt_circle_r, "mm)");
echo("  Length          :", post_length, "mm  (computed)");
echo("");
echo("Vertical stack (z=0 at floor top):");
echo("  Plate top       : z =", z_plate_top);
echo("  Plate bottom    : z =", z_plate_bottom);
echo("  Floor bottom    : z =", z_floor_bottom);
echo("  Receiver top    : z =", z_receiver_top);
echo("  Post tip        : z =", z_post_tip, "(in receiver,",
       receiver_engagement, "mm engagement)");
echo("  Pan top         : z =", z_pan_top);
echo("  Pan bottom      : z =", z_pan_bottom, "(on load cell button)");
echo("=========================================");
echo("");

// ============================================================
// MODULE
// ============================================================
module weighing_plate() {

    // Origin: plate sits with its bottom face at z=0; posts hang in -z.
    difference() {
        union() {
            // Main disc
            cylinder(d = plate_od, h = plate_thickness);

            // Integral posts — extend DOWN from the plate bottom
            for (i = [0 : post_count - 1]) {
                rotate([0, 0, i * (360 / post_count)])
                    translate([bolt_circle_r, 0, -(post_length - plate_thickness)])
                        cylinder(d = post_od, h = post_length);
                //                              ↑ post starts post_length-plate_t
                //                                below plate top so it runs from
                //                                post tip up through the plate.
            }
        }

        // Center hole — clears the column
        translate([0, 0, -1])
            cylinder(d = plate_center_hole, h = plate_thickness + 2);

        // Edge chamfers
        if (plate_chamfer > 0) {
            // top edge
            translate([0, 0, plate_thickness - plate_chamfer])
                difference() {
                    cylinder(d = plate_od + 2, h = plate_chamfer + 0.1);
                    cylinder(d1 = plate_od - 2*plate_chamfer,
                             d2 = plate_od,
                             h  = plate_chamfer + 0.1);
                }
            // bottom edge
            translate([0, 0, -0.05])
                difference() {
                    cylinder(d = plate_od + 2, h = plate_chamfer + 0.1);
                    cylinder(d1 = plate_od,
                             d2 = plate_od - 2*plate_chamfer,
                             h  = plate_chamfer + 0.1);
                }
        }
    }
}

weighing_plate();
