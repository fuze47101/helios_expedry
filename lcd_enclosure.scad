// ==========================================================
// HELIOS — Load Cell LCD/PCB Enclosure (Two-Piece Clamshell)
// Material: PC (PolyMax PC Tough Blue)
// Printer:  Bambu H2D
// Date:     2026-05-29
// ==========================================================
// CLAMSHELL: print FRONT half and BACK half separately,
// then screw together with 4× M3 corner screws into
// heat-set inserts in the BACK half.
// ==========================================================

// ----- TOP-LEVEL TOGGLES -----
PART = "both";       // "front" | "back" | "both" | "preview"
                     //   "both"    = side-by-side on build plate (PRINT THIS)
                     //   "preview" = stacked + exploded for visual check only
PLATE_GAP = 10.0;    // mm gap between halves on the build plate
EXPLODE   = 0;       // preview-only: pulls halves apart in Z

// ----- BRANDING (FUZE LOGO) -----
// Uses PURE OpenSCAD POLYGONS — no SVG import. Bypasses all OpenSCAD SVG quirks.
// Geometry generated from "FUZE Logo Horizontal (2).ai" by Python svgpathtools.
// File: fuze_logo_h.scad — Y already flipped so logo is right-side-up.
// Native size 55.4 × 17.0mm, center dot at (9.3496, 9.0193).
include <fuze_logo_h.scad>;        // pulls in fuze_logo_native() + constants

// Logo geometric-bbox CENTER in native mm. Anchor the logo by its CENTER
// (NOT the off-center symbol dot) so FUZE_LOGO_X/Y position the logo's middle.
FUZE_LOGO_CX_NATIVE = 27.6948;     // logo bbox center X (native pt) - regen 6-dot trace
FUZE_LOGO_CY_NATIVE = 8.5813;      // logo bbox center Y (native pt) - regen 6-dot trace

FUZE_LOGO_ENABLE  = true;
FUZE_LOGO_DEPTH   = 1.0;           // deboss depth
FUZE_LOGO_SCALE   = 1.9;           // 1.9x → 102mm x 30mm tall (fits the 105.4 face)
                                   // Andrew 2026-05-29: he wants it BIG

// Position of the logo's CENTER DOT in face coords
FUZE_LOGO_X       = 0.0;           // X offset of LOGO CENTER (0 = face center)
FUZE_LOGO_Y       = -32.7;         // Y offset of LOGO CENTER (below buttons, shorter face)

// Optional sacrificial bridge floor inside the deboss (for PC bridge safety)
FUZE_DEBOSS_SUPPORT   = false;    // OFF: deboss faces up in print; full 1mm pocket for white inlay
FUZE_DEBOSS_SUPPORT_T = 0.4;      // 2 layers @ 0.2mm
FUZE_DEBOSS_SUPPORT_Z = 0.4;      // distance from outer face to support floor

$fn = 96;

// ============================================================
// LOCKED SPECS (per Andrew + photos 2026-05-29)
// ============================================================
// MAIN LCD PCB (the big board with the LCD display)
PCB_W = 133.0;          // LCD PCB width
PCB_H = 41.0;           // LCD PCB height
PCB_T = 1.6;            // PCB thickness (std FR-4)

// LCD PCB mounting holes (4 corners on LCD PCB)
PCB_MNT_DX = 126.5;     // hole spacing long way (center-to-center)
PCB_MNT_DY = 33.0;      // hole spacing short way (center-to-center)
PCB_MNT_D  = 3.2;       // M3 clearance

// LCD visible window (centered laterally on front face)
LCD_W = 102.0;
LCD_H = 30.0;
LCD_TOP_INSET = 5.0;    // from top of front face to top of LCD window

