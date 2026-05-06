$fn = 120;

// Drill Template for Helios Weighing System
// Print FIRST — lay on chamber floor, register on center hole, drill through guides
//
// - Center hole: registers on existing 27mm floor hole
// - 3 guide holes: 12mm at R=65mm (Ø130mm bolt circle), 120° apart
// - Arrow marker on 0° hole for orientation

bolt_circle_r = 65.0;

difference() {
    // Flat disc
    cylinder(d = 2*bolt_circle_r + 30, h = 3.0);
    // Center registration hole (fits over existing 27mm floor hole)
    translate([0, 0, -0.1])
        cylinder(d = 27.2, h = 3.2);
    // 3 drill guide holes at bolt circle
    for (i = [0 : 2]) {
        rotate([0, 0, i * 120])
            translate([bolt_circle_r, 0, -0.1])
                cylinder(d = 12.0, h = 3.2);
    }
}

// Arrow marker at 0° hole for orientation
translate([bolt_circle_r, 0, 3.0])
    cylinder(d1 = 6, d2 = 0, h = 3);
