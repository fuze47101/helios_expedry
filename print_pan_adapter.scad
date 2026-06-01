$fn = 160;

// ============================================================
// HELIOS — Pan Adapter (Rev V4 — integrated disc, plug-in receivers)
// ============================================================
// Material: Polycarbonate (PC)
// Printer:  Bambu H2D, enclosed
// Date:     2026-05-12
// Rev:      V4.5 (receiver bore updated for V3 weighing plate's Ø6.5 posts)
// ============================================================
// DESIGN RATIONALE (final)
//   • Load-cell alignment (pin + sleeve cavity) is CRITICAL —
//     must be one rigid piece, accurate, no glue joint between
//     it and the pan disc.
//   • Receivers are NOT critical — they just guide three Ø8
//     posts onto the pan.  They can be separate parts glued
//     into small recesses on the pan top.
//
//   So the pan adapter is now TWO things to print:
//     PIECE 1  pan + pin + sleeve cavity         (one part)
//     PIECE 2  3 × receiver posts                (3 parts)
//
//   The PRINT TRICK:
//     Print Piece 1 UPSIDE DOWN — pan TOP face on the bed.
//     • Bed contact: smooth Ø155 disc face (the surface the
//       capsule will sit on later → gets a nice bed-finish)
//     • Three Ø14.4 × 3 mm recesses appear in the first ~15
//       layers (the receiver pockets)
//     • At pan_thickness above the bed, the pan BOTTOM face
//       (in use) is reached → pin + sleeve features grow UP
//       from a solid Ø155 disc.  No floating ring, no air.
//     • Pin is a 7.5 mm column rising from a solid base — easy.
//     • Sleeve wall is a Ø14 OD / Ø10 ID tube rising from the
//       same solid base — also easy.
// ============================================================
// LOAD CELL INTERFACE — measured 2026-05-12
//   Standoff on the live-end of the bar:
//     • Top OD       :  8.9 mm
//     • Bottom OD    :  9.8 mm
//     • Height       :  8.1 mm
//     • Internal bore:  7.0 mm
// ============================================================

// ============================================================
// PARAMETERS
// ============================================================

// --- Standoff (measured) ---
standoff_id           = 7.0;
standoff_top_od       = 8.9;
standoff_bot_od       = 9.8;
standoff_height       = 8.1;

// --- Centering pin (drops INTO standoff bore) ---
pin_clearance         = 0.2;
pin_od                = standoff_id - pin_clearance;       // 6.8 mm
pin_height            = 7.5;
pin_chamfer           = 0.6;   // tip taper (added as cone, not subtracted)

// --- Screw head counterbore on pan TOP (gives the head a seat) ---
//   M4 button head ≈ Ø7.6 × ~2.2 mm tall — use Ø8.0 × 2.5 mm.
//   For M4 socket head:  Ø7.0 × 4.0 mm.
//   For M5 button head:  Ø9.2 × 2.7 mm.
counterbore_d         = 8.0;
counterbore_depth     = 2.5;

// --- Stability sleeve cavity (captures standoff OD) ---
sleeve_clearance      = 0.2;
sleeve_id             = standoff_bot_od + sleeve_clearance; // 10.0 mm
sleeve_wall           = 2.0;
sleeve_od             = sleeve_id + 2*sleeve_wall;          // 14.0 mm
sleeve_height         = 6.0;
sleeve_id_chamfer     = 0.6;

// --- Pan disc (Piece 1) ---
pan_od                = 155.0;
pan_thickness         = 5.0;
pan_chamfer           = 1.0;

// --- Screw through pan + pin (guess M4 = 4.5) ---
screw_hole_d          = 4.5;

// --- Receiver recesses on pan TOP face (where Piece 2 posts glue in) ---
receiver_recess_d     = 14.4;     // 0.4 mm diametric clearance over Ø14 receiver
receiver_recess_depth = 3.0;      // shallow — pan top retains ~2 mm of floor
                                  // material below each recess
bolt_circle_r         = 65.0;

// --- Receiver posts (Piece 2 — separate plug-in parts) ---
receiver_count        = 3;
receiver_od           = 14.0;
receiver_total_h      = 18.0;     // 3 mm in recess + 15 mm visible above pan top
receiver_bore_d       = 6.9;      // 0.4 mm clearance over Ø6.5 posts (V3 plate)
receiver_bore_depth   = 12.0;
receiver_chamfer      = 1.5;      // top chamfer (funnels in weighing-plate post)

// --- Layout / show flags ---
show_piece1           = true;
show_piece2           = true;
piece2_x              = -100.0;   // place receiver-post strip west of the pan