// BUTTON STRIP — SEPARATE small PCB, not part of LCD board.
// Connected to LCD board by white ribbon cable.
// Holds 5 tactile switches in a row.
BTN_X = [-59, -37, 0, 37, 59];   // c-c measured directly from center button (Andrew)
BTN_ACTUATOR_D = 4.0;
BTN_HOLE_D     = 4.4;       // nominal (layout math only - feeds height/button-Y)
BTN_HOLE_CUT_D = 5.4;       // ACTUAL cut Ø: +1mm over nominal for assembly variance (Andrew)
BTN_STRIP_W    = 130.0;     // length of button strip PCB
BTN_STRIP_H    = 12.0;      // height of button strip PCB
BTN_STRIP_T    = 1.6;
BTN_BODY_H     = 4.0;       // tactile switch body height above PCB
BTN_GAP_FROM_LCD = 25.0;    // ≥20mm requested (gap from LCD bottom to button row)

// Button body recess pockets — 5× 6×6mm pockets cut from INSIDE the front
// wall at each button position. Button body slides into the pocket so only
// 1.5mm of wall remains at each button spot, giving ~1.9mm of actuator
// protrusion. Rest of front face stays 3mm for stiffness. Andrew 2026-05-29.
BTN_BODY_W      = 6.4;      // 6mm body + 0.4mm clearance
BTN_BODY_POCKET_SQ = 6.4;   // 6.4 x 6.4 mm square pocket
BTN_BODY_POCKET_D  = 1.5;   // pocket depth into front wall

// Back-face cutouts
// Rocker switch: KCD11-style snap-in, 18.5×11.5mm panel cutout
PWR_SWITCH_W = 11.5;        // narrow dim (X)
PWR_SWITCH_H = 18.5;        // tall dim (Y)

// DC barrel jack — simple round pass-through hole (not panel mount, not slide-in
// slot). Jack body passes through, wires pre-soldered, held by friction/epoxy
// or just routed through. Andrew 2026-05-29.
PWR_PLUG_HOLE_D = 11.0;      // Ø11mm round hole — fits standard 5.5/2.1 jack body

// RS232 DB9 panel cutout — proper panel-cutout spec (not connector-body spec)
// Per Norcomp/Conec/Amphenol DB9 panel mount drawings.
// The cutout is for the connector SHELL to pass through; the connector's
// flange sits OUTSIDE the cutout and the M3 screws go through the flange
// into the panel, OUTSIDE the trapezoid envelope.
RS232_BOTTOM_W = 15.90;    // DE-9 cutout wide edge  - NorComp C [15.90mm]
RS232_TOP_W    = 13.47;    // DE-9 cutout narrow edge - NorComp E [13.47mm], ~10deg sides
RS232_H        = 12.50;    // DE-9 cutout height      - NorComp D [12.50mm]
RS232_MNT_DX   = 24.99;    // DE-9 mounting holes c-c - NorComp A [24.99mm]
RS232_MNT_D    = 3.20;     // M3 clearance (NorComp screw hole Ø3.05)

// ============================================================
// ASSUMPTIONS / SIZING (override as needed)
// 2026-05-29: bumped up per Andrew — bigger for future hardware/sensors,
// fits 19×17×80mm battery + headroom for additional boards/wiring.
// ============================================================
WALL = 3.0;                 // shell wall thickness (was 2.5, bulked up)
INTERNAL_DEPTH = 100.0;     // was 25 → 40 → 100 per Andrew 2026-05-29
                            // Deep box — room for battery, future sensors,
                            // RS232 driver board, extra wiring, etc.
FRONT_HALF_DEPTH = 12.0;    // depth of front shell (LCD side)
BACK_HALF_DEPTH  = INTERNAL_DEPTH - FRONT_HALF_DEPTH + WALL;

// PCB standoff config — standoffs hang DOWN from inside-front-face into cavity.
// LCD module protrudes 7mm above PCB front face (per Andrew, measured).
// 3mm WALL + 4mm standoff = 7mm from outside to PCB front → LCD top FLUSH
// with outside surface of front face (Z = 0). Andrew 2026-05-29.
PCB_STANDOFF_H = 4.0;       // 4mm: LCD top flush with outside of front face
PCB_STANDOFF_OD = 8.0;      // OD of PCB standoff bosses

