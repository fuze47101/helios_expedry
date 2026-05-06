$fn = 120;

// ============================================================
// Helios Weighing System & Center Tube Assembly
// ============================================================
// Rev 1.0 — Initial design
//
// Components:
//   1. Center tube inner core (cable spool with helical channel)
//   2. Center tube outer sleeve (smooth, vent holes)
//   3. Weighing plate (annular, 3-post tripod)
//   4. Labyrinth bushing (press-fit into floor holes)
//   5. Scale pan adapter (receives 3 post tips)
//   6. Drill template (print first — jig for drilling 3 new floor holes)
// ============================================================

// === VISIBILITY FLAGS ===
show_center_core   = false;
show_center_sleeve = false;
show_weighing_plate = true;
show_labyrinth     = false;
show_pan_adapter   = false;
show_drill_template = false;  // drill jig — print FIRST
show_assembly      = false;   // true = assembled view, false = print layout
show_floor         = false;   // show phantom floor for reference

// ============================================================
//  CENTER TUBE PARAMETERS
// ============================================================
tube_od            = 75.0;       // outer sleeve OD (matches current tube)
tube_height        = 228.6;      // 9 inches
sleeve_wall        = 3.0;        // outer sleeve wall thickness
sleeve_id          = tube_od - 2*sleeve_wall;  // 69.0mm

core_od            = sleeve_id - 2*5.0;  // 59.0mm (5mm cable channel)
core_wall          = 3.0;
core_id            = core_od - 2*core_wall;  // 53.0mm

// Cable parameters
cable_width        = 15.0;       // 14-15mm, using 15 for clearance
cable_thick        = 5.0;        // 5mm thick flat cable
cable_wraps        = 6;
cable_pitch        = cable_width + 2.0;  // 17mm pitch (2mm gap between wraps)
cable_zone_start   = 10.0;       // start wraps 10mm above base
cable_channel_depth = cable_thick + 0.5;  // 5.5mm deep channel in core

// Vent hole parameters (both core and sleeve)
vent_hole_d        = 10.0;       // vent hole diameter
vent_rows          = 6;          // rows of vent holes
vent_per_row       = 8;          // holes per row
vent_start_z       = 30.0;       // start vents above cable zone
vent_row_spacing   = 30.0;       // spacing between rows

// Core base flange
core_flange_od     = sleeve_id - 0.3;  // snug fit inside sleeve
core_flange_h      = 5.0;

// ============================================================
//  WEIGHING PLATE PARAMETERS
// ============================================================
plate_od           = 170.0;      // wider than capsule base (160mm)
plate_center_hole  = tube_od + 5.0;  // 80mm, 2.5mm clearance to tube
plate_thickness    = 6.0;        // sturdy platform
plate_rim_h        = 3.0;        // raised rim to locate capsule

// Cage seat grooves in weighing plate (replaces old base)
outer_seat_od      = 150.2;
outer_seat_id      = 143.8;
outer_seat_depth   = 2.0;
inner_seat_od      = 86.2;
inner_seat_id      = 82.2;
inner_seat_depth   = 2.0;

// ============================================================
//  POST / TRIPOD PARAMETERS
// ============================================================
post_od            = 8.0;
post_count         = 3;          // tripod at 120°
bolt_circle_r      = 65.0;       // Ø130mm — between inner (R=43) and outer (R=72) cage seats
                                 // Drill 3 NEW 12mm holes at this radius, 120° apart

// Post length: plate thickness + clearance above floor + floor thickness + drop to scale pan
floor_thickness    = 2.5;
above_floor_gap    = 2.0;        // plate sits 2mm above floor (no contact)
below_floor_drop   = 55.0;       // distance from floor bottom to scale pan
post_length        = plate_thickness + above_floor_gap + floor_thickness + below_floor_drop;

// ============================================================
//  LABYRINTH BUSHING PARAMETERS
// ============================================================
bushing_press_od   = 12.0;       // press-fit into 12mm drilled hole
bushing_bore       = 8.5;        // 0.25mm clearance to 8mm post
bushing_floor_h    = floor_thickness + 0.5;  // spans floor + slight proud

// Labyrinth rings above floor
lab_ring_count     = 3;
lab_ring_h         = 3.0;        // height of each ring
lab_ring_gap       = 2.0;        // gap between rings
lab_ring_wall      = 1.0;        // ring wall thickness
lab_above_total    = 10.0;       // total height above floor
lab_below_total    = 8.0;        // total height below floor