// ============================================================
// MATH VERIFICATION
// ============================================================
echo("");
echo("=========================================");
echo("HELIOS PAN ADAPTER — V4 (integrated + plug-in receivers)");
echo("=========================================");
echo("PIECE 1: pan + pin + sleeve cavity");
echo("  Pan OD                :", pan_od, "mm");
echo("  Pan thickness         :", pan_thickness, "mm");
echo("  Pin (down in use)     : Ø",pin_od,"x", pin_height, "mm");
echo("  Sleeve cavity         : Ø",sleeve_id,"OD x", sleeve_height, "mm tall");
echo("  Sleeve outer (Ø14)    : integrated into the disc edge of the boss");
echo("  Screw bore            : Ø",screw_hole_d, "mm through pan + pin");
echo("  Screw head c-bore     : Ø",counterbore_d,"x",counterbore_depth,"mm  (seat for M4 head)");
echo("  Receiver recesses (3) : Ø",receiver_recess_d,"x",receiver_recess_depth,
       "mm  at R =", bolt_circle_r);
echo("");
echo("PIECE 2: receiver posts (3x)");
echo("  OD x H                : Ø",receiver_od,"x", receiver_total_h, "mm");
echo("  Bore D x depth        : Ø",receiver_bore_d,"x", receiver_bore_depth, "mm");
echo("  Engagement in recess  :", receiver_recess_depth, "mm");
echo("  Visible above pan top :", receiver_total_h - receiver_recess_depth, "mm");
echo("");
echo("ASSEMBLY:");
echo("  1. Print Piece 1 upside-down (pan TOP on bed).");
echo("  2. Print 3x Piece 2 standing up (bore-up).");
echo("  3. Glue receivers into the 3 pan-top recesses (CA gel).");
echo("  4. M4 screw drops through pan + pin into standoff thread.");
echo("=========================================");
echo("");

// ============================================================
// PIECE 1 — Pan with integrated pin + sleeve (printed UPSIDE DOWN)
// In the SCAD, we DRAW it in the IN-USE orientation:
//   • Pan disc occupies z=0 (bottom face, toward load cell) to z=pan_thickness (top, toward capsule)
//   • Pin + sleeve features extend DOWN into -z
//   • Receiver recesses cut DOWN into the top face from z=pan_thickness
// In the slicer, FLIP 180° about X (auto-orient should do this) so
// the pan-top face lands on the bed and features grow upward.
// ============================================================
module piece1_pan() {

    // ──────────────────────────────────────────────────────────
    // BUG FIX (V4→V4.1):
    // In the previous union, the Ø10 sleeve-cavity subtraction at
    // the OUTER difference was carving through the middle of the
    // Ø6.8 pin (because Ø10 > Ø6.8).  Result: the pin's center
    // section vanished and only the 1.5 mm tip survived — visible
    // as a "floating disk" in the slicer preview.
    //
    // Fix: build the sleeve as a hollow tube LOCALLY inside the
    // union (the Ø10 cavity only removes sleeve material, not pin).
    // Then add the pin as an independent solid cylinder.  They
    // coexist concentrically with a 1.6 mm radial air gap.  Both
    // are anchored to the pan disc above.
    // ──────────────────────────────────────────────────────────

