// ==========================================
// PRINT FILE: Floor Mounting Flange v2
// ==========================================
// Flat flange that sits on the floor.
// Sleeve sits on top — centering lip goes INSIDE
// the sleeve so nothing exceeds the 75mm sleeve OD.
// Capsule slides over sleeve with no interference.
//
// Assembly order:
//   1. Screw flange to floor (or attach to sleeve first)
//   2. Set sleeve onto flange — centering lip registers it
//   3. Epoxy sleeve to flange at the joint
// ==========================================

$fn = 120;

// --- Sleeve dimensions ---
sleeve_od       = 75;       // outer sleeve OD
sleeve_id       = 69;       // outer sleeve inner diameter

// --- Flange dimensions ---
flange_od       = 110;      // wide base for floor screws
flange_h        = 6;        // base flange thickness

// --- Centering lip (goes INSIDE sleeve bottom) ---
lip_od          = sleeve_id - 0.5;  // 68.5mm — snug inside 69mm sleeve bore
lip_h           = 8;        // 8mm lip for good registration

// --- Center opening for cables/airflow ---
center_bore     = 53;       // matches core inner diameter for airflow

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

            // Centering lip — goes UP inside the sleeve
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
