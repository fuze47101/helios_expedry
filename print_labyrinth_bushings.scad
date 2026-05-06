$fn = 120;

// ==========================================
// PRINT FILE: Floor Bushings (3x)
// ==========================================
// Press-fit into 12mm drilled floor holes.
// Solid flange on top blocks moisture from above.
// Drip skirt below sheds any moisture that creeps through.
// All connected — no floating geometry, no supports needed.
//
// Prints flange-down on bed. 100% infill — small solid parts.
// ==========================================

// Parameters
bushing_press_od   = 12.0;       // press-fit into 12mm drilled hole
bushing_bore       = 8.5;        // 0.25mm clearance to 8mm post
floor_thickness    = 2.5;

// Press-fit section (sits in floor hole)
press_fit_h        = floor_thickness + 1.0;  // 3.5mm — spans floor + slight proud

// Top flange — wide solid disc that sits on the floor surface
// Overlaps the hole by 4mm per side = 20mm OD over a 12mm hole
flange_od          = 20.0;
flange_h           = 2.0;        // 2mm thick solid cap

// Drip collar below floor — tapered cone sheds moisture outward
drip_od            = 18.0;       // slightly wider than press-fit
drip_h             = 5.0;        // hangs 5mm below floor

module floor_bushing() {
    difference() {
        union() {
            // Top flange (prints on bed — this face goes UP against floor)
            cylinder(d = flange_od, h = flange_h);

            // Press-fit tube (goes through floor hole)
            translate([0, 0, flange_h])
                cylinder(d = bushing_press_od, h = press_fit_h);

            // Drip collar below floor (tapered — wide at floor, narrow at tip)
            translate([0, 0, flange_h + press_fit_h])
                cylinder(d1 = drip_od, d2 = bushing_press_od, h = drip_h);
        }

        // Bore through entire part for the post
        translate([0, 0, -0.1])
            cylinder(d = bushing_bore, h = flange_h + press_fit_h + drip_h + 0.2);
    }
}

// 3 bushings spaced apart on the build plate
translate([-25, 0, 0]) floor_bushing();
translate([0, 0, 0])   floor_bushing();
translate([25, 0, 0])  floor_bushing();
