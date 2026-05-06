#!/usr/bin/env python3
"""
Solaris FZ-500 — 9-run comparison protocol runner.

Automates the baseline / untreated / treated comparison specified in
TEST_PROTOCOL.md §6. Prompts the operator between runs to stage the next
sample, triggers tests via the dashboard's Flask API, collects and renames
each CSV, waits for plate reset between runs, and prints a final summary
with an automated efficacy check.

Requires the dashboard to be running:
    python app.py
or via the solaris-dashboard.service systemd unit.

Usage:
    python run_comparison.py                       # defaults: 3x baseline, 3x untreated, 3x treated
    python run_comparison.py --replicates 5        # 5 of each condition
    python run_comparison.py --lamp 300            # longer lamp-on phase
    python run_comparison.py --sample-id S047      # embed sample ID in filenames
    python run_comparison.py --reset-wait 600      # 10 min between runs instead of 5
    python run_comparison.py --plot-only ~/solaris_logs/comparison_20260422/
                                                   # just regenerate the overlay PNG from existing CSVs

Outputs produced in <out>/:
    solaris_<date>_<cond>_r<N>.csv           — renamed per-run CSVs
    comparison_summary_<date>.csv            — one row per run with derived metrics
    comparison_<date>.png                    — overlay chart (requires matplotlib)

Run with --help for the full list.
"""
from __future__ import annotations

import argparse
import csv
import json
import statistics
import sys
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import Request, urlopen
from urllib.error import URLError


