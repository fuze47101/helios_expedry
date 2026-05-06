$fn = 120;

// ==========================================
// PRINT FILE: Scale Pan Adapter (replacement pan)
// ==========================================
// Wider replacement for stock Bonvoisin pan (109.5mm).
// Sits on the load cell center pin same as stock pan.
// Has 3 post sockets at R=65mm to receive tripod posts.
//
// MEASURE the load cell center pin diameter and update
// center_pin_d below before printing!
// ==========================================

// --- Stock pan measurements ---
stock_pan_od       = 109.5;       // 4 10/32"
stock_rim_h        = 7.1;         // 9/32" edge fold
stock_socket_depth = 15.1;        // 19/32" center post depth

// --- Center pin (MEASURE THIS on the load cell) ---
// The pin sticking up from the scale's well
center_pin_d       = 9.0;         // measured with calipers
center_socket_d    = center_pin_d + 0.3;  // 9.3mm socket — 0.15mm clearance per side
center_socket_depth = stock_socket_depth;  // match stock pan depth

// --- Replacement pan dimensions ---
// Must catch 3 posts at R=65mm with 8mm post diameter
// Minimum OD = 2*(65+4+4) = 146mm, using 155mm for margin
pan_od             = 155.0;
pan_thickness      = 5.0;         // solid disc thickness

// --- Post interface ---
post_od            = 8.0;
post_count         = 3;
bolt_circle_r      = 65.0;
post_socket_d      = post_od + 0.4;  // 8.4mm socket for 8mm post
post_socket_depth  = 4.0;            // post tip sits 4mm into socket

// --- Center boss (replicates stock pan bottom) ---
// Raised cylinder on bottom that drops into the scale well
center_boss_od     = 30.0;        // wide enough to be stable on the load cell
center_boss_h      = stock_socket_depth;  // same depth as stock

// --- The part ---
// Prints UPSIDE DOWN — post sockets face up on bed,
// center boss points up (will face down when installed)

difference() {
    union() {
        // Main disc
        cylinder(d = pan_od, h = pan_thickness);

        // Center boss (load cell interface)
        // This drops into the scale well and sits on the pin
        translate([0, 0, pan_thickness])
            cylinder(d = center_boss_od, h = center_boss_h);
    }

    // Center pin socket (hole in the boss for the load cell pin)
    translate([0, 0, pan_thickness - 0.1])
        cylinder(d = center_socket_d, h = center_boss_h + 0.2);

    // 3 post sockets on TOP surface (which is the bottom when flipped)
    // These face DOWN in use — post tips push up into them
    for (i = [0 : post_count-1]) {
        rotate([0, 0, i * 120])
            translate([bolt_circle_r, 0, -0.1])
                cylinder(d = post_socket_d, h = post_socket_depth + 0.1);
    }
}
