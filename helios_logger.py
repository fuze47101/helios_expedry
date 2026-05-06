#!/usr/bin/env python3
"""
Helios Data Logger — Expedry Capsule Test System
=================================================
Reads weight from Bonvoisin 500g x 0.001g scale via RS232-USB,
logs to CSV, and displays live readings in terminal.

Future expansion slots:
  - Humidity sensor(s) via GPIO or USB
  - IR camera via USB or CSI
  - Humidifier control relay via GPIO

Usage:
  python3 helios_logger.py                    # auto-detect scale, log to CSV
  python3 helios_logger.py --port /dev/ttyUSB0  # specify port
  python3 helios_logger.py --plot             # live plot in terminal
  python3 helios_logger.py --duration 3600    # run for 1 hour
  python3 helios_logger.py --list-ports       # show available serial ports

Requirements:
  pip install pyserial
  pip install matplotlib   (optional, for --plot)
"""

import argparse
import csv
import os
import signal
import sys
import time
from datetime import datetime
from pathlib import Path

try:
    import serial
    import serial.tools.list_ports
except ImportError:
    print("ERROR: pyserial not installed. Run: pip install pyserial")
    sys.exit(1)


# ============================================================
#  CONFIGURATION — adjust these when scale arrives
# ============================================================

# Bonvoisin RS232 defaults (verify with scale manual)
DEFAULT_BAUD = 9600
DEFAULT_BYTESIZE = serial.EIGHTBITS
DEFAULT_PARITY = serial.PARITY_NONE
DEFAULT_STOPBITS = serial.STOPBITS_ONE
DEFAULT_TIMEOUT = 2  # seconds

# Polling interval (seconds between readings)
DEFAULT_INTERVAL = 1.0

# Scale command to request a reading
# Common commands for lab scales:
#   "S\r\n"   = send stable weight
#   "SI\r\n"  = send weight immediately
#   "SIR\r\n" = continuous output
#   ""         = some scales auto-transmit
SCALE_CMD = "SI\r\n"

# CSV output directory
LOG_DIR = Path.home() / "helios_logs"


# ============================================================
#  SCALE COMMUNICATION
# ============================================================

