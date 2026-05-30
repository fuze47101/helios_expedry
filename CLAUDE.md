# Memory

## CRITICAL BRANDING / TERMINOLOGY (external-facing docs, decks, emails)
- **NEVER use the words "silver" or "nano"** in any external-facing material. The chemistries are F1 and Helios. They are described as **meta-materials**, not silver nanoparticles.
- **Helios is NOT silver.** Helios is one F1-family chemistry variant; both are meta-materials.
- **Apparatus name**: "Solaris FZ-500 Apparatus" (never "the rig" in external docs — internal shorthand only)
- **Company**: Legal entity is 801 Inc. External DBAs: **FUZE Technologies** (preferred for industry/partner-facing work like Nike), **FUZE Biotech** (biotech/science-forward contexts). Default to **FUZE Technologies** for partnership decks unless Andrew says otherwise.
- **Andrew's email**: `andrew@fuze47.com` (NOT andrew@801inc.com)
- **Nike context**: The April 2026 meeting is a **follow-up** to the Portland meeting from 2 weeks prior (early April 2026). Never frame it as a first pitch.

## Helios v2 — Wine Fridge Build (Major Overhaul, May 13, 2026)
This SUPERSEDES the old 12×12×13" test box build. The original box is being abandoned for a much larger purpose-built chamber inside a converted wine fridge.

### Two Distinct Tests (LOCKED — do not lose this)
The Helios apparatus must support BOTH of these tests:

**Test 1 — Jacket Moisture Egress (sweat-through testing):**
- Heated 3" aluminum column = body simulator at ~95-100°F
- 2× 12V 40W cartridge heaters inside column base, water dripped on heated puck via peristaltic pump
- Generates steam INSIDE the column = simulated sweat
- Jacket layer stack wrapped on column (inner liner / down or fill / outer shell)
- Vapor pressure pushes sweat outward through the layer stack
- SDP810 measures ΔP across layers; SHT41 measures column-internal RH
- Chamber background = COLD + DRY (winter outdoor conditions; drives outward vapor pressure gradient)
- Classic skin-model / sweating-hot-plate physics (similar to ISO 11092)

**Test 2 — Free-Form Down Moisture Pickup (capsule on load cell):**
- Concentric mesh TPU capsule (V4) holds free-form down (treated Expedry Gold vs untreated control)
- Capsule HANGS from the load cell (top-mount) over the heated column
- Chamber must be HIGH RH + variable temp (humid wear/storage simulation)
- Capsule drops over the column with 1.9mm radial clearance per side
- Down absorbs water vapor from the humid chamber air
- Load cell weight gain over time = moisture absorption rate
- Test compares treated vs untreated under matched conditions

### Chamber (Wine Fridge Conversion)
- Top compartment of repurposed wine fridge becomes the test chamber
- Dimensions: 20" W × 18" D × 31" H = ~150 L volume (~5× the old box)
- Glass door retained (some leakage OK)
- All factory shelving removed; only side wall metal ledges remain
- Aluminum cross-members slide in on those ledges to support load cell + heated column plate
- Fluorescent light at top retained for visibility / IR camera baseline
- Refrigeration capability preserved for cold testing (cold + humid + cold + dry modes)

### Load Cell (Bonvoisin disassembled, hanging)
- Bonvoisin analytical balance stripped down to bare strain-gauge beam
- Validated to read in negative direction (hanging load OK)
- Same 500g / 0.001g resolution; capsule target weight ~350g unchanged
- Beam mounts to steel L-bracket on aluminum cross-members across chamber top
- Free end has machined aluminum extension with M5 bolts for capsule hook attachment
- Capsule hangs from the beam's free end via wire/cable