# --------------------------------------------------------------------------
# Tiny HTTP helpers (stdlib only — no requests dependency)
# --------------------------------------------------------------------------
def http_get(url, timeout=5):
    with urlopen(Request(url), timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def http_post(url, payload, timeout=5):
    data = json.dumps(payload).encode("utf-8")
    req = Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


# --------------------------------------------------------------------------
# Banner / prompt helpers
# --------------------------------------------------------------------------
def banner(msg, char="="):
    line = char * 72
    print(f"\n{line}\n {msg}\n{line}")


def wait_enter(prompt):
    print(prompt, end="", flush=True)
    try:
        input()
    except (KeyboardInterrupt, EOFError):
        print("\n  Aborted by operator.")
        sys.exit(1)


# --------------------------------------------------------------------------
# API wrappers
# --------------------------------------------------------------------------
def get_state(api):
    return http_get(urljoin(api, "/api/state"))


def start_test(api, warmup, lamp_on, cooldown):
    return http_post(
        urljoin(api, "/api/test/start"),
        {"warmup_sec": warmup, "lamp_on_sec": lamp_on, "cooldown_sec": cooldown},
    )


# --------------------------------------------------------------------------
# CSV handling
# --------------------------------------------------------------------------
def find_latest_csv(log_dir):
    files = sorted(Path(log_dir).glob("solaris_*.csv"), key=lambda p: p.stat().st_mtime)
    return files[-1] if files else None


def summarize_csv(csv_path):
    """Compute ambient (mean of warmup phase), peak plate temp, and ΔT at end of lamp_on."""
    rows = []
    with open(csv_path, newline="") as f:
        for row in csv.DictReader(f):
            rows.append(row)
    if not rows:
        return None
    try:
        warmup = [r for r in rows if r["phase"] == "warmup"]
        if warmup:
            amb_a = statistics.mean(float(r["tc_a_c"]) for r in warmup)
            amb_b = statistics.mean(float(r["tc_b_c"]) for r in warmup)
        else:
            amb_a = float(rows[0]["tc_a_c"])
            amb_b = float(rows[0]["tc_b_c"])
        ambient = (amb_a + amb_b) / 2
        lamp = [r for r in rows if r["phase"] == "lamp_on"]
        if not lamp:
            return None
        last = lamp[-1]
        peak_a = max(float(r["tc_a_c"]) for r in rows)
        peak_b = max(float(r["tc_b_c"]) for r in rows)
        peak_plate = max(peak_a, peak_b)
        end_plate = (float(last["tc_a_c"]) + float(last["tc_b_c"])) / 2
        return {
            "ambient": round(ambient, 2),
            "peak_plate": round(peak_plate, 2),
            "delta_end": round(end_plate - ambient, 2),
        }
    except (KeyError, ValueError) as e:
        print(f"  WARNING: could not summarize {csv_path.name}: {e}")
        return None


# --------------------------------------------------------------------------
# Overlay chart (matplotlib, lazy-imported so it's optional)
# --------------------------------------------------------------------------
def generate_overlay_chart(out_dir, date_tag, warmup_sec, lamp_sec, cooldown_sec, verbose=True):
    """
    Generate an overlay PNG of all run CSVs in out_dir, grouped by condition.

    Y-axis is ΔT_plate above each run's own warmup-phase mean (so room-temp drift
    between runs doesn't contaminate the comparison). Three layers per condition:
    shaded phase background, thin translucent individual runs, thick mean line.
    """
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("  [plot] matplotlib not installed — skipping overlay chart.")
        print("  [plot] to enable, install with: pip install matplotlib")
        return None

    out_dir = Path(out_dir)
    csvs = sorted(out_dir.glob("solaris_*_r*.csv"))
    if not csvs:
        print(f"  [plot] No run CSVs found in {out_dir}")
        return None

    # Condition → color. Extras fall back to a default palette.
    colors = {
        "baseline":  "#ef5350",   # red — max-flux reference
        "untreated": "#ffb300",   # amber — native fabric
        "treated":   "#42a5f5",   # blue — FUZE-treated
    }
    fallback = ["#66bb6a", "#ab47bc", "#26a69a", "#7e57c2", "#ec407a"]

    # Load + group
    by_cond = {}
    for csv_file in csvs:
        parts = csv_file.stem.split("_")
        if len(parts) < 3:
            continue
        cond = parts[-2]
        rep = parts[-1]
        t_elapsed, plate_temps, phases = [], [], []
        with open(csv_file, newline="") as f:
            for row in csv.DictReader(f):
                try:
                    t_elapsed.append(float(row["t_elapsed_s"]))
                    plate_temps.append((float(row["tc_a_c"]) + float(row["tc_b_c"])) / 2)
                    phases.append(row["phase"])
                except (KeyError, ValueError):
                    continue
        if not plate_temps:
            continue
        warmup_temps = [plate_temps[i] for i, ph in enumerate(phases) if ph == "warmup"]
        ambient = statistics.mean(warmup_temps) if warmup_temps else plate_temps[0]
        dt = [t - ambient for t in plate_temps]
        by_cond.setdefault(cond, []).append({"file": csv_file.name, "rep": rep, "t": t_elapsed, "dt": dt})

    if not by_cond:
        print("  [plot] No valid run data to plot.")
        return None

    fig, ax = plt.subplots(figsize=(12, 7), dpi=110, facecolor="#ffffff")
    total_sec = warmup_sec + lamp_sec + cooldown_sec

    # Phase shading (under the lines)
    ax.axvspan(0, warmup_sec, alpha=0.10, color="#9aa4b7", zorder=0)
    ax.axvspan(warmup_sec, warmup_sec + lamp_sec, alpha=0.14, color="#ff7043", zorder=0)
    ax.axvspan(warmup_sec + lamp_sec, total_sec, alpha=0.08, color="#42a5f5", zorder=0)
    ax.axvline(warmup_sec, color="#555", linestyle="--", linewidth=0.8, alpha=0.6, zorder=1)
    ax.axvline(warmup_sec + lamp_sec, color="#555", linestyle="--", linewidth=0.8, alpha=0.6, zorder=1)

    # Phase labels at top of shaded bands
    ymax_guess = max((max(r["dt"]) for runs in by_cond.values() for r in runs), default=40)
    label_y = ymax_guess * 1.02
    ax.text(warmup_sec / 2, label_y, "warmup", ha="center", va="bottom", fontsize=9, color="#666", alpha=0.7)
    ax.text(warmup_sec + lamp_sec / 2, label_y, "lamp on", ha="center", va="bottom", fontsize=9, color="#c35c27", alpha=0.9)
    ax.text(warmup_sec + lamp_sec + cooldown_sec / 2, label_y, "cooldown", ha="center", va="bottom", fontsize=9, color="#1976a5", alpha=0.9)

    # Plot in a consistent order
    order = ["baseline", "untreated", "treated"]
    ordered = [c for c in order if c in by_cond] + [c for c in by_cond if c not in order]

    summary_lines = []
    for idx, cond in enumerate(ordered):
        color = colors.get(cond, fallback[idx % len(fallback)])
        runs = by_cond[cond]

        # Individual runs — thin + translucent
        for run in runs:
            ax.plot(run["t"], run["dt"], color=color, alpha=0.30, linewidth=1.0, zorder=2)

        # Mean line — only if we have 2+ runs (otherwise just bold the single)
        if len(runs) >= 2:
            max_len = min(len(r["t"]) for r in runs)
            mean_dt = [statistics.mean(r["dt"][j] for r in runs) for j in range(max_len)]
            mean_t = runs[0]["t"][:max_len]
            ax.plot(mean_t, mean_dt, color=color, alpha=1.0, linewidth=2.6,
                    label=f"{cond} (n={len(runs)})", zorder=3)
        else:
            ax.plot(runs[0]["t"], runs[0]["dt"], color=color, alpha=1.0, linewidth=2.6,
                    label=f"{cond} (n=1)", zorder=3)

        # Collect end-of-lamp delta for summary annotation
        end_deltas = []
        for run in runs:
            end_idx = min(range(len(run["t"])), key=lambda i: abs(run["t"][i] - (warmup_sec + lamp_sec)))
            end_deltas.append(run["dt"][end_idx])
        if end_deltas:
            m = statistics.mean(end_deltas)
            summary_lines.append((cond, m, color))

    ax.set_xlabel("Time since test start (s)", fontsize=11)
    ax.set_ylabel("ΔT plate above warmup baseline (°C)", fontsize=11)
    ax.set_title(
        f"Solaris FZ-500 — Comparison {date_tag}  ·  "
        f"warmup {warmup_sec}s · lamp {lamp_sec}s · cooldown {cooldown_sec}s",
        fontsize=12.5, pad=14,
    )
    ax.grid(True, alpha=0.25, zorder=1)
    ax.set_xlim(0, total_sec)
    ax.legend(loc="upper left", fontsize=10, framealpha=0.9)

    # Annotation box with end-of-lamp means (bottom-right)
    if summary_lines:
        txt = "ΔT at end of lamp_on:\n"
        for cond, m, c in summary_lines:
            txt += f"  {cond:<10} {m:+5.1f}°C\n"
        ax.text(
            0.98, 0.02, txt.strip(),
            transform=ax.transAxes, ha="right", va="bottom",
            fontsize=10, family="monospace",
            bbox=dict(boxstyle="round,pad=0.4", fc="#ffffff", ec="#ccc", alpha=0.95),
        )

    plt.tight_layout()
    out_png = out_dir / f"comparison_{date_tag}.png"
    plt.savefig(out_png, dpi=150, bbox_inches="tight")
    plt.close(fig)
    if verbose:
        print(f"  [plot] Saved: {out_png}")
    return out_png


# --------------------------------------------------------------------------
# Reset wait (live-polling optional, time-based fallback always works)
# --------------------------------------------------------------------------
def wait_for_reset(api, ambient, tol_amb, tol_pair, max_wait, poll=10):
    """Poll dashboard state until TC-A/TC-B/air are within tolerance of captured ambient."""
    start = time.time()
    while time.time() - start < max_wait:
        try:
            s = get_state(api)
        except URLError:
            time.sleep(poll)
            continue
        tc_a = s.get("tc_a")
        tc_b = s.get("tc_b")
        air = s.get("air")
        if None in (tc_a, tc_b, air):
            # State endpoint doesn't expose live readings on this build — fall back
            return None
        da = abs(tc_a - ambient["tc_a"])
        db = abs(tc_b - ambient["tc_b"])
        d_air = abs(air - ambient["air"])
        dab = abs(tc_a - tc_b)
        elapsed = int(time.time() - start)
        print(f"    [reset check {elapsed:4d}s]  TC-A Δ{da:+4.1f}  TC-B Δ{db:+4.1f}  air Δ{d_air:+4.1f}  |A-B|={dab:.1f}")
        if da <= tol_amb and db <= tol_amb and d_air <= tol_amb and dab <= tol_pair:
            return True
        time.sleep(poll)
    return False


def wait_fixed(seconds):
    """Dumb time-based wait with a progress ticker."""
    for i in range(int(seconds)):
        if i % 30 == 0 and i > 0:
            remaining = int(seconds) - i
            print(f"    [{i}s elapsed, {remaining}s remaining until next run]")
        time.sleep(1)


# --------------------------------------------------------------------------
# Ambient capture (before the first run)
# --------------------------------------------------------------------------
def capture_ambient(api, samples=10, interval=1.0):
    """Grab N samples of live readings to establish an ambient baseline."""
    vals_a, vals_b, vals_air = [], [], []
    for _ in range(samples):
        try:
            s = get_state(api)
        except URLError:
            time.sleep(interval)
            continue
        if s.get("tc_a") is not None: vals_a.append(s["tc_a"])
        if s.get("tc_b") is not None: vals_b.append(s["tc_b"])
        if s.get("air") is not None: vals_air.append(s["air"])
        time.sleep(interval)
    if not (vals_a and vals_b and vals_air):
        return None
    return {
        "tc_a": statistics.mean(vals_a),
        "tc_b": statistics.mean(vals_b),
        "air": statistics.mean(vals_air),
    }


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------
def main():
    p = argparse.ArgumentParser(description="Run the Solaris 9-test comparison protocol.")
    p.add_argument("--warmup", type=int, default=30, help="Warmup seconds (default 30)")
    p.add_argument("--lamp", type=int, default=180, help="Lamp-on seconds (default 180)")
    p.add_argument("--cooldown", type=int, default=60, help="Cooldown seconds (default 60)")
    p.add_argument("--conditions", nargs="+", default=["baseline", "untreated", "treated"],
                   help="Conditions to test in order (default: baseline untreated treated)")
    p.add_argument("--replicates", type=int, default=3, help="Replicates per condition (default 3)")
    p.add_argument("--reset-wait", type=int, default=300, help="Seconds to wait between runs for plate reset (default 300 = 5 min)")
    p.add_argument("--reset-tol", type=float, default=2.0, help="Live-reset: ambient tolerance in °C (default 2.0)")
    p.add_argument("--pair-tol", type=float, default=1.5, help="Live-reset: TC-A vs TC-B tolerance (default 1.5)")
    p.add_argument("--api", default="http://localhost:5000", help="Dashboard API base URL")
    p.add_argument("--log-dir", default=str(Path.home() / "solaris_logs"), help="Where Flask writes CSVs")
    p.add_argument("--out", default=None, help="Output dir for renamed CSVs (default: <log-dir>/comparison_<date>/)")
    p.add_argument("--sample-id", default="", help="Optional sample ID embedded in filenames")
    p.add_argument("--skip-plot", action="store_true", help="Skip overlay chart generation at end")
    p.add_argument("--plot-only", default=None, metavar="DIR",
                   help="Regenerate overlay chart from CSVs in an existing comparison dir and exit (no tests run)")
    args = p.parse_args()

    date_tag = datetime.now().strftime("%Y%m%d")

    # Plot-only path: regenerate chart from existing data without running any tests
    if args.plot_only:
        target = Path(args.plot_only).expanduser()
        if not target.exists():
            sys.exit(f"  ERROR: {target} does not exist")
        # Extract date from dir name if possible: comparison_YYYYMMDD
        inferred_date = date_tag
        if target.name.startswith("comparison_") and len(target.name) >= 19:
            inferred_date = target.name.replace("comparison_", "")
        banner(f"Plot-only mode — regenerating overlay from {target}")
        result = generate_overlay_chart(target, inferred_date, args.warmup, args.lamp, args.cooldown)
        sys.exit(0 if result else 1)
    log_dir = Path(args.log_dir)
    out_dir = Path(args.out) if args.out else log_dir / f"comparison_{date_tag}"
    out_dir.mkdir(parents=True, exist_ok=True)

    total = len(args.conditions) * args.replicates
    per_run_sec = args.warmup + args.lamp + args.cooldown
    est_min = total * (per_run_sec + args.reset_wait) / 60

    banner("Solaris FZ-500 — Comparison protocol runner")
    print(f"  Conditions         : {args.conditions}")
    print(f"  Replicates         : {args.replicates} per condition")
    print(f"  Total runs         : {total}")
    print(f"  Per-run duration   : {per_run_sec}s  (warmup={args.warmup}  lamp={args.lamp}  cooldown={args.cooldown})")
    print(f"  Reset wait         : {args.reset_wait}s between runs")
    print(f"  Estimated total    : ~{est_min:.0f} min")
    print(f"  Dashboard API      : {args.api}")
    print(f"  CSV source         : {log_dir}")
    print(f"  CSV destination    : {out_dir}")
    if args.sample_id:
        print(f"  Sample ID tag      : {args.sample_id}")

    # Preflight
    try:
        s = get_state(args.api)
    except URLError as e:
        sys.exit(f"\n  ERROR: dashboard not reachable at {args.api}: {e.reason}")
    if not s.get("spi_available"):
        sys.exit("\n  ERROR: SPI not available — check Pi PSU and wiring before proceeding.")
    if not s.get("lamp_available"):
        sys.exit("\n  ERROR: lamp GPIO not available — check SSR trigger wiring.")
    if not s.get("ds18b20_detected"):
        print("  WARNING: DS18B20 not detected — air gap readings will be synthetic. Continue anyway? (y/N)")
        if input().strip().lower() != "y":
            sys.exit("  Aborted.")

    # Ambient baseline
    banner("Capture ambient baseline")
    print("  Plate must be at room temperature. Wait 10 min after any prior test before continuing.")
    wait_enter("  Press ENTER when the plate is cold and you're ready to capture ambient: ")
    ambient = capture_ambient(args.api, samples=10, interval=1.0)
    if ambient:
        print(f"  Ambient captured:  TC-A={ambient['tc_a']:.1f}°C   TC-B={ambient['tc_b']:.1f}°C   air={ambient['air']:.1f}°C")
    else:
        print("  WARNING: could not read live sensor values from /api/state.")
        print("  Will use fixed time-based reset waits instead of live polling.")

    # Run the matrix
    results = []
    run_n = 0
    for cond in args.conditions:
        for rep in range(1, args.replicates + 1):
            run_n += 1
            banner(f"Run {run_n}/{total}  —  condition: {cond.upper()}   replicate: r{rep}")
            if cond == "baseline":
                print("  Sample setup: BARE PLATE. Remove any fabric. Probe still in place.")
            else:
                print(f"  Sample setup: {cond.upper()} fabric, centered on plate, ~10mm overhang each side.")
            print(f"  Parameters:   warmup={args.warmup}s  lamp_on={args.lamp}s  cooldown={args.cooldown}s")
            wait_enter("  Press ENTER when sample is staged and sensors are at ambient: ")

            pre_latest = find_latest_csv(log_dir)
            try:
                start_test(args.api, args.warmup, args.lamp, args.cooldown)
            except Exception as e:
                print(f"  ERROR starting test: {e}  — skipping this run")
                continue

            total_sec = per_run_sec + 5  # small buffer for CSV flush
            print(f"  Test running ({total_sec}s total) — do not touch the rig.")
            for i in range(total_sec):
                time.sleep(1)
                if i > 0 and i % 30 == 0:
                    phase = "warmup" if i < args.warmup else ("lamp_on" if i < args.warmup + args.lamp else "cooldown")
                    print(f"    [{i:3d}s / {total_sec}s]  phase: {phase}")

            # Locate the newly written CSV
            latest = find_latest_csv(log_dir)
            if latest is None or (pre_latest is not None and latest == pre_latest):
                print("  WARNING: no new CSV found after test — skipping rename.")
                continue

            sample_tag = f"_{args.sample_id}" if args.sample_id else ""
            new_name = f"solaris_{date_tag}{sample_tag}_{cond}_r{rep}.csv"
            new_path = out_dir / new_name
            latest.rename(new_path)
            print(f"  Saved: {new_path}")

            # Compute per-run metrics
            summary = summarize_csv(new_path)
            if summary:
                print(f"  Result: peak_plate={summary['peak_plate']:.1f}°C   ΔT_end_lamp={summary['delta_end']:+.1f}°C")
                results.append({
                    "run": run_n, "condition": cond, "replicate": rep,
                    "file": new_path.name, **summary,
                })

            # Between-run reset
            if run_n < total:
                print("  Waiting for plate reset before next run…")
                outcome = None
                if ambient is not None:
                    outcome = wait_for_reset(args.api, ambient, args.reset_tol, args.pair_tol, args.reset_wait)
                if outcome is True:
                    print("  Plate reset confirmed (within tolerance).")
                elif outcome is False:
                    print(f"  Reset wait timed out after {args.reset_wait}s — check plate manually before continuing.")
                    wait_enter("  Press ENTER when ready to proceed: ")
                else:
                    # No live reading available — fall back to fixed wait
                    print(f"  Using fixed wait of {args.reset_wait}s (live reset check unavailable)")
                    wait_fixed(args.reset_wait)

    # --------------------------------------------------------------------------
    # Final summary
    # --------------------------------------------------------------------------
    banner("Comparison summary")
    if not results:
        print("  No successful runs. Nothing to summarize.")
        return

    by_cond = {}
    for r in results:
        by_cond.setdefault(r["condition"], []).append(r)

    print(f"  {'condition':<14} {'n':>3} {'ΔT_mean':>10} {'ΔT_stdev':>10} {'ΔT_range':>16} {'peak_mean':>10}")
    print(f"  {'-'*14} {'-'*3} {'-'*10} {'-'*10} {'-'*16} {'-'*10}")
    for cond, runs in by_cond.items():
        deltas = [r["delta_end"] for r in runs]
        peaks = [r["peak_plate"] for r in runs]
        m = statistics.mean(deltas)
        sd = statistics.stdev(deltas) if len(deltas) > 1 else 0.0
        print(f"  {cond:<14} {len(runs):>3} {m:>+9.2f}° {sd:>9.2f}° [{min(deltas):>+5.1f}, {max(deltas):>+5.1f}] {statistics.mean(peaks):>9.1f}°")

    # Summary CSV
    summary_path = out_dir / f"comparison_summary_{date_tag}.csv"
    with open(summary_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["run", "condition", "replicate", "file", "ambient", "peak_plate", "delta_end"])
        w.writeheader()
        for r in results:
            w.writerow(r)
    print(f"\n  Per-run summary CSV: {summary_path}")

    # Efficacy check (only if all three standard conditions are present with ≥2 reps each)
    required = {"baseline", "untreated", "treated"}
    if required.issubset(by_cond) and all(len(by_cond[c]) >= 2 for c in required):
        b = statistics.mean(r["delta_end"] for r in by_cond["baseline"])
        u = statistics.mean(r["delta_end"] for r in by_cond["untreated"])
        t = statistics.mean(r["delta_end"] for r in by_cond["treated"])
        banner("Efficacy check")
        print(f"  baseline  ΔT mean: {b:+6.2f}°C")
        print(f"  untreated ΔT mean: {u:+6.2f}°C   ({(u-b)/b*100:+5.0f}% vs baseline)")
        print(f"  treated   ΔT mean: {t:+6.2f}°C   ({(t-u)/u*100:+5.0f}% vs untreated)")
        print()
        if b > u > t:
            gap = (u - t) / u * 100
            print(f"  Ordering: baseline > untreated > treated  [OK]")
            print(f"  Treatment reduction: {gap:.1f}% vs untreated")
            if gap >= 15:
                print(f"  Threshold (≥15%): MET — treatment effect is meaningful.")
            else:
                print(f"  Threshold (≥15%): NOT MET — treatment effect is marginal. Investigate.")

            # Check intra-condition variance
            for cond in ("baseline", "untreated", "treated"):
                deltas = [r["delta_end"] for r in by_cond[cond]]
                if len(deltas) > 1:
                    m = statistics.mean(deltas)
                    sd = statistics.stdev(deltas)
                    cv = (sd / abs(m)) * 100 if m != 0 else 0
                    flag = "[OK]" if cv < 10 else "[HIGH]"
                    print(f"  {cond} variance (CV): {cv:.1f}%  {flag}")
        else:
            print(f"  Ordering: NOT baseline > untreated > treated  [WARN]")
            print(f"  Expected plate temp rise to decrease as treatment is applied.")
            print(f"  Possible causes: treatment batch issue, fabric contamination, sensor drift, lamp geometry changed mid-session.")

    # Overlay chart
    if not args.skip_plot:
        banner("Overlay chart")
        generate_overlay_chart(out_dir, date_tag, args.warmup, args.lamp, args.cooldown)

    banner("Done.")
    print(f"  All CSVs in: {out_dir}")
    print(f"  Run count:   {len(results)} successful / {total} attempted")


if __name__ == "__main__":
    main()
