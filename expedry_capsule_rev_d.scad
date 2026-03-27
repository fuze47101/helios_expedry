$fn = 160;

// ============================================================
// Expedry Capsule Rev D4
// ============================================================
// Joint redesign: socket wraps DOWN over section below like a
// pipe coupling. ZERO net height added by joints. Both cages
// drop into seat grooves in base. Assembled height = exact
// target (228.6 outer, 231.6 inner — inner 3mm above outer).
//
// Each section has:
//   - Structural ring at bottom (posts anchor to this)
//   - Cage body (posts + mid-rings + gussets)
//   - Structural ring at top
//   - Socket collar extending DOWN from bottom ring (sections 2 & 3)
//     that wraps over the top ring of the section below.
// ============================================================

// === VISIBILITY FLAGS ===
show_assembly      = true;
show_print_layout  = false;

show_base          = true;
show_outer_cage    = true;
show_inner_cage    = true;
show_lid           = true;
show_disk          = true;

// Set to 1, 2, or 3 to show individual sections (0 = show all)
show_outer_section = 0;
show_inner_section = 0;

// ============================================================
//  OUTER CAGE
// ============================================================
outer_cage_height     = 228.6;
outer_cage_od         = 150.0;
outer_ring_radial     = 3.2;
outer_ring_height     = 4.0;
outer_post_count      = 12;
outer_post_tan        = 2.8;
outer_post_rad        = 2.8;
outer_mid_ring_count  = 4;
outer_mid_ring_radial = 1.8;
outer_mid_ring_height = 2.0;
outer_snap_lip_h      = 1.2;

outer_sections        = 3;
outer_section_h       = outer_cage_height / outer_sections;  // 76.2

// ============================================================
//  BASE
// ============================================================
base_od            = 160.0;
base_t             = 8.0;
outer_seat_od      = 150.2;
outer_seat_id      = 143.8;
outer_seat_depth   = 2.0;
inner_seat_od      = 86.2;    // inner cage OD (86) + 0.2 clearance
inner_seat_id      = 82.2;    // inner cage ID (82) + 0.2 clearance
inner_seat_depth   = 2.0;     // same depth as outer seat
center_opening_d   = 80.0;
bearing_od         = 85.0;
bearing_seat_depth = 4.0;
bearing_bore_d     = center_opening_d;

// ============================================================
//  INNER CAGE  (3 mm taller than outer, assembled)
// ============================================================
inner_cage_bottom_od = 86.0;
inner_cage_top_od    = 86.0;
inner_cage_height    = outer_cage_height - outer_seat_depth + inner_seat_depth + 3.0;  // 231.6
inner_ring_radial    = 2.0;
inner_ring_height    = 2.0;
inner_post_count     = 12;
inner_post_tan       = 2.2;
inner_post_rad       = 2.2;
inner_mid_ring_count = 6;

inner_sections       = 3;
inner_section_h      = inner_cage_height / inner_sections;  // 76.53

// ============================================================
//  BOUNDARY RINGS (wider than mid-rings — fully capture posts)
// ============================================================
// These are the structural platforms at section cut boundaries.
// They must extend well inside the post inner edge so the printer
// lays down the ring solidly ON TOP of the posts.
outer_boundary_radial = 5.0;   // wall: ID=Ø140, posts at Ø144 → 2mm past posts
outer_boundary_height = 4.0;
inner_boundary_radial = 4.0;   // wall: ID=Ø78, posts at Ø81.8 → 1.9mm past posts
inner_boundary_height = 3.0;

// ============================================================
//  JOINT GEOMETRY
// ============================================================
// Socket collar extends DOWN from bottom of sections 2 & 3.
// It wraps OVER the top ring of the section below.
// Net height added: ZERO (collar overlaps existing geometry).
joint_h       = 8.0;    // collar depth (wraps 8mm down over section below)
joint_gap     = 0.35;   // clearance between socket ID and cage OD
socket_wall   = 2.0;    // wall thickness of socket collar
detent_h      = 0.5;    // snap bump height
detent_w      = 8.0;    // snap bump width

// ============================================================
//  FLOATING DISK
// ============================================================
outer_cage_id  = outer_cage_od - 2*outer_ring_radial;
disk_od        = outer_cage_id - 1.0;
disk_id        = inner_cage_top_od + 1.0;
disk_t         = 3.0;
disk_tab_w     = 12.0;
disk_tab_l     = 10.0;
disk_tab_t     = 3.0;

