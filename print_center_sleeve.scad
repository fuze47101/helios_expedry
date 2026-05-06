$fn = 120;

// ==========================================
// PRINT FILE: Center Tube Outer Sleeve
// ==========================================
// Smooth outer shell that slides over the core + cable.
// Vent holes for heat radiation and moisture transport.
// Bottom has a recess pocket for the core's flange.
// Prints upright.
//
// Bambu settings:
//   Brim: 8mm outer brim (tall print)
//   Speed: 60mm/s max
//   Infill: 20% gyroid
//   Walls: 3
//   Layer height: 0.2mm
//   Supports: NONE
// ==========================================

// Parameters
tube_od            = 75.0;        // outer sleeve OD
tube_height        = 228.6;       // 9 inches
sleeve_wall        = 3.0;
sleeve_id          = tube_od - 2*sleeve_wall;  // 69.0mm

// Core flange dimensions (must match print_center_core.scad)
flange_od          = 68.7;        // core flange OD (sleeve_id - 0.3)
flange_h           = 8.0;         // core flange height (~1/4")

// Flange recess in sleeve bottom — wider clearance for PLA tolerance
recess_id          = flange_od + 1.0;  // 69.7mm — 0.5mm clearance per side to flange
recess_depth       = flange_h + 0.5;   // 8.5mm — flange drops in with 0.5mm air

// Vent holes
vent_hole_d        = 10.0;
vent_rows          = 6;
vent_per_row       = 8;
vent_start_z       = 30.0;
vent_row_spacing   = 30.0;

// --- Vent holes pattern ---
module vent_holes(od, rows, per_row, start_z, spacing, hole_d) {
    for (row = [0 : rows-1]) {
        z = start_z + row * spacing;
        for (i = [0 : per_row-1]) {
            angle = i * (360/per_row) + (row % 2) * (180/per_row);
            rotate([0, 0, angle])
                translate([od/2, 0, z])
                    rotate([0, 90, 0])
                        cylinder(d = hole_d, h = sleeve_wall + 2, center = true);
        }
    }
}

// --- The part ---
difference() {
    cylinder(d = tube_od, h = tube_height);

    // Main hollow interior (69mm ID for cable clearance)
    translate([0, 0, recess_depth])
        cylinder(d = sleeve_id, h = tube_height - recess_depth + 0.1);

    // Flange recess pocket at bottom (wider, to accept the core flange)
    translate([0, 0, -0.1])
        cylinder(d = recess_id, h = recess_depth + 0.1);

    // Vent holes
    vent_holes(tube_od, vent_rows, vent_per_row, vent_start_z, vent_row_spacing, vent_hole_d);
}
