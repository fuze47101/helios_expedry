# Solaris FZ-500 — Test Protocol

Standard operating procedure for IR heat deflection + sweat egress tests on FUZE-treated fabrics using the Solaris FZ-500 test rig.

**Revision:** 2026-04-21 (v1.0) · **Maintainer:** Andrew Peterson / FUZE Biotech

---

## 1. Safety

- **AC mains.** The SSR enclosure carries 120VAC to the IR lamp. Never operate with the enclosure open. Verify GFCI upstream of the outlet box. If anything smells, sparks, or visibly fails, kill power at the wall — do not rely on the software stop alone.
- **Hot plate.** The aluminum heat plate can exceed 200°C during extended lamp-on runs. Treat as an active burn hazard until both plate TCs read <45°C.
- **IR lamp.** Do not stare at the lamp element when energized. Wear IR-rated safety glasses for runs >5 min.
- **Fabric ignition.** Synthetic fabrics can combust above ~350°C. If either TC exceeds 250°C, stop the test immediately (software, then wall if needed). Treated fabric is designed to deflect, not to be fireproof.
- **Fire suppression.** Keep a CO2 extinguisher within arm's reach. Do not use water near the rig.
- **Emergency stop.** Dashboard **Stop Test** button kills lamp power via GPIO 17. For redundancy, unplug the SSR's AC feed at the wall.

---

## 2. Pre-flight checklist

Complete every item before the first test of the day. All must pass.

### 2.1 Hardware

- [ ] Pi powered by the CanaKit 27W USB-C supply (not a phone charger, not an older Pi 4 supply)
- [ ] Pi power LED is solid green. Amber/orange = under-voltage → SPI will be unreliable → stop and fix PSU
- [ ] IR lamp mounted 200mm above fabric plane, 260mm above plate — verified with rule/calipers
- [ ] Lamp centered over the aperture cutout in the frame
- [ ] SSR enclosure closed, AC cord plugged into a GFCI outlet
- [ ] Heat plate painted matte flat black, high-temp rated (≥500°F), no chips or bare aluminum, facing UP
- [ ] TC-A and TC-B mounted on plate **underside**, diagonally opposite quadrants, 25–30% in from edge
- [ ] TC bond: MX-6 paste under bead + electrical tape retention (interim — Arctic Alumina epoxy bond post-Portland)
- [ ] DS18B20 probe positioned in the ~60mm air gap between fabric and plate; not touching plate, not in direct lamp cone
- [ ] CO2 extinguisher within arm's reach
- [ ] IR-rated safety glasses on the operator

### 2.2 Software

- [ ] Pi boots cleanly; WiFi connects to ISEEYOU2 (check dashboard header)
- [ ] Dashboard reachable at `http://solaris.local:5000/` or the Pi's current IP
- [ ] Header status dots all **green**: SPI, DS18B20, Lamp, WiFi
- [ ] All three readouts show numbers (not `--`)
- [ ] All three readouts within ±2°C of ambient room temp
- [ ] Manual lamp toggle fires cleanly: click ON → audible SSR click → lamp on → click OFF → lamp dark
- [ ] `~/solaris_logs/` directory exists on the Pi (CSV destination)

### 2.3 Sensor sanity — 30 seconds

Validates each channel is actually reading live, not stuck or cross-wired.

1. Pinch TC-A bead between two fingers for 5s. TC-A trace climbs 3–5°C. TC-B and air gap stay flat.
2. Pinch TC-B bead for 5s. TC-B climbs. TC-A and air gap stay flat.
3. Wrap the DS18B20 probe tip in your fist for 10s. Air gap trace climbs 2–4°C.
4. Release all three. All three decay back to ambient within 30s.

If any step fails or the wrong trace moves, **do not proceed**. See §9 Troubleshooting.

---

## 3. Test parameters

### 3.0 Geometry (MUST BE LOCKED BETWEEN RUNS)