// ============================================================
//  LID
// ============================================================
lid_top_d              = 156.0;
lid_top_t              = 5.0;
lid_skirt_id           = outer_cage_od + 0.8;
lid_skirt_od           = lid_skirt_id + 6.0;
lid_skirt_depth        = 12.0;
snap_count             = 6;
snap_w                 = 8.0;
snap_h                 = 1.4;
snap_depth             = 2.0;
lid_recess_clearance   = 0.4;
lid_inner_recess_id    = inner_cage_top_od + lid_recess_clearance;
lid_inner_recess_od    = lid_inner_recess_id + 6.0;
lid_inner_recess_depth = 3.4;
lid_center_hole_d      = center_opening_d + 1.0;

// ============================================================
//  DERIVED
// ============================================================
outer_r      = outer_cage_od / 2;
outer_ri     = outer_r - outer_ring_radial;
outer_post_r = outer_r - outer_ring_radial/2 - outer_post_rad/2;
inner_top_r  = inner_cage_top_od / 2;
inner_post_r = inner_top_r - inner_ring_radial/2 - inner_post_rad/2;


// ============================================================
//  UTILITY MODULES
// ============================================================

module ring(od, radial, h) {
    difference() {
        cylinder(d = od, h = h);
        translate([0, 0, -0.1])
            cylinder(d = od - 2*radial, h = h + 0.2);
    }
}

module straight_post(r, tan, rad, z0, h, a) {
    rotate([0, 0, a])
        translate([r, -tan/2, z0])
            cube([rad, tan, h]);
}

module mid_ring_gusset(post_r, post_tan, ring_h, gusset_drop, angle) {
    rotate([0, 0, angle])
        translate([post_r - 0.5, -post_tan/2, -gusset_drop])
            linear_extrude(height = gusset_drop)
                polygon([
                    [0, 0],
                    [gusset_drop + 1.0, 0],
                    [gusset_drop + 1.0, post_tan],
                    [0, post_tan]
                ]);
}

module clip(z_start, z_end) {
    intersection() {
        children();
        translate([0, 0, z_start - 0.01])
            cylinder(d = 999, h = z_end - z_start + 0.02);
    }
}

// --- SOCKET COLLAR ---
// A ring wider than the cage that extends DOWNWARD.
// In print orientation: this sits at the bottom on the build plate.
// In assembly: it wraps over the top of the section below.
// cage_od = the OD of the cage this wraps over
module socket_collar(cage_od) {
    collar_id = cage_od + 2*joint_gap;
    collar_od = collar_id + 2*socket_wall;

    difference() {
        ring(collar_od, socket_wall, joint_h);

        // detent grooves on the inside (bumps on section below's
        // top ring click into these)
        for (i = [0 : 5]) {
            a = i * 60;
            rotate([0, 0, a])
                translate([collar_id/2 - 0.2, -detent_w/2, joint_h - 3.0])
                    cube([detent_h + 0.4, detent_w, 1.5]);
        }
    }
}

// Bridge platform at top of collar connecting collar to cage body above.
// Spans from well inside the posts out to the collar ID.
// This is the solid floor that posts land on and the collar connects to.
// Overlaps 0.5mm into collar top for solid union.
module collar_bridge(cage_od, boundary_radial, boundary_h) {
    bridge_od = cage_od + 2*joint_gap + 0.01;  // just past collar ID
    bridge_id = cage_od - 2*boundary_radial;     // well inside posts
    translate([0, 0, joint_h - 0.5])
        difference() {
            cylinder(d = bridge_od, h = boundary_h + 0.5);
            translate([0, 0, -0.1])
                cylinder(d = bridge_id, h = boundary_h + 0.7);
        }
}

// Small detent bumps on the OUTSIDE of a structural ring's top edge
// These click into the socket collar grooves
module ring_detents(cage_od) {
    for (i = [0 : 5]) {
        a = i * 60;
        rotate([0, 0, a])
            translate([cage_od/2 - 0.1, -detent_w/2, 0])
                cube([detent_h, detent_w, 1.2]);
    }
}


// ============================================================
//  FULL CAGE BODIES (posts + mid-rings + gussets + boundary rings)
// ============================================================

module outer_cage_body() {
    union() {
        // vertical posts (full height)
        for (i = [0 : outer_post_count - 1]) {
            a = i * 360 / outer_post_count;
            straight_post(outer_post_r, outer_post_tan, outer_post_rad,
                          0, outer_cage_height, a);
        }

