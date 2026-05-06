"""
Solaris FZ-500 Dashboard
Flask + Socket.IO kiosk app for the Raspberry Pi.

Reads TC-A, TC-B (MAX31855 via SPI), DS18B20 (air gap via OneWire).
Controls IR lamp SSR on GPIO 17.
Serves a real-time web dashboard with Plotly.js charts.
Supports Start/End test automation with CSV logging.
Provides WiFi network switching (ISEEYOU2 <-> FX4).
"""

import csv
import glob
import os
import subprocess
import threading
import time
from collections import deque
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_file
from flask_socketio import SocketIO

# --------------------------------------------------------------------------
# Config
# --------------------------------------------------------------------------
LAMP_GPIO = 17
SAMPLE_HZ = 1.0  # readings per second pushed to the UI
CHART_WINDOW_SEC = 600  # 10 minutes of history in-memory
LOG_DIR = Path.home() / "Desktop" / "solaris_data"
LOG_DIR.mkdir(parents=True, exist_ok=True)

WIFI_PROFILES = {
    "home": "ISEEYOU2",
    "hotspot": "FX4",
}

# --------------------------------------------------------------------------
# Hardware shims (gracefully degrade if not on the Pi)
# --------------------------------------------------------------------------
try:
    import spidev

    spi0 = spidev.SpiDev()
    spi0.open(0, 0)
    spi0.max_speed_hz = 5_000_000
    spi1 = spidev.SpiDev()
    spi1.open(0, 1)
    spi1.max_speed_hz = 5_000_000
    SPI_AVAILABLE = True
except Exception as e:
    print(f"[WARN] SPI unavailable ({e}), using fake data for TCs")
    spi0 = spi1 = None
    SPI_AVAILABLE = False

try:
    from gpiozero import LED

    lamp = LED(LAMP_GPIO)
    LAMP_AVAILABLE = True
except Exception as e:
    print(f"[WARN] gpiozero unavailable ({e}), using fake lamp")
    lamp = None
    LAMP_AVAILABLE = False

# --------------------------------------------------------------------------
# Sensor readers
# --------------------------------------------------------------------------
def read_max31855(spi):
    """Return temperature in Celsius or None on fault."""
    if spi is None:
        # fake: 20-25°C with slight drift
        import random
        return 22 + random.uniform(-1, 3)
    raw = spi.readbytes(4)
    val = (raw[0] << 24) | (raw[1] << 16) | (raw[2] << 8) | raw[3]
    fault = val & 0x7
    if fault:
        return None
    tc = (val >> 18) & 0x3FFF
    if tc & 0x2000:
        tc -= 16384
    return tc * 0.25


def find_ds18b20():
    """Locate the first DS18B20 device path, or None."""
    paths = glob.glob("/sys/bus/w1/devices/28-*/w1_slave")
    return paths[0] if paths else None


DS18B20_PATH = find_ds18b20()
if DS18B20_PATH:
    print(f"[OK] DS18B20 found at {DS18B20_PATH}")
else:
    print("[WARN] No DS18B20 detected on OneWire bus, using fake data for air temp")


def read_ds18b20():
    """Return temperature in Celsius or None."""
    if not DS18B20_PATH:
        import random
        return 21 + random.uniform(-0.5, 2)
    try:
        with open(DS18B20_PATH) as f:
            data = f.read()
        if "YES" not in data.split("\n")[0]:
            return None
        t_str = data.split("t=")[-1].strip()
        return int(t_str) / 1000.0
    except Exception:
        return None


# --------------------------------------------------------------------------
# State
# --------------------------------------------------------------------------
history = {
    "time": deque(maxlen=int(CHART_WINDOW_SEC * SAMPLE_HZ)),
    "tc_a": deque(maxlen=int(CHART_WINDOW_SEC * SAMPLE_HZ)),
    "tc_b": deque(maxlen=int(CHART_WINDOW_SEC * SAMPLE_HZ)),
    "air": deque(maxlen=int(CHART_WINDOW_SEC * SAMPLE_HZ)),
    "lamp": deque(maxlen=int(CHART_WINDOW_SEC * SAMPLE_HZ)),
}

state = {
    "lamp_on": False,
    "lamp_on_since": None,
    "test_active": False,
    "test_id": None,
    "test_name": None,
    "sample_id": None,
    "test_start": None,
    "test_csv": None,
    "test_phase": "idle",  # idle | warmup | lamp_on | cooldown | done
    "test_phase_start": None,
    "test_phase_duration": 0,
    "test_config": {"lamp_on_sec": 300, "cooldown_sec": 60, "warmup_sec": 30},
}
state_lock = threading.Lock()
csv_writer_lock = threading.Lock()


def lamp_on():
    with state_lock:
        state["lamp_on"] = True
        state["lamp_on_since"] = time.time()
    if lamp:
        lamp.on()


def lamp_off():
    with state_lock:
        state["lamp_on"] = False
        state["lamp_on_since"] = None
    if lamp:
        lamp.off()


