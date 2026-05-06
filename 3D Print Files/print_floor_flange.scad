// ==========================================
// PRINT FILE: Floor Mounting Flange v2
// ==========================================
// Flat flange that sits on the floor.
// Centering lip goes UP inside the inner core bore (53mm).
// Outer sleeve heat-presses down over the flange top.
//
// Assembly order:
//   1. Screw flange to floor
//   2. Drop inner core over the lip (registers center)
//   3. Heat sleeve bottom, press down over flange + core
// ==========================================

$fn = 120;

// --- Sleeve dimensions ---
sleeve_od       = 75;       // outer sleeve OD
sleeve_id       = 69;       // outer sleeve inner diameter

// --- Flange dimensions ---
flange_od       = 110;      // wide base for floor screws
flange_h        = 6;        // base flange thickness

// --- Centering lip (goes UP inside inner core bore) ---
lip_od          = 52;       // fits inside 53mm core ID (0.5mm clearance/side)
lip_h           = 8;        // 8mm lip for good registration

// --- Center opening for cables/airflow ---
center_bore     = 40;       // cable pass-through (smaller than lip for wall thickness)

// --- Floor screw holes ---
num_screws      = 4;
screw_d         = 5.5;      // M5 clearance
screw_circle_r  = 46;       // between sleeve edge and flange edge

// --- Countersink ---
countersink_d   = 10;
countersink_h   = 3;

module floor_flange() {
    difference() {
        union() {
            // Wide flat base — sits on floor
            cylinder(d = flange_od, h = flange_h);

            // Centering lip — goes up inside inner core bore
            translate([0, 0, flange_h])
                cylinder(d = lip_od, h = lip_h);
        }

        // Center bore — airflow and cable pass-through
        translate([0, 0, -0.1])
            cylinder(d = center_bore, h = flange_h + lip_h + 0.2);

        // Floor screw holes
        for (i = [0 : num_screws - 1]) {
            angle = i * (360 / num_screws) + 45;
            // Through hole
            translate([screw_circle_r * cos(angle),
                       screw_circle_r * sin(angle),
                       -0.1])
                cylinder(d = screw_d, h = flange_h + 0.2);

            // Countersink on bottom
            translate([screw_circle_r * cos(angle),
                       screw_circle_r * sin(angle),
                       -0.1])
                cylinder(d = countersink_d, h = countersink_h + 0.1);
        }
    }
}

// Print flat — lip pointing up
floor_flange();
