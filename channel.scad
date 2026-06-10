// =====================================================================
// FUZE / Helios — Down Sandwich Test Frame  (V3 clamshell, 2026-06-04)
// Two separate halves, NO printed hinge. Lift the lid right off to lay an
// even layer of free-form down in the tray; set the lid back (a perimeter
// spigot self-aligns it) and clamp with 4 corner screws. Mesh on BOTH outer
// faces. Hangs vertically: a top rail slides into a side-loading C-channel.
//
//   PART = "tray"    -> deep half (10 mm down cavity)        [print 1]
//   PART = "lid"     -> mesh lid half                        [print 1]
//   PART = "channel" -> side-loading C-channel (load cell)   [print 1]
//   PART = "both"    -> tray + lid + channel preview
//
// Material: PC (PETG later). Print each half FLAT, mesh-face DOWN.
// MESH: pause-embed at layer 8 = Z 1.5 mm @ 0.2 mm layers (both halves).
// =====================================================================

PART = "channel";
$fn = 48;

SIZE     = 250;     // outer square (mm)
WALL     = 4;       // frame wall thickness
CAV      = 10;      // down cavity depth (tray)
FLOOR_H  = 3.0;     // mesh-support rib plane (1.5 backing + 1.5 cap, mesh @ layer 8)
RIB_W    = 2.0;     // rib width
CELLS    = 4;       // NxN support-rib cells
CLR      = 0.4;     // fit clearance

TRAY_T = FLOOR_H + CAV;   // tray wall height (13)
LID_RIM = 5.0;            // lid wall height
LID_T   = FLOOR_H + LID_RIM;

// registration spigot (drops into the tray cavity mouth to self-align the lid)
SPIG_T   = 2.0;     // spigot wall thickness
SPIG_H   = 4.0;     // how far it drops into the tray

// corner closure screws (M3)
SCREW_CLR = 3.4;    // clearance hole (lid)
INSERT_D  = 4.2;    // M3 heat-set insert bore (tray)
INSERT_H  = 6.0;
BOSS_D    = 9;
INSET     = BOSS_D/2 + 2;   // boss center inset from the corner

// top hang tab (flat, in the plane of the frame, sticks OUT past the top edge so
// it never conflicts with the lid) + side-loading C-channel that grips the tab.
RAIL_LEN = 150;   // tab width along the top edge (X)
RAIL_OUT = 16;    // how far the tab sticks out past the top edge (Y)
RAIL_T   = 6;     // tab thickness (Z) — what the channel grips
CH_CLR = 0.5; CH_WALL = 3; CH_LEN = RAIL_LEN + 30;
// locking pins: 2 holes through channel-lip + tab + channel-lip; drop M3 screws/pins
LOCK_D    = 3.4;          // M3 clearance / 3 mm pin
LOCK_SP   = 90;           // spacing between the 2 lock holes
LOCK_Y    = RAIL_OUT/2;   // depth into the tab where the holes sit

WIN = SIZE - 2*WALL;
EPS = 0.01;

// ---------------------------------------------------------------
module sq(s,h){ cube([s,s,h]); }

module rib_grid(h){
    step = WIN/CELLS;
    intersection(){
        union(){
            for(i=[0:CELLS]) translate([i*step-RIB_W/2,0,0]) cube([RIB_W,WIN,h]);
            for(j=[0:CELLS]) translate([0,j*step-RIB_W/2,0]) cube([WIN,RIB_W,h]);
        }
        cube([WIN,WIN,h]);
    }
}
module ring(h){ difference(){ sq(SIZE,h); translate([WALL,WALL,-EPS]) sq(WIN,h+2*EPS);} }

// 4 corner positions
function corners() = [[INSET,INSET],[SIZE-INSET,INSET],[INSET,SIZE-INSET],[SIZE-INSET,SIZE-INSET]];