// Extra padding beyond minimum-PCB-fit
FRONT_MARGIN_X = 15.0;       // lateral room around PCB (was 6)
BOTTOM_PAD     = 35.0;       // extra Y space below button row for battery bay
                             // AND room for a proper-sized FUZE logo below buttons
                             // (was 35, bumped to 50 for logo headroom — Andrew 2026-05-29)

// Clamshell join screws (4 corners)
JOIN_SCREW_D    = 3.2;      // M3 clearance
JOIN_INSERT_D   = 4.2;      // heat-set insert OD (typical M3 brass insert)
JOIN_INSERT_H   = 5.0;      // insert depth
JOIN_BOSS_OD    = 8.0;
JOIN_INSET      = 6.0;      // distance from outer wall to screw centerline

// External mounting (to NEW FAB load cell carrier shelf, ~20"L × 7"W, slides
// into wine fridge as a removable shelf). Two mount-style options:
//   MOUNT_STYLE = "side_ears"  → bolt to a vertical face on the shelf
//   MOUNT_STYLE = "bottom_feet" → sits flat on top of the shelf, screws down
MOUNT_STYLE     = "none";  // "side_ears" | "bottom_feet" | "none"
                            // Andrew 2026-05-29: VHB tape for now, smooth sides

// Side ears (vertical-face mount)
EAR_W           = 18.0;     // extends out from side
EAR_H           = 18.0;
EAR_T           = 6.0;
EAR_SLOT_LEN    = 8.0;
EAR_SLOT_D      = 5.2;      // for M5

// Bottom feet (top-of-shelf mount) — 4 short standoffs on the bottom edge
// of the back half, with M4 through-holes for shelf bolts
FOOT_W          = 14.0;
FOOT_DEPTH      = 14.0;
FOOT_H          = 5.0;      // rise above main shell bottom (clearance for wires)
FOOT_HOLE_D     = 4.4;      // M4 clearance
FOOT_X_INSET    = 12.0;     // from outer edge of shell, X
FOOT_Y_PROJ     = 10.0;     // how far feet project beyond back-half bottom

// ============================================================
// DERIVED DIMENSIONS
// ============================================================
TOP_MARGIN     = LCD_TOP_INSET;
// (FRONT_MARGIN_X and BOTTOM_PAD now defined in ASSUMPTIONS section above)

// Front face inner usable height: LCD + gap + button row + bottom battery bay
FACE_INNER_H = LCD_H + BTN_GAP_FROM_LCD + BTN_HOLE_D + BOTTOM_PAD + TOP_MARGIN;
// Make sure PCB fits inside
FACE_INNER_H_MIN_PCB = PCB_H + 2*8;  // 8mm pad above/below PCB
FACE_INNER_H_FINAL = max(FACE_INNER_H, FACE_INNER_H_MIN_PCB);

INNER_W = PCB_W + 2*FRONT_MARGIN_X;
INNER_H = FACE_INNER_H_FINAL;

OUTER_W = INNER_W + 2*WALL;
OUTER_H = INNER_H + 2*WALL;

// PCB position inside enclosure (centered laterally, biased to top
// so LCD lines up with LCD window).
// LCD is NOT centered on the PCB — top mount hole is only 4mm from PCB
// top edge, so the LCD is positioned closer to the top of the PCB with
// MORE PCB area extending DOWN below it. PCB center is therefore lower
// than LCD center. Per Andrew 2026-05-29: 7mm offset.
LCD_CY_FROM_TOP = TOP_MARGIN + LCD_H/2;          // LCD center Y from inside top
PCB_LCD_OFFSET  = 7.0;                           // drops PCB to 27mm from top => 6.5mm top-edge clearance
PCB_CY_FROM_TOP = LCD_CY_FROM_TOP + PCB_LCD_OFFSET;
// → PCB top edge from inside top:
PCB_TOP_FROM_INSIDE_TOP = PCB_CY_FROM_TOP - PCB_H/2;