        // mid rings with gussets
        for (j = [1 : outer_mid_ring_count]) {
            z = 20 + j * ((outer_cage_height - 40) / (outer_mid_ring_count + 1));
            translate([0, 0, z]) {
                ring(outer_cage_od - 1.2, outer_mid_ring_radial, outer_mid_ring_height);
                for (i = [0 : outer_post_count - 1]) {
                    a = i * 360 / outer_post_count;
                    mid_ring_gusset(outer_post_r, outer_post_tan,
                                    outer_mid_ring_height, 4.0, a);
                }
            }
        }

        // structural platforms at section boundaries
        // Wide rings that fully capture posts for solid printing
        translate([0, 0, outer_section_h])
            ring(outer_cage_od, outer_boundary_radial, outer_boundary_height);
        translate([0, 0, 2*outer_section_h])
            ring(outer_cage_od, outer_boundary_radial, outer_boundary_height);
    }
}

module inner_cage_body() {
    union() {
        for (i = [0 : inner_post_count - 1]) {
            a = i * 360 / inner_post_count;
            straight_post(inner_post_r, inner_post_tan, inner_post_rad,
                          0, inner_cage_height, a);
        }

        for (j = [1 : inner_mid_ring_count]) {
            z = 12 + j * ((inner_cage_height - 24) / (inner_mid_ring_count + 1));
            translate([0, 0, z]) {
                ring(inner_cage_top_od - 0.8, 1.2, inner_ring_height);
                for (i = [0 : inner_post_count - 1]) {
                    a = i * 360 / inner_post_count;
                    mid_ring_gusset(inner_post_r, inner_post_tan,
                                    inner_ring_height, 3.0, a);
                }
            }
        }

        // structural platforms at section boundaries
        // Wide rings that fully capture posts for solid printing
        translate([0, 0, inner_section_h])
            ring(inner_cage_top_od, inner_boundary_radial, inner_boundary_height);
        translate([0, 0, 2*inner_section_h])
            ring(inner_cage_top_od, inner_boundary_radial, inner_boundary_height);
    }
}


// ============================================================
//  OUTER CAGE SECTIONS
// ============================================================
//
// Heights in assembly coordinates (z=0 at cage bottom):
//   Section 1: z = 0 to outer_section_h           (76.2)
//   Section 2: z = outer_section_h to 2*outer_section_h   (76.2 to 152.4)
//   Section 3: z = 2*outer_section_h to outer_cage_height (152.4 to 228.6)
//
// Sockets extend DOWN from sections 2 & 3 but overlap with section below.
// ZERO net height addition.

module outer_section_1() {
    // Print height: 76.2 mm (no socket, no extra)
    union() {
        // foot ring (sits in base groove)
        difference() {
            cylinder(d = outer_seat_od - 0.4, h = outer_seat_depth);
            translate([0, 0, -0.1])
                cylinder(d = outer_seat_id + 0.4, h = outer_seat_depth + 0.2);
        }
        // bottom structural platform (wide, captures posts)
        translate([0, 0, outer_seat_depth])
            ring(outer_cage_od, outer_boundary_radial, outer_boundary_height);

        // cage body clipped to section 1
        clip(0, outer_section_h) outer_cage_body();

        // top structural platform at section boundary
        translate([0, 0, outer_section_h - outer_boundary_height])
            ring(outer_cage_od, outer_boundary_radial, outer_boundary_height);

        // detent bumps near the top (snap into section 2's collar)
        translate([0, 0, outer_section_h - 2.0])
            ring_detents(outer_cage_od);
    }
}

module outer_section_2() {
    // Print orientation: collar at bottom on build plate, cage body above
    // Print height: joint_h + outer_section_h = 8 + 76.2 = 84.2 mm
    // Assembly height contribution: outer_section_h = 76.2 mm (collar overlaps section 1)
    union() {
        // Socket collar at bottom (on build plate when printing)
        // In assembly this wraps DOWN over section 1's top
        socket_collar(outer_cage_od);

        // Bridge platform connecting collar to cage body (wide, captures posts)
        collar_bridge(outer_cage_od, outer_boundary_radial, outer_boundary_height);

        // Cage body clipped to section 2 range
        // Shifted up by joint_h so it sits above the collar in print
        translate([0, 0, joint_h - outer_section_h])
            clip(outer_section_h, 2*outer_section_h) outer_cage_body();

        // top structural platform at section boundary
        translate([0, 0, joint_h + outer_section_h - outer_boundary_height])
            ring(outer_cage_od, outer_boundary_radial, outer_boundary_height);