    difference() {
        union() {
            // Pan disc, z=0 (in-use bottom) → z=pan_thickness (in-use top)
            cylinder(d = pan_od, h = pan_thickness);

            // Sleeve as a HOLLOW TUBE with chamfered mouth — local difference
            // scoped to the sleeve only.  (Mouth chamfer MUST be local: if it
            // lives at the outer difference, its Ø11.2 cone is wider than the
            // pin Ø6.8 and carves a section out of the pin, leaving the pin
            // tip as a detached ring.)
            translate([0, 0, -sleeve_height])
                difference() {
                    cylinder(d = sleeve_od, h = sleeve_height);
                    translate([0, 0, -0.01])
                        cylinder(d = sleeve_id, h = sleeve_height + 0.02);
                    // Mouth chamfer: flares the cavity at the bottom from Ø10
                    // up to Ø(10 + 2*chamfer) at the very mouth, funneling the
                    // standoff in.
                    if (sleeve_id_chamfer > 0) {
                        translate([0, 0, -0.01])
                            cylinder(d1 = sleeve_id + 2*sleeve_id_chamfer,
                                     d2 = sleeve_id,
                                     h  = sleeve_id_chamfer + 0.02);
                    }
                }

            // Centering pin — built as TAPERED TIP + STRAIGHT SHAFT (additive,
            // not subtracted, so the pin can't get carved into a detached ring).
            if (pin_chamfer > 0) {
                // Tip cone: Ø(pin_od - 2*chamfer) at the very tip, growing to
                // Ø(pin_od) at the top of the chamfer.
                translate([0, 0, -pin_height])
                    cylinder(d1 = pin_od - 2*pin_chamfer,
                             d2 = pin_od,
                             h  = pin_chamfer);
                // Straight shaft above the chamfer.
                translate([0, 0, -pin_height + pin_chamfer])
                    cylinder(d = pin_od,
                             h = pin_height - pin_chamfer);
            } else {
                translate([0, 0, -pin_height])
                    cylinder(d = pin_od, h = pin_height);
            }
        }

        // (Mouth chamfer is now inside the local sleeve difference above —
        // do NOT re-add it here or it will carve the pin.)

        // Screw hole — through pan + pin
        translate([0, 0, -pin_height - 1])
            cylinder(d = screw_hole_d,
                     h = pin_height + pan_thickness + 2);

        // Screw head counterbore on pan TOP face — the seat for the head
        translate([0, 0, pan_thickness - counterbore_depth])
            cylinder(d = counterbore_d, h = counterbore_depth + 0.01);

        // Three receiver recesses on pan TOP face
        for (i = [0 : receiver_count - 1]) {
            rotate([0, 0, i * (360 / receiver_count)])
                translate([bolt_circle_r, 0,
                           pan_thickness - receiver_recess_depth])
                    cylinder(d = receiver_recess_d,
                             h = receiver_recess_depth + 0.01);
        }

        // Pan edge chamfers (top + bottom)
        if (pan_chamfer > 0) {
            translate([0, 0, pan_thickness - pan_chamfer])
                difference() {
                    cylinder(d = pan_od + 2, h = pan_chamfer + 0.1);
                    cylinder(d1 = pan_od - 2*pan_chamfer,
                             d2 = pan_od,
                             h  = pan_chamfer + 0.1);
                }
            translate([0, 0, -0.05])
                difference() {
                    cylinder(d = pan_od + 2, h = pan_chamfer + 0.1);
                    cylinder(d1 = pan_od,
                             d2 = pan_od - 2*pan_chamfer,
                             h  = pan_chamfer + 0.1);
                }
        }
    }
}

// ============================================================
// PIECE 2 — Receiver post (one of three)
// Cylinder Ø14 × 18 mm with a Ø8.4 × 12 mm bore from the TOP and
// a chamfer on the bore mouth.  Bottom face is flat — glues into
// the pan-top recess.
// Print standing on the bed, bore UP.
// ============================================================
module receiver_post() {
    difference() {
        cylinder(d = receiver_od, h = receiver_total_h);

        // Top bore (where the weighing-plate post enters)
        translate([0, 0, receiver_total_h - receiver_bore_depth])
            cylinder(d = receiver_bore_d,
                     h = receiver_bore_depth + 1);

        // Top chamfer (funnel)
        if (receiver_chamfer > 0) {
            translate([0, 0, receiver_total_h - receiver_chamfer])
                cylinder(d1 = receiver_bore_d,
                         d2 = receiver_bore_d + 2*receiver_chamfer,
                         h  = receiver_chamfer + 0.01);
        }
    }
}

// ============================================================
// LAYOUT — pre-oriented for printing (lowest face = bed)
// ============================================================
//   Piece 1 is FLIPPED 180° about X here so the pan TOP face
//   lands on the bed.  In the SCAD module itself, the pan is
//   drawn in in-use orientation (top face up, features hanging
//   below); the flip + translate below puts it in print
//   orientation so the export goes straight to the bed.
//
//   After this transform:
//     z = 0       → pan TOP face (capsule-side, on the bed)
//     z = 0..3    → the 3 receiver recesses are first-layer holes
//     z = 0..2.5  → the screw-head counterbore is also a first-layer hole
//     z = 5       → pan BOTTOM face (load-cell-side, top of the disc in print)
//     z = 5..11   → sleeve wall (Ø14 OD ring) growing UP, with pin in center
//     z = 5..12.5 → pin (Ø6.8) growing UP, with tip chamfer at the very top
//
//   Piece 2 receivers already stand upright (lowest point z=0).
// ============================================================
if (show_piece1)
    translate([0, 0, pan_thickness])
        rotate([180, 0, 0])
            piece1_pan();

if (show_piece2) {
    // 3 receiver posts standing upright, west of the pan
    for (i = [0 : receiver_count - 1]) {
        translate([piece2_x, (i - 1) * (receiver_od + 6), 0])
            receiver_post();
    }
}