// Y positions (measured from inside top of front face, +Y = down)
LCD_Y_TOP    = TOP_MARGIN;
LCD_Y_BOTTOM = TOP_MARGIN + LCD_H;
BTN_Y        = LCD_Y_BOTTOM + BTN_GAP_FROM_LCD + BTN_HOLE_D/2;

// Convert to "from center of face" coordinates for cutting
function y_from_center(y_from_top) = INNER_H/2 - y_from_top;
LCD_CY = y_from_center(PCB_CY_FROM_TOP);   // window CENTERED on PCB (glass is centered on PCB: 5.5mm margins, Andrew measured)
BTN_CY = y_from_center(BTN_Y);

// PCB origin in shell coords (centered laterally; offset vertically)
PCB_OFFSET_Y = y_from_center(PCB_CY_FROM_TOP);

// ============================================================
// MODULES
// ============================================================

// rounded rectangle prism
module rrect(w, h, t, r=2) {
    hull() {
        for (sx=[-1,1], sy=[-1,1])
            translate([sx*(w/2 - r), sy*(h/2 - r), 0])
                cylinder(h=t, r=r);
    }
}

// rounded slot
module slot(len, d, t) {
    hull() {
        translate([-len/2, 0, 0]) cylinder(h=t, d=d);
        translate([ len/2, 0, 0]) cylinder(h=t, d=d);
    }
}

// ============================================================
// FUZE LOGO — 2D shape using pure OpenSCAD polygons (no SVG import).
// Output: logo with inner-dot center at SCAD origin (0,0), right-side-up.
// ============================================================
module fuze_logo_2d() {
    scale([FUZE_LOGO_SCALE, FUZE_LOGO_SCALE])
        translate([-FUZE_LOGO_CX_NATIVE, -FUZE_LOGO_CY_NATIVE])  // center-anchored
            fuze_logo_native();
}

// DB9 trapezoidal D-shape panel cutout (proper spec, not a rectangle)
module db9_dshape(t) {
    linear_extrude(height = t)
        polygon([
            [-RS232_BOTTOM_W/2, -RS232_H/2],
            [ RS232_BOTTOM_W/2, -RS232_H/2],
            [ RS232_TOP_W/2,     RS232_H/2],
            [-RS232_TOP_W/2,     RS232_H/2]
        ]);
}

// corner positions for clamshell screws + external mounting
module corner_positions() {
    for (sx=[-1,1], sy=[-1,1])
        translate([sx*(OUTER_W/2 - JOIN_INSET),
                   sy*(OUTER_H/2 - JOIN_INSET), 0])
            children();
}

// LCD PCB mount positions (laterally centered; PCB centered at PCB_OFFSET_Y)
module pcb_mount_positions() {
    for (sx=[-1,1], sy=[-1,1])
        translate([sx*PCB_MNT_DX/2,
                   PCB_OFFSET_Y + sy*PCB_MNT_DY/2, 0])
            children();
}

// Button strip slide-in rail positions (two rails on left/right that capture
// the strip PCB top + bottom edges). Strip is centered on BTN_CY.
BTN_STRIP_CY = BTN_CY;  // strip PCB Y center = button row Y
module btn_strip_rail_positions() {
    // two side rails capture the strip PCB
    for (sx = [-1, 1])
        translate([sx * (BTN_STRIP_W/2 + 1.0), BTN_STRIP_CY, 0])
            children();
}