        // detent bumps near the top for section 3's collar
        translate([0, 0, joint_h + outer_section_h - 2.0])
            ring_detents(outer_cage_od);
    }
}

module outer_section_3() {
    // Print height: joint_h + outer_section_h = 8 + 76.2 = 84.2 mm
    union() {
        // Socket collar at bottom
        socket_collar(outer_cage_od);

        // Bridge platform connecting collar to cage body (wide, captures posts)
        collar_bridge(outer_cage_od, outer_boundary_radial, outer_boundary_height);

        // Cage body clipped to section 3 range
        translate([0, 0, joint_h - 2*outer_section_h])
            clip(2*outer_section_h, outer_cage_height) outer_cage_body();

        // Top structural ring + snap lip for lid
        translate([0, 0, joint_h + outer_section_h - outer_ring_height]) {
            ring(outer_cage_od, outer_ring_radial, outer_ring_height);
            translate([0, 0, outer_ring_height - outer_snap_lip_h])
                difference() {
                    cylinder(d = outer_cage_od + 0.8, h = outer_snap_lip_h);
                    cylinder(d = outer_cage_od - 2*outer_ring_radial,
                             h = outer_snap_lip_h + 0.1);
                }
        }
    }
}


// ============================================================
//  INNER CAGE SECTIONS
// ============================================================

module inner_section_1() {
    union() {
        // foot ring (sits in base groove)
        difference() {
            cylinder(d = inner_seat_od - 0.4, h = inner_seat_depth);
            translate([0, 0, -0.1])
                cylinder(d = inner_seat_id + 0.4, h = inner_seat_depth + 0.2);
        }
        // bottom structural platform (wide, captures posts)
        translate([0, 0, inner_seat_depth])
            ring(inner_cage_bottom_od, inner_boundary_radial, inner_boundary_height);
        clip(0, inner_section_h) inner_cage_body();
        // top structural platform at section boundary
        translate([0, 0, inner_section_h - inner_boundary_height])
            ring(inner_cage_top_od, inner_boundary_radial, inner_boundary_height);
        translate([0, 0, inner_section_h - 2.0])
            ring_detents(inner_cage_top_od);
    }
}

module inner_section_2() {
    union() {
        socket_collar(inner_cage_top_od);
        collar_bridge(inner_cage_top_od, inner_boundary_radial, inner_boundary_height);
        translate([0, 0, joint_h - inner_section_h])
            clip(inner_section_h, 2*inner_section_h) inner_cage_body();
        // top structural platform at section boundary
        translate([0, 0, joint_h + inner_section_h - inner_boundary_height])
            ring(inner_cage_top_od, inner_boundary_radial, inner_boundary_height);
        translate([0, 0, joint_h + inner_section_h - 2.0])
            ring_detents(inner_cage_top_od);
    }
}

module inner_section_3() {
    union() {
        socket_collar(inner_cage_top_od);
        collar_bridge(inner_cage_top_od, inner_boundary_radial, inner_boundary_height);
        translate([0, 0, joint_h - 2*inner_section_h])
            clip(2*inner_section_h, inner_cage_height) inner_cage_body();
        // top structural platform
        translate([0, 0, joint_h + inner_section_h - inner_boundary_height])
            ring(inner_cage_top_od, inner_boundary_radial, inner_boundary_height);
    }
}


// ============================================================
//  BASE
// ============================================================

module base_part() {
    difference() {
        cylinder(d = base_od, h = base_t);
        translate([0, 0, -0.1])
            cylinder(d = center_opening_d, h = base_t + 0.2);
        translate([0, 0, -0.1])
            difference() {
                cylinder(d = bearing_od, h = bearing_seat_depth + 0.1);
                translate([0, 0, -0.1])
                    cylinder(d = bearing_bore_d, h = bearing_seat_depth + 0.3);
            }
        // outer cage seat groove
        translate([0, 0, base_t - outer_seat_depth])
            difference() {
                cylinder(d = outer_seat_od, h = outer_seat_depth + 0.1);
                cylinder(d = outer_seat_id, h = outer_seat_depth + 0.1);
            }
        // inner cage seat groove
        translate([0, 0, base_t - inner_seat_depth])
            difference() {
                cylinder(d = inner_seat_od, h = inner_seat_depth + 0.1);
                cylinder(d = inner_seat_id, h = inner_seat_depth + 0.1);
            }
        for (a = [30, 150, 270]) {
            rotate([0, 0, a])
                translate([base_od/2 - 10, 0, -0.1])
                    cylinder(d = 4.2, h = base_t + 0.2);
        }
    }
}

