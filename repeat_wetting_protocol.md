# Repeat-Wetting Collapse Test — DWR vs Expedry

**Purpose:** A single conditioned 80% cycle cannot separate DWR from Expedry (06-12: tied, both ~44% under untreated). The hypothesized differentiator is that **DWR collapses over repeat use / higher water and stops releasing**, while Expedry holds its performance. This test stresses that directly.

## Samples (run side by side, identical conditions)
- **Frame F — Goose 800 DWR** (sample 3) — the one expected to collapse.
- **Frame C — Goose 800 Expedry** (sample 2, low ICP ~2.0) — control that should hold.
- (Optional) **Frame G — Goose 800 untreated** (sample 4) — upper-bound reference.

> All PETG-in-channel frames. Subtract the PETG blank (0.167 g abs / 0.184 g ret) per frame. A same-day conditioned empty-frame blank would be even better — run one if time allows.

## Conditioning (ONCE, before cycle 1 — do NOT recondition between cycles)
The whole point is to let moisture accumulate cycle-over-cycle, so condition only at the start:
1. Dehydrator 120 °F, weigh on the balance every ~15 min until mass plateaus (two reads within ~2 mg).
2. Seal in a Ziploc until cool (~15 min).
3. Weigh-in, load on the channel, tare.

## Cycle settings (keep identical every cycle)
Dashboard → Moisture Test (full protocol):
- specimen g: **3.0**
- target RH%: **80** (hold at 80 for cycle 1; consider a 90% variant on a later day)
- wet min: **60**
- dry min: **30**
- dry to RH%: **35**
- Sample ID: **DWR_c1, DWR_c2 …** and **EXP_c1, EXP_c2 …** (CHANGE THE NUMBER EACH CYCLE so filenames are unique — last time the default "sample" collided)

## Procedure
1. Run cycle 1 (wet 60 → dry 30) to completion. **Do not remove or recondition the sample.**
2. Immediately start cycle 2 with the same settings, new Sample ID. Repeat through **5 cycles**.
3. If running F and C on one load cell, alternate them; if two load cells are wired, run simultaneously (preferred — identical chamber conditions).
4. Pull all CSVs at the end:
   `scp 'helios@helios:~/helios/data/*<date>*.csv' ~/Desktop/helios/data/`

## What "collapse" looks like (the metrics to watch across cycles 1→5)
For each cycle, off the footers (blank-subtracted, down-only):
- **Retained_g trend** — DWR climbing cycle-over-cycle = water it can't shed (collapse). Expedry should stay flat.
- **Released % trend** (released/absorbed) — DWR falling = losing its ability to dry out. Expedry flat.
- **Absorbed_g trend** — DWR rising = treatment wearing off.
- **Baseline creep** — each cycle's starting (tared) weight before wetting; DWR not returning to its post-dry weight = accumulating.

**Pass/fail signal:** if DWR's retained climbs and released% drops monotonically over 5 cycles while Expedry holds flat, that's the collapse — the thing single-cycle testing can't show. If both stay flat, the treatments are equivalent even under repeat stress (also a real, reportable finding).

## Caveats
- Still n=1 per treatment — a trend across 5 cycles is more convincing than any single endpoint, but replicate later (n≥3) to nail the noise floor.
- Low-ICP Expedry (~2.0 vs 2.5–3.0 target): if Expedry also drifts, note it may be the under-spec ICP, not the chemistry — re-run with in-spec material when available.
- Watch for condensation near the sample at the longer cumulative run time; keep the circulation fan on during wet hold, off + settle-capture for weighing.
