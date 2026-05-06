$fn = 120;

// ==========================================
// PRINT FILE: Center Tube Inner Core
// ==========================================
// Cable spool with spiral ribs on outside.
// Cable wraps BETWEEN the ribs (like a bolt thread).
// Wall stays solid — no through-cuts.
//
// Cable: 36" (914.4mm) total length
// 5 wraps spread over full tube height
//
// Prints upright — floor flange on bed.
//
// Bambu settings:
//   Brim: 8mm outer brim
//   Speed: 60mm/s max
//   Infill: 20% gyroid
//   Walls: 3
//   Layer height: 0.2mm
// ==========================================

// Parameters
tube_od            = 75.0;
tube_height        = 228.6;      // 9 inches
sleeve_wall        = 3.0;
sleeve_id          = tube_od - 2*sleeve_wall;  // 69.0mm

core_od            = sleeve_id - 2*5.0;  // 59.0mm
core_wall          = 3.0;
core_id            = core_od - 2*core_wall;  // 53.0mm

// Cable parameters — based on 36" cable
cable_width        = 15.0;        // 14-15mm wide
cable_thick        = 5.0;         // 5mm thick

// Spiral layout
cable_wraps        = 5;
cable_zone_start   = 15.0;
cable_zone_end     = tube_height - 10.0;
cable_zone_height  = cable_zone_end - cable_zone_start;
cable_pitch        = cable_zone_height / cable_wraps;  // ~40.7mm

// Guide ridge parameters — low ridges to keep cable tracking in spiral
// Cable is 5mm thick, gap to sleeve is 5mm per side
// Ridges are just 1.5mm tall — cable sits on core, ridge keeps it from sliding
// Sleeve slides over and holds cable against core
ridge_height       = 1.5;                // low guide ridge
ridge_width        = 2.0;                // thin ridge wall

// Cable entry slot
cable_slot_width   = cable_width + 2.0;   // 17mm wide
cable_slot_height  = cable_thick + 2.0;   // 7mm tall
cable_slot_z       = cable_zone_start;

// Vent holes (between ribs where there's clear wall)
vent_rows          = 4;
vent_per_row       = 6;
vent_hole_d        = 6.0;         // smaller to not weaken wall
vent_start_z       = cable_zone_start + cable_pitch * 0.5;
vent_row_spacing   = cable_pitch;

// Floor mounting flange
flange_od          = sleeve_id - 0.3;  // 68.7mm
flange_h           = 8.0;
flange_hole_d      = 4.5;
flange_holes       = 4;

// --- Vent holes pattern ---
module vent_holes(od, rows, per_row, start_z, spacing, hole_d) {
    for (row = [0 : rows-1]) {
        z = start_z + row * spacing;
        for (i = [0 : per_row-1]) {
            angle = i * (360/per_row) + (row % 2) * (180/per_row);
            rotate([0, 0, angle])
                translate([od/2, 0, z])
                    rotate([0, 90, 0])
                        cylinder(d = hole_d, h = core_wall + 1, center = true);
        }
    }
}

// --- Spiral guide ridges on core exterior ---
// Low ridges on each side of the cable path to keep it tracking
// Ridge OD = 59 + 2*1.5 = 62mm — well inside sleeve_id 69mm
// Cable (5mm thick) sits on core surface, sticks up to 64mm — inside 69mm sleeve
module spiral_ridges() {
    steps_per_wrap = 24;
    total_steps = cable_wraps * steps_per_wrap;

    // Ridge on the LOWER side of cable path
    for (s = [0 : total_steps - 1]) {
        angle = s * (360 / steps_per_wrap);
        z = cable_zone_start + s * (cable_pitch / steps_per_wrap) - cable_width/2 - ridge_width/2;
        rotate([0, 0, angle])
            translate([core_od/2 + ridge_height/2, 0, z])
                rotate([0, 90, 0])
                    cylinder(d = ridge_width, h = ridge_height, center = true, $fn=8);
    }
    // Ridge on the UPPER side of cable path
    for (s = [0 : total_steps - 1]) {
        angle = s * (360 / steps_per_wrap);
        z = cable_zone_start + s * (cable_pitch / steps_per_wrap) + cable_width/2 + ridge_width/2;
        if (z < cable_zone_end + cable_width) {
            rotate([0, 0, angle])
                translate([core_od/2 + ridge_height/2, 0, z])
                    rotate([0, 90, 0])
                        cylinder(d = ridge_width, h = ridge_height, center = true, $fn=8);
        }
    }
}

// --- Cable entry slot ---
module cable_entry_slot() {
    translate([0, 0, cable_slot_z])
        translate([core_od/4, 0, 0])
            cube([core_od/2 + 2, cable_slot_width, cable_slot_height], center = true);
}

// --- The part ---
union() {
    difference() {
        union() {
            // Main solid cylinder
            cylinder(d = core_od, h = tube_height);

            // Floor mounting flange
            cylinder(d = flange_od, h = flange_h);
        }

        // Hollow center
        translate([0, 0, -0.1])
            cylinder(d = core_id, h = tube_height + 0.2);

        // Cable entry slot
        cable_entry_slot();

        // Vent holes (shallow — only through core wall)
        vent_holes(core_od, vent_rows, vent_per_row, vent_start_z, vent_row_spacing, vent_hole_d);

        // Flange mounting screw holes
        for (i = [0 : flange_holes-1]) {
            rotate([0, 0, i * 90 + 45])
                translate([flange_od/2 - 5, 0, -0.1])
                    cylinder(d = flange_hole_d, h = flange_h + 0.2);
        }
    }

    // ADD spiral guide ridges on outside
    spiral_ridges();
}