These distances govern the IR irradiance on the fabric. Inverse-square law is unforgiving — a 2cm drift in lamp height contaminates every comparison. Mark lamp and plate positions with tape on the stand and table. Re-measure with calipers or a rule before each session. Tolerance: **±5mm**.

| Measurement | Value | Why it matters |
|---|---|---|
| Lamp filament centerline → fabric top surface | **200mm** | Governs IR power reaching the sample — the input side of the test |
| Lamp filament centerline → plate surface | **260mm** | Derived (fabric + ~60mm air gap); plate sees ~60% of fabric irradiance |
| Fabric top → plate surface | **~60mm** | Convective air column; houses DS18B20 air-gap probe |
| Plate diameter (visible aperture) | measure and log | Plate is matte-black 6061 aluminum, ~25cm diameter through the cutout |
| DS18B20 probe position | air column above plate, inside aperture | Not touching plate, not in direct lamp cone |
| TC-A, TC-B bond position | diagonally opposite quadrants, 25–30% from edge | Symmetric around center; see §2.1 |

**Why 200mm to fabric, not plate:** the fabric is what's being tested. Irradiance at the fabric is the "dose" — the plate is a downstream detector.

**Re-measure any time you:** move the rig, replace the lamp bulb, swap the plate, reposition the stand, or come back from transport.

### 3.1 Dashboard inputs

Three user inputs in the dashboard's Test Sequence card.

| Parameter | Default | Purpose | When to change |
|---|---|---|---|
| Warmup (s) | 30 | Captures clean baseline before lamp fires | Increase for more baseline samples |
| Lamp on (s) | 180 | Active measurement period | 120 for rapid demos, 300 for stronger treated/untreated separation |
| Cooldown (s) | 60 | Captures decay slope; does NOT fully reset plate | 120 for more complete decay curve |

### 3.2 Recommended parameter sets

| Use case | Warmup | Lamp on | Cooldown | Total |
|---|---|---|---|---|
| Portland demo / early R&D | 30 | 180 | 60 | 4m 30s |
| QC / batch validation | 30 | 300 | 120 | 7m 30s |
| Rapid screening (triage) | 15 | 90 | 30 | 2m 15s |
| Endurance / thermal limit | 60 | 600 | 180 | 14m |

Between every run, allow **5–10 min idle** for the plate to fully reset to ambient.

---

## 4. Per-test procedure

### 4.1 Reset verification

Before every test, confirm the plate has recovered from the previous run:

- TC-A and TC-B both within ±2°C of ambient
- TC-A and TC-B within ±1°C of each other
- Air gap within ±2°C of ambient

If any value is outside these bounds, wait. Typical recovery after a 180s lamp-on run is 5–10 min; 10–15 min after a 300s run.

### 4.2 Sample handling

1. Retrieve sample from its labeled container.
2. In your lab notebook, log: sample ID, condition (baseline / untreated / treated), treatment batch number, time of day, operator initials.
3. Inspect the fabric for defects — holes, folds, contamination, moisture. Reject if compromised.
4. For fabric tests: center the sample over the heat plate with ~10mm overhang on each side. Ensure it lays flat.
5. For baseline runs: leave the plate bare; confirm nothing is on or above it except the DS18B20 probe.

### 4.3 Run

1. Open the dashboard in a browser (Mac or Pi HDMI kiosk — either works).
2. Confirm all three sensor dots are green and all three readouts are stable.
3. Set Warmup / Lamp on / Cooldown per §3.1.
4. Write the sample ID on a sticky note and place it next to the Pi (critical — test IDs are only embedded in the CSV filename, not the data rows).
5. Click **Start Test**. The phase pill at the bottom of the Test Sequence card will cycle:
   - `warmup` — baseline capture, lamp OFF
   - `lamp_on` — IR lamp energized (indicator glows orange)
   - `cooldown` — lamp OFF, decay capture
   - `done` — test complete, CSV ready
6. Monitor the live chart. Flag any anomaly: sensor dropout, discontinuity in a trace, unexpected rate change, plate TC divergence.
7. When `done` appears, click **Download CSV**.