module tray_bosses(){          // bosses with heat-set insert bores
    for(c=corners()) translate([c[0],c[1],0])
        difference(){ cylinder(d=BOSS_D,h=TRAY_T); translate([0,0,TRAY_T-INSERT_H]) cylinder(d=INSERT_D,h=INSERT_H+EPS,$fn=24); }
}
module lid_bosses(){           // bosses with screw clearance + counterbore
    for(c=corners()) translate([c[0],c[1],0])
        difference(){ cylinder(d=BOSS_D,h=LID_T); translate([0,0,-EPS]) cylinder(d=SCREW_CLR,h=LID_T+2*EPS,$fn=24);
                      translate([0,0,LID_T-2.5]) cylinder(d=6,h=3,$fn=24); }
}
// registration spigot ring on the lid (fits inside the tray cavity mouth)
module spigot(){
    o = WALL + CLR;                       // sits just inside the tray inner wall
    translate([o,o,LID_T-EPS])
        difference(){
            sq(SIZE-2*o, SPIG_H+EPS);
            translate([SPIG_T,SPIG_T,-EPS]) sq(SIZE-2*o-2*SPIG_T, SPIG_H+3*EPS);
        }
}

// Flat hang tab: a plate sticking OUT past the top edge (+Y), thickness in Z.
// Sits at the top of the tray wall so the lid (which stacks in +Z) clears it.
module hang_tab(){
    difference(){
        translate([(SIZE-RAIL_LEN)/2, SIZE-EPS, TRAY_T-RAIL_T])
            cube([RAIL_LEN, RAIL_OUT+EPS, RAIL_T]);
        for(sx=[SIZE/2-LOCK_SP/2, SIZE/2+LOCK_SP/2])
            translate([sx, SIZE+LOCK_Y, TRAY_T-RAIL_T-EPS]) cylinder(d=LOCK_D, h=RAIL_T+2*EPS, $fn=24);
    }
}
// C-channel grips the tab top+bottom (Z) and the back (Y); the tab slides in from
// one X end to an end-stop; the front (toward the frame) is open so the neck passes.
module c_channel(){
    slotY = RAIL_OUT + CH_CLR;            // tab depth into the channel (Y)
    slotZ = RAIL_T + CH_CLR;              // tab thickness (Z)
    outerY = slotY + CH_WALL;             // back wall
    outerZ = slotZ + 2*CH_WALL;           // top + bottom lips
    difference(){
        cube([CH_LEN, outerY, outerZ]);
        // pocket: open at X=0 (insert) and at Y=0 (front, frame neck passes); far X end = stop
        translate([-EPS, -EPS, CH_WALL]) cube([CH_LEN-CH_WALL, slotY, slotZ]);
        // mount holes on the back flange to bolt onto the inverted load cell
        for(x=[CH_LEN*0.3,CH_LEN*0.7]) translate([x, outerY+EPS, outerZ/2]) rotate([90,0,0]) cylinder(d=4.3,h=CH_WALL+2*EPS,$fn=24);
        // LOCK holes: vertical, through top lip + tab + bottom lip, aligned when the
        // tab is fully seated against the end-stop. Drop in 2 M3 screws/pins to lock.
        for(sx=[(CH_LEN-CH_WALL)-RAIL_LEN/2 - LOCK_SP/2, (CH_LEN-CH_WALL)-RAIL_LEN/2 + LOCK_SP/2])
            translate([sx, LOCK_Y, -EPS]) cylinder(d=LOCK_D, h=outerZ+2*EPS, $fn=24);
    }
}

// ---------------- HALVES ----------------
module tray_half(){
    union(){
        translate([WALL,WALL,0]) rib_grid(FLOOR_H);
        ring(TRAY_T);
        tray_bosses();
        hang_tab();
    }
}
module lid_half(){
    union(){
        translate([WALL,WALL,0]) rib_grid(FLOOR_H);
        ring(LID_T);
        lid_bosses();
        spigot();
    }
}

// ---------------- selector ----------------
if      (PART=="tray")    tray_half();
else if (PART=="lid")     lid_half();
else if (PART=="channel") c_channel();
else { tray_half(); translate([SIZE+30,0,0]) lid_half(); translate([0,-70,0]) c_channel(); }

// =====================================================================
// ASSEMBLY
// 1. Print tray + lid (mesh-face DOWN, pause layer 8 for mesh) + 1 C-channel, PC.
// 2. Stretch/embed bridal mesh on each rib grid.
// 3. Press 4x M3 heat-set inserts into the tray corner bosses.
// 4. Lay a standardized small even down layer in the tray. Set the lid on — the
//    perimeter spigot drops into the cavity mouth and self-aligns it. Drive 4x M3.
// 5. Bolt the C-channel to the inverted load cell; slide the tray's top rail in
//    from the open end to the end-stop; tare; run protocol.
// To reload: back out the 4 screws, lift the lid straight off.
// =====================================================================
