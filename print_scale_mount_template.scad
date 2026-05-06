$fn = 120;

// ==========================================
// PRINT FILE: Scale Mounting Drill Template
// ==========================================
// Lay this on the BOTTOM of the chamber floor.
// Registers on the existing 27mm center hole.
// Marks 4 drill positions for scale mounting bolts.
//
// Scale foot pattern: 171.5mm x 211.1mm rectangle
// Bolt size: 4.75mm (likely M5) — drill 5.5mm for clearance
// ==========================================

// Scale foot rectangle (center to center)
foot_width         = 171.5;       // 6.75" between feet (short axis)
foot_length        = 211.1;       // 8 5/16" between feet (long axis)
bolt_d             = 4.75;        // foot bolt diameter
drill_d            = 5.5;         // clearance hole for M5 bolt

// Center registration
center_hole_d      = 27.2;        // existing floor center hole + clearance

// Template dimensions
template_thickness = 3.0;
// Template needs to span the full foot pattern + margin
template_w         = foot_width + 30;   // 201.5mm
template_l         = foot_length + 30;  // 241.1mm
corner_r           = 5.0;

// --- The template ---
difference() {
    // Rounded rectangle base
    hull() {
        translate([-(template_l/2 - corner_r), -(template_w/2 - corner_r), 0])
            cylinder(r = corner_r, h = template_thickness);
        translate([(template_l/2 - corner_r), -(template_w/2 - corner_r), 0])
            cylinder(r = corner_r, h = template_thickness);
        translate([-(template_l/2 - corner_r), (template_w/2 - corner_r), 0])
            cylinder(r = corner_r, h = template_thickness);
        translate([(template_l/2 - corner_r), (template_w/2 - corner_r), 0])
            cylinder(r = corner_r, h = template_thickness);
    }

    // Center registration hole
    translate([0, 0, -0.1])
        cylinder(d = center_hole_d, h = template_thickness + 0.2);

    // 4 scale mounting drill holes
    // Rectangle centered on origin
    for (x = [-foot_length/2, foot_length/2]) {
        for (y = [-foot_width/2, foot_width/2]) {
            translate([x, y, -0.1])
                cylinder(d = drill_d, h = template_thickness + 0.2);
        }
    }

    // Arrow marker showing "FRONT" (long axis direction)
    translate([foot_length/2 + 10, 0, template_thickness - 0.5])
        cylinder(d1 = 8, d2 = 0, h = 1);
}

// Labels — raised dots next to each drill hole for easy ID
for (x = [-foot_length/2, foot_length/2]) {
    for (y = [-foot_width/2, foot_width/2]) {
        translate([x, y + drill_d, template_thickness])
            cylinder(d = 2, h = 1);
    }
}