class BonvoisinScale:
    """Interface to Bonvoisin analytical balance via RS232."""

    def __init__(self, port=None, baud=DEFAULT_BAUD):
        self.port = port
        self.baud = baud
        self.ser = None
        self.unit = "g"
        self.connected = False

    def find_port(self):
        """Auto-detect scale on USB-serial adapter."""
        ports = serial.tools.list_ports.comports()
        candidates = []
        for p in ports:
            desc = (p.description or "").lower()
            hwid = (p.hwid or "").lower()
            # Look for common USB-serial chipsets
            if any(chip in desc + hwid for chip in
                   ["ftdi", "cp210", "ch340", "pl2303", "usb-serial",
                    "usb serial", "uart", "rs232"]):
                candidates.append(p.device)
            # Also grab any ttyUSB or ttyACM devices (Linux)
            elif "ttyusb" in p.device.lower() or "ttyacm" in p.device.lower():
                candidates.append(p.device)
            # macOS: cu.usbserial
            elif "cu.usbserial" in p.device.lower():
                candidates.append(p.device)

        if not candidates:
            return None
        if len(candidates) == 1:
            return candidates[0]
        # Multiple found — return first, print warning
        print(f"  Multiple serial ports found: {candidates}")
        print(f"  Using: {candidates[0]} (override with --port)")
        return candidates[0]

    def connect(self):
        """Open serial connection to scale."""
        if not self.port:
            self.port = self.find_port()
        if not self.port:
            raise ConnectionError(
                "No USB-serial device found. Is the RS232 cable plugged in?\n"
                "  Available ports: " +
                str([p.device for p in serial.tools.list_ports.comports()])
            )

        print(f"  Connecting to scale on {self.port} @ {self.baud} baud...")
        self.ser = serial.Serial(
            port=self.port,
            baudrate=self.baud,
            bytesize=DEFAULT_BYTESIZE,
            parity=DEFAULT_PARITY,
            stopbits=DEFAULT_STOPBITS,
            timeout=DEFAULT_TIMEOUT
        )
        time.sleep(0.5)  # let scale initialize
        self.ser.reset_input_buffer()
        self.connected = True
        print(f"  Connected.")

    def read_weight(self):
        """Request and parse a weight reading from the scale.

        Returns:
            tuple: (weight_grams: float, stable: bool, raw: str)
            Returns (None, False, raw) if parse fails.
        """
        if not self.connected:
            raise ConnectionError("Scale not connected")

        # Send request command
        if SCALE_CMD:
            self.ser.write(SCALE_CMD.encode())

        # Read response line
        raw = ""
        try:
            raw = self.ser.readline().decode("ascii", errors="replace").strip()
        except serial.SerialException as e:
            print(f"  Serial error: {e}")
            return None, False, str(e)

        if not raw:
            return None, False, "(no response)"

        # Parse weight from response
        # Bonvoisin typically sends: "ST,GS,+  123.456 g" or similar
        # Common formats:
        #   "+  123.456 g"
        #   "S  +123.456  g"
        #   "ST,+0000123.456 g"
        # Strategy: find the numeric value and unit
        weight = None
        stable = False

        # Check for stability indicator
        if raw.upper().startswith("ST") or "ST," in raw.upper():
            stable = True
        elif raw.upper().startswith("US") or "US," in raw.upper():
            stable = False

        # Extract numeric value
        parts = raw.replace(",", " ").split()
        for part in parts:
            cleaned = part.strip().lstrip("+")
            try:
                weight = float(cleaned)
                break
            except ValueError:
                continue

        # Detect unit
        raw_upper = raw.upper()
        if " OZ" in raw_upper:
            self.unit = "oz"
        elif " CT" in raw_upper:
            self.unit = "ct"
        elif " GN" in raw_upper:
            self.unit = "gn"
        else:
            self.unit = "g"

        return weight, stable, raw

    def tare(self):
        """Send tare command to scale."""
        if self.connected:
            self.ser.write(b"T\r\n")
            time.sleep(1)
            print("  Tare sent.")

    def disconnect(self):
        """Close serial connection."""
        if self.ser and self.ser.is_open:
            self.ser.close()
            self.connected = False
            print("  Scale disconnected.")


# ============================================================
#  SENSOR EXPANSION SLOTS (for future use)
# ============================================================

class SensorHub:
    """Placeholder for additional sensors.

    When you add humidity sensors and IR camera,
    register them here and they'll be included in the log.
    """

    def __init__(self):
        self.sensors = {}

    def register(self, name, read_func):
        """Register a sensor.

        Args:
            name: column name for CSV (e.g., 'humidity_1', 'temp_ir')
            read_func: callable that returns a numeric value
        """
        self.sensors[name] = read_func

    def read_all(self):
        """Read all registered sensors.

        Returns:
            dict: {sensor_name: value}
        """
        readings = {}
        for name, func in self.sensors.items():
            try:
                readings[name] = func()
            except Exception as e:
                readings[name] = None
                print(f"  Sensor '{name}' error: {e}")
        return readings

    def headers(self):
        """Return CSV column headers for all sensors."""
        return list(self.sensors.keys())


# ============================================================
#  DATA LOGGER
# ============================================================