// ============================================================
// FRONT HALF (LCD window + button holes facing user)
// ============================================================
module front_half() {
    difference() {
        union() {
            // outer shell
            rrect(OUTER_W, OUTER_H, FRONT_HALF_DEPTH, r=4);
            // join lip (extends down to mate with back half)
            translate([0,0,FRONT_HALF_DEPTH])
                difference() {
                    rrect(OUTER_W - 2*WALL + 0.4, OUTER_H - 2*WALL + 0.4, 3, r=3);
                    translate([0,0,-0.1])
                        rrect(OUTER_W - 2*WALL - 2.0, OUTER_H - 2*WALL - 2.0, 4, r=2);
                }
        }

        // hollow inside
        translate([0,0,WALL])
            rrect(INNER_W, INNER_H, FRONT_HALF_DEPTH+5, r=3);

        // LCD window
        translate([0, LCD_CY, -1])
            rrect(LCD_W, LCD_H, WALL+2, r=2);

        // Button actuator pass-through holes (Ø4.4mm through full wall)
        for (x = BTN_X)
            translate([x, BTN_CY, -1])
                cylinder(h=WALL+2, d=BTN_HOLE_CUT_D);

        // Button body recess pockets — 6.4×6.4mm × 1.5mm deep, cut from
        // INSIDE of front wall (from Z=1.5 to past Z=3 for clean subtraction).
        // Button body sits in pocket, only 1.5mm of wall above the actuator.
        for (x = BTN_X)
            translate([x - BTN_BODY_POCKET_SQ/2,
                       BTN_CY - BTN_BODY_POCKET_SQ/2,
                       WALL - BTN_BODY_POCKET_D])
                cube([BTN_BODY_POCKET_SQ,
                      BTN_BODY_POCKET_SQ,
                      BTN_BODY_POCKET_D + 0.5]);

        // FUZE LOGO DEBOSS — recess on OUTSIDE of front face, 1mm deep.
        // Horizontal logo (symbol on left, FUZE text on right).
        // Position: (FUZE_LOGO_X, FUZE_LOGO_Y) = where the LOGO CENTER lands.
        // Mirrored in X so logo reads correctly from outside.
        if (FUZE_LOGO_ENABLE) {
            translate([FUZE_LOGO_X, FUZE_LOGO_Y, -0.01])
                linear_extrude(height = FUZE_LOGO_DEPTH + 0.02)
                    mirror([1, 0, 0])
                        fuze_logo_2d();
        }

        // Clamshell join screw clearance (through front)
        corner_positions()
            translate([0,0,-1])
                cylinder(h=FRONT_HALF_DEPTH+2, d=JOIN_SCREW_D);

        // Countersink for join screws on front face
        corner_positions()
            translate([0,0,-0.01])
                cylinder(h=2.0, d1=JOIN_SCREW_D+3, d2=JOIN_SCREW_D);
    }

    // OPTIONAL SACRIFICIAL BRIDGE FLOOR inside the FUZE deboss.
    // Adds a thin 0.4mm-thick floor of plastic inside the debossed area,
    // sitting 0.4mm above the outside surface. Helps PC bridge cleanly.
    if (FUZE_LOGO_ENABLE && FUZE_DEBOSS_SUPPORT) {
        translate([FUZE_LOGO_X, FUZE_LOGO_Y, FUZE_DEBOSS_SUPPORT_Z])
            linear_extrude(height = FUZE_DEBOSS_SUPPORT_T)
                mirror([1, 0, 0])
                    fuze_logo_2d();
    }

    // PCB STANDOFFS — hang DOWN from inside of front face into the cavity.
    // PCB seats on the cavity end of the standoffs with its FRONT face
    // (LCD-module side) toward the window. LCD module pokes through the
    // window cutout. Screws come from the cavity (back) side of the PCB
    // into M3 heat-set inserts installed at the cavity end of each standoff.
    difference() {
        // 4 solid standoff bosses surrounding the LCD window cutout
        translate([0,0,WALL])
            pcb_mount_positions()
                cylinder(h=PCB_STANDOFF_H, d=PCB_STANDOFF_OD);
        // M3 heat-set insert pocket at the cavity end of each standoff
        translate([0,0,WALL + PCB_STANDOFF_H - JOIN_INSERT_H])
            pcb_mount_positions()
                cylinder(h=JOIN_INSERT_H + 0.1, d=JOIN_INSERT_D);
    }

    // Mounting features (side ears, bottom feet, or none)
    mounting_features();
}

