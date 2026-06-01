$fn = 120;

// ============================================================
// HELIOS — Load Cell Mounting Stand
// Material: Polycarbonate (PC) — straight, dry filament only
// Printer:  Bambu H2D, enclosed
// Date:     2026-05-11
// Rev:      V1
// ============================================================
// PURPOSE
//   Rigid pedestal that lifts the single-point bar load cell to
//   the correct Z so the live-end button receives the weighing
//   plate / scale-pan adapter from the upper chamber posts.
//
//   Per Andrew, 2026-05-11:
//     Overall:  6.5" L  ×  3" W  ×  4" H
//                165.1  ×  76.2 ×  101.6 mm
//     Structure: closed tube / hollow box — firm base, strong
//                walls, firm top.  Slicer-infill the interior
//                (gyroid 25–30%) or print with supports.
//     Alignment: shallow crosshair indent on the top face,
//                centered longitude AND latitude, for placing
//                the L-bracket dead-center.
// ============================================================
// PRINT SETTINGS (Bambu H2D + PC)
//   Nozzle 270 °C   |   Bed 100 °C   |   Chamber heater ON
//   Outer wall 30 mm/s, inner 50 mm/s, first layer 25 mm/s
//   Fan 0% layers 1–3, then 10–20%
//   Walls: 4   |   Top/Bottom: 5 layers
//   Infill: GYROID 25–30%  (this is the "lattice" — slicer fills the cavity)
//   Brim: 5 mm   |   Z-hop 0.4 mm
//   Filament must be DRY (PC absorbs moisture fast)
//
//   Orientation: print STANDING (101.6 mm tall as Z).  Top face
//   is a 165 × 76 mm bridge, but at 30% gyroid the infill carries
//   the top layers without supports.  If you'd rather, print on
//   its side (76 mm tall) and skip infill entirely — the crosshair
//   then prints as a vertical feature, which is fine on H2D.
// ============================================================

// === OUTER ENVELOPE (from Andrew) ===
stand_l        = 165.1;     // 6.5"
stand_w        = 76.2;      // 3.0"
stand_h        = 101.6;     // 4.0"

// === SHELL THICKNESS ===
// 1.5 kg load on a 165x76 mm footprint uses 0.014% of PC's compressive
// strength — 3 mm walls are massive overkill structurally but feel firm
// in the hand and print fast.  Drop wall_t to 2.0 if you want it even faster.
wall_t         = 3.0;       // side walls
top_t          = 3.0;       // top face (firm — load cell bracket bolts/sits here)
base_t         = 3.0;       // bottom face (firm — sits on lower bay floor)

// === ALIGNMENT CROSSHAIR ON TOP ===
cross_depth    = 1.0;       // shallow indent
cross_width    = 1.5;       // line width
cross_run_l    = stand_l - 10;   // longitudinal line (X): leaves 5mm margin each end
cross_run_w    = stand_w - 10;   // latitudinal line (Y):  leaves 5mm margin each side

// === OPTIONAL FLOOR-MOUNT THROUGH-HOLES ===
// Set true if you want bolt-down holes in the BASE only.
// (Top stays solid so the L-bracket gets a clean firm surface.)
use_floor_holes = false;
floor_hole_d    = 5.2;      // M5 clearance
floor_hole_inset = 12.0;    // from corner

// ============================================================
// MATH / VERIFICATION
// ============================================================
echo("");
echo("=========================================");
echo("HELIOS LOAD CELL STAND — V1");
echo("=========================================");
echo("Envelope (mm) :", stand_l, " x ", stand_w, " x ", stand_h);
echo("Envelope (in) :", stand_l/25.4, " x ", stand_w/25.4, " x ", stand_h/25.4);
echo("Wall t        :", wall_t, " mm");
echo("Top/Base t    :", top_t, " /", base_t, " mm");
echo("Internal cavity :", stand_l - 2*wall_t, " x ", stand_w - 2*wall_t, " x ", stand_h - top_t - base_t);
echo("Crosshair: 1mm deep, 1.5mm wide, runs through center");
echo("=========================================");
echo("");

// ============================================================
// MODULE
// ============================================================
module load_cell_stand() {
    difference() {
        // ── solid outer envelope
        cube([stand_l, stand_w, stand_h]);

        // ── internal cavity (the "tube" — closed top, base, and walls)
        translate([wall_t, wall_t, base_t])
            cube([stand_l - 2*wall_t,
                  stand_w - 2*wall_t,
                  stand_h - top_t - base_t]);

        // ── alignment crosshair on the TOP face
        //    longitudinal line (along X)
        translate([(stand_l - cross_run_l)/2,
                   (stand_w - cross_width)/2,
                   stand_h - cross_depth])
            cube([cross_run_l, cross_width, cross_depth + 0.5]);

        //    latitudinal line (along Y)
        translate([(stand_l - cross_width)/2,
                   (stand_w - cross_run_w)/2,
                   stand_h - cross_depth])
            cube([cross_width, cross_run_w, cross_depth + 0.5]);

        // ── optional floor through-holes
        if (use_floor_holes) {
            for (xf = [floor_hole_inset, stand_l - floor_hole_inset]) {
                for (yf = [floor_hole_inset, stand_w - floor_hole_inset]) {
                    translate([xf, yf, -0.5])
                        cylinder(d=floor_hole_d, h=base_t + 1);
                }
            }
        }
    }
}

load_cell_stand();