// ============================================================
//  SCALE PAN ADAPTER PARAMETERS
// ============================================================
pan_adapter_od     = 169.0;      // was 150, +3/4" (19mm) for scale alignment offset in box
pan_adapter_h      = 5.0;
post_socket_depth  = 3.0;        // post tips sit in 3mm deep sockets
post_socket_d      = post_od + 0.4;  // 8.4mm socket for 8mm post


// ============================================================
//  MODULES
// ============================================================

// --- Vent holes pattern ---
module vent_holes(od, rows, per_row, start_z, spacing, hole_d) {
    for (row = [0 : rows-1]) {
        z = start_z + row * spacing;
        for (i = [0 : per_row-1]) {
            angle = i * (360/per_row) + (row % 2) * (180/per_row);  // staggered
            rotate([0, 0, angle])
                translate([od/2, 0, z])
                    rotate([0, 90, 0])
                        cylinder(d = hole_d, h = 20, center = true);
        }
    }
}

// --- Helical channel on core exterior ---
// Corkscrew groove using overlapping cylinders along helix path
module helical_channel() {
    steps_per_wrap = 48;
    total_steps = cable_wraps * steps_per_wrap;
    channel_d = cable_width * 0.75;  // 11.25mm wide groove

    for (s = [0 : total_steps - 1]) {
        angle = s * (360 / steps_per_wrap);
        z = cable_zone_start + s * (cable_pitch / steps_per_wrap);
        rotate([0, 0, angle])
            translate([core_od/2 + 1, 0, z])
                rotate([0, 90, 0])
                    cylinder(d = channel_d, h = cable_channel_depth + 2, center = true);
    }
}

// --- Center tube inner core ---
module center_core() {
    color("SteelBlue")
    difference() {
        union() {
            // Main cylinder
            cylinder(d = core_od, h = tube_height);
            // Bottom flange for alignment inside sleeve
            cylinder(d = core_flange_od, h = core_flange_h);
        }
        // Hollow center
        translate([0, 0, -0.1])
            cylinder(d = core_id, h = tube_height + 0.2);
        // Helical cable channel
        helical_channel();
        // Vent holes through core wall
        vent_holes(core_od, vent_rows, 6, vent_start_z, vent_row_spacing, 8.0);
    }
}

// --- Center tube outer sleeve ---
module center_sleeve() {
    color("LightGray")
    difference() {
        cylinder(d = tube_od, h = tube_height);
        // Hollow interior
        translate([0, 0, -0.1])
            cylinder(d = sleeve_id, h = tube_height + 0.2);
        // Vent holes for heat radiation and moisture transport
        vent_holes(tube_od, vent_rows, vent_per_row, vent_start_z, vent_row_spacing, vent_hole_d);
    }
}

// --- Weighing plate with cage seats ---
module weighing_plate() {
    color("Orange", 0.8)
    difference() {
        union() {
            // Main plate
            cylinder(d = plate_od, h = plate_thickness);
            // Raised rim for capsule alignment
            translate([0, 0, plate_thickness])
                difference() {
                    cylinder(d = plate_od, h = plate_rim_h);
                    translate([0, 0, -0.1])
                        cylinder(d = plate_od - 6.0, h = plate_rim_h + 0.2);
                }
        }
        // Center hole (clears center tube with no contact)
        translate([0, 0, -0.1])
            cylinder(d = plate_center_hole, h = plate_thickness + plate_rim_h + 0.2);

        // Outer cage seat groove
        translate([0, 0, plate_thickness - outer_seat_depth])
            difference() {
                cylinder(d = outer_seat_od, h = outer_seat_depth + 0.1);
                translate([0, 0, -0.1])
                    cylinder(d = outer_seat_id, h = outer_seat_depth + 0.3);
            }

        // Inner cage seat groove
        translate([0, 0, plate_thickness - inner_seat_depth])
            difference() {
                cylinder(d = inner_seat_od, h = inner_seat_depth + 0.1);
                translate([0, 0, -0.1])
                    cylinder(d = inner_seat_id, h = inner_seat_depth + 0.3);
            }
    }

    // 3 posts extending downward
    for (i = [0 : post_count-1]) {
        angle = i * 120;  // 120° spacing
        rotate([0, 0, angle])
            translate([bolt_circle_r, 0, 0])
                // Post goes down from plate bottom
                translate([0, 0, -post_length + plate_thickness])
                    cylinder(d = post_od, h = post_length);
    }
}

// --- Labyrinth bushing (one unit — print 3) ---
module labyrinth_bushing() {
    color("Green", 0.7)
    union() {
        // Press-fit section (sits in floor hole)
        translate([0, 0, -bushing_floor_h/2])
            difference() {
                cylinder(d = bushing_press_od, h = bushing_floor_h);
                translate([0, 0, -0.1])
                    cylinder(d = bushing_bore, h = bushing_floor_h + 0.2);
            }

