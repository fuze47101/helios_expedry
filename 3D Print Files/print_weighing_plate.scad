$fn = 120;

// ==========================================
// PRINT FILE: Weighing Plate + Posts (separate)
// ==========================================
// Plate prints FLAT on bed (rim side up)
// Posts print FLAT on their side (stronger, no spaghetti)
// Posts press-fit into sockets in the plate bottom
//
// Print both, then press posts into plate sockets.
// ==========================================

// --- Parameters ---
tube_od            = 75.0;
plate_od           = 170.0;
plate_center_hole  = tube_od + 5.0;  // 80mm
plate_thickness    = 6.0;
plate_rim_h        = 3.0;

outer_seat_od      = 150.2;
outer_seat_id      = 143.8;
outer_seat_depth   = 2.0;
inner_seat_od      = 86.2;
inner_seat_id      = 82.2;
inner_seat_depth   = 2.0;

post_od            = 8.0;
post_count         = 3;
bolt_circle_r      = 65.0;

floor_thickness    = 2.5;
above_floor_gap    = 2.0;
below_floor_drop   = 55.0;
post_length        = plate_thickness + above_floor_gap + floor_thickness + below_floor_drop;

// Press-fit socket in plate bottom for posts
socket_depth       = 8.0;        // how deep post inserts into plate
socket_d           = post_od + 0.2;  // 8.2mm socket for 8mm post (snug press-fit)

// What to show
show_plate         = true;
show_posts         = true;

// ==========================================
// PLATE — prints flat, rim side UP
// ==========================================
if (show_plate) {
    difference() {
        union() {
            // Main plate body
            cylinder(d = plate_od, h = plate_thickness);
            // Raised rim on top
            translate([0, 0, plate_thickness])
                difference() {
                    cylinder(d = plate_od, h = plate_rim_h);
                    translate([0, 0, -0.1])
                        cylinder(d = plate_od - 6.0, h = plate_rim_h + 0.2);
                }
        }

        // Center hole
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

        // 3 post sockets in plate BOTTOM (blind holes, don't go all the way through)
        for (i = [0 : post_count-1]) {
            rotate([0, 0, i * 120])
                translate([bolt_circle_r, 0, -0.1])
                    cylinder(d = socket_d, h = socket_depth + 0.1);
        }
    }
}

// ==========================================
// POSTS — print on their side (3 of them)
// ==========================================
if (show_posts) {
    // Effective post length: total minus the part that sockets into the plate
    effective_post = post_length - socket_depth;

    for (i = [0 : post_count-1]) {
        translate([0, -110 - i*12, post_od/2])
            rotate([0, 90, 0])
                union() {
                    // Main post shaft
                    cylinder(d = post_od, h = effective_post);
                    // Socket stub (slightly undersized for press-fit)
                    translate([0, 0, -socket_depth])
                        cylinder(d = post_od - 0.1, h = socket_depth);
                }
    }
}
