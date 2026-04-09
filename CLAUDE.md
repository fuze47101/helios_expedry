# Memory

## Me
Andrew Peterson, CEO/Founder of FUZE Biotech (801 Inc). Building Expedry moisture resistance testing apparatus for down insulation treated with Expedry Gold.

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

## Related Projects
| Project | Repo | Description |
|---------|------|-------------|
| FUZE Atlas | fuzeatlas | Multi-portal web app |
| fuzefaq.com | fuzecost | Public landing page |
| **Helios** | **helios** | **Expedry Capsule test apparatus** |
