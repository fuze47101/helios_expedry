$fn = 120;

// ==========================================
// PRINT FILE: Floor Bushings v4 (3x)
// ==========================================
// Drop-through sleeves — epoxy from below.
// 2x medium (1/2" / 12.7mm re-drilled holes)
// 1x oversized (15.2mm hole)
//
// >>> RE-DRILL the two 3/8" holes to 1/2" (12.7mm) <<<
// The old 3/8" holes left only 0.26mm wall — unprintable.
// 1/2" gives ~2mm wall — solid part.
//
// Carbon fiber 8mm posts slide through the bore.
// All bushings drop through from above, epoxy from below.
// ==========================================

// Post bore — clearance for 8mm carbon fiber rod
post_bore          = 8.5;

// --- Medium bushing (2x) ---
// Re-drilled to 1/2" = 12.7mm
med_hole           = 12.7;
med_od             = med_hole - 0.5;  // 12.2mm — drops through easily
med_flange_od      = med_hole + 8.0;  // 20.7mm — 4mm overhang per side
// Wall thickness: (12.2 - 8.5) / 2 = 1.85mm — solid!
flange_h           = 2.5;

// Tube below floor
floor_thickness    = 2.5;
tube_below         = 5.0;
tube_total         = floor_thickness + tube_below;

// --- Oversized bushing (1x) ---
// Over-drilled hole = 15.2mm
big_hole           = 15.2;
big_od             = big_hole - 0.5;  // 14.7mm
big_flange_od      = big_hole + 8.0;  // 23.2mm
// Wall thickness: (14.7 - 8.5) / 2 = 3.1mm — plenty

module bushing(od, flange_d) {
    difference() {
        union() {
            // Top flange — sits on floor surface
            cylinder(d = flange_d, h = flange_h);
            // Drop-through tube
            translate([0, 0, flange_h])
                cylinder(d = od, h = tube_total);
        }
        // Bore for carbon fiber post
        translate([0, 0, -0.1])
            cylinder(d = post_bore, h = flange_h + tube_total + 0.2);
    }
}

// 2 medium + 1 oversized, spaced on build plate
translate([-25, 0, 0]) bushing(med_od, med_flange_od);
translate([0, 0, 0])   bushing(med_od, med_flange_od);
translate([30, 0, 0])  bushing(big_od, big_flange_od);