### 4.4 Emergency stop

Click the red **Stop Test** button. Lamp de-energizes via GPIO 17; test state returns to `idle`; CSV saves with partial data.

If software stop doesn't respond: **unplug the SSR AC cord at the wall**. Then log out the rig and call it before doing anything else.

---

## 5. Data management

### 5.1 CSV destination and naming

Raw files auto-save to `~/solaris_logs/solaris_YYYYMMDD_HHMMSS.csv` on the Pi.

Immediately after each run, rename to the lab convention:

```
solaris_YYYYMMDD_<sampleID>_<condition>_<replicate>.csv
```

Examples:
- `solaris_20260422_S047_treated_r1.csv`
- `solaris_20260422_baseline_r3.csv`
- `solaris_20260422_S047_untreated_r2.csv`

### 5.2 File structure

Each CSV has a header row and one row per sample (1 Hz sample rate, so row count ≈ test duration in seconds).

| Column | Description |
|---|---|
| `t_epoch` | Unix timestamp, seconds |
| `t_elapsed_s` | Seconds since test start |
| `phase` | `warmup`, `lamp_on`, or `cooldown` |
| `tc_a_c` | TC-A plate temperature, °C |
| `tc_b_c` | TC-B plate temperature, °C |
| `air_c` | DS18B20 air-gap temperature, °C |
| `lamp` | SSR state: 0 (off) or 1 (on) |

### 5.3 Backup

**Same day, before leaving the bench:**

```bash
# From the Mac
scp -r fuze@192.168.1.152:/home/fuze/solaris_logs/ ~/Desktop/solaris_data_YYYYMMDD/
```

For Portland or any off-site demo, copy the day's data to a USB stick before packing up the rig. Do not trust cloud sync to survive the drive home.

### 5.4 Post-test review

Before calling a test complete, sanity-check the CSV:

1. Open in Excel, Pandas, or any plotter. Row count should equal `warmup + lamp_on + cooldown` seconds, ±3.
2. Plot `tc_a_c` and `tc_b_c` vs `t_elapsed_s`. They should track within 2°C of each other for the whole run. Divergence >5°C = a TC bond is failing; re-paste before the next test.
3. Record in lab notebook: max plate temp during lamp_on, ΔT_plate (max minus ambient), any visible anomaly in the chart.
4. Compare to the previous replicate under the same condition. Variance >20% = investigate (check fabric placement, lamp height, plate recovery).

---

## 6. Comparison protocol (for efficacy claims)

Any claim about treatment efficacy requires at minimum:

- **3× baseline** — bare plate, no fabric
- **3× untreated** — fabric as-delivered, no FUZE additive
- **3× treated** — fabric with FUZE additive, note batch number

**9 total tests. Budget ~2 hours** (9 × 4m 30s per run + 5 min recovery between = ~85 min running, ~95 min with notebook time).

Order to run in: randomize if possible, otherwise treated → untreated → baseline (so any drift hurts your own case first).

Accept the result only if:

1. Intra-condition variance (3 replicates of same condition) < 10% on ΔT_plate at t=180s
2. Ordering is consistent: `ΔT_baseline > ΔT_untreated > ΔT_treated` (peak plate temp descending)
3. Treated vs untreated gap is meaningful — at least 15% reduction in ΔT_plate, ideally 25%+

If all three hold, the treatment is behaving as designed. If any fail, dig in — don't ship a weak result.

---

## 7. What the numbers mean

### 7.1 TC-A / TC-B (plate thermocouples)

Two MAX31855-backed K-type thermocouples bonded to the plate underside with MX-6 thermal paste. Measures the aluminum plate's bulk temperature. Two channels for redundancy and to detect bond failure — if one starts drifting relative to the other mid-test, that bond is going.

### 7.2 Air-gap DS18B20

OneWire silicon probe positioned 45mm above the plate in the air column between plate and fabric (or bare plate on baseline runs). Measures the convective sink temperature. A hotter air gap = less heat escaping upward = better deflection by the fabric. Secondary metric; supports the plate-temp story.

