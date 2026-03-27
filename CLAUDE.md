# Memory

## Me
Andrew Peterson, CEO/Founder of FUZE Biotech (801 Inc). Building Expedry moisture resistance testing apparatus for down insulation treated with Expedry Gold.

## Project: Helios (Expedry Capsule)
The Expedry Capsule is a scientific humidity testing apparatus for measuring moisture resistance of Expedry Gold-treated down insulation. Named "Helios" as the project codename.

## What It Is
Concentric cylindrical cage assembly — inner and outer cages with bridal mesh wrapped around them and treated down packed between. A heated shaft (connected through sealed bearing in base) rotates the assembly inside a humidity chamber. Weight gain over time measures moisture absorption resistance.

## Physical Design
| Component | Description |
|-----------|-------------|
| **Base** | Ø160mm platform, 8mm thick, bearing seat center, grooves for both cage seats |
| **Outer Cage** | Ø150mm OD, 228.6mm tall (9.0"), 12 vertical posts, 4 mid-rings, split into 3 snap-together sections |
| **Inner Cage** | Ø86mm OD, 231.6mm tall (3mm taller than outer), 12 posts, 6 mid-rings, split into 3 snap-together sections |
| **Floating Disk** | Annular ring that sits between cages, rests on packed down |
| **Lid** | Snap-on cap over outer cage top, recess for inner cage protrusion |
| **Sealed Bearing** | In base center — heated shaft passes through |

## Key Dimensions (Rev D4 — CURRENT)
| Parameter | Value | Notes |
|-----------|-------|-------|
| outer_cage_height | 228.6mm | 9.0 inches |
| inner_cage_height | 231.6mm | outer - outer_seat + inner_seat + 3.0 |
| outer_section_h | 76.2mm | cage_height / 3 |
| inner_section_h | 77.2mm | cage_height / 3 |
| joint_h | 8.0 | Socket collar depth |
| joint_gap | 0.35 | Clearance between socket and cage |
| socket_wall | 2.0 | Collar wall thickness |
| outer_boundary_radial | 5.0 | Wide ring wall (ID=Ø140) — must capture posts |
| inner_boundary_radial | 4.0 | Wide ring wall (ID=Ø78) — must capture posts |
| base_t | 8.0 | Base thickness |
| outer_seat_depth | 2.0 | Both cages drop into 2mm grooves in base |
| inner_seat_depth | 2.0 | Same as outer |
| bearing_od | 85.0 | Bearing outer diameter |
| center_opening_d | 80.0 | Center hole in base |

## Section Print Heights (Rev D4)
| Section | Height | Notes |
|---------|--------|-------|
| Outer Section 1 | 76.2mm | No collar, has foot ring |
| Outer Section 2 | 84.2mm | 8mm collar + 76.2mm body |
| Outer Section 3 | 84.2mm | 8mm collar + 76.2mm body + snap lip |
| Inner Section 1 | 77.2mm | No collar, has foot ring |
| Inner Section 2 | 85.2mm | 8mm collar + 77.2mm body |
| Inner Section 3 | 85.2mm | 8mm collar + 77.2mm body |

## Joint Design (Socket-Wraps-Down)
Pipe coupling style: sections 2 & 3 have a socket collar at the bottom that wraps DOWN over the top of the section below. Zero net height added. Collar_bridge module connects the collar to the cage body (there was a 0.35mm air gap without it). Detent bumps provide snap-fit.

## Assembly Positions (from z=0 at base bottom)
- Outer cage: z = base_t - outer_seat_depth = 6.0
- Inner cage: z = base_t - inner_seat_depth = 6.0
- Outer cage top: z = 6.0 + 228.6 = 234.6
- Inner cage top: z = 6.0 + 231.6 = 237.6 (3mm above outer)
- Lid bottom: z = 234.6 (sits on outer cage)

## Design File
- **Source**: `expedry_capsule_rev_d.scad` (OpenSCAD parametric, $fn=160)
- **Current revision**: Rev D4
- **Printer**: Bambu H2D (direct drive), PLA filament
- **Slicer**: Bambu Studio

## Printing Notes (CRITICAL — learned the hard way)
- **50% failure rate on cage sections** — thin vertical posts lose adhesion mid-print
- MUST use **brim** (8mm), NOT anchors — anchors don't provide enough base for posts
- Outer wall speed: **60 mm/s** (not 100+)
- Nozzle temp: **215°C** (hotter than standard PLA for inter-layer bonding)
- Fan: **0% first 3 layers**, 70% after (not 100%)
- Min layer time: **15 seconds** at 15 mm/s min speed
- **Print ONE section per plate** — travel moves between tall sections knock posts loose
- Detect thin walls: ON
- Avoid crossing walls: ON
- Z-hop: 0.4mm
- Wall count: 3 (makes thin posts nearly solid)

## Boundary Ring Fix (Rev D4)
Previous revisions had boundary rings barely touching posts — printer couldn't get attachment. Fixed by widening rings well past post inner edges (outer: 5mm wall captures 2mm past posts, inner: 4mm wall captures 1.9mm past posts).

## Collar Bridge Fix (Rev D4)
Socket collar was disconnected from cage body by 0.35mm air gap. Added collar_bridge module — solid annular platform from inside posts out to collar ID, overlapping 0.5mm into collar top.

## Known Issues / Open Items
- **3mf export caching**: OpenSCAD sometimes exports from cached geometry. Must F4 (force reload) then F6 (full render) before exporting.
- **Bearing seat**: Dimensions (Ø85mm OD, Ø80mm bore) are placeholder — update once shaft diameter determined
- **Heated shaft**: To be designed — can match cage dimensions or adjust cages to commercial shaft
- **Power converter needed**: US 110V test equipment going to Munich, Germany (230V) — need step-down converter
- **Inner cage sections**: Print settings need validation (same issues as outer likely)

## Revision History
| Rev | Changes |
|-----|---------|
| D3 | Socket-wraps-down joint design, 3-section split |
| D4 | Inner cage seat groove in base, foot ring on inner section 1, collar_bridge module, widened boundary rings (5mm outer / 4mm inner), lid position fix, inner_cage_height recalc (229.6 → 231.6) |

## Test Protocol (Munich)
Humidity chamber testing — mount capsule on heated rotating shaft, expose to controlled humidity, weigh at intervals to measure moisture uptake. Compare Expedry Gold treated vs untreated down.

## Related Projects
| Project | Repo | Description |
|---------|------|-------------|
| FUZE Atlas | fuzeatlas | Multi-portal web app |
| fuzefaq.com | fuzecost | Public landing page |
| **Helios** | **helios** | **Expedry Capsule test apparatus** |

## Preferences
- Move fast — Munich trip deadline
- Direct, no fluff
- Precision matters — these parts must assemble perfectly
- Always verify dimensions mathematically before printing