### Heated Column Mount (welded)
- 3" (76.2mm) OD × 228.6mm (9.0") tall aluminum tube (existing from old build)
- Weld to ~150×150×6mm (¼" thick) aluminum baseplate with 76.2mm center bore
- Plate has 4 corner M6 holes for cross-member mounting
- Rubber thermal-isolation grommets between plate and cross-members
- Tube extends BELOW plate ~30-50mm for cartridge heater base

### Humidifier (Test 2 background) — PURE VAPOR required, not fog
**Critical:** Ultrasonic piezo foggers produce 1-5μm droplets, NOT vapor. Droplets settle on the down sample directly and contaminate weight readings. For Test 2, use ONLY boiling-water (warm mist) humidifiers that emit pure vapor.

Recommended unit (May 13 2026):
- TURBRO Greenland GLS04 Stainless Steel Steam Humidifier — 4L tank, 500mL/h, 304 SS boiler, ~$120
- Plug into mains via SSR-25DA (DC trigger, AC output) controlled by Pi GPIO
- GFCI outlet upstream (mandatory — water + mains)
- Pi runs closed-loop PID using a SECOND SHT41 mounted inside the chamber → switches mains on/off to maintain setpoint ±2% RH

### Sensors Needed
- **Existing SHT41 (in-column)** — measures inside the heated column (sweat-side RH/T for Test 1)
- **NEW SHT41 (in-chamber)** — chamber background RH/T for Test 2 humidity control loop
- **SDP810** — pressure differential across jacket layer stack (Test 1)
- **MAX31855 + K-type TC** — puck temperature
- **Load cell** — capsule weight (Test 2)

### IR Cameras (last install)
- Currently have 1 camera in hand
- Cameras live INSIDE the chamber, view jacket sleeve over heated column
- Looking for heat bleed-through patterns on the outer shell layer
- Possibly add a second from different angle later

### Electronics Enclosure
- Pi + relay HAT + SSRs + signal conditioning all live in EXTERNAL enclosure mounted on back of fridge
- Single bulkhead pass-through panel for cables:
  - Mains GFCI feed for humidifier + cartridge heater (separate rated gland)
  - Multi-pin Phoenix-style screw terminal block for sensor + load cell wires
  - USB pass-through for IR cameras
  - Silicone tube pass-through for pump water line
- Touchscreen mounted on side of fridge, horizontal orientation
- HDMI + USB-touch + DC power cables out to touchscreen

### Open Questions Still to Resolve
- Cold-mode interlock — disable cartridge heater when fridge refrigeration is on?
- Final SSR vs relay-HAT division of labor for the new build
- Connector spec for bulkhead pass-through (cable glands vs M16 industrial)
- Whether to keep the factory fridge thermostat or have the Pi take over cold control

## Solaris FZ-500 physical corrections (supersede earlier notes below)
- **Heat plate**: 175mm × 175mm (NOT ~30×30cm)
- **Air gap** (fabric top → plate surface): **45mm** (NOT 60mm — earlier docs were wrong)
- **Sensing**: 1 Hz across 3 sensors (TC-A, TC-B on plate underside; DS18B20 in air gap). Emphasize sensor count and accuracy (±0.1 °C) in external material, NOT the Raspberry Pi or CSV plumbing.

## Me
Andrew Peterson, CEO/Founder of 801 Inc (dba FUZE Technologies / FUZE Biotech). Building Expedry moisture resistance testing apparatus for down insulation treated with Expedry Gold, AND the Solaris FZ-500 IR characterization apparatus for F1 meta-material thermal fabrics.

## Preferences
- Move fast — Portland show deadline NOW
- Direct, no fluff
- Precision matters — these parts must assemble perfectly
- Always verify dimensions mathematically before printing

## Current Status (April 2026)
- **Show**: Portland (next show) — need working demo on screen
- Munich is done/past — Portland is current focus
- Pi is connected via phone hotspot FX4 / Jetflow101
- deploy_v3 is built and verified, needs to get onto Pi

## Raspberry Pi / Data Acquisition
- **Board**: Raspberry Pi (in test box) — running Debian 12 Bookworm, kernel 6.6.51, aarch64
- **Hostname**: alliedV2
- **User**: allied2 (NOT alliedV2 — the username changed during rebuild)
- **Password**: Allied2025
- **OS**: Debian GNU/Linux 12, kernel 6.6.51-rpt-rpi-2712 (2024-10-08)
- **App Location**: `/home/allied2/FeatherV2/`
- **Known WiFi networks**: ISEEYOU2 / Fuze47101 (home), FX4 / Jetflow101 (Andrew's hotspot)
- **SSH**: Enabled — IP changes per network, use hotspot client list to find it
- **Display**: Touchscreen running ExpeDRY TEST SYSTEM GUI app (rotated 270°)

## GitHub Repo
- **Repo**: github.com/Mfuze/FeatherV2 (PRIVATE)
- **Auth**: Password auth is DISABLED on GitHub. Need Personal Access Token (PAT) for clone.
- **Local copy**: `helios/FeatherV2/` (downloaded as ZIP, extracted)
- **Original code**: Kivy 2.3.1 + NeuKivy, uses minimalmodbus (COM5 — Windows), smbus3

## Project: Helios (Expedry Capsule)
The Expedry Capsule is a scientific humidity testing apparatus for measuring moisture resistance of Expedry Gold-treated down insulation. Named "Helios" as the project codename.

## What It Is
Concentric cylindrical cage assembly — inner and outer cages with bridal mesh wrapped around them and treated down packed between. Capsule sits inside a humidity/temperature chamber on 4 posts that pass through the chamber floor and rest on a precision scale below. Weight gain over time measures moisture absorption resistance of Expedry Gold-treated vs untreated down.

## Physical Design
| Component | Description |
|-----------|-------------|
| **Base** | Ø160mm platform, 8mm thick, bearing seat center, grooves for both cage seats |
| **Outer Cage** | Ø150mm OD, 228.6mm tall (9.0"), 12 vertical posts, 4 mid-rings, split into 3 snap-together sections |
| **Inner Cage** | Ø86mm OD, 231.6mm tall (3mm taller than outer), 12 posts, 6 mid-rings, split into 3 snap-together sections |
| **Floating Disk** | Annular ring that sits between cages, rests on packed down |
| **Lid** | Snap-on cap over outer cage top, recess for inner cage protrusion |
| **4 Support Posts** | Pass through chamber floor, rest on scale pan below — transfer capsule weight to scale |
| **Floor Seal** | Non-contact labyrinth seal around each post penetration — blocks moisture without adding friction |
| **Scale Pan Adapter** | 3D-printed platform on scale pan — receives and centers the 4 post tips |

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

## Humidity Chamber
| Item | Details |
|------|---------|
| **Chamber** | Two-level: upper test area (glass/acrylic windows), lower equipment bay |
| **Lower bay** | 300mm x 280mm x 160mm height |
| **Humidifier** | Ultrasonic sonic fogger, draws water from small bottle |
| **Controller** | Timer-based controller runs humidity on/off cycles AND heat on/off |
| **Sensor** | Sintered metal probe in upper chamber (humidity + temperature) |
| **Heating** | Controlled by same timer controller |

## Scale (ORDERED)
| Spec | Value |
|------|-------|
| **Model** | Bonvoisin Lab Analytical Balance 500g x 0.001g |
| **Amazon ASIN** | B0C8CK4VBM |
| **Capacity** | 500g |
| **Resolution** | 0.001g (1mg) |
| **Accuracy** | ±0.004g |
| **Interface** | RS232 serial data output |
| **Power** | AC adapter + lithium battery (36hr) |
| **Unit dimensions** | ~280 x 220 x 178mm (with draft shield) |
| **Pan** | Round, stainless steel — MEASURE DIAMETER ON ARRIVAL |
| **Fits in lower bay?** | Yes — 280x220 footprint fits in 300x280 bay. Remove draft shield glass; base only ~90-100mm tall, leaves 60-70mm for post drop. |

## Center Tube Assembly (2-piece redesign)
| Parameter | Value | Notes |
|-----------|-------|-------|
| Tube OD | 75.0mm | Same as current, capsule already fits |
| Tube height | 228.6mm | 9 inches |
| Sleeve wall | 3.0mm | OD=75, ID=69 |
| Core OD | 59.0mm | Cable channel between core and sleeve |
| Core wall | 3.0mm | ID=53mm (hollow for wiring) |
| Cable channel | 5.0mm | Fits 14.5mm x 5mm heating cable |
| Cable length | 36" (914.4mm) | Heating cable, measured |
| Cable wraps | 5 | Recalculated from 36" cable / π×59mm circumference |
| Cable pitch | ~40.7mm | Spread over full tube height (15mm–218.6mm) |
| Vent holes | Ø10mm sleeve, Ø6mm core | Staggered, between cable wraps |
| Guide ridges | 1.5mm tall | On core exterior, keep cable tracking — sleeve clears at 69mm |
| Floor flange | 8mm thick, Ø68.7mm | 4 screw holes for mounting core to chamber floor |
| Cable entry slot | 17mm × 7mm | Through core wall at bottom — cable exits center, wraps outside |

**Inner core:** Solid wall cylinder with spiral guide ridges on exterior. Cable enters hollow center from below, exits through side slot at base, wraps between ridges climbing up the outside. Floor flange bolts to chamber floor.
**Outer sleeve:** Smooth cylinder slides over core + cable. 2.5mm clearance above cable. Vent holes for heat radiation AND moisture transport (sweat simulation in sleeve mode).

## Two Test Modes
| Mode | Center Tube | Humidity | Heat | Measurement |
|------|-------------|----------|------|-------------|
| **Capsule moisture** | No heat, capsule slides over tube | ON (fogger) | OFF on tube | Scale: weight gain over time |
| **Sleeve thermal** | Heated to body temp | ON (fogger) | ON | Wattage to maintain temp |

## Weighing System Design (CONFIRMED)
- **No bearing, no rotation** — capsule is static, weight transfers to scale
- **3 posts (tripod)** at 120° spacing — inherently stable, no wobble
- **Bolt circle: Ø130mm (R=65mm)** — between inner seat (R=43.1) and outer seat (R=71.9)
- **3 NEW 12mm holes drilled** in chamber floor (existing holes don't work — wrong bolt circle)
- **Drill template** included in SCAD file — registers on center hole, guides 3 drill positions
- **Non-contact labyrinth bushing** press-fits into each 12mm hole
- **Center tube sits on floor directly** — does NOT touch scale or weighing plate
- **Weighing plate** has Ø80mm center hole clearing tube by 2.5mm per side — NO CONTACT
- **Capsule + plate weight**: ~350g (70% of 500g capacity)
- **Data logging**: RS232 from scale → laptop/Pi → CSV → live moisture uptake curve

## Weighing System Parts (SCAD: helios_weighing_system.scad)
| Part | Description | Print Qty |
|------|-------------|-----------|
| **Center core** | Ø59mm spool with helical cable channel, vent holes | 1 |
| **Center sleeve** | Ø75mm smooth outer with vent holes, slides over core | 1 |
| **Weighing plate** | Ø170mm annular platform, cage seat grooves, 3 integral posts | 1 |
| **Labyrinth bushing** | Ø12mm press-fit, Ø8.5mm bore, concentric rings above/below | 3 |
| **Scale pan adapter** | Ø155mm replacement pan, center boss for load cell pin | 1 |
| **Drill template** | Ø160mm flat disc, registers on center hole, 3 guide holes | 1 |

## Key Dimensions (Weighing System)
| Parameter | Value | Notes |
|-----------|-------|-------|
| post_od | 8.0mm | PLA posts integral to weighing plate |
| bolt_circle_r | 65.0mm | Ø130mm, drill 3 NEW holes |
| drill_size | 12.0mm | For labyrinth bushing press-fit |
| bushing_bore | 8.5mm | 0.25mm clearance to post |
| plate_center_hole | 80.0mm | 2.5mm clearance to 75mm tube |
| plate_od | 170.0mm | 20mm solid material outside posts |
| floor_thickness | 2.5mm | Measured |
| floor_center_hole | 27.0mm | Existing |
| floor_small_holes | 5.0mm x 6 | Existing at R=95.25mm (NOT used) |
| pan_adapter_od | 155.0mm | Replacement pan for Bonvoisin scale |
| stock_pan_od | 109.5mm | 4 10/32" measured |
| center_pin_d | ~7.9mm | ~9-10/32" measured with tape — REFINE WITH CALIPERS |
| stock_socket_depth | 15.1mm | 19/32" — how deep pan sits on load cell pin |
| stock_rim_h | 7.1mm | 9/32" edge fold on stock pan |

## Measurements Still Needed
- [x] Scale pan diameter — 109.5mm (4 10/32")
- [x] Scale pan socket depth — 15.1mm (19/32")
- [ ] Center load cell pin diameter — ~7.9mm, NEED CALIPERS for exact fit
- [ ] Scale pan height above table surface (draft shield removed)

## Floor Flange (v2 — replaces core's built-in flange)
| Parameter | Value | Notes |
|-----------|-------|-------|
| flange_od | 110mm | Wide base for 4 floor screws |
| flange_h | 6mm | Flat disc thickness |
| lip_od | 68.5mm | Centering lip goes INSIDE sleeve (69mm bore) |
| lip_h | 8mm | Registration depth |
| center_bore | 53mm | Matches core ID for airflow |
| screw_circle_r | 46mm | 4× M5 countersunk floor screws |
**Key**: Nothing extends beyond the 75mm sleeve OD — capsule (80mm center opening) slides over with 2.5mm clearance per side. Old built-in core flange couldn't be pre-attached due to force needed for core+sleeve press-fit.

## Floor Bushings (v4 — re-drilled holes)
- 2× medium: 12.2mm OD for 1/2" (12.7mm) re-drilled holes, 1.85mm wall
- 1× oversized: 14.7mm OD for 15.2mm over-drilled hole, 3.1mm wall
- All: 8.5mm bore for 8mm carbon fiber rods, 2.5mm flange, drop-through + epoxy
- **v3 standard bushings FAILED**: 9.025mm OD / 8.5mm bore = 0.26mm wall — unprintable

## Humidifier Upgrade Plan (TODO: April 15, 2026)
**Problem**: Sonic humidifier with straw wick mechanism failed. Tried gravity-feed bag — leaked everywhere. Can't gravity feed because the scale now sits where the water bottles were.

**Solution: Piezo mist maker + peristaltic pump (~$25 total)**
- **16mm ultrasonic mist maker module** ($8-15 on Amazon, search "16mm ultrasonic mist maker module USB")
  - Piezoelectric disc, 3-7V USB power, silent
  - Sits in a tiny water cup mounted near (NOT on) the chamber/scale platform
  - Mist output goes into chamber through small tube or port
  - Relay on/off control — same relay board we already have
- **12V peristaltic pump** ($10-12 on Amazon, search "12V peristaltic pump dosing")
  - Feeds water from separate reservoir to the mist maker cup on demand
  - No backflow, no gravity issues, no leaking
  - Precise metering — only runs when cup needs refilling
  - Relay controllable from Pi (5th relay channel, or share existing)
- **Small silicone tubing** to connect pump to mist cup

**Why this works:**
- Water reservoir completely off the scale platform — no weight interference
- Peristaltic pump = no backflow, no leaking, precise dosing
- Both components relay-controllable (same I2C relay board, addr=0x10)
- Tiny footprint — piezo cup is ~30mm diameter
- No wicking, no gravity feed, no bags

**Integration:**
- Relay ch1: ext humidifier → replace with peristaltic pump control
- Relay ch2: int humidifier → replace with mist maker on/off
- Or add 5th relay channel if keeping existing humidifier wiring
- Software: add pump prime cycle to test setup wizard

## IR Camera Upgrade (TODO: Purchase next week)
**Current camera**: InfiRay 256x192 USB thermal — likely blown/failing (showing insane temps, heatmap garbage)

**Replacement: Sipeed T256s** — $219
- 256x192 native LWIR + 640x480 AI upscaling (built-in 2.4 TOPS NPU)
- UVC compatible — plug-and-play with Linux/OpenCV, no drivers needed
- USB Type-C, 25 Hz frame rate, <50mK thermal sensitivity
- Built-in touchscreen for standalone operation
- Can record thermal video
- **Buy from**: AliExpress — https://wiki.sipeed.com/hardware/en/ThermalCam/T256s/Intro.html
- **Drop-in replacement** for current InfiRay — same resolution, same USB UVC protocol
- OpenCV code in camera/thermalcameraController.py should work with minimal changes (may need to adjust frame split logic since T256s may not pack thermal data the same way as InfiRay)

**Alternative if needed fast (Amazon Prime):**
- InfiRay P2 Pro (~$200-300) — same 256x192 sensor but designed for phones, needs USB adapter, limited Linux support
- Search: "InfiRay T2S+ USB thermal camera" for closest UVC-compatible module

## Known Issues / Open Items
- **3mf export caching**: OpenSCAD sometimes exports from cached geometry. Must F4 (force reload) then F6 (full render) before exporting.
- **Pan adapter**: Designed as replacement pan (Ø155mm) with center boss — needs caliper measurement of load cell pin
- **Inner cage sections**: Print settings need validation (same issues as outer likely)
- **RS232 data format**: Likely 9600 baud 8N1 ASCII — verify when scale arrives

## Revision History
| Rev | Changes |
|-----|---------|
| D3 | Socket-wraps-down joint design, 3-section split |
| D4 | Inner cage seat groove in base, foot ring on inner section 1, collar_bridge module, widened boundary rings (5mm outer / 4mm inner), lid position fix, inner_cage_height recalc (229.6 → 231.6) |
| D5 (PLANNED) | Remove bearing/shaft from base, add 4-post passthrough design, floor seal system, scale integration |

## ExpeDRY App Architecture (FeatherV2) — deploy_v3 CURRENT

### Deploy History
| Version | Location | What changed |
|---------|----------|-------------|
| **Original** | `helios/FeatherV2/` | GitHub ZIP download, original Mike code, COM5/Windows, commented relay |
| **deploy_v2** | `helios/deploy_v2/` | Scale integration, weight tracking, phase badges, enhanced theme, deploy.sh |
| **rebuild** | `helios/rebuild/` | Fixed RS485 (/dev/serial0), Relay (smbus2), SaveDialog CSV, WarningDialog, all __init__.py, camera modules |
| **deploy_v3** | `helios/deploy_v3/` | Dual graphs, WiFi settings, unified package, Builder.load_file fixes |
| **deploy_v4** | `helios/deploy_v3/` | **CURRENT** — NeuKivy shim (library gone from GitHub), install_v4.py with 29 files |

### NeuKivy Shim (deploy_v4 fix)
- **Problem**: NeuKivy (GuhanSenSam/NeuKivy) repo deleted/private — 404 on all download attempts
- **Fix**: Created `neukivy/` compatibility package inside deploy_v3
- `neukivy/__init__.py` — imports NeuApp
- `neukivy/app.py` — NeuApp (extends App with dummy theme_manager), NeuRoundedButton (Button with flat dark style), NeuCard (BoxLayout with rounded dark background)
- Registers NeuRoundedButton and NeuCard in Kivy Factory — ALL existing .kv files work unchanged
- **Installer**: `install_v4.py` — 29 files (was 25 in v3), includes neukivy shim

### App Structure (deploy_v3)
| File/Dir | Purpose |
|----------|---------|
| `main.py` | Main app — test logic, camera feed, sensor reading, relay control, scale polling, dual graph |
| `tester.kv` | Kivy layout — dual graphs (humidity + weight), camera, phase badge, WiFi button, tare |
| `components/Controls.py/.kv` | On/Off toggle controls for humidifier, fan, heater |
| `components/Test_Settings.py/.kv` | Duration, interval, endpoint, test type selector |
| `components/SaveDialog.py/.kv` | Save test data CSV to USB drive (with weight data + metadata) |
| `components/WeighDialog.py/.kv` | **LIVE weight display** — polls scale, stability detection, tare, auto-capture |
| `components/WarningDialog.py/.kv` | Warning when starting new test with unsaved data |
| `components/WifiDialog.py/.kv` | **NEW** — WiFi scan, connect, disconnect from touchscreen via nmcli |
| `camera/thermalcameraController.py` | IR thermal camera data processing |
| `camera/guiController.py` | Thermal heatmap rendering with OpenCV |
| `camera/ColormapEnum.py` | Colormap options for thermal display |
| `camera/values.py` | Camera constants |
| `utils/Relay.py` | I2C relay control — smbus2, bus=1, addr=0x10, mock mode if no hardware |
| `utils/RS485.py` | Modbus RTU sensors — /dev/serial0, 9600 baud, raw serial (no minimalmodbus dependency) |
| `utils/Scale.py` | Bonvoisin RS232 scale — /dev/ttyUSB0, background thread, continuous read |
| `utils/theme.py` | UI colors — bg, light, dark, text, go, stop, wet, dry, idle, weight, accent |

### Hardware Interfaces
| Interface | Protocol | Details |
|-----------|----------|---------|
| **Humidity/Temp sensor** | Modbus RTU | /dev/serial0, addr=1, registers 0(temp) & 1(humd), function code 3 |
| **Power sensor** | Modbus RTU | /dev/serial0, addr=3, register 3 (power), function code 4 |
| **Relay board** | I2C | SMBus bus=1, addr=0x10, 4 channels (1=ext hum, 2=int hum, 3=fan, 4=heater) |
| **IR camera** | USB Video | /dev/video0, OpenCV capture, 256x192 thermal |
| **Scale** | RS232-USB | /dev/ttyUSB0, 9600/8/N/1, pyserial, continuous streaming |

### Test Modes
| Mode | Relays Active | Plots | Weigh Dialog |
|------|--------------|-------|-------------|
| Moisture Movement | Int Humidifier + Fan | Humidity + Weight vs Time | Before & After |
| Moisture Resistance | Ext Humidifier → Fan (dry phase) | Humidity + Weight vs Time | Before, Mid, After |
| Dry Thermal | Heater | Calories + Weight vs Time | None |
| Wet Thermal | Heater + Fan | Calories + Weight vs Time | None |

### v3 Features
- **Dual graphs**: Top graph = humidity or power, Bottom graph = weight — both plot simultaneously
- **Scale integration**: Live weight at 2Hz, tare button, weight delta tracking, max weight
- **Phase tracking**: IDLE → WET → WET DONE → DRY BACK → DRY COMPLETE → COMPLETE
- **WiFi dialog**: Scan networks, enter password, connect/disconnect — all from touchscreen
- **CSV export**: time, humidity/power, temp, weight, delta, phase + metadata footer
- **Builder.load_file**: All dialogs properly load their .kv files (bug fix from rebuild)

### Deploy Script (deploy_v3/deploy.sh)
```
./deploy.sh              # default IP 192.168.1.178
./deploy.sh <pi-ip>      # pass current Pi IP
```
- SSH user: allied2 (was alliedV2 before rebuild)
- Backs up current files, creates directories, SCPs everything, installs pyserial + smbus2

### Pi Networking Notes
- Pi user is `allied2` at `/home/allied2/FeatherV2/`
- Previous install_gui_v4.py wrote to `/home/alliedV2/` — Andrew moved it to `~/FeatherV2/`
- WiFi managed via nmcli (NetworkManager)
- Known networks: ISEEYOU2 / Fuze47101, FX4 / Jetflow101
- To add new network: `sudo nmcli dev wifi connect "SSID" password "PSK"`
- After deploy_v3, WiFi can be managed from the touchscreen GUI

## Solaris FZ-500 — IR Heat Deflection + Sweat Egress (STANDALONE SYSTEM)

**This is a SEPARATE apparatus from Helios.** Separate Pi, separate sensors, separate purpose. Do NOT confuse with the Helios humidity chamber.

### What It Is
Combined solar-radiation + saturated-steam rig for FUZE-treated fabric performance testing. IR lamp heats a fabric sample from above (simulating sun), while steam rises from below (simulating body sweat). Measures whether FUZE treatment reduces plate temperature AND allows moisture to pass through.

### Physical Layout (top to bottom)
1. **175W halogen IR lamp** — ceramic socket, reflector housing in stainless shroud
2. **Fabric sample** — laid on top of stainless aperture frame, ~25cm circular opening
3. **~60mm air gap** — DS18B20 probe lives here (measures microclimate), SHT41 deferred to v2
4. **Matte-black heat plate** — 6061 aluminum, ~30×30cm, high-emissivity top face
5. **2× K-type TC** bonded to plate underside, diagonally opposite quadrants, 25–30% from edge
6. **Stainless fixture** holds plate and aperture frame
7. **[DEFERRED v2]** Steam plenum, aluminum post, vaporizer block, cartridge heater — not in Portland demo scope

### Geometry Lock (MUST REPRODUCE ±5mm BETWEEN RUNS)
| Measurement | Value |
|---|---|
| Lamp filament centerline → fabric top surface | **200mm** |
| Lamp filament centerline → plate surface | **260mm** |
| Fabric top → plate surface (air gap) | **~60mm** |
| Plate aperture diameter | ~25cm (circular cutout in frame) |
| TC bond position | diagonally opposite quadrants, 25-30% in from plate edge, underside |
| DS18B20 position | inside aperture, suspended in air gap above plate, not touching |

Irradiance governed by inverse-square; a 2cm lamp drift contaminates comparisons. Mark lamp and plate positions with tape on stand/table. Re-measure before every session and after any transport.

### Solaris Pi 5 (STANDALONE — separate from Helios Pi)
| Parameter | Value |
|-----------|-------|
| **Board** | Raspberry Pi 5 · 8GB RAM · CanaKit Starter Kit (128GB) |
| **Hostname** | solaris |
| **User** | fuze |
| **Password** | Fuze47101 |
| **OS** | Raspberry Pi OS Lite 64-bit (headless, no desktop) |
| **SD Card** | 128GB from CanaKit kit |
| **WiFi** | Flashed with FX4 / Jetflow101 (Andrew's hotspot) |
| **SSH** | Enabled with password auth |
| **Status** | FLASHED, BOOTING — need to SSH in and verify connection |

### Current Pi IP (as of 2026-04-21 evening — office network)
- **IP**: `10.100.102.92`
- **Dashboard**: `http://10.100.102.92:5000/` (from any device on same network)
- **SSH**: `ssh fuze@10.100.102.92`
- Previous known IPs (for reference): `192.168.1.152` (home ISEEYOU2), hotspot-assigned (FX4)

### WiFi Notes (Solaris Pi)
- **Evoq-Biz / Allotrope#1** — office network, Pi 5 FAILED to connect (UniFi, possibly VLAN/policy issue). The other Helios Pi connects fine to this network, so it's specific to the Pi 5 or cloud-init config.
- **FX4 / Jetflow101** — Andrew's phone hotspot, reflashed with this as primary
- **ISEEYOU2 / Fuze47101** — home network, add after first SSH
- Once SSH'd in, add networks: `sudo nmcli dev wifi connect "SSID" password "PSK"`

### Sensor Wiring — Pi 5 GPIO
| Device | Pi Pin | GPIO | Bus | Notes |
|--------|--------|------|-----|-------|
| MAX31855 #1 VCC | Pin 1 | 3V3 | Power | TC-A (heat plate) |
| MAX31855 #1 GND | Pin 6 | GND | Power | |
| MAX31855 #1 CLK | Pin 23 | GPIO 11 | SPI0 SCLK | |
| MAX31855 #1 DO | Pin 21 | GPIO 9 | SPI0 MISO | |
| MAX31855 #1 CS | Pin 24 | GPIO 8 | SPI0 CE0 | /dev/spidev0.0 |
| MAX31855 #2 VCC | Pin 17 | 3V3 | Power | TC-B (heat plate) |
| MAX31855 #2 GND | Pin 14 | GND | Power | |
| MAX31855 #2 CLK | Pin 23 | GPIO 11 | SPI0 SCLK (shared) | |
| MAX31855 #2 DO | Pin 21 | GPIO 9 | SPI0 MISO (shared) | |
| MAX31855 #2 CS | Pin 26 | GPIO 7 | SPI0 CE1 | /dev/spidev0.1 |
| SHT41 SDA | Pin 3 | GPIO 2 | I2C1 SDA | addr 0x44 |
| SHT41 SCL | Pin 5 | GPIO 3 | I2C1 SCL | |
| SHT41 VCC | Pin 1 | 3V3 | Power | QWIIC/Stemma QT |
| SHT41 GND | Pin 9 | GND | Power | |
| MLX90640 SDA | Pin 3 | GPIO 2 | I2C1 SDA (shared) | addr 0x33, optional |
| MLX90640 SCL | Pin 5 | GPIO 3 | I2C1 SCL (shared) | |
| MLX90640 VCC | Pin 17 | 3V3 | Power | |
| MLX90640 GND | Pin 20 | GND | Power | |
| Pump MOSFET gate | Pin 32 | GPIO 12 | PWM0 | 1kΩ to gate, 10kΩ pulldown |

### K-Type Thermocouple Polarity (IMPORTANT — EMPIRICALLY VERIFIED 2026-04-20)
- **On THIS batch of probes: Red wire = POSITIVE (+), Yellow wire = NEGATIVE (−)**
- This is OPPOSITE of ANSI standard (which says yellow=+, red=−)
- Our probes are IEC-coded under the jacket even though they have yellow/red insulation
- Validated on TC-A: pinch test went 21°C → 33°C when wired red→T+, yellow→T−
- If readings go DOWN when plate heats up, swap the leads at the MAX31855 screw terminal
- **Wire TC-B the same way when second MAX31855 arrives**: red on T+, yellow on T−

**Visual reference for screw terminal** (use this, ignore silkscreen "Yellow/Red" labels):
```
Hold MAX31855 with 6-pin header on LEFT edge, screw terminal on TOP
  ┌─────────────┐
  │ [RED][YEL]  │ ← screw terminal
  │   Vin       │
  │   3V0       │
  │   GND       │
  │   DO        │
  │   CS        │
  │   CLK       │
  └─────────────┘
LEFT screw  = Red wire  (T+)
RIGHT screw = Yellow wire (T-)
```

### TC-A Assembly Status (2026-04-20)
- MAX31855 #1 (blue variant w/ 6-pin header: Vin/3V0/GND/DO/CS/CLK)
- Powered via Vin pin → Pi Pin 1 (3.3V) — board regulator passes through at 3.3V, works fine
- Wire colors on #1 (for reference when wiring #2):
  - green → Vin → Pi Pin 1
  - red → GND → Pi Pin 6
  - yellow → DO → Pi Pin 21 (MISO)
  - purple → CS → Pi Pin 24 (CE0)
  - green (second) → CLK → Pi Pin 23 (SCLK)
- TC-B will use Pi Pin 26 (CE1) for CS instead of Pin 24

### TC-B Assembly Status (2026-04-21 — VALIDATED)
- MAX31855 #2 (same blue variant as #1) wired via breadboard fan-out
- SPI bus shared with TC-A via breadboard rails/rows:
  - **+ rail**: Pi Pin 1 (3.3V) + MAX #1 Vin + MAX #2 Vin
  - **− rail**: Pi Pin 6 (GND) + MAX #1 GND + MAX #2 GND
  - **Row 5 (A/B/C)**: DO fan-out — Pi Pin 21 (MISO) + MAX #1 DO + MAX #2 DO
  - **Row 28**: CLK fan-out — Pi Pin 23 (SCLK) + MAX #1 CLK + MAX #2 CLK
  - **Row 18 (A/B)**: CS for MAX #1 — Pi Pin 24 (CE0) → MAX #1 CS only
  - **Row 14 (A/B)**: CS for MAX #2 — Pi Pin 26 (CE1) → MAX #2 CS only
  - (CS lines MUST stay isolated per chip — do not fan out CS)
- Thermocouple: red→T+ (left screw), yellow→T− (right screw), same IEC convention as TC-A
- **Smoke test 2026-04-21**: idle A=20.0°C / B=20.2°C, pinch-A climbed 27→30, pinch-B climbed 30.8→31.5, channels independent, no FAULT codes, polarity correct on both

### PID + SSR (NOT connected to Pi — standalone mains loop)
- Inkbird ITC-100VH PID → reads K-type TC in vaporizer block → drives SSR-40DA
- SSR switches 120V mains to 300W cartridge heater
- Thermal fuse 240°C in series with cartridge heater (MANDATORY safety)
- Set PID: SV=200°C, alarm=220°C
- GFCI outlet required for mains heater circuit
- DEFERRED for Portland show — needed only for sweat vaporizer; plate-only demo doesn't require it

### IR Lamp Mains Control (2026-04-21 — VALIDATED)
- **SSR**: DIWD SSR-25 DA (25A rating, 3–32V DC input, 24–380V AC load) — sufficient for ~2–4A IR lamp
- **Box**: DIY severed extension cord inside black project box
- **AC wiring** (verified working):
  - Hot (black) cut, wall-side → SSR terminal 1, lamp-side → SSR terminal 2
  - Neutral (white) passes through uncut via Wago lever nut
  - Ground (green) passes through uncut via Wago lever nut
- **DC input** (Pi control):
  - SSR terminal 3 (+) → Pi Pin 11 (GPIO 17)
  - SSR terminal 4 (−) → Pi Pin 6 (GND)
- **GFCI outlet required upstream** (mandatory for Portland demo)
- **Python control**: `gpiozero.LED(17)` with `lgpio` backend — validated 2026-04-21, 5-cycle toggle test passed
- **Dependencies installed in solaris-env**: `gpiozero`, `lgpio` (required `sudo apt install liblgpio-dev python3-lgpio` first)
- Digital Loggers IoT Relay will replace this box (~1 week out per 2026-04-20 order)

### Parts on Desk (ALL ARRIVED April 2026)
- Pi 5 8GB + CanaKit heatsink/fan + 128GB SD ✓
- MX-6 thermal paste ✓
- K-type TC probes (5-pack, ALLmeter) ✓
- MAX31855 breakouts (4-pack, NOYITO) ✓
- SHT41 sensor (QWIIC) ✓
- QWIIC cable kit ✓
- SSR (Fotek SSR-40DA) ✓
- Cartridge heaters (300W, red) ✓
- INTLLAB peristaltic pumps (4-pack) ✓
- Silicone tubing ✓
- DC barrel jack adapter ✓
- Stainless steel fixture (base plate + column) — FABRICATED ✓

### Software
- **Daemon script**: `solaris_daemon.py` — on Desktop, ready to SCP to Pi
- Reads 2× MAX31855 (SPI), SHT41 (I²C), optional MLX90640 (I²C) at 1 Hz
- Buffers 60 samples, POSTs to FUZE Atlas `/api/admin/solaris-tests/[id]/ingest`
- Also saves local CSV backup (`~/solaris_run_YYYYMMDD_HHMMSS.csv`)
- Systemd service file: `/etc/systemd/system/solaris.service`
- Python venv: `~/solaris-env/` with spidev, smbus2, requests, adafruit-circuitpython-sht4x, adafruit-circuitpython-mlx90640
- **Design doc**: `Desktop/fuzecost/Solaris_FZ500_Design.html` (full BOM, physics, architecture)
- **Assembly guide**: `Desktop/Solaris_FZ500_Assembly_Guide.html` (wiring, GPIO, step-by-step)

### Assembly Status (as of 2026-04-21 evening)
- [x] Pi 5 heatsink + fan + thermal paste
- [x] Flash SD card (Pi OS Lite 64-bit, hostname=solaris, user=fuze)
- [x] SSH'd into Pi (root cause of earlier failures: macOS Internet Sharing intercepting LAN packets — turn OFF)
- [x] Install Python deps in `~/solaris-env/` (flask, flask-socketio, eventlet, spidev, gpiozero, lgpio, matplotlib)
- [x] Enable SPI + I2C via raspi-config
- [x] Wire MAX31855 #1 → SPI CE0 (TC-A) — validated 2026-04-20
- [x] Wire MAX31855 #2 → SPI CE1 (TC-B) — validated 2026-04-21 (dual-channel smoke test passed)
- [x] Rewire breadboard with F-M jumpers in office location after intermittent contact failures
- [x] Wire DS18B20 air-gap probe (OneWire, 4.7kΩ pull-up to 3.3V, w1-gpio overlay persisted in /boot/firmware/config.txt)
- [x] Bond TC-A + TC-B to plate underside — INTERIM: MX-6 paste + electrical tape, diagonally opposite quadrants. Post-Portland: rebond with Arctic Alumina epoxy.
- [x] Mount DS18B20 in ~60mm air gap (inside aperture frame, suspended above plate)
- [x] Mount IR lamp — 200mm to fabric, 260mm to plate (geometry locked, see above)
- [x] Build DIY SSR outlet box for IR lamp control (2026-04-21 validated, GPIO 17 → SSR terminal 3)
- [x] Build Flask kiosk dashboard (charts + test control, served at :5000)
- [x] Build run_comparison.py automation (3×baseline + 3×untreated + 3×treated + matplotlib overlay chart)
- [x] Write TEST_PROTOCOL.md (10 sections: safety, pre-flight, geometry, parameters, procedure, data, comparison, physics, limitations, troubleshooting)
- [ ] First dry run — heat plate only, no fabric (verify 3-sensor pinch test passes after rewire)
- [ ] First full fabric test — baseline → untreated → treated 9-test sequence
- [ ] **DEFERRED v2:** Wire SHT41 → I²C, MLX90640 thermal cam, PID+SSR+cartridge heater (steam side), Pi HAT PCB design, Digital Loggers IoT Relay swap

### Solaris Project File Tree (`/Desktop/helios/solaris_dashboard/`)
- `app.py` — Flask + Socket.IO backend, sensor sampling, test sequencer, CSV writer
- `templates/index.html` — dashboard UI (Plotly traces, status dots, controls)
- `static/dashboard.js` — frontend live updates via Socket.IO
- `setup_kiosk.sh` — one-shot Pi setup: deps, OneWire overlay, systemd services, Chromium kiosk
- `run_comparison.py` — CLI automation: runs 9-test comparison, generates overlay PNG, validates efficacy criteria
- `TEST_PROTOCOL.md` — formal test SOP for the rig
- `README.md` — quick reference

### Capsule Test Geometry — LOCKED FOR ASTM/AATCC/ISO/IDFB SUBMISSION
These numbers are the formal test geometry for all reports, SOPs, patent filings, and standards submissions.

| Parameter | Metric | Imperial | Notes |
|-----------|--------|----------|-------|
| Outer cylinder OD | 150.0 mm | 5.906" | Rev D4, locked |
| Outer cylinder ID (at ribs) | 138.0 mm | 5.433" | OD minus 2×6mm wall |
| Inner sleeve OD | 86.0 mm | 3.386" | Rev D4, locked |
| Inner sleeve ID | 82.55 mm | 3.250" | Clears 3" aluminum post |
| Annular gap (radial) | 27 mm | 1.063" | Down packing space |
| Cylinder height | 228.6 mm | 9.000" | Outer cage height |
| Down volume (annular) | 2,340 cm³ | 142.8 in³ | π×(72²−45²)×228.6 |
| Mesh open area (V2, 6-window) | ~72% | — | Target for V2 redesign |
| Outer exposed mesh area | ~714 cm² | ~110.7 in² | π×138×228.6×0.72 |
| Inner exposed mesh area | ~445 cm² | ~69.0 in² | π×86×228.6×0.72 |
| Total exposed mesh | ~1,159 cm² | ~179.6 in² | Both surfaces combined |
| **Surface area per gram** | **= 1,159 / (grams packed)** | — | Key metric for SOP |

**Standards targets:** ASTM, AATCC, ISO, IDFB
**Patent scope:** Test apparatus including pressurized saturated steam vapor delivery (Solaris FZ-500 vaporizer block + Helios capsule chamber), combined IR heat deflection + sweat egress protocol, concentric mesh-embedded TPU cylinder geometry with calculated exposed surface area per unit mass of fill.

### TPU Mesh-Embedded Capsule Frame V4 (Current — April 29, 2026)
All parts renamed to V4 to track this morning's changes. Material: TPU 95A.

**Design Philosophy:** Concentric cylinders with mesh lattice walls. Pause print at mesh layer to embed bridal mesh. Expedry-treated down fills the void space between inner and outer column mesh walls. Capsule sits on load cell — must drop freely over 3" aluminum steam generator tube with NO rubbing/contact.

#### V4 STL Files (on Desktop)
| File | Description | Print Qty |
|------|-------------|-----------|
| `FUZE_Capsule Cap V4.stl` (96 KB) | Cap — 166mm disk, 153mm outer lip, 90.4mm inner lip | 1 (PRINTED ✓) |
| `FUZE_OuterPanel_V4.stl` (83 KB) | Outer panel — both edges female T-slots, 258.3mm wide | 2 |
| `FUZE_InnerColumn_V4.stl` (15 KB) | Inner column — thin wall, lap joint tabs | 2 |
| `FUZE_CouplerKeys_V4.stl` (54 KB) | 18 solid dogbone coupler keys on one plate | 1 |

#### Outer Panel V4 — Both Edges Female
- **Panel:** 258.3 × 232.6 × 6.0mm (3mm backing + 3mm tooth layer)
- **Assembled cylinder:** OD 164.4mm, **ID 152.4mm (6" exactly)**
- **Both edges identical female T-slots** (no male tabs — cleaner 24mm seam vs old 50mm)
- T-slot geometry: 10mm narrow opening at edge (7mm stem depth) → 14mm wide pocket (5mm head depth)
- 12mm rail width on each edge
- Crossbars at X=84.19 and X=165.25 (scaled for wider panel)
- Mesh pause at layer 12 (Z=2.4mm at 0.2mm layer height)
- **Print TWO identical copies, join with dogbone coupler keys at both seams**
- Generator: `gen_outer_v3.py`

#### Inner Column V4 — Lap Joint
- **Panel:** 135.1 × 232.6 × 3.0mm (1.5mm backing + 1.5mm tooth layer)
- **Assembled cylinder:** OD 86.0mm, ID 80.0mm, wall 3.0mm
- **Clearance from 3" aluminum tube:** 1.9mm per side (76.2mm tube OD)
- **Cap fit:** OD 86mm fits inside cap inner lip (86.4mm ID) with 0.2mm gap
- **Lap joint tabs** for glue + clamp assembly:
  - Left edge: 8mm wide, layers 1-7 only (Z=0 to 1.5mm) — prints on bed
  - Right edge: 8mm wide, layers 8-15 only (Z=1.5 to 3.0mm) — **NEEDS SLICER SUPPORT** (cantilever)
- Frame: 6mm crossbars at thirds, 8mm top/bottom borders, 6mm middle bar
- Mesh pause at layer 8 (Z=1.5mm at 0.2mm layer height)
- **Print TWO identical copies, glue + clamp at lap seams**
- Generator: `gen_inner_column.py`

#### Cap V4 — Printed and Confirmed
- 166mm outer disk diameter
- 153mm outer lip OD (registers on outer cylinder 152.4mm ID)
- 86.4mm inner lip ID / 90.4mm inner lip OD (goes around inner column 86mm OD)
- Old undersized cap (that fell through) works as interior support ring sitting inside the bore
- Generator: cap section in `gen_capsule_frame_v2b.py` (dimensions updated inline)

#### Coupler Keys V4 — 18 Solid Dogbones
- **Key dimensions:** 25mm × 13.5mm × 2.8mm (updated from caliper measurements)
- End wings: 5.5mm × 13.5mm, center stem: 14mm × 9.5mm
- 18 solid keys (9 per seam × 2 seams), 0 slotted (both edges female, no male connectors)
- Layout: 3 rows × 6 columns on one plate
- Keys act as male-to-male bridges across two female T-slot pockets at each seam
- Generator: `gen_keys_final.py`

#### Assembly Order
1. Print 2× inner column halves (with slicer support for right-edge cantilever tab)
2. Glue + clamp inner column lap joints
3. Print 2× outer panels (pause at layer 12 for mesh embedding)
4. Print 1× coupler key plate (18 keys)
5. Join outer panels with dogbone keys at both 24mm seams
6. Wrap bridal mesh around inner and outer cylinders
7. Pack Expedry-treated down in annular void between columns
8. Cap seals assembly — outer lip on outer cylinder, inner lip around inner column
9. Capsule drops freely over aluminum steam generator tube onto load cell

### Helios Steam Generator — Wiring Status (April 29, 2026)

#### Aluminum Column Steam Generator (replacing old sonic humidifier setup)
New components wiring into existing Pi + relay HAT enclosure:
- 2× 12V 40W cartridge heaters (heat pegs) — in aluminum column base
- 1× peristaltic pump (12V DC) — drips water onto heated plate
- 1× SHT41 temp/humidity sensor (I2C, addr 0x44) — inside column
- 1× SDP810 differential pressure sensor (I2C, addr 0x25) — inside column
- 1× MAX31855 thermocouple amplifier (SPI, CE0) — K-type TC on aluminum puck
- 1× DS18B20 temperature probe (1-Wire, GPIO4) — inside column
- 1× sonic humidifier disc (RETAINED from old setup, one only)
- Sensors + pump tube route through removable column cap

#### Power Supply
- **In-box PSU:** 12V 60W / 5A LED driver (IP67 waterproof) — **UNDERSIZED for 2× 40W heaters**
- **New PSU (ready to swap):** ALITOVE ALT-1230T — **12V 30A 360W** — more than enough for everything
- PSU output wires: Brown = positive (+), Blue = negative (−)
- PSU COM terminal = ground/negative
- Distribution block in box: 3rd terminal from bottom = 12V, wired by Mike

#### SSR (Solid State Relay)
- **Model:** DMWD SSR-10 DD — DC input (3-32VDC trigger), DC output (5-60VDC, 10A max)
- **This is the correct SSR type** for switching 12V DC loads (NOT the SSR-25DA which is AC-only)
- **Wiring:**
  - Terminal 1: PSU brown (+12V in)
  - Terminal 2: heater leads out (+)
  - Terminal 3 (+): Pi GPIO17 (Pin 11) — trigger
  - Terminal 4 (−): Pi GND (Pin 6) — trigger ground
- **RESOLVED (2026-04-29):** SSR was NOT faulty — polarity was reversed. Rewired correctly and validated with GPIO17 toggle test (10s ON/OFF). Works perfectly.
- **Pull-down resistor recommended:** 10kΩ between GPIO17 and GND to prevent floating HIGH at boot triggering SSR
- **Andrew's preference:** Use SSR for heater control, NOT the relay HAT. Relay HAT reserved for humidifier, pump, other loads.

#### Pi GPIO Allocation (Helios Pi) — UPDATED 2026-05-13 (hardware I2C bus 1)
| Pin | GPIO | Function | Status |
|-----|------|----------|--------|
| Pin 1 | 3.3V | Power — SHT41, SDP810 VDD, MAX31855 | Wired |
| Pin 3 | GPIO2 (SDA) | **Hardware I2C bus 1 SDA** — SHT41 (0x44) + SDP810 (0x25) | **Validated 2026-05-13** |
| Pin 5 | GPIO3 (SCL) | **Hardware I2C bus 1 SCL** — SHT41 + SDP810 | **Validated 2026-05-13** |
| Pin 6 | GND | Common ground bus (SSR, sensors) | Wired |
| Pin 14 | GND | SDP810 GND (red wire) | Wired |
| Pin 7 | GPIO4 | 1-Wire — DS18B20 (needs 4.7kΩ pull-up) | Planned |
| Pin 11 | **GPIO17** | **SSR trigger (+) for cartridge heaters** | **Validated** |
| Pin 21 | GPIO9 (MISO) | SPI — MAX31855 DO | **Validated** |
| Pin 23 | GPIO11 (SCLK) | SPI — MAX31855 CLK | **Validated** |
| Pin 24 | GPIO8 (CE0) | SPI — MAX31855 CS | **Validated** |
| Relay HAT | Channels 1-4 | Humidifier, pump, TBD (addr 0x10) | Existing |

#### SDP810 Wiring — LOCKED 2026-05-13 (HARDWARE I2C BUS 1)
**Critical lesson:** SDP810 does NOT work on software I2C (bus 15 via dtoverlay i2c-gpio) — bit-banged timing isn't tight enough. Must use hardware I2C bus 1 on the dedicated Pi pins (3 + 5).

**Pin 1 of the sensor is SCL, NOT VDD.** Per Sensirion datasheet (SDP8xx-Digital v1.1, April 2019, section 4):

| SDP810 Pin | Signal | Wire Color (v2, updated 2026-05-29 for 36" cable run) | Goes To |
|------------|--------|------------|---------|
| Pin 1 | **SCL** | yellow | Pi **Pin 5** (GPIO3, hardware SCL) |
| Pin 2 | **VDD** | red | Pi **Pin 1** (3.3V) |
| Pin 3 | **GND** | black | Pi **Pin 14** (GND) |
| Pin 4 | **SDA** | blue | Pi **Pin 3** (GPIO2, hardware SDA) |

*(Original v1 colors were yellow/orange/red/brown — rewired with conventional colors during wine fridge build.)*

**No external pullups required** — Pi hardware I2C bus 1 has built-in 1.8kΩ pullups on GPIO2/3.

**Detection quirk:** SDP810 does NOT respond to `i2cdetect` quick-write probe on some buses, but does ACK on hardware bus 1. To prove it's alive:

```bash
sudo i2cdetect -y 1                              # should show 0x25 and 0x44
sudo i2ctransfer -y 1 w2@0x25 0x36 0x1E          # start continuous DP measurement
sleep 1
sudo i2ctransfer -y 1 r9@0x25                    # returns 9 bytes: DP MSB/LSB/CRC, T MSB/LSB/CRC, scale MSB/LSB/CRC
```

**Reading decode:**
- DP raw / 60 = pressure in Pa (SDP8xx-500Pa scale factor)
- T raw / 200 = temperature in °C
- Scale factor = 60 (constant for -500Pa variant)

**Validated 2026-05-13:** read 0xff 0xfd 0xce 0x15 0x4e 0xba 0x00 0x3c 0x39 → -0.05 Pa, 27.27 °C, scale 60. Chip is alive and accurate.

**bus 15 software I2C overlay can be removed** from /boot/firmware/config.txt — no longer used.

#### SHT41 #1 Wiring — LOCKED 2026-05-29 (in-column, software I2C bus 15)
Stays on software I2C bus 15 (works fine for SHT41 — SDP810 is the picky one).

| SHT41 Pad | Signal | Wire Color (v2, updated 2026-05-29) | Goes To |
|-----------|--------|------------|---------|
| VDD | 3.3V | red | Pi **Pin 1** (3.3V, or Pin 17 backup) |
| GND | GND | black | Pi **Pin 6** (GND, or Pin 9 backup) |
| SCL | clock | blue | Pi **Pin 22** (GPIO25, software I2C bus 15 SCL) |
| SDA | data | white | Pi **Pin 15** (GPIO22, software I2C bus 15 SDA) |

I2C address: 0x44 (fixed — cannot have two SHT41s on the same bus).

#### SHT41 #2 — chamber RH sensor (PLANNED for Test 2 humidity PID)
Mounts inside the wine fridge chamber for chamber-air RH/temp. Cannot share bus 15 with SHT41 #1 (same 0x44 address). Plan:
- **Share hardware I2C bus 1 with SDP810** — no address conflict (SDP810 at 0x25, SHT41 at 0x44).
- Wire colors TBD on install; recommend matching the SDP810 convention (red=VDD, black=GND) but using DIFFERENT colors for SDA/SCL than SDP810's blue/yellow to avoid confusion (e.g., green=SCL, white=SDA).
- 36" cable run requires twisted-pair shielded cable + 4.7kΩ pullups at sensor end.

#### MAX31855 Wiring — LOCKED 2026-05-29 (puck thermocouple, hardware SPI bus 0 CE1)
Board sits at back panel near the Pi; only the K-type TC probe extends into the puck. No cable lengthening required.

| Wire | Signal | Pi Pin | Notes |
|------|--------|--------|-------|
| Red | Vin (3.3V) | **Pin 17** | shared 3.3V rail with SHT41 #1 |
| White | GND | **Pin 39** | any GND works |
| Yellow | DO (MISO) | **Pin 21** | GPIO9, hardware SPI MISO |
| Orange | CLK (SCLK) | **Pin 23** | GPIO11, hardware SPI SCLK |
| Brown | CS (CE1) | **Pin 26** | GPIO7, CE1 (Pin 24/CE0 dead on this Pi) |

K-type thermocouple at screw terminal:
- **Red TC wire** → left screw (T+)
- **Yellow TC wire** → right screw (T−)
- IEC convention (opposite of ANSI labels). If puck temp drops instead of rises when heated, swap.

#### 3.3V + GND Distribution (PLANNED, v2)
Pi header has only 2 dedicated 3.3V pins (Pin 1 + Pin 17) — exhausted by SDP810 + MAX31855. For all new sensors (SHT41 #2, future additions), use a distribution block:
- **3.3V bus block** — one wire from Pi Pin 17 (or Pin 1) → CESFONJER lever connector OR DIN terminal block → fan out to all sensor VDD wires
- **GND bus block** — one wire from any Pi GND pin → distribution block → fan out to all sensor GND wires
- Cleaner than stacking multiple wires into Pi header pins; allows hot-swap of sensors without disturbing Pi.

#### Relay HAT
- 4-channel relay DDL board (orange HUI KE relays)
- I2C controlled, addr=0x10
- **INVERTED LOGIC:** 0x00 = relay ON, 0xFF = relay OFF
- Protocol: `bus.write_byte_data(0x10, channel, value)` where channel=1-4
- DIP switches: both OFF
- Channel allocation:
  - CH1: Sonic humidifier (existing)
  - CH2: **Peristaltic pump** (INTLLAB DP-DIY, 12V 5W, 0.42A)
  - CH3: Available
  - CH4: Available

#### Peristaltic Pump
- **Model:** INTLLAB DP-DIY — 12V, 5W (0.42A)
- **Wiring:** 12V from distribution block → Relay CH2 COM → CH2 NO → Pump + (red dot spade) → Pump − → PSU COM (ground)
- **Speed:** Full speed is WAY too fast for drip application — needs pulse control (0.5s ON / 10-15s OFF)
- **Polarity:** Red dot on plastic housing = positive terminal. Wrong polarity = reverse flow direction (just swap leads)

#### Validated Systems (2026-04-29)
- [x] SSR-10 DD — polarity fixed, GPIO17 toggle test passed
- [x] SDP810 differential pressure — I2C 0x25, reading 0.00 Pa (correct at rest)
- [x] SHT41 temp/humidity — I2C 0x44, reading 74.9°F / 30.7% RH
- [x] MAX31855 thermocouple — SPI CE0, reading 78.3°F (puck temp)
- [x] Heater cartridge — SSR fires on GPIO17 HIGH, shuts off on LOW
- [x] Peristaltic pump — Relay CH2, ON/OFF validated from Pi
- [x] **Web dashboard** — Flask app at http://<pi-ip>:5000, live sensor charts + controls
- [x] **All 4 sensors + 2 actuators running simultaneously on dashboard**

#### Known Issue: MAX31855 TC Short to GND
- Intermittent "TC short to GND" fault when thermocouple tip contacts aluminum puck directly
- Fix: Kapton tape between TC tip and puck surface (insulates ground loop, still conducts heat)
- Also: route TC wires away from heater power leads to reduce noise

#### SHT41 I2C Note
- SHT41 uses single-byte commands, NOT register addressing
- Must use `bus.write_byte(0x44, 0xFD)` then raw `i2c_msg.read()` — NOT `write_i2c_block_data` or `read_i2c_block_data`
- Soft reset command: `bus.write_byte(0x44, 0x94)`

#### TODO (Pre-Demo — Friday April 30)
- [ ] Swap in ALITOVE 360W PSU (both cartridges need full power for fast heat-up)
- [ ] Kapton tape on TC tip → puck (fix ground fault)
- [ ] Build insulator stand for hot aluminum column
- [ ] Assemble capsule frame (inner + outer columns, down fill)
- [ ] Route pump tubing into column
- [ ] Add pump pulse logic to dashboard (0.5s ON / 10-15s OFF cycle)
- [ ] Test full steam generation cycle: heat puck to 250°F → pulse water → monitor humidity rise

#### TODO (Post-Demo)
- [ ] Add 10kΩ pull-down resistor on GPIO17 → GND (boot safety)
- [ ] Wire DS18B20 to GPIO4 (4.7kΩ pull-up needed)
- [ ] Add PID temperature control to dashboard
- [ ] Add CSV data logging for test runs
- [ ] PWM pump speed control via MOSFET (replace relay for finer flow rate)

## Related Projects
| Project | Repo | Description |
|---------|------|-------------|
| FUZE Atlas | fuzeatlas | Multi-portal web app |
| fuzefaq.com | fuzecost | Public landing page |
| **Helios** | **helios** | **Expedry Capsule test apparatus (humidity chamber)** |
| **Solaris** | **N/A (standalone Pi)** | **IR Heat Deflection + Sweat Egress test rig** |

## Load Cell LCD/Control Enclosure — 3D Printed Clamshell (May 29, 2026)

This is a purpose-built two-piece clamshell that houses the salvaged Bonvoisin LCD board + button strip + battery + RS232 + DC jack + power switch for the Helios v2 hanging load cell setup. It mounts to the new fab load cell carrier shelf (~20"L × 7"W) that slides into the wine fridge as a removable shelf.

### Files (all in `/Users/a801/Desktop/helios/`)
- `lcd_enclosure.scad` — master SCAD with `PART = "both"` for side-by-side preview
- `lcd_enclosure_FRONT.scad` — front half only (with `PART = "front"`)
- `lcd_enclosure_BACK.scad` — back half only (with `PART = "back"`)
- `fuze_logo_clean.svg` — REQUIRED — clean-path FUZE logo extracted from Fuze_Logo_2019.ai. **Must live in the same directory as the .scad files** because OpenSCAD's `import()` is relative to the .scad.
- `render_lcd_stls.sh` — bash script that invokes OpenSCAD CLI to produce both STLs

### What the Enclosure Houses
| Component | Source | Mount |
|-----------|--------|-------|
| Bonvoisin LCD PCB (133×41mm, 4× M3 holes at 126.5×33mm) | Salvaged from Bonvoisin scale | 4× standoff posts from inside front face, 4mm tall, with M3 heat-set inserts |
| Button strip PCB (5 tactile keys: POW/CAL/O/T/UNIT/COU) | Salvaged from Bonvoisin scale | Slide-in side rails on back-half interior |
| 7.4V Li-ion battery pack (19 × 17 × 80mm) | Bonvoisin internal battery | Loose in cavity bottom area |
| KCD11 rocker switch (18.5×11.5mm panel cutout) | Bonvoisin original | Snap-in to back face |
| 5.5/2.1mm DC barrel jack | Bonvoisin original | Ø11mm round pass-through in back face |
| DB9 RS232 panel connector | New | Trapezoidal D-shape cutout (DIN 41652) in back face with 2× M3 mounting holes |

### Locked Dimensions (CURRENT — Andrew's specs)
| Parameter | Value | Notes |
|-----------|-------|-------|
| PCB_W × PCB_H | 133 × 41mm | LCD PCB |
| PCB_MNT_DX × PCB_MNT_DY | 126.5 × 33mm | Mounting hole spacing C-to-C |
| LCD window | 103 × 30mm | Centered laterally |
| LCD_TOP_INSET | 5mm | from inside top to top of LCD window |
| PCB_LCD_OFFSET | 7mm | PCB center sits 7mm BELOW LCD center (LCD is high on the PCB) |
| Buttons | 5× at X = -59, -36.5, 0, +36.5, +59mm | Ø4.4mm actuator pass-through |
| Button body pockets | 6.4 × 6.4 × 1.5mm | recessed INSIDE wall at each button → wall locally 1.5mm thick → 1.9mm actuator protrusion |
| BTN_GAP_FROM_LCD | 25mm | Vertical gap between LCD bottom and button row |
| BTN_STRIP_W × BTN_STRIP_H | 130 × 12mm | Button strip PCB |
| Front wall WALL | 3.0mm | bulked from initial 2.5mm |
| INTERNAL_DEPTH | **100mm** | bumped up per Andrew for battery + future hardware/sensors |
| FRONT_HALF_DEPTH | 12mm | shallow cap |
| BACK_HALF_DEPTH | 91mm | deep box |
| Outer W × H | 169 × 106mm | Total external footprint per half |
| FRONT_MARGIN_X | 15mm | lateral pad around PCB |
| BOTTOM_PAD | 35mm | space below button row for battery bay |
| PCB_STANDOFF_H | 4mm | LCD top FLUSH with outside of front face (3mm WALL + 4mm standoff + 7mm LCD-above-PCB = LCD at Z=0) |
| PCB_STANDOFF_OD | 8mm | Ø |
| Heat-set insert | Ø4.2mm × 5mm deep | for M3 brass inserts |
| Clamshell joins | 4× corner M3 | screw from front into back half corner bosses |
| Wall mount | None — VHB tape per Andrew 2026-05-29 | No ears/feet, smooth flat sides |

### Back-Face Cutouts
- **DB9 RS232** (upper center): proper trapezoidal D-shape per DIN 41652 — 25.40mm bottom × 19.05mm top × 12.55mm tall + 2× Ø3.2mm M3 mounting holes at ±12.50mm
- **DC barrel jack** (lower left): Ø11mm round pass-through (wires pre-soldered, jack body held by friction/epoxy — Andrew's call: "we can just run it in a circular hole though")
- **KCD11 rocker switch** (lower right): 18.5mm tall × 11.5mm wide snap-in cutout

### FUZE Logo (front face, debossed)
- Imported from `fuze_logo_clean.svg` — clean SVG extracted from Fuze_Logo_2019.ai by stripping the gradients and clipPaths (kept only the artwork paths)
- 1mm debossed into outside of front face
- Symbol center dot positioned EXACTLY on the center button (KEY3 / O/T, at X=0, Y=BTN_CY)
- Mirrored in X so it reads correctly when viewed from outside (compensates for SCAD orientation)
- Default scale 0.35 → symbol ~12mm, full logo ~62mm wide
- Optional sacrificial bridge floor inside the deboss (`FUZE_DEBOSS_SUPPORT = true`) — 0.4mm thick at 0.4mm above outer face, helps PC bridge cleanly
- **Embossed/raised mode REJECTED** because that would require supporting the entire front face during print (the whole face would float 1mm above the bed on tiny logo features). Deboss only.

### Print Orientation
- **FRONT half**: print open side DOWN on bed (LCD window face UP), Bambu H2D, PolyMax PC Tough Blue, 0.2mm layers, 3 perimeters, 25% infill, 12mm brim, 8mm join lip prints last
- **BACK half**: print open side UP on bed (back wall on bed), same settings, 12mm brim around the ~169×106mm footprint. ~91mm tall — long print (~8–12 hours)

### Print Settings That Matter (PC Tough on Bambu H2D — May 29 2026 lesson learned)
The first PC print of the back half failed due to bed adhesion (corner lift → blobby mess). Settings for a successful PC print:
- **Bed: 105–110°C** (NOT 100°C — Polymaker datasheet 100–110 means run 108)
- **Nozzle: 270°C**
- **Magigoo PC OR Elmer's purple glue stick on the plate** — mandatory on textured PEI
- **Switch to Cool Plate / Smooth PEI side if available** — way better PC adhesion than textured
- **Brim: 12mm with ≥10 perimeter loops** — structural for the print, not optional
- **First layer speed: 15 mm/s, line width 0.5mm** — slow + fat = bonded
- **Dry the filament 80°C × 8h before print** — wet PC bubbles, kills layer 1
- **Chamber door + lid CLOSED**, preheat chamber 20 min before print starts — no drafts; PC contracts hard on cooldown and will lift corners on the slightest draft
- **Layer time min 15s, fan 0% first 3 layers then 30%**
- **Z-hop 0.4mm, avoid crossing walls ON**

### Mounting (to load cell carrier shelf)
- The enclosure mounts to the new-fab load cell shelf (~20" × 7" black-painted steel/aluminum) via **double-stick VHB tape** for now
- Side ears + bottom feet options exist in the SCAD (`MOUNT_STYLE = "side_ears" | "bottom_feet" | "none"`) — currently set to `"none"` for clean flat sides
- The load cell carrier shelf is THE NEW FAB — NOT the original Bonvoisin shell. Only the bare strain-gauge beam was salvaged from the Bonvoisin.

### Internal Layout (with 100mm depth)
- Front face: LCD PCB pressed against standoffs (LCD module flush with front face)
- Button strip: in side rails near front, actuators poking through button holes
- Battery (19 × 17 × 80mm): rests in bottom area of cavity (laterally along the 145mm width)
- RS232 driver board (e.g. MAX3232 module): plenty of room behind LCD PCB
- Lots of headroom for future sensors / additional boards / wiring harness

### Things I Got Wrong During Development (so the next session knows)
1. Originally put PCB standoffs on the BACK wall 100mm from the LCD. Bug — fixed by moving them to inside of FRONT face.
2. Originally had `PART = "both"` stacking halves in Z (looked like one block). Fixed to lay them side-by-side on the build plate.
3. Originally used wrong DB9 cutout dimensions (30.81mm connector body width instead of 25.40mm panel cutout width) — M3 mounting holes fell INSIDE the trapezoid and disappeared. Fixed.
4. Originally assumed LCD was centered on PCB. Wrong — LCD is high on the PCB, top mount hole is only 4mm from PCB top. Added `PCB_LCD_OFFSET = 7.0` to push PCB down so standoffs don't clip the wall.
5. First attempt at FUZE logo was a primitive 6-spoke reconstruction. Andrew correctly called it garbage — switched to importing the real SVG paths from the .ai file.
6. Initially had the back-stop bar across the button strip — removed per Andrew, the side rails grip the strip fine.
7. Initially gave PCB standoffs on the back floor — they got carved away by the hollow operation. Fixed by moving them outside the difference() block.

### Open Items For The Next Session
- **First good back-half print** — apply the PC adhesion fixes above and retry
- **Heat-set insert installation** — need 4× M3 inserts for clamshell screws + 4× M3 inserts for LCD PCB standoffs. Use a soldering iron at 220-240°C
- **Verify button protrusion** — actuator should poke ~1.9mm out of the front face. If too tight, deepen `BTN_BODY_POCKET_D` from 1.5 to 2.0mm
- **Optional: source the DB9 chassis-mount jack** — confirm pin 2/3/5 (TX/RX/GND) wiring matches what the Bonvoisin RS232 expects
- **VHB mount the printed enclosure** to the load cell carrier shelf when ready
- **Update the bigger Helios v2 plan** with the enclosure now done (Task #51: Mount load cell beam + capsule hanging hook; Task #52: full v2 integration test)

## LCD Enclosure — CORRECTED LOCKED VALUES (Helios 5 session, May 30 2026) — SUPERSEDES ALL ABOVE
The first PC print exposed several errors that all traced back to stale notes. These are the verified, caliper-confirmed values. Files: `lcd_enclosure_FRONT.scad`, `lcd_enclosure_BACK.scad`, master `lcd_enclosure.scad` — all three carry identical values.

### Face size — FRONT MUST MATCH ALREADY-PRINTED BACK BOX
- **OUTER FACE = 169.0 W × 105.4 H mm** (both halves). Width 169 is correct/perfect — DO NOT change.
- Height 105.4 comes from **`BOTTOM_PAD = 35.0`** (NOT 50). The front had been bloated to 120.4mm because BOTTOM_PAD got bumped 35→50 "for logo headroom." That 15mm is what made the front taller than the back box. Reverted to 35.
- Depths unchanged: `FRONT_HALF_DEPTH = 12`, `BACK_HALF_DEPTH = 91`, `INTERNAL_DEPTH = 100`. The back box (6-hr print) is KEPT as-is; only the front (1-hr) gets reprinted to match.

### LCD window — datumed to PCB center
- LCD glass **102 × 30 mm**, **centered on the PCB** (5.5mm margin top AND bottom: 5.5+30+5.5 = 41mm PCB height). The old "LCD is high on the PCB, 7mm offset" assumption was WRONG.
- PCB: **41 mm tall × 132.65 mm wide** (kept `PCB_W = 133` in SCAD so OUTER_W stays 169; the 0.35mm is absorbed by side margin). Mounting holes 126.5 × 33 c-c.
- Window now tracks PCB center: `LCD_CY = y_from_center(PCB_CY_FROM_TOP)`. `PCB_LCD_OFFSET = 7.0` now just drops the PCB to 27mm-from-top for 6.5mm top-edge clearance (NOT a glass offset). Glass assumed horizontally centered on PCB (Andrew confirmed).
- `LCD_W = 102` (was 103), `LCD_H = 30`.

### Buttons — caliper-confirmed center-to-center
- **`BTN_X = [-59, -37, 0, 37, 59]`** (center-to-center from the center button; measured directly). Old ±36.5/±59 were ~0.5mm off.
- Button row **Y = -12.5** (driven by the 105.4 face) — this matches the back box's button-strip rails, which were printed in the BOTTOM_PAD=35 era. The buttons looked "off" mostly because the row dropped 7.5mm when the height was corrected.
- **`BTN_HOLE_CUT_D = 5.4`** — actual actuator hole Ø (+1mm over the 4.0mm post = 0.70mm clearance/side, for assembly variance). NOTE: `BTN_HOLE_D = 4.4` is kept ONLY for the height/button-Y layout math — do NOT route the cut through BTN_HOLE_D or you'll change OUTER_H and BTN_CY. The cut uses BTN_HOLE_CUT_D.
- Body pockets still `BTN_BODY_POCKET_SQ = 6.4` — bump if the 6mm bodies bind.

### DB9 (RS232) — real NorComp DE-9 panel spec
- Old file had a 1"-wide cutout with screws at 25mm → screws punched into the opening. CORRECTED to NorComp DE-9: cutout **15.90 wide / 13.47 narrow / 12.50 tall**, mounting screws **24.99 c-c**, Ø3.2. Gives 2.94mm of solid between hole and cutout.
- **DB9 + DC jack + rocker switch live on the BACK half.** The back box in hand still has the OLD oversized DB9 — this fix only helps a future back reprint. Hand-fix the existing back if needed.

### FUZE logo — regenerated + inlay
- Old `fuze_logo_h.scad` was a garbage trace (lost the 6 dots). REGENERATED from `FUZE Logo Horizontal (2).ai` (it's a PDF) via `pdftocairo` → raster → `cv2` contour trace. 13 contours (4 letters + connected symbol body + 6 dots + ™), center-anchored at native bbox center **(27.6948, 8.5813)** so `FUZE_LOGO_X=0` truly centers it.
- Logo deboss now **`FUZE_LOGO_SCALE = 1.9`** (≈102 × 30mm), **`FUZE_LOGO_Y = -32.7`** — shrunk from 2.4× because 2.4× (38mm tall) does not fit the shorter 105.4 face. `FUZE_DEBOSS_SUPPORT = false`.
- **STALE: `FUZE_logo_inlay_white_TPU.stl` was generated at 2.4× (129mm) and NO LONGER matches the 1.9× deboss.** Must regenerate the white TPU inlay at 1.9× before printing it. 11 pieces, 1.0mm thick, 0.125mm clearance, ™ dropped.

### Print note
Reprint ONLY the front from `lcd_enclosure_FRONT.scad` (open-side-down, LCD face up). It mates with the existing back box.
