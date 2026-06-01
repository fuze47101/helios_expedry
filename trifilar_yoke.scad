// ==========================================================
// HELIOS — Trifilar Suspension Yoke (anti-swing for capsule)
// One load-cell attachment at the top eyelet; three bridle
// wires fan out from the arms to 3 points 120° apart on the
// capsule's top rim. Single vertical load path (all 3 tensions
// sum into the one load cell) but rotation + sway are killed.
// Print PLA/PETG, ~30% infill, 3 walls. Tiny part.
// ==========================================================
$fn = 72;

// ---- parameters ----
HUB_D        = 18;    // central hub diameter
HUB_H        = 9;     // hub / arm thickness base
ARM_LEN      = 26;    // center -> bridle hole (more spread = stiffer against rotation)
ARM_W        = 6;     // arm width
ARM_TH       = 5;     // arm thickness
WIRE_HOLE_D  = 3.2;   // bridle wire holes (tie a knot/figure-8 under each)

EYE_POST_W   = 7;     // top eyelet post (X)
EYE_POST_TH  = 6;     // top eyelet post (Y)
EYE_POST_H   = 14;    // post height above hub
EYE_HOLE_D   = 5;     // load-cell hook / ring hole (horizontal)

CENTER_BORE  = 5;     // light vertical bore through hub (optional cable pass / weight save)

module yoke() {
    difference() {
        union() {
            cylinder(d = HUB_D, h = HUB_H);                 // hub
            for (a = [0:120:240])                           // 3 arms @120
                rotate([0,0,a])
                    translate([0, -ARM_W/2, 0])
                        cube([ARM_LEN, ARM_W, ARM_TH]);
            translate([-EYE_POST_W/2, -EYE_POST_TH/2, HUB_H])   // top eyelet post
                cube([EYE_POST_W, EYE_POST_TH, EYE_POST_H]);
        }
        // bridle wire holes at each arm tip
        for (a = [0:120:240])
            rotate([0,0,a])
                translate([ARM_LEN - 4, 0, -1])
                    cylinder(d = WIRE_HOLE_D, h = ARM_TH + 2);
        // horizontal eyelet hole through the top post (for the load-cell hook)
        translate([0, EYE_POST_TH/2 + 1, HUB_H + EYE_POST_H - EYE_HOLE_D])
            rotate([90,0,0])
                cylinder(d = EYE_HOLE_D, h = EYE_POST_TH + 2);
        // light center bore
        translate([0,0,-1]) cylinder(d = CENTER_BORE, h = HUB_H + 2);
    }
}
yoke();

// ==========================================================
// ASSEMBLY NOTES
// - Hook the load cell to the TOP eyelet (5mm hole).
// - Run 3 equal-length wires from the arm holes down to 3
//   points 120° apart on the capsule top rim (6.5" OD ≈ Ø165,
//   so rim radius ≈ 82.5mm).
// - Keep the yoke ~60–100mm above the cap: the taller/narrower
//   the cone, the more it resists rotation; wider = more sway
//   resistance. ~70mm is a good start.
// - Make the 3 wires EQUAL length so the capsule hangs plumb
//   and centered over the column (you have only 1.9mm clearance).
// - Take weight readings with the mixing fan OFF, on "stable".
// ==========================================================
