# Polymaker PolyMax PC Tough Blue on the Bambu H2D

First-run guide for SKU **PC02011** (1.75 mm, Tough Blue) on the **Bambu Lab H2D**, written for the Helios insulator stand / load cell stand prints.

---

## TL;DR — the numbers

| Setting | Value |
|---|---|
| Nozzle (printing) | **260 °C** |
| Nozzle (first layer) | **265 °C** |
| Bed | **100 °C** |
| Chamber heater | **50 °C** (on) |
| Fan (first 3 layers) | **0 %** |
| Fan (after layer 3) | **0–20 %** |
| Overhang fan | **40 %** |
| Print speed | **40–60 mm/s** outer wall, **80 mm/s** inner |
| Walls | **4** |
| Top/bottom layers | **5** |
| Infill | **gyroid 30 %** |
| Brim | **5 mm** |
| Z-hop | **0.4 mm** |
| Retraction (direct drive) | **1.2 mm @ 30 mm/s** |
| Build plate | **Engineering Plate + glue stick** (preferred), or **PEI + thin glue** |
| Adhesive | **Magigoo PC** if you have it, otherwise standard Elmer's glue stick |
| Layer height | **0.20 mm** (first run); 0.16 mm for finer features |
| Filament dry? | **Yes — 75 °C × 6 h** in a dryer if it's been out of the bag |

---

## 1. Physical loading on the H2D

### If you have AMS HT (heated AMS) — recommended
1. Power on H2D and the AMS HT.
2. Open Bambu Studio → Device tab → AMS settings → set the slot you'll use to **dry at 70 °C**, **active during print**.
3. Mount the PolyMax PC spool onto an AMS HT slot (spool fits the standard 73mm core).
4. On the touchscreen: AMS → that slot → set filament type to **PC** (or "Custom — Polymaker PolyMax PC Tough Blue" if you imported the profile, see §3).
5. Load: AMS → slot → **Load Filament**. Printer pulls it to the toolhead.

### If you have plain AMS (not HT) or external spool
PC absorbs moisture fast. If a print runs longer than ~4 hours, use the external spool holder with a **drybox** in line.

1. Take the PolyMax PC out of its vacuum bag immediately before printing — do not leave it sitting on the bench for hours.
2. **External spool path** (top-rear of the H2D): hang the spool on the back hook, route through the top filament guide, into the toolhead's external filament entry.
3. On the touchscreen: External filament → **Load Filament** → choose PC profile.

### If filament has been out of the bag > 24 hours
Dry it first: **75 °C for 6 hours** in a filament dryer (or 80 °C × 8 h on a heated bed with a tote over it). PC that's wet will pop and string and the surface will look cloudy.

---

## 2. Build plate choice

| Plate | Works with PC? | Notes |
|---|---|---|
| **Engineering plate** | ✅ best | Wipe with IPA, thin layer of glue stick. Best for engineering filaments per Bambu's own guide. |
| **Smooth PEI** | ✅ at 110 °C | PC sticks *aggressively* to bare PEI — can damage the sheet on removal. Use a thin glue stick layer as a release agent. |
| **Textured PEI** | ⚠️ | Some success, less consistent. |
| **Cool plate / Super tack** | ❌ | Too aggressive a bond — you'll tear chunks out of the plate. |

For both Helios parts (insulator stand + load cell stand), **Engineering plate + glue stick** is the safe choice.

---

## 3. Importing the filament profile

I generated **`Polymaker_PolyMax_PC_Tough_Blue.bbsflmt`** in the helios folder. This is a real Bambu Studio filament bundle (zipped JSON + manifest in the format Bambu Studio expects).

### A. Import (fastest)
1. Open Bambu Studio.
2. **File → Import → Import Configs…**
3. Select `Polymaker_PolyMax_PC_Tough_Blue.bbsflmt`.
4. Bambu Studio loads it under your filament library.
5. In the filament dropdown for an H2D print, choose **"Polymaker PolyMax PC Tough Blue @BBL H2D"**.

The `.filament.json` file next to it is the same data as a human-readable reference — **don't try to import the .json directly**, Bambu Studio only accepts the zipped `.bbsflmt`.

If the import still fails (rare — usually means a Bambu Studio version difference), fall through to method B.