// ============================================================
// BACK HALF (PCB seat + power cutouts + heat-set bosses)
// ============================================================
module back_half() {
    // STEP 1: hollow shell (no standoffs/bosses inside the union — they get
    // carved by the hollow). Standoffs added AFTER as separate solids.
    difference() {
        rrect(OUTER_W, OUTER_H, BACK_HALF_DEPTH, r=4);

        // Hollow inside
        translate([0,0,WALL])
            rrect(INNER_W, INNER_H, BACK_HALF_DEPTH+5, r=3);

        // Mating recess for front half join lip
        translate([0,0,BACK_HALF_DEPTH - 3])
            rrect(OUTER_W - 2*WALL + 0.5, OUTER_H - 2*WALL + 0.5, 3.2, r=3);

        // ---- BACK-FACE CUTOUTS ----
        // Both on the back wall, lower portion. Orientation: tall.
        // Rocker switch on right, DC barrel jack on left.

        // Rocker switch panel cutout (KCD11-style snap-in)
        // Center cube at Z=WALL/2 so it cuts cleanly from below floor to
        // above wall (full through-hole).
        translate([OUTER_W/4, -OUTER_H/4, WALL/2])
            cube([PWR_SWITCH_W, PWR_SWITCH_H, WALL+4], center=true);

        // DC barrel jack — simple round pass-through hole
        translate([-OUTER_W/4, -OUTER_H/4, -1])
            cylinder(h=WALL+2, d=PWR_PLUG_HOLE_D);

        // RS232 DB9 panel cutout — proper trapezoidal D-shape (DIN 41652)
        // Centered laterally, upper portion of back face. Wide end DOWN
        // (matches connector orientation — pins 1-5 on bottom row).
        translate([0, OUTER_H/4, -1])
            db9_dshape(WALL+2);
        // RS232 mounting screw holes (2× M3, horizontal axis through center)
        for (sx = [-1, 1])
            translate([sx*RS232_MNT_DX/2, OUTER_H/4, -1])
                cylinder(h=WALL+2, d=RS232_MNT_D);
    }

    // PCB standoffs are NOT in the back half — they belong on the FRONT half,
    // descending from inside-front-face. See front_half() module.

    // STEP 2: Clamshell corner bosses — full-height columns at corners,
    // with insert pocket at TOP for M3 screws coming from front half
    difference() {
        translate([0,0,WALL])
            corner_positions()
                cylinder(h=BACK_HALF_DEPTH - WALL, d=JOIN_BOSS_OD);
        // heat-set insert pocket at top of each boss
        translate([0,0,BACK_HALF_DEPTH - JOIN_INSERT_H])
            corner_positions()
                cylinder(h=JOIN_INSERT_H+0.1, d=JOIN_INSERT_D);
    }

    // Button strip retention rails (on inside of back half)
    // Two vertical rails capture the strip PCB ends — slide-in from one side
    translate([0, 0, WALL])
        btn_strip_rail_positions()
            difference() {
                // outer rail post
                cube([4, BTN_STRIP_H + 4, 6], center=true);
                // slot to catch PCB
                translate([0,0,1])
                    cube([2, BTN_STRIP_H + 0.4, 7], center=true);
            }

    // (back-stop bar removed 2026-05-29 per Andrew — rails grip the strip fine)

    // Mounting features (side ears or bottom feet)
    mounting_features();
}

// ============================================================
// MOUNTING FEATURES (to load cell carrier shelf)
// ============================================================
// Side ears — bolt to a VERTICAL face on the shelf
module ears_block() {
    for (sx = [-1, 1])
        translate([sx*(OUTER_W/2 + EAR_W/2 - 0.1), 0, 0])
            difference() {
                rrect(EAR_W, EAR_H, EAR_T, r=3);
                // slotted M5 hole
                rotate([0,0,90])
                    slot(EAR_SLOT_LEN, EAR_SLOT_D, EAR_T+2);
            }
}

