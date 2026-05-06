$fn = 120;

// ==========================================
// PRINT FILE: Pan Adapter Expansion Disc
// ==========================================
// Thin disc that sits ON TOP of the existing 155mm pan adapter.
// 3 nubs drop into the post sockets for alignment.
// Adds 3/4" (19mm) to the diameter — temporary fix until
// full new box is built.
//
// Print flat, nubs facing UP (flip to install).
// PLA, no supports.
// ==========================================

// --- Existing pan adapter reference ---
existing_pan_od    = 155.0;
post_socket_d      = 8.4;       // existing socket diameter
post_socket_depth  = 4.0;       // existing socket depth
post_count         = 3;
bolt_circle_r      = 65.0;

// --- Expansion disc ---
expansion          = 19.0;      // 3/4 inch
disc_od            = existing_pan_od + expansion;  // 174mm
disc_thickness     = 3.0;       // thin, just a platform

// --- Alignment nubs (drop into post sockets) ---
nub_d              = post_socket_d - 0.4;  // 8.0mm — snug in 8.4mm socket
nub_h              = post_socket_depth - 0.5;  // 3.5mm — doesn't bottom out

// --- The part ---
union() {
    // Main disc
    cylinder(d = disc_od, h = disc_thickness);

    // 3 alignment nubs on bottom (printed facing up, flip to install)
    for (i = [0 : post_count - 1]) {
        rotate([0, 0, i * 120])
            translate([bolt_circle_r, 0, disc_thickness])
                cylinder(d = nub_d, h = nub_h);
    }
}