# --------------------------------------------------------------------------
# Test automation
# --------------------------------------------------------------------------
def _slugify(s):
    """Make a filename-safe slug from user input."""
    if not s:
        return ""
    s = "".join(c if c.isalnum() or c in "-_" else "_" for c in s.strip())
    return s[:40]  # keep filenames reasonable


def run_test(lamp_on_sec, cooldown_sec, warmup_sec=30, sample_id="", test_name=""):
    """Background thread: execute the full test sequence."""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    sample_slug = _slugify(sample_id) or "nosample"
    test_slug = _slugify(test_name)
    parts = [ts, sample_slug]
    if test_slug:
        parts.append(test_slug)
    test_id = "_".join(parts)
    csv_path = LOG_DIR / f"{test_id}.csv"

    with state_lock:
        state["test_active"] = True
        state["test_id"] = test_id
        state["test_name"] = test_name
        state["sample_id"] = sample_id
        state["test_start"] = time.time()
        state["test_csv"] = str(csv_path)
        state["test_phase"] = "warmup"
        state["test_config"] = {
            "lamp_on_sec": lamp_on_sec,
            "cooldown_sec": cooldown_sec,
            "warmup_sec": warmup_sec,
        }

    socketio.emit("test_state", _test_state_snapshot())

    # Open CSV and write header (plus a metadata preamble row)
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([f"# sample_id={sample_id}  test_name={test_name}  started={datetime.now().isoformat()}"])
        writer.writerow(
            [
                "iso_time",
                "elapsed_s",
                "tc_a_c",
                "tc_b_c",
                "air_c",
                "lamp_on",
                "phase",
            ]
        )

    def phase(name, duration):
        with state_lock:
            state["test_phase"] = name
            state["test_phase_start"] = time.time()
            state["test_phase_duration"] = duration
        socketio.emit("test_state", _test_state_snapshot())
        start = time.time()
        while time.time() - start < duration:
            if not state["test_active"]:
                return False
            time.sleep(0.2)
        return True

    try:
        # Warmup: baseline, lamp off
        lamp_off()
        if not phase("warmup", warmup_sec):
            return

        # Lamp on
        lamp_on()
        if not phase("lamp_on", lamp_on_sec):
            return

        # Cooldown: lamp off, continue logging
        lamp_off()
        if not phase("cooldown", cooldown_sec):
            return

        with state_lock:
            state["test_phase"] = "done"
    finally:
        lamp_off()
        with state_lock:
            state["test_active"] = False
        socketio.emit("test_state", _test_state_snapshot())


def _test_state_snapshot():
    with state_lock:
        now = time.time()
        elapsed = now - state["test_start"] if state["test_start"] else 0
        phase_elapsed = now - state["test_phase_start"] if state["test_phase_start"] else 0
        phase_dur = state.get("test_phase_duration", 0)
        phase_remaining = max(0, phase_dur - phase_elapsed) if phase_dur else 0
        # Total test duration = warmup + lamp + cooldown
        cfg = state["test_config"]
        total_dur = cfg.get("warmup_sec", 0) + cfg.get("lamp_on_sec", 0) + cfg.get("cooldown_sec", 0)
        total_remaining = max(0, total_dur - elapsed) if state["test_active"] else 0
        return {
            "active": state["test_active"],
            "id": state["test_id"],
            "sample_id": state.get("sample_id"),
            "test_name": state.get("test_name"),
            "phase": state["test_phase"],
            "elapsed_s": round(elapsed, 1),
            "phase_elapsed_s": round(phase_elapsed, 1),
            "phase_duration_s": round(phase_dur, 1),
            "phase_remaining_s": round(phase_remaining, 1),
            "total_duration_s": total_dur,
            "total_remaining_s": round(total_remaining, 1),
            "config": dict(state["test_config"]),
            "csv_path": state["test_csv"],
        }


