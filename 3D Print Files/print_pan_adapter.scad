$fn = 120;

// ==========================================
// PRINT FILE: Scale Pan Adapter
// ==========================================
// Sits on the scale pan, receives the 3 post tips from
// the weighing plate above. Increased OD by 3/4" to
// account for scale-to-box alignment offset.
//
// Print flat, socket side UP. PLA, no supports.
// ==========================================

pan_adapter_od     = 169.0;    // was 150, +3/4" for alignment
pan_adapter_h      = 5.0;
post_od            = 8.0;
post_count         = 3;
bolt_circle_r      = 65.0;
post_socket_depth  = 3.0;
post_socket_d      = post_od + 0.4;  // 8.4mm

difference() {
    cylinder(d = pan_adapter_od, h = pan_adapter_h);

    // 3 post sockets
    for (i = [0 : post_count-1]) {
        rotate([0, 0, i * 120])
            translate([bolt_circle_r, 0, pan_adapter_h - post_socket_depth])
                cylinder(d = post_socket_d, h = post_socket_depth + 0.1);
    }
}