module floating_disk() {
    union() {
        difference() {
            cylinder(d = disk_od, h = disk_t);
            translate([0, 0, -0.1])
                cylinder(d = disk_id, h = disk_t + 0.2);
        }
        translate([disk_od/2 - 2, -disk_tab_w/2, 0])
            cube([disk_tab_l, disk_tab_w, disk_tab_t]);
    }
}

module lid_part() {
    difference() {
        union() {
            cylinder(d = lid_top_d, h = lid_top_t);
            translate([0, 0, -lid_skirt_depth])
                difference() {
                    cylinder(d = lid_skirt_od, h = lid_skirt_depth);
                    translate([0, 0, -0.1])
                        cylinder(d = lid_skirt_id, h = lid_skirt_depth + 0.2);
                }
            for (i = [0 : snap_count - 1]) {
                a = i * 360 / snap_count;
                rotate([0, 0, a])
                    translate([lid_skirt_id/2 - snap_depth, -snap_w/2,
                               -lid_skirt_depth + 2.0])
                        cube([snap_depth, snap_w, snap_h]);
            }
        }
        translate([0, 0, -0.1])
            cylinder(d = lid_inner_recess_id, h = lid_inner_recess_depth + 0.1);
        translate([0, 0, -lid_skirt_depth - 0.1])
            cylinder(d = lid_center_hole_d, h = lid_top_t + lid_skirt_depth + 0.2);
    }
}


// ============================================================
//  ASSEMBLY
// ============================================================

module assembly() {
    if (show_base)
        color([0.55, 0.85, 0.65, 1.0])
            base_part();

    if (show_outer_cage) {
        oz = base_t - outer_seat_depth;
        if (show_outer_section == 0 || show_outer_section == 1)
            color([0.45, 0.80, 0.58, 1.0])
                translate([0, 0, oz])
                    outer_section_1();

        // Section 2: cage body starts at outer_section_h in assembly.
        // In the module, cage body starts at z = joint_h.
        // So place it at: oz + outer_section_h - joint_h
        // (the collar extends from oz+outer_section_h-joint_h down to
        //  oz+outer_section_h-joint_h, overlapping section 1's top)
        if (show_outer_section == 0 || show_outer_section == 2)
            color([0.40, 0.75, 0.53, 1.0])
                translate([0, 0, oz + outer_section_h - joint_h])
                    outer_section_2();

        if (show_outer_section == 0 || show_outer_section == 3)
            color([0.35, 0.70, 0.48, 1.0])
                translate([0, 0, oz + 2*outer_section_h - joint_h])
                    outer_section_3();
    }

    if (show_inner_cage) {
        iz = base_t - inner_seat_depth;
        if (show_inner_section == 0 || show_inner_section == 1)
            color([0.15, 0.35, 0.15, 0.55])
                translate([0, 0, iz])
                    inner_section_1();
        if (show_inner_section == 0 || show_inner_section == 2)
            color([0.20, 0.40, 0.20, 0.55])
                translate([0, 0, iz + inner_section_h - joint_h])
                    inner_section_2();
        if (show_inner_section == 0 || show_inner_section == 3)
            color([0.25, 0.45, 0.25, 0.55])
                translate([0, 0, iz + 2*inner_section_h - joint_h])
                    inner_section_3();
    }

    if (show_disk)
        color([0.25, 0.55, 0.88, 1.0])
            translate([0, 0, 95])
                floating_disk();

    if (show_lid)
        color([0.55, 0.85, 0.65, 0.95])
            translate([0, 0, base_t - outer_seat_depth + outer_cage_height])
                lid_part();
}


// ============================================================
//  PRINT LAYOUT
// ============================================================

module print_layout() {
    translate([-180, 0, 0])   base_part();
    translate([0, 0, lid_skirt_depth])
        rotate([180, 0, 0])   lid_part();
    translate([180, 0, 0])    floating_disk();

    translate([-180, -180, 0]) outer_section_1();
    translate([0, -180, 0])    outer_section_2();
    translate([180, -180, 0])  outer_section_3();

    translate([-180, -360, 0]) inner_section_1();
    translate([0, -360, 0])    inner_section_2();
    translate([180, -360, 0])  inner_section_3();
}

if (show_print_layout)
    print_layout();
else
    assembly();