        // Labyrinth rings ABOVE floor
        for (r = [0 : lab_ring_count-1]) {
            ring_od = bushing_press_od + 2*(r+1) * (lab_ring_wall + lab_ring_gap);
            translate([0, 0, bushing_floor_h/2])
                difference() {
                    cylinder(d = ring_od, h = lab_above_total);
                    translate([0, 0, -0.1])
                        cylinder(d = ring_od - 2*lab_ring_wall, h = lab_above_total + 0.2);
                }
        }

        // Drip skirt BELOW floor (inverted cone to shed moisture outward)
        translate([0, 0, -bushing_floor_h/2 - lab_below_total])
            difference() {
                cylinder(d1 = bushing_press_od + 10, d2 = bushing_press_od, h = lab_below_total);
                translate([0, 0, -0.1])
                    cylinder(d = bushing_bore, h = lab_below_total + 0.2);
            }
    }
}

// --- Scale pan adapter ---
module pan_adapter() {
    color("Yellow", 0.7)
    difference() {
        // Base disc
        cylinder(d = pan_adapter_od, h = pan_adapter_h);

        // 3 post sockets
        for (i = [0 : post_count-1]) {
            angle = i * 120;
            rotate([0, 0, angle])
                translate([bolt_circle_r, 0, pan_adapter_h - post_socket_depth])
                    cylinder(d = post_socket_d, h = post_socket_depth + 0.1);
        }
    }
}

// --- Phantom floor for reference ---
module phantom_floor() {
    color("DimGray", 0.3)
    difference() {
        translate([-150, -150, 0])
            cube([300, 300, floor_thickness]);
        // Center hole (existing, 27mm)
        translate([0, 0, -0.1])
            cylinder(d = 27.0, h = floor_thickness + 0.2);
        // 6 existing small holes at R=95.25, 60° spacing (5mm)
        for (i = [0 : 5]) {
            rotate([0, 0, i * 60])
                translate([95.25, 0, -0.1])
                    cylinder(d = 5.0, h = floor_thickness + 0.2);
        }
        // 3 NEW drilled holes at R=65, 120° spacing (12mm)
        for (i = [0 : 2]) {
            rotate([0, 0, i * 120])
                translate([bolt_circle_r, 0, -0.1])
                    cylinder(d = 12.0, h = floor_thickness + 0.2);
        }
    }
}


// --- Drill template (print this, lay on floor, drill through guide holes) ---
module drill_template() {
    color("Red", 0.5)
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
    rotate([0, 0, 0])
        translate([bolt_circle_r, 0, 3.0])
            cylinder(d1 = 6, d2 = 0, h = 3);
}


// ============================================================
//  ASSEMBLY / PRINT LAYOUT
// ============================================================

if (show_assembly) {
    // Floor at z=0
    if (show_floor) phantom_floor();

    // Center tube sits ON the floor
    if (show_center_core)
        translate([0, 0, floor_thickness])
            center_core();

    if (show_center_sleeve)
        translate([0, 0, floor_thickness])
            center_sleeve();

    // Weighing plate floats above floor (supported by posts)
    // Plate bottom is above_floor_gap above floor top
    if (show_weighing_plate)
        translate([0, 0, floor_thickness + above_floor_gap])
            weighing_plate();

    // Labyrinth bushings in floor holes
    if (show_labyrinth) {
        for (i = [0 : 2]) {
            rotate([0, 0, i * 120])
                translate([bolt_circle_r, 0, floor_thickness/2])
                    labyrinth_bushing();
        }
    }

    // Scale pan adapter below floor
    if (show_pan_adapter)
        translate([0, 0, -(below_floor_drop - pan_adapter_h)])
            pan_adapter();
}

if (!show_assembly) {
    // Print layout — all parts flat on build plate
    // Each part respects its visibility flag
    if (show_center_core)
        translate([-100, 0, 0]) center_core();
    if (show_center_sleeve)
        translate([100, 0, 0]) center_sleeve();
    if (show_weighing_plate)
        translate([0, 120, post_length - plate_thickness]) weighing_plate();
    if (show_labyrinth) {
        translate([-80, -80, 0]) labyrinth_bushing();
        translate([0, -80, 0]) labyrinth_bushing();
        translate([80, -80, 0]) labyrinth_bushing();
    }
    if (show_pan_adapter)
        translate([0, -120, 0]) pan_adapter();
    if (show_drill_template)
        translate([0, -250, 0]) drill_template();
}