### B. Duplicate and edit (manual — always works)
1. Open Bambu Studio with the H2D selected.
2. Click the filament icon (gear) next to the filament dropdown.
3. Select **Bambu PC @BBL H2D 0.4 nozzle** → click **Duplicate**.
4. Rename to **"Polymaker PolyMax PC Tough Blue"**.
5. Set values from the TL;DR table above.
6. **Save** the profile.

---

## 4. Process / print settings (per part)

These go on the **Process** side (left panel, not filament).

| Process setting | Value | Why |
|---|---|---|
| Layer height | 0.20 mm | Good balance for engineering parts. Go to 0.16 mm if you want finer detail on the lip. |
| First layer height | 0.24 mm | Better adhesion to glue stick. |
| Wall loops | **4** | PC is brittle in thin sections; more walls = more stiffness. |
| Top/bottom shells | **5** | Seals the part against the gyroid infill. |
| Infill pattern | **Gyroid** | Best stiffness-to-weight, prints fast. |
| Infill density | **30 %** (load cell stand) / **40 %** (insulator stand) | Insulator stand is shorter, gets compressed by column weight — more infill helps. |
| Print speed outer | **40 mm/s** | PC needs time to bond layer to layer. |
| Print speed inner | **80 mm/s** | Faster on internal walls. |
| Infill speed | **150 mm/s** | Doesn't affect look — go fast. |
| First layer speed | **25 mm/s** | Slow first layer = adhesion. |
| Travel speed | **300 mm/s** | OK, H2D handles. |
| Brim type | **Outer brim only** | 5mm width. Removes cleanly with PC. |
| Z-hop | **0.4 mm** auto-lift | Avoids stringing on retract over walls. |
| Wipe on retract | **on** | Keeps blobs off vertical surfaces. |

---

## 5. Chamber + environment

- **Door closed** for the entire print.
- **Top glass cover on** — PC really wants the chamber at temp.
- **Auxiliary fan: OFF** — PC chases warping if you cool it.
- **Chamber heater: 50 °C** — set this BEFORE the print starts, let the chamber soak for 5 min.
- **Room temp** — try to print in a stable room (no AC kicking on/off). H2D handles this better than open printers, but PC is sensitive.

---

## 6. First-print checklist (do this once)

Before slicing the actual stand:

1. **Print a 20 × 20 × 20 mm calibration cube** in PolyMax PC at 260 °C / 100 °C bed.
   - Check first layer squish — glue stick coverage uniform?
   - Check overhangs — any sagging on the top face?
   - Check inter-layer bonding — try to snap a wall with pliers. Should require force.
2. **Flow ratio calibration** — Bambu Studio → Calibration → Flow Ratio. Run a Pass 1 + Pass 2 with PolyMax PC. Update the filament profile flow ratio (currently 0.96 — yours will likely land between 0.94 and 0.99).
3. **Pressure advance (optional but worth it)** — Calibration → PA Pattern. Update the profile PA value (currently 0.04).
4. **Save your tuned profile.**

After this, kick off the actual insulator / load cell prints with confidence.

---

## 7. Print orientation for the Helios parts

### Insulator stand (`print_column_insulator_stand.scad`)
- **Stand vertically** — open end up, feet down on the bed.
- The lip underside is a 45° chamfer → prints without supports.
- 4× M5 holes go top-to-bottom; they print clean as vertical holes.
- Total height in PC: ~29.5 mm, OD 110 — small print, ~2 hrs.

### Load cell stand (`print_load_cell_stand.scad`)
- **Stand vertically** — long axis (165 mm) on the bed, height (101.6 mm) on Z.
- Gyroid infill at 30 % carries the top.
- The crosshair on top prints as the final layer — clean.
- ~6–8 hrs print depending on speed.

---

## 8. Removing the part

PC + glue = aggressive bond. Wait until the **bed cools below 40 °C** — the part will pop off on its own. If it doesn't, use a thin spatula gently at one corner; don't pry hard or you'll lift the PEI/Engineering plate coating.

---

## 9. Storage between prints

PolyMax PC absorbs moisture fast. Between prints:
- Back into a sealed bag with the desiccant pack, OR
- Drybox at 15 % RH, OR
- Leave in AMS HT with humidity control set to dry.

If you hear popping at the nozzle on the next print, the spool has absorbed water — dry it again.