# --------------------------------------------------------------------------
# Sensor polling thread — reads at SAMPLE_HZ, pushes to clients, logs CSV
# --------------------------------------------------------------------------
def sensor_loop():
    interval = 1.0 / SAMPLE_HZ
    while True:
        t0 = time.time()
        t_iso = datetime.now().isoformat()

        tc_a = read_max31855(spi0)
        tc_b = read_max31855(spi1)
        air = read_ds18b20()

        with state_lock:
            lamp_is_on = state["lamp_on"]
            test_active = state["test_active"]
            test_start = state["test_start"]
            test_phase = state["test_phase"]
            test_csv = state["test_csv"]

        # In-memory history
        history["time"].append(t0)
        history["tc_a"].append(tc_a)
        history["tc_b"].append(tc_b)
        history["air"].append(air)
        history["lamp"].append(1 if lamp_is_on else 0)

        payload = {
            "t": t0,
            "tc_a": tc_a,
            "tc_b": tc_b,
            "air": air,
            "lamp": lamp_is_on,
            "lamp_elapsed": round(t0 - state["lamp_on_since"], 1)
            if state["lamp_on_since"]
            else 0,
        }
        socketio.emit("reading", payload)

        # Live timer tick — push test state each second while a test is running
        if test_active:
            socketio.emit("test_state", _test_state_snapshot())

        # CSV log during an active test
        if test_active and test_csv:
            try:
                with csv_writer_lock, open(test_csv, "a", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(
                        [
                            t_iso,
                            round(t0 - test_start, 2) if test_start else "",
                            f"{tc_a:.2f}" if tc_a is not None else "",
                            f"{tc_b:.2f}" if tc_b is not None else "",
                            f"{air:.2f}" if air is not None else "",
                            int(lamp_is_on),
                            test_phase,
                        ]
                    )
            except Exception as e:
                print(f"[ERR] CSV write: {e}")

        # Pace
        elapsed = time.time() - t0
        if elapsed < interval:
            time.sleep(interval - elapsed)


# --------------------------------------------------------------------------
# Flask + Socket.IO
# --------------------------------------------------------------------------
app = Flask(__name__)
app.config["SECRET_KEY"] = "solaris"
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/state")
def api_state():
    return jsonify(
        {
            "lamp_on": state["lamp_on"],
            "test": _test_state_snapshot(),
            "ds18b20_detected": DS18B20_PATH is not None,
            "spi_available": SPI_AVAILABLE,
            "lamp_available": LAMP_AVAILABLE,
        }
    )


@app.route("/api/lamp", methods=["POST"])
def api_lamp():
    data = request.get_json() or {}
    if data.get("on"):
        lamp_on()
    else:
        lamp_off()
    return jsonify({"lamp_on": state["lamp_on"]})


@app.route("/api/test/start", methods=["POST"])
def api_test_start():
    if state["test_active"]:
        return jsonify({"error": "test already running"}), 400
    data = request.get_json() or {}
    lamp_on_sec = int(data.get("lamp_on_sec", 300))
    cooldown_sec = int(data.get("cooldown_sec", 60))
    warmup_sec = int(data.get("warmup_sec", 30))
    sample_id = str(data.get("sample_id", "")).strip()
    test_name = str(data.get("test_name", "")).strip()
    t = threading.Thread(
        target=run_test,
        kwargs={
            "lamp_on_sec": lamp_on_sec,
            "cooldown_sec": cooldown_sec,
            "warmup_sec": warmup_sec,
            "sample_id": sample_id,
            "test_name": test_name,
        },
        daemon=True,
    )
    t.start()
    return jsonify({"started": True, "sample_id": sample_id, "test_name": test_name})


@app.route("/api/test/stop", methods=["POST"])
def api_test_stop():
    with state_lock:
        state["test_active"] = False
        state["test_phase"] = "idle"
    lamp_off()
    return jsonify({"stopped": True})


@app.route("/api/test/csv/<test_id>")
def api_test_csv(test_id):
    # Basic sanity check to prevent path traversal
    if "/" in test_id or ".." in test_id:
        return "bad id", 400
    path = LOG_DIR / f"{test_id}.csv"
    if not path.exists():
        return "not found", 404
    return send_file(path, as_attachment=True)


@app.route("/api/wifi/list")
def api_wifi_list():
    """List saved connection profiles and current active one."""
    try:
        out = subprocess.run(
            ["nmcli", "-t", "-f", "NAME,TYPE,ACTIVE", "connection", "show"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        profiles = []
        for line in out.stdout.strip().split("\n"):
            parts = line.split(":")
            if len(parts) >= 3 and parts[1] in ("802-11-wireless", "wifi"):
                profiles.append({"name": parts[0], "active": parts[2] == "yes"})
        return jsonify({"profiles": profiles})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/wifi/switch", methods=["POST"])
def api_wifi_switch():
    """Switch to a named WiFi profile."""
    data = request.get_json() or {}
    name = data.get("name")
    if not name:
        return jsonify({"error": "missing name"}), 400
    try:
        result = subprocess.run(
            ["sudo", "-n", "nmcli", "connection", "up", name],
            capture_output=True,
            text=True,
            timeout=20,
        )
        if result.returncode != 0:
            return jsonify({"error": result.stderr.strip()}), 500
        return jsonify({"switched": True, "name": name})
    except subprocess.TimeoutExpired:
        return jsonify({"error": "timeout (network may have switched)"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/wifi/status")
def api_wifi_status():
    """Get currently active SSID and IP."""
    try:
        ssid = subprocess.run(
            ["iwgetid", "-r"], capture_output=True, text=True, timeout=3
        ).stdout.strip()
        ip = subprocess.run(
            ["hostname", "-I"], capture_output=True, text=True, timeout=3
        ).stdout.strip().split(" ")[0]
        return jsonify({"ssid": ssid, "ip": ip})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@socketio.on("connect")
def on_connect():
    # Send initial history snapshot
    socketio.emit(
        "history",
        {
            "time": list(history["time"]),
            "tc_a": list(history["tc_a"]),
            "tc_b": list(history["tc_b"]),
            "air": list(history["air"]),
        },
    )
    socketio.emit("test_state", _test_state_snapshot())


if __name__ == "__main__":
    threading.Thread(target=sensor_loop, daemon=True).start()
    socketio.run(app, host="0.0.0.0", port=5000, debug=False, allow_unsafe_werkzeug=True)