### 7.3 Derived metrics

| Metric | Formula | What it tells you |
|---|---|---|
| ΔT_plate(180) | max(TC-A, TC-B) at t=180s − ambient | **Primary efficacy metric** |
| Slope_early | dT/dt over first 30s of lamp_on | Sensitive to fabric thermal mass |
| Slope_decay | dT/dt over cooldown phase | Sensitive to fabric insulation properties |
| ΔT_air(180) | air_c at t=180s − ambient | Secondary: convective coupling |
| T_peak | max(TC-A, TC-B) anywhere in run | Safety / upper bound |

---

## 8. Known limitations (v1, 2026-04-21)

Document what v1 of this rig cannot do, so claims stay honest.

- **Lamp geometry.** Manually positioned at 200mm. No closed-loop distance or intensity control. Treat geometry as fixed per session; re-measure between sessions.
- **No humidity measurement.** SHT41 deferred. Sweat-egress claims are indirect — inferred from plate/air-gap thermal response, not measured water vapor. State this clearly in any report.
- **No thermal imaging.** MLX90640 deferred. Assumes uniform sample behavior; may miss edge effects, wrinkles, or local treatment gaps. Consider adding for v2.
- **Cooldown is partial.** 60s cooldown captures decay slope but does not reset the plate. Wait 5–10 min between tests for true ambient reset.
- **Breadboard interconnect.** Wiring is F-M jumpers on a breadboard until the Pi HAT PCB is fabbed (task #21). Reseat jumpers if a sensor dropout occurs; expect occasional intermittent faults until HAT v1 arrives.

---

## 9. Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| SPI TimeoutError in Flask log | Under-voltage from weak PSU | Switch to CanaKit 27W supply; power LED must be solid green |
| DS18B20 reads `--` in UI | Probe not detected on OneWire bus | Check 4.7kΩ pull-up between data and 3.3V; verify `/sys/bus/w1/devices/28-*/` exists |
| DS18B20 reads 85.0°C constant | Power glitch mid-read (ghost reading) | Verify 3.3V rail stable; check parasitic power mode is off |
| Lamp doesn't fire on manual toggle | SSR DC trigger not getting GPIO 17 signal | Check wiring: pin 11 (GPIO 17) → SSR +input; GND to SSR −input. Confirm with `gpioinfo` |
| Lamp stays on after Stop | SSR stuck closed (welded contacts) | **Unplug AC at wall immediately.** SSR must be replaced; do not trust software control |
| TC-A and TC-B diverge >5°C mid-test | One TC bond is failing | Stop test, re-bond divergent channel with fresh MX-6 |
| Chart traces jump or discontinue | Jumper wire unseated on breadboard | Reseat all jumpers; primary motivator for Pi HAT v1 |
| Dashboard shows `--` for a reading mid-test | Sensor returned None (fault flag or dropout) | Stop test; inspect physical connection; check Flask log for warnings |
| WiFi drops mid-test | Router reset or roaming event | Test continues and data still saves locally. Reconnect via Manual WiFi switcher in dashboard |
| Dashboard URL won't load from Mac | mDNS flaky or Pi IP changed | Use IP directly: `hostname -I` on Pi, then `http://<ip>:5000/` |
| SSH times out | macOS Internet Sharing intercepting packets | System Settings → Sharing → Internet Sharing OFF |

---

## 10. Revision log

- **2026-04-21 (v1.0)** — Initial protocol. v1 hardware: 2× MAX31855 (SPI CE0/CE1), 1× DS18B20 (GPIO 4 OneWire), DIWD SSR-25 DA in DIY outlet box, Pi 5 + CanaKit 27W PSU, breadboard interconnect. Dashboard: Flask + Socket.IO + Plotly. Deferred for v2: SHT41 humidity, MLX90640 thermal camera, Digital Loggers IoT Relay, Pi HAT PCB.