class HeliosLogger:
    """Main data logging engine."""

    def __init__(self, scale, sensor_hub, interval=DEFAULT_INTERVAL,
                 log_dir=LOG_DIR, test_name=None):
        self.scale = scale
        self.sensors = sensor_hub
        self.interval = interval
        self.log_dir = Path(log_dir)
        self.running = False
        self.readings = []

        # Create log directory
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Generate log filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name = test_name or "test"
        self.csv_path = self.log_dir / f"helios_{name}_{timestamp}.csv"
        self.csv_file = None
        self.csv_writer = None

    def start_csv(self):
        """Open CSV file and write header."""
        headers = [
            "timestamp",
            "elapsed_sec",
            "weight_g",
            "stable",
            "raw_scale",
        ]
        # Add sensor columns
        headers.extend(self.sensors.headers())

        self.csv_file = open(self.csv_path, "w", newline="")
        self.csv_writer = csv.writer(self.csv_file)
        self.csv_writer.writerow(headers)
        print(f"\n  Logging to: {self.csv_path}")

    def log_reading(self, elapsed, weight, stable, raw, sensor_data):
        """Write one row to CSV and flush."""
        timestamp = datetime.now().isoformat(timespec="milliseconds")
        row = [
            timestamp,
            f"{elapsed:.1f}",
            f"{weight:.3f}" if weight is not None else "",
            "Y" if stable else "N",
            raw,
        ]
        # Append sensor values in registration order
        for name in self.sensors.headers():
            val = sensor_data.get(name)
            row.append(f"{val:.2f}" if val is not None else "")

        self.csv_writer.writerow(row)
        self.csv_file.flush()

    def print_header(self):
        """Print terminal display header."""
        print("\n" + "=" * 60)
        print("  HELIOS DATA LOGGER")
        print("  Expedry Capsule Test System")
        print("=" * 60)
        sensor_info = ""
        if self.sensors.headers():
            sensor_info = f" + {', '.join(self.sensors.headers())}"
        print(f"  Scale: {self.scale.port}{sensor_info}")
        print(f"  Interval: {self.interval}s")
        print(f"  Log: {self.csv_path.name}")
        print("-" * 60)
        print(f"  {'Time':>10}  {'Elapsed':>8}  {'Weight (g)':>12}  {'Stable':>6}")
        print("-" * 60)

    def print_reading(self, elapsed, weight, stable, delta=None):
        """Print one reading to terminal."""
        now = datetime.now().strftime("%H:%M:%S")
        w_str = f"{weight:>12.3f}" if weight is not None else "      ------"
        s_str = "  Y" if stable else "  N"
        d_str = ""
        if delta is not None:
            sign = "+" if delta >= 0 else ""
            d_str = f"  ({sign}{delta:.3f})"

        print(f"  {now:>10}  {elapsed:>7.1f}s  {w_str}  {s_str}{d_str}")

    def run(self, duration=None):
        """Main logging loop.

        Args:
            duration: max seconds to run (None = until Ctrl+C)
        """
        self.running = True
        self.start_csv()
        self.print_header()

        start_time = time.time()
        baseline_weight = None
        reading_count = 0

        try:
            while self.running:
                elapsed = time.time() - start_time

                # Check duration limit
                if duration and elapsed >= duration:
                    print(f"\n  Duration reached ({duration}s). Stopping.")
                    break

                # Read scale
                weight, stable, raw = self.scale.read_weight()

                # Read additional sensors
                sensor_data = self.sensors.read_all()

                # Track baseline for delta display
                if weight is not None and baseline_weight is None:
                    baseline_weight = weight
                delta = (weight - baseline_weight) if (
                    weight is not None and baseline_weight is not None
                ) else None

                # Log and display
                self.log_reading(elapsed, weight, stable, raw, sensor_data)
                self.print_reading(elapsed, weight, stable, delta)

                reading_count += 1
                self.readings.append({
                    "elapsed": elapsed,
                    "weight": weight,
                    "stable": stable,
                })

                # Wait for next interval
                next_time = start_time + (reading_count * self.interval)
                sleep_time = next_time - time.time()
                if sleep_time > 0:
                    time.sleep(sleep_time)

        except KeyboardInterrupt:
            print("\n\n  Ctrl+C — stopping logger.")

        finally:
            self.stop()

    def stop(self):
        """Clean shutdown."""
        self.running = False
        if self.csv_file:
            self.csv_file.close()
        total = len(self.readings)
        weights = [r["weight"] for r in self.readings if r["weight"] is not None]

        print("\n" + "=" * 60)
        print("  TEST COMPLETE")
        print(f"  Total readings: {total}")
        if weights:
            print(f"  Weight range: {min(weights):.3f}g — {max(weights):.3f}g")
            print(f"  Net change:   {weights[-1] - weights[0]:+.3f}g")
        print(f"  Log saved: {self.csv_path}")
        print("=" * 60)


# ============================================================
#  LIVE PLOT (optional)
# ============================================================

