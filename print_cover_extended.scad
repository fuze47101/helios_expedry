// ==========================================
// Humidifier Refill Cover — Box Extension
// ==========================================
// Flat flange FRAME screws to cabinet (rectangular
// opening cut through center). Box extends outward
// from the opening, sealed on the far end.
//
// Print: sealed top on bed, walls build up, flange on top.
//        Opening faces UP. No bridging needed.
// Install: flip over, screw flange to cabinet, box hangs down.
// ==========================================

$fn = 80;

// === COVER DIMENSIONS (from Mike's STEP) ===
cover_w        = 232.4;     // 9.15" total width
cover_d        = 146.8;     // 5.78" total depth
cover_t        = 2.0;       // flange thickness
corner_r       = 12.83;     // 0.505" corner radius

// Screw holes at (±4.325", 0)
screw_hole_r   = 2.25;
screw_x        = 109.86;

// === BOX EXTENSION ===
flange_border  = 12.7;      // 1/2" flat border all around
box_ext        = 19.05;     // 3/4" outward
box_wall       = 2.0;

// Opening dimensions
open_w         = cover_w - 2 * flange_border;   // 207mm
open_d         = cover_d - 2 * flange_border;   // 121.4mm
open_r         = max(corner_r - flange_border, 2);

// Total height of the assembled part
total_h        = cover_t + box_ext + box_wall;   // ~23mm

module rounded_rect(w, d, h, r) {
    hull() {
        for (x = [-w/2 + r, w/2 - r])
            for (y = [-d/2 + r, d/2 - r])
                translate([x, y, 0])
                    cylinder(r = r, h = h);
    }
}

module cover_assembly() {
    // PART 1: Flange frame (plate with rectangular hole)
    difference() {
        rounded_rect(cover_w, cover_d, cover_t, corner_r);
        translate([0, 0, -0.1])
            rounded_rect(open_w, open_d, cover_t + 0.2, open_r);
        translate([screw_x, 0, -0.1])
            cylinder(r = screw_hole_r, h = cover_t + 0.2);
        translate([-screw_x, 0, -0.1])
            cylinder(r = screw_hole_r, h = cover_t + 0.2);
    }

    // PART 2: Box walls (rising from flange, around the opening)
    translate([0, 0, cover_t])
        difference() {
            rounded_rect(open_w + 2 * box_wall, open_d + 2 * box_wall,
                         box_ext, open_r + box_wall);
            translate([0, 0, -0.1])
                rounded_rect(open_w, open_d,
                             box_ext + 0.2, open_r);
        }

    // PART 3: Sealed top (closes the far end of the box)
    translate([0, 0, cover_t + box_ext])
        rounded_rect(open_w + 2 * box_wall, open_d + 2 * box_wall,
                     box_wall, open_r + box_wall);
}

// === FLIPPED FOR PRINTING ===
// Rotate 180° around X so sealed top is on the bed,
// then shift up so bottom sits at z=0
rotate([180, 0, 0])
    translate([0, 0, -total_h])
        cover_assembly();