// Bottom feet — sits FLAT on top of the shelf, M4 screws down through feet.
// Feet project forward (toward viewer in back-half print orientation) so
// they don't interfere with the clamshell seam.
module feet_block() {
    for (sx = [-1, 1])
        translate([sx * (OUTER_W/2 - FOOT_X_INSET - FOOT_W/2),
                   -OUTER_H/2 - FOOT_Y_PROJ/2 + 1, 0])
            difference() {
                rrect(FOOT_W, FOOT_DEPTH + FOOT_Y_PROJ, FOOT_H, r=2);
                translate([0, -FOOT_Y_PROJ/2, -1])
                    cylinder(h=FOOT_H+2, d=FOOT_HOLE_D);
            }
    // Mirror to back side (so 4 total feet, one at each corner of footprint)
    for (sx = [-1, 1])
        translate([sx * (OUTER_W/2 - FOOT_X_INSET - FOOT_W/2),
                   OUTER_H/2 + FOOT_Y_PROJ/2 - 1, 0])
            difference() {
                rrect(FOOT_W, FOOT_DEPTH + FOOT_Y_PROJ, FOOT_H, r=2);
                translate([0, FOOT_Y_PROJ/2, -1])
                    cylinder(h=FOOT_H+2, d=FOOT_HOLE_D);
            }
}

module mounting_features() {
    if (MOUNT_STYLE == "side_ears")  ears_block();
    if (MOUNT_STYLE == "bottom_feet") feet_block();
}

// ============================================================
// PREVIEW / EXPORT
// ============================================================
if (PART == "front") {
    // Single half — print front lying open-side-down (LCD face on bed)
    front_half();
} else if (PART == "back") {
    // Single half — print back lying open-side-up (back wall on bed)
    back_half();
} else if (PART == "preview") {
    // Visual preview only — DO NOT SLICE THIS. Halves stacked + exploded.
    translate([0,0, EXPLODE + BACK_HALF_DEPTH]) front_half();
    back_half();
} else {
    // "both" — side-by-side on build plate, ready to slice in one job
    translate([-(OUTER_W + PLATE_GAP)/2, 0, 0])
        back_half();
    translate([ (OUTER_W + PLATE_GAP)/2, 0, 0])
        front_half();
}

// ============================================================
// PRINT NOTES
// ============================================================
// FRONT HALF: print open side DOWN on bed (LCD window face up).
//   Use 3 perimeters, 25% infill, 0.2mm layer, supports OFF.
//
// BACK HALF: print open side UP (back wall on bed).
//   Use 3 perimeters, 25% infill, 0.2mm layer, supports OFF.
//   Heat-set inserts go into the corner bosses and PCB standoffs
//   AFTER print using a soldering iron at 220-240°C for PC.
//
// PC TOUGH BLUE BAMBU H2D SETTINGS:
//   Bed: 100°C, Nozzle: 270°C, fan 0% first layer / 30% after.
//   Enclosure preheat recommended for PC adhesion.
//   Brim 8mm for the back half (large flat footprint).
//
// ASSEMBLY:
//   1. Heat-set 4× M3 inserts into back-half corner bosses (for clamshell screws)
//   2. Heat-set 4× M3 inserts into back-half PCB standoffs (for LCD PCB)
//   3. Snap KCD11 rocker switch into back-face switch cutout (clips lock it)
//   4. Run DC barrel jack wires through Ø11mm round hole (jack body is loose
//      inside — held by harness routing or dab of epoxy if you want it locked)
//   5. Mount LCD PCB onto standoffs with 4× M3×6 screws
//   6. Slide button strip PCB into the side retention rails (button bodies
//      facing front), so the actuator posts line up with the front face holes
//   7. Wire battery → switch → DC jack → LCD board → button strip per existing harness
//   8. Mate front half over back, drive 4× M3×12 screws from front
//   9. Bolt side ears to load cell frame with 2× M5
//
// NOTES FROM PHOTOS (2026-05-29):
// - Button strip is a SEPARATE PCB connected to LCD board by white ribbon cable
// - Rocker switch is KCD11-style snap-in (no extra screws needed)
// - DC barrel jack has a square flange ~15×17mm, body is round through-hole