def plot_results(csv_path):
    """Plot weight vs time from a completed log file."""
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("ERROR: matplotlib not installed. Run: pip install matplotlib")
        return

    times = []
    weights = []

    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["weight_g"]:
                times.append(float(row["elapsed_sec"]))
                weights.append(float(row["weight_g"]))

    if not weights:
        print("No weight data to plot.")
        return

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(times, weights, "b-", linewidth=1.5)
    ax.set_xlabel("Elapsed Time (seconds)")
    ax.set_ylabel("Weight (grams)")
    ax.set_title(f"Helios Weight Log — {Path(csv_path).stem}")
    ax.grid(True, alpha=0.3)

    # Add delta annotation
    delta = weights[-1] - weights[0]
    ax.annotate(
        f"Net change: {delta:+.3f}g",
        xy=(times[-1], weights[-1]),
        xytext=(-120, 20),
        textcoords="offset points",
        fontsize=11,
        arrowprops=dict(arrowstyle="->"),
        bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.8),
    )

    plt.tight_layout()
    plot_path = csv_path.replace(".csv", ".png")
    plt.savefig(plot_path, dpi=150)
    print(f"  Plot saved: {plot_path}")
    plt.show()


# ============================================================
#  CLI
# ============================================================

def list_ports():
    """Print all available serial ports."""
    ports = serial.tools.list_ports.comports()
    if not ports:
        print("  No serial ports found.")
        return
    print("\n  Available serial ports:")
    print("  " + "-" * 50)
    for p in ports:
        print(f"  {p.device:20s}  {p.description}")
        if p.hwid and p.hwid != "n/a":
            print(f"  {'':20s}  HW: {p.hwid}")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Helios Data Logger — Expedry Capsule Test System"
    )
    parser.add_argument("--port", "-p", help="Serial port (e.g., /dev/ttyUSB0)")
    parser.add_argument("--baud", "-b", type=int, default=DEFAULT_BAUD,
                        help=f"Baud rate (default: {DEFAULT_BAUD})")
    parser.add_argument("--interval", "-i", type=float, default=DEFAULT_INTERVAL,
                        help=f"Seconds between readings (default: {DEFAULT_INTERVAL})")
    parser.add_argument("--duration", "-d", type=float, default=None,
                        help="Max test duration in seconds (default: unlimited)")
    parser.add_argument("--name", "-n", default="capsule",
                        help="Test name for log filename (default: capsule)")
    parser.add_argument("--tare", "-t", action="store_true",
                        help="Send tare command before logging")
    parser.add_argument("--list-ports", "-l", action="store_true",
                        help="List available serial ports and exit")
    parser.add_argument("--plot", action="store_true",
                        help="Show plot after logging completes")
    parser.add_argument("--plot-file", help="Plot an existing CSV log file")
    parser.add_argument("--log-dir", default=str(LOG_DIR),
                        help=f"Log directory (default: {LOG_DIR})")

    args = parser.parse_args()

    # List ports mode
    if args.list_ports:
        list_ports()
        return

    # Plot existing file mode
    if args.plot_file:
        plot_results(args.plot_file)
        return

    # Normal logging mode
    print("\n  HELIOS LOGGER — Starting up...")

    # Initialize scale
    scale = BonvoisinScale(port=args.port, baud=args.baud)
    try:
        scale.connect()
    except ConnectionError as e:
        print(f"\n  ERROR: {e}")
        print("  Tip: Run with --list-ports to see available devices")
        sys.exit(1)

    # Tare if requested
    if args.tare:
        scale.tare()

    # Initialize sensor hub (empty for now — add sensors here later)
    sensors = SensorHub()
    # Example future additions:
    # sensors.register("humidity_chamber", lambda: read_dht22(pin=4))
    # sensors.register("humidity_ambient", lambda: read_dht22(pin=17))
    # sensors.register("temp_ir", lambda: read_mlx90614())

    # Initialize logger
    logger = HeliosLogger(
        scale=scale,
        sensor_hub=sensors,
        interval=args.interval,
        log_dir=args.log_dir,
        test_name=args.name,
    )

    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        logger.running = False
    signal.signal(signal.SIGINT, signal_handler)

    # Run
    logger.run(duration=args.duration)

    # Cleanup
    scale.disconnect()

    # Plot if requested
    if args.plot:
        plot_results(str(logger.csv_path))

    print("\n  Done.\n")


if __name__ == "__main__":
    main()
