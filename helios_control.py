#!/usr/bin/env python3
"""
HELIOS Steam Generator — Control System
Web-based dashboard for sensor monitoring and actuator control.

Access from any browser: http://<pi-ip>:5000

Hardware (Updated 2026-05-13):
  - MAX31855 (Hardware SPI bus 0, CE1=GPIO7=Pin 26)               → Puck thermocouple  (CE0/Pin 24 dead)
  - SHT41   (Software I2C bus 15: SDA=GPIO22, SCL=GPIO25)         → Chamber temp + humidity
  - SDP810  (Hardware I2C bus 1: SDA=GPIO2/Pin 3, SCL=GPIO3/Pin 5) → Differential pressure  (won't work on bus 15)
  - SSR-10 DD (GPIO5, Pin 29)     → Cartridge heater control  (GPIO27 + GPIO23 both dead/conflicted)
  - SSR-25 DA (GPIO6, Pin 31)     → MIFASOL boiling-pot humidifier (mains, 10k pulldown to GND)
  - Waveshare Modbus RTU Relay (RS485 /dev/ttyAMA0, 9600 baud)  → Pump CH2, Fan CH4  (humidifier moved to SSR-25DA)
  - Bonvoisin RS232 Scale (/dev/ttyUSB0, 9600 8N1)              → Weight (g) at 1Hz

Usage:
  sudo dtoverlay i2c-gpio i2c_gpio_sda=22 i2c_gpio_scl=25
  python3 helios_control.py
"""

import time
import json
import os
import threading
from collections import deque

# ── Hardware imports ────────────────────────────────────────────────
try:
    import smbus2
    from smbus2 import SMBus, i2c_msg
    import RPi.GPIO as GPIO
    import spidev
    from pymodbus.client import ModbusSerialClient
    import serial
    MOCK = False
except ImportError:
    MOCK = True
    print("⚠ Hardware libraries not found — running in MOCK mode")

from flask import Flask, jsonify, request, Response

# ── Configuration ───────────────────────────────────────────────────

HEATER_PIN      = 5          # BCM GPIO5 = Pin 29 (SSR-10 DD trigger +). Was GPIO27 (damaged), then GPIO23 (CAN HAT conflict), now GPIO5 (validated 2026-05-13).
HUMIDIFIER_PIN  = 6          # BCM GPIO6 = Pin 31 (SSR-25DA trigger +). Switches MIFASOL boiling-pot humidifier (mains). 10k pulldown to GND. Replaces sonic/Modbus-CH6 humidifier for the big chamber.

# Humidity PID — closed-loop chamber RH via slow-PWM of the MIFASOL boiler SSR.
HUM_KP          = 4.0        # %duty per %RH error
HUM_KI          = 0.08       # integral gain (closes steady offset)
HUM_KD          = 0.0        # derivative (start 0; add if it overshoots)
HUM_PWM_WINDOW  = 20.0       # seconds per boiler on/off cycle (boiler has thermal lag)
HUM_DEADBAND    = 1.0        # %RH; inside this band, hold

# Per-sensor calibration offsets (ADDED to each reading). Co-locate all sensors
# in still air, note each one's spread vs a chosen reference, and set these so
# they agree. Leave at 0.0 until you've done a co-location reading.
PUCK_T_OFFSET_F    = 0.0
CHAMBER_T_OFFSET_F = 0.0
CHAMBER_RH_OFFSET  = 0.0
COLUMN_T_OFFSET_F  = 0.0
COLUMN_RH_OFFSET   = 0.0
SHT41_BUS       = 15         # Software I2C via dtoverlay i2c-gpio (GPIO22=SDA, GPIO25=SCL) — SHT41 works fine here
SDP810_BUS      = 1          # Hardware I2C bus 1 (GPIO2/Pin3 = SDA, GPIO3/Pin5 = SCL) — SDP810 won't ACK on software bus 15
SDP810_ADDR     = 0x25
SHT41_ADDR      = 0x44       # SHT41 #1 (bus 15) = EXTERNAL chamber temp/RH
SHT41_COL_BUS   = 1          # SHT41 #2 shares hardware I2C bus 1 with the SDP810
SHT41_COL_ADDR  = 0x44       # SHT41 #2 (bus 1) = IN-COLUMN temp/RH (inside aluminum column, by the heating puck)

# Hardware SPI for MAX31855 (validated 2026-05-13: CE0/Pin 24 dead, using CE1/Pin 26)
SPI_BUS         = 0
SPI_DEVICE      = 1          # CE1 = Pin 26 (GPIO7). CE0/Pin 24 damaged on this Pi.
SPI_SPEED_HZ    = 500000     # Conservative; chip max is 5 MHz but 500 kHz is rock-solid

# Waveshare Modbus RTU Relay (RS485 via CAN HAT)
MODBUS_PORT     = '/dev/ttyAMA0'
MODBUS_BAUD     = 9600
MODBUS_ID       = 1
RELAY_PUMP      = 1          # Coil address 1 = CH2
RELAY_FAN       = 3          # Coil address 3 = CH4
RELAY_HUMID     = 5          # Coil address 5 = CH6 (DEPRECATED — humidifier moved to SSR-25DA on GPIO6; kept for reference)

# Bonvoisin RS232 Scale
SCALE_PORT      = '/dev/ttyUSB0'
SCALE_BAUD      = 9600

SENSOR_HZ       = 1          # sensor poll rate
HISTORY_SECONDS = 600        # 10 min rolling buffer

# ── Global state ────────────────────────────────────────────────────

state = {
    'puck_f': 0.0, 'puck_c': 0.0,
    'chamber_f': 0.0, 'chamber_c': 0.0,
    'humidity': 0.0,          # external chamber RH (SHT41 #1, bus 15)
    'column_c': 0.0, 'column_f': 0.0,
    'column_humidity': 0.0,   # in-column RH (SHT41 #2, bus 1)
    'pressure_pa': 0.0,
    'heater': False,
    'pump': False,
    'pump_cycle': 1,         # 0 = continuous, 1/2/3/5 = seconds between pulses
    'pump_pulse_ms': 300,    # pump ON duration per cycle (ms)
    'fan': False,
    'humidifier': False,
    'target_f': 300.0,
    'target_rh': 50.0,
    'humidity_auto': False,
    'weight_g': 0.0,
    'weight_stable': False,
    'scale_connected': False,
    'uptime': 0,
    'errors': [],
}
pump_cycle_thread = None
pump_cycle_stop = threading.Event()
history = deque(maxlen=HISTORY_SECONDS)
lock = threading.Lock()


def pump_cycle_loop():
    """Cycles pump on/off at the configured interval."""
    while not pump_cycle_stop.is_set():
        interval = state['pump_cycle']
        pulse = state['pump_pulse_ms'] / 1000.0
        if interval <= 0:
            # Continuous mode — pump stays on
            hw.set_pump(True)
            pump_cycle_stop.wait(0.5)
        else:
            hw.set_pump(True)
            pump_cycle_stop.wait(pulse)
            if pump_cycle_stop.is_set():
                break
            hw.set_pump(False)
            remaining = interval - pulse
            if remaining > 0:
                pump_cycle_stop.wait(remaining)
    hw.set_pump(False)


# ── Hardware abstraction ────────────────────────────────────────────

class Hardware:
    def __init__(self):
        if MOCK:
            return
        # I2C — SHT41 on software bus 15, SDP810 on hardware bus 1
        self.bus_sht41 = SMBus(SHT41_BUS)
        self.bus_sdp810 = SMBus(SDP810_BUS)

        # Hardware SPI for MAX31855 (CE1/Pin 26; CE0/Pin 24 damaged)
        self.spi = spidev.SpiDev()
        self.spi.open(SPI_BUS, SPI_DEVICE)
        self.spi.max_speed_hz = SPI_SPEED_HZ
        self.spi.mode = 0

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)

        # Heater SSR (SSR-10 DD) + Humidifier SSR (SSR-25DA → MIFASOL)
        GPIO.setup(HEATER_PIN, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(HUMIDIFIER_PIN, GPIO.OUT, initial=GPIO.LOW)

        # Modbus relay client
        self.modbus = ModbusSerialClient(
            port=MODBUS_PORT,
            baudrate=MODBUS_BAUD,
            parity='N',
            stopbits=1,
            timeout=1
        )
        self.modbus.connect()

        # Init SDP810 continuous mode — Differential pressure, average till read (0x3615)
        try:
            msg = i2c_msg.write(SDP810_ADDR, [0x36, 0x15])
            self.bus_sdp810.i2c_rdwr(msg)
            time.sleep(0.1)
        except Exception as e:
            print(f"SDP810 init failed: {e}")
        # Soft-reset SHT41
        try:
            self.bus_sht41.write_byte(SHT41_ADDR, 0x94)
            time.sleep(0.01)
        except:
            pass

        # Ensure all relays off at startup (humidifier is now a GPIO SSR, not a relay)
        for coil in [RELAY_PUMP, RELAY_FAN]:
            try:
                self.modbus.write_coil(coil, False, device_id=MODBUS_ID)
            except:
                pass

        # RS232 Scale
        self.scale_ser = None
        self._scale_lock = threading.Lock()
        self._last_weight = 0.0
        self._weight_stable = False
        self._scale_connected = False
        # The reader thread opens the port itself and self-heals — handles the
        # port being briefly busy at startup, or the scale unplugged/replugged.
        self._scale_thread = threading.Thread(target=self._scale_reader, daemon=True)
        self._scale_thread.start()

    # ── MAX31855 (Hardware SPI, CE1/Pin 26) ────────────────────────
    def read_thermocouple(self):
        if MOCK:
            return 25.0, 77.0
        raw = self.spi.xfer2([0, 0, 0, 0])
        val = (raw[0] << 24) | (raw[1] << 16) | (raw[2] << 8) | raw[3]

        if val == 0:
            raise RuntimeError("MAX31855: all zeros — check wiring")
        if val == 0xFFFFFFFF:
            raise RuntimeError("MAX31855: all ones — CS not pulsing or chip dead")
        if val & 0x10000:
            faults = val & 0x07
            msgs = []
            if faults & 0x01: msgs.append('TC open')
            if faults & 0x02: msgs.append('TC short GND')
            if faults & 0x04: msgs.append('TC short VCC')
            raise RuntimeError(f"MAX31855 fault: {', '.join(msgs)}")
        tc = (val >> 18) & 0x3FFF
        if tc & 0x2000:
            tc -= 16384
        c = tc * 0.25
        return c, c * 9 / 5 + 32

    # ── SHT41 #1 (I2C bus 15) — EXTERNAL chamber temp/RH ───────────
    def read_sht41(self):
        if MOCK:
            return 23.0, 73.4, 35.0
        self.bus_sht41.write_byte(SHT41_ADDR, 0xFD)
        time.sleep(0.03)
        msg = i2c_msg.read(SHT41_ADDR, 6)
        self.bus_sht41.i2c_rdwr(msg)
        d = list(msg)
        t = (d[0] << 8) | d[1]
        h = (d[3] << 8) | d[4]
        c = -45.0 + 175.0 * (t / 65535.0)
        rh = max(0, min(100, -6.0 + 125.0 * (h / 65535.0)))
        return c, c * 9 / 5 + 32, rh

    # ── SHT41 #2 (I2C bus 1, shared w/ SDP810) — IN-COLUMN temp/RH ──
    def read_sht41_column(self):
        if MOCK:
            return 40.0, 104.0, 80.0
        self.bus_sdp810.write_byte(SHT41_COL_ADDR, 0xFD)
        time.sleep(0.03)
        msg = i2c_msg.read(SHT41_COL_ADDR, 6)
        self.bus_sdp810.i2c_rdwr(msg)
        d = list(msg)
        t = (d[0] << 8) | d[1]
        h = (d[3] << 8) | d[4]
        c = -45.0 + 175.0 * (t / 65535.0)
        rh = max(0, min(100, -6.0 + 125.0 * (h / 65535.0)))
        return c, c * 9 / 5 + 32, rh

    # ── SDP810 (I2C bus 1, hardware) ───────────────────────────────
    def read_pressure(self):
        if MOCK:
            return 0.0
        # Read 9 bytes — SDP810 streams continuous result after the init command.
        try:
            msg = i2c_msg.read(SDP810_ADDR, 9)
            self.bus_sdp810.i2c_rdwr(msg)
            data = list(msg)
            dp = (data[0] << 8) | data[1]
            if dp > 32767:
                dp -= 65536
            scale = (data[6] << 8) | data[7]
            if scale == 0:
                scale = 60
            self._last_pa = dp / scale
            return self._last_pa
        except Exception:
            # A glitch (usually boiler-SSR switching noise) knocked it out of
            # continuous mode — re-arm the measurement so the next read recovers,
            # and hold the last good value instead of erroring.
            try:
                self.bus_sdp810.i2c_rdwr(i2c_msg.write(SDP810_ADDR, [0x36, 0x15]))
            except Exception:
                pass
            return getattr(self, '_last_pa', 0.0)

    # ── Heater (GPIO → SSR) ────────────────────────────────────────
    def set_heater(self, on):
        if MOCK:
            return
        GPIO.output(HEATER_PIN, GPIO.HIGH if on else GPIO.LOW)

    # ── Pump (Modbus relay CH2) ────────────────────────────────────
    def set_pump(self, on):
        if MOCK:
            return
        try:
            self.modbus.write_coil(RELAY_PUMP, on, device_id=MODBUS_ID)
        except Exception as e:
            print(f"Pump relay error: {e}")

    # ── Fan (Modbus relay CH4) ─────────────────────────────────────
    def set_fan(self, on):
        if MOCK:
            return
        try:
            self.modbus.write_coil(RELAY_FAN, on, device_id=MODBUS_ID)
        except Exception as e:
            print(f"Fan relay error: {e}")

    # ── Humidifier (GPIO → SSR-25DA → MIFASOL boiling-pot, mains) ───
    def set_humidifier(self, on):
        if MOCK:
            return
        GPIO.output(HUMIDIFIER_PIN, GPIO.HIGH if on else GPIO.LOW)

    # ── Scale (RS232) ─────────────────────────────────────────────────
    def _scale_reader(self):
        """Background thread: continuously reads scale RS232 stream."""
        buf = b''
        while True:
            try:
                if self.scale_ser is None or not self.scale_ser.is_open:
                    self.scale_ser = serial.Serial(
                        SCALE_PORT, SCALE_BAUD,
                        bytesize=8, parity='N', stopbits=1, timeout=2
                    )
                    self._scale_connected = True
                data = self.scale_ser.read(64)
                if not data:
                    continue
                buf += data
                # Process complete lines
                while b'\n' in buf or b'\r' in buf:
                    # Split on any line ending
                    line = b''
                    for i, byte in enumerate(buf):
                        if byte in (10, 13):  # \n or \r
                            line = buf[:i]
                            # Skip consecutive terminators
                            j = i + 1
                            while j < len(buf) and buf[j] in (10, 13):
                                j += 1
                            buf = buf[j:]
                            break
                    if not line:
                        if buf and buf[0] in (10, 13):
                            buf = buf[1:]
                        continue
                    self._parse_scale_line(line.decode('ascii', errors='ignore').strip())
            except Exception:
                self._scale_connected = False
                try:
                    if self.scale_ser:
                        self.scale_ser.close()
                except Exception:
                    pass
                self.scale_ser = None
                time.sleep(2)

    def _parse_scale_line(self, line):
        """Parse a weight reading line from the Bonvoisin scale.
        Formats: '  0.260', 'ST,  0.260 g', 'US,  0.123 g'
        """
        if not line:
            return
        stable = True
        # Check for stability prefix
        if line.startswith('ST,'):
            stable = True
            line = line[3:]
        elif line.startswith('US,'):
            stable = False
            line = line[3:]
        # Strip unit suffix
        for unit in ('g', 'oz', 'ct', 'ozt'):
            line = line.replace(unit, '')
        line = line.strip()
        try:
            weight = float(line)
            with self._scale_lock:
                self._last_weight = weight
                self._weight_stable = stable
                self._scale_connected = True
        except ValueError:
            pass

    def read_scale(self):
        """Return (weight_g, stable, connected)."""
        if MOCK:
            return 0.0, False, False
        with self._scale_lock:
            return self._last_weight, self._weight_stable, self._scale_connected

    def tare_scale(self):
        """Send tare command to scale."""
        if MOCK or not self.scale_ser:
            return False
        try:
            self.scale_ser.write(b'T\r\n')
            return True
        except:
            return False

    # ── Cleanup ─────────────────────────────────────────────────────
    def shutdown(self):
        if MOCK:
            return
        GPIO.output(HEATER_PIN, GPIO.LOW)
        GPIO.output(HUMIDIFIER_PIN, GPIO.LOW)
        for coil in [RELAY_PUMP, RELAY_FAN]:
            try:
                self.modbus.write_coil(coil, False, device_id=MODBUS_ID)
            except:
                pass
        self.modbus.close()
        if self.scale_ser:
            self.scale_ser.close()
        GPIO.cleanup()


hw = Hardware()


# ── Sensor polling thread ──────────────────────────────────────────

def sensor_loop():
    t0 = time.time()
    while True:
        errors = []
        try:
            c, f = hw.read_thermocouple()
            f += PUCK_T_OFFSET_F; c = (f - 32) * 5 / 9
            state['puck_c'] = round(c, 1)
            state['puck_f'] = round(f, 1)
        except Exception as e:
            errors.append(f"TC: {e}")

        try:
            c, f, rh = hw.read_sht41()
            f += CHAMBER_T_OFFSET_F; c = (f - 32) * 5 / 9; rh += CHAMBER_RH_OFFSET
            state['chamber_c'] = round(c, 1)
            state['chamber_f'] = round(f, 1)
            state['humidity'] = round(rh, 1)
        except Exception as e:
            errors.append(f"SHT41-chamber: {e}")

        try:
            cc, cf, crh = hw.read_sht41_column()
            cf += COLUMN_T_OFFSET_F; cc = (cf - 32) * 5 / 9; crh += COLUMN_RH_OFFSET
            state['column_c'] = round(cc, 1)
            state['column_f'] = round(cf, 1)
            state['column_humidity'] = round(crh, 1)
        except Exception as e:
            errors.append(f"SHT41-column: {e}")

        try:
            pa = hw.read_pressure()
            state['pressure_pa'] = round(pa, 2)
        except Exception as e:
            errors.append(f"SDP810: {e}")

        try:
            wg, ws, wc = hw.read_scale()
            state['weight_g'] = round(wg, 3)
            state['weight_stable'] = ws
            state['scale_connected'] = wc
        except Exception as e:
            errors.append(f"Scale: {e}")

        state['uptime'] = int(time.time() - t0)
        state['errors'] = errors

        with lock:
            history.append({
                't': round(time.time() - t0, 1),
                'puck': state['puck_f'],
                'chamber': state['chamber_f'],
                'rh': state['humidity'],
                'col_f': state['column_f'],
                'col_rh': state['column_humidity'],
                'pa': state['pressure_pa'],
                'wt': state['weight_g'],
            })

        time.sleep(1.0 / SENSOR_HZ)


# ── Flask app ──────────────────────────────────────────────────────

app = Flask(__name__)

DASHBOARD_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>HELIOS Control</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
<style>
  :root {
    --bg: #0f1117; --card: #1a1d27; --border: #2a2d3a;
    --text: #e4e4e7; --dim: #d1d5db; --accent: #f59e0b;
    --green: #22c55e; --red: #ef4444; --blue: #3b82f6;
  }
  * { margin:0; padding:0; box-sizing:border-box; }
  body {
    font-family: -apple-system, 'Segoe UI', Roboto, monospace;
    background: var(--bg); color: var(--text);
    min-height: 100vh;
    touch-action: pan-y; -webkit-overflow-scrolling: touch; overscroll-behavior-y: contain;
  }
  header {
    background: linear-gradient(135deg, #1a1d27 0%, #252836 100%);
    border-bottom: 1px solid var(--border);
    padding: 16px 24px;
    display: flex; justify-content: space-between; align-items: center;
  }
  header h1 {
    font-size: 20px; font-weight: 700; letter-spacing: 2px;
    color: var(--accent);
  }
  header .status {
    font-size: 15px; color: var(--dim);
  }
  header .status .dot {
    display: inline-block; width:8px; height:8px; border-radius:50%;
    background: var(--green); margin-right:6px; vertical-align: middle;
  }
  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 16px; padding: 20px 24px;
  }
  .card {
    background: var(--card); border: 1px solid var(--border);
    border-radius: 12px; padding: 20px;
  }
  .card .label {
    font-size: 14px; text-transform: uppercase; letter-spacing: 1.5px;
    color: var(--dim); margin-bottom: 8px;
  }
  .card .value {
    font-size: 36px; font-weight: 700; font-variant-numeric: tabular-nums;
    line-height: 1.1;
  }
  .card .unit {
    font-size: 18px; font-weight: 400; color: var(--dim); margin-left: 4px;
  }
  .card .sub {
    font-size: 15px; color: var(--dim); margin-top: 6px;
  }
  .card.puck .value { color: var(--accent); }
  .card.chamber .value { color: var(--blue); }
  .card.humidity .value { color: #06b6d4; }
  .card.pressure .value { color: #a78bfa; }
  .card.weight .value { color: #f472b6; }
  .card.weight .stable { color: var(--green); font-size: 11px; }
  .card.weight .unstable { color: var(--accent); font-size: 11px; }
  .card.weight .disconnected { color: var(--red); font-size: 11px; }
  .tare-btn {
    margin-top: 8px; padding: 8px 20px;
    background: #252836; color: var(--text); border: 1px solid var(--border);
    border-radius: 8px; font-size: 13px; font-weight: 600;
    cursor: pointer; touch-action: manipulation;
  }
  .tare-btn:active { background: var(--green); color: #000; }

  .controls {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 16px; padding: 0 24px 20px;
  }
  .ctrl-card {
    background: var(--card); border: 1px solid var(--border);
    border-radius: 12px; padding: 20px;
    display: flex; justify-content: space-between; align-items: center;
  }
  .ctrl-card .info h3 {
    font-size: 17px; font-weight: 600; margin-bottom: 4px;
  }
  .ctrl-card .info p {
    font-size: 15px; color: var(--dim);
  }
  .toggle {
    position: relative; width: 56px; height: 30px; cursor: pointer;
  }
  .toggle input { display: none; }
  .toggle .slider {
    position: absolute; inset: 0;
    background: #333; border-radius: 15px;
    transition: background 0.2s;
  }
  .toggle .slider::before {
    content: ''; position: absolute;
    width: 24px; height: 24px; border-radius: 50%;
    background: #fff; left: 3px; top: 3px;
    transition: transform 0.2s;
  }
  .toggle input:checked + .slider {
    background: var(--green);
  }
  .toggle input:checked + .slider::before {
    transform: translateX(26px);
  }
  .toggle.heater input:checked + .slider {
    background: var(--red);
  }
  .cyc-btn {
    flex: 1; min-width: 50px; padding: 12px 8px;
    background: #252836; color: var(--dim); border: 1px solid var(--border);
    border-radius: 8px; font-size: 15px; font-weight: 600;
    cursor: pointer; text-align: center;
    touch-action: manipulation;
  }
  .cyc-btn.active {
    background: var(--green); color: #000; border-color: var(--green);
  }

  .target-section {
    padding: 0 24px 20px;
  }
  .target-card {
    background: var(--card); border: 1px solid var(--border);
    border-radius: 12px; padding: 20px;
    display: flex; align-items: center; gap: 20px; flex-wrap: wrap;
  }
  .target-card label {
    font-size: 13px; font-weight: 600; white-space: nowrap;
  }
  .target-card input[type=range] {
    -webkit-appearance: none; appearance: none;
    flex: 1; min-width: 220px; height: 22px; border-radius: 11px;
    background: #2a2d3a; outline: none; cursor: pointer;
  }
  .target-card input[type=range]::-webkit-slider-thumb {
    -webkit-appearance: none; appearance: none;
    width: 46px; height: 46px; border-radius: 50%;
    background: var(--accent); border: 3px solid #fff; cursor: pointer;
  }
  .target-card input[type=range]::-moz-range-thumb {
    width: 46px; height: 46px; border-radius: 50%;
    background: var(--accent); border: 3px solid #fff; cursor: pointer;
  }
  .target-card .target-val {
    font-size: 24px; font-weight: 700; color: var(--accent);
    min-width: 80px; text-align: right;
  }

  .chart-section {
    padding: 0 24px 24px;
    display: grid; grid-template-columns: repeat(auto-fit, minmax(420px, 1fr)); gap: 16px;
  }
  .chart-card {
    background: var(--card); border: 1px solid var(--border);
    border-radius: 12px; padding: 16px 20px;
  }
  .chart-card h3 {
    font-size: 16px; font-weight: 600; color: var(--dim);
    text-transform: uppercase; letter-spacing: 1px;
    margin-bottom: 8px;
  }
  .chart-wrap {
    position: relative; height: 220px;
  }

  .errors {
    padding: 0 24px 16px;
  }
  .errors .err {
    background: #2d1215; border: 1px solid #5c2327;
    border-radius: 8px; padding: 10px 16px;
    font-size: 13px; color: #fca5a5;
  }
</style>
</head>
<body>

<header>
  <h1>HELIOS STEAM GENERATOR</h1>
  <div class="status">
    <span class="dot" id="statusDot"></span>
    <span id="statusText">Connecting...</span>
  </div>
</header>

<div class="grid">
  <div class="card puck">
    <div class="label">Puck Temperature</div>
    <div class="value"><span id="puckF">--</span><span class="unit">&deg;F</span></div>
    <div class="sub"><span id="puckC">--</span>&deg;C &bull; MAX31855</div>
  </div>
  <div class="card chamber">
    <div class="label">Chamber Temperature</div>
    <div class="value"><span id="chamberF">--</span><span class="unit">&deg;F</span></div>
    <div class="sub"><span id="chamberC">--</span>&deg;C &bull; SHT41</div>
  </div>
  <div class="card humidity">
    <div class="label">Chamber RH (external)</div>
    <div class="value"><span id="rh">--</span><span class="unit">%</span></div>
    <div class="sub">SHT41 #1 &bull; bus 15</div>
  </div>
  <div class="card chamber">
    <div class="label">Column Temp (in-tube)</div>
    <div class="value"><span id="colF">--</span><span class="unit">&deg;F</span></div>
    <div class="sub"><span id="colC">--</span>&deg;C &bull; SHT41 #2</div>
  </div>
  <div class="card humidity">
    <div class="label">Column RH (in-tube)</div>
    <div class="value"><span id="colRh">--</span><span class="unit">%</span></div>
    <div class="sub">SHT41 #2 &bull; bus 1</div>
  </div>
  <div class="card pressure">
    <div class="label">Differential Pressure</div>
    <div class="value"><span id="pa">--</span><span class="unit">Pa</span></div>
    <div class="sub">SDP810</div>
  </div>
  <div class="card weight">
    <div class="label">Scale Weight</div>
    <div class="value"><span id="weightG">--</span><span class="unit">g</span></div>
    <div class="sub">
      <span id="scaleStatus" class="disconnected">Disconnected</span> &bull; RS232
    </div>
    <button class="tare-btn" onclick="tareScale()">TARE</button>
  </div>
</div>

<div class="controls">
  <div class="ctrl-card">
    <div class="info">
      <h3>Cartridge Heater</h3>
      <p>GPIO5 &rarr; SSR-10 DD &rarr; 12V 40W&times;2</p>
    </div>
    <label class="toggle heater">
      <input type="checkbox" id="heaterToggle" onchange="toggleActuator('heater', this.checked)">
      <span class="slider"></span>
    </label>
  </div>
  <div class="ctrl-card" style="flex-wrap:wrap;">
    <div class="info" style="width:100%;display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
      <div>
        <h3>Peristaltic Pump</h3>
        <p>Modbus CH2 &rarr; 12V pump</p>
      </div>
      <label class="toggle">
        <input type="checkbox" id="pumpToggle" onchange="togglePump(this.checked)">
        <span class="slider"></span>
      </label>
    </div>
    <div id="pumpBtns" style="display:flex;gap:8px;flex-wrap:wrap;width:100%;">
      <button class="cyc-btn" data-cyc="0" onclick="setPumpCycle(0)">CONT</button>
      <button class="cyc-btn active" data-cyc="1" onclick="setPumpCycle(1)">1s</button>
      <button class="cyc-btn" data-cyc="2" onclick="setPumpCycle(2)">2s</button>
      <button class="cyc-btn" data-cyc="3" onclick="setPumpCycle(3)">3s</button>
      <button class="cyc-btn" data-cyc="5" onclick="setPumpCycle(5)">5s</button>
      <button class="cyc-btn" data-cyc="10" onclick="setPumpCycle(10)">10s</button>
    </div>
    <input type="hidden" id="pumpCycle" value="1">
  </div>
  <div class="ctrl-card">
    <div class="info">
      <h3>Exhaust Fan</h3>
      <p>Modbus CH4</p>
    </div>
    <label class="toggle">
      <input type="checkbox" id="fanToggle" onchange="toggleActuator('fan', this.checked)">
      <span class="slider"></span>
    </label>
  </div>
  <div class="ctrl-card">
    <div class="info">
      <h3>Chamber Humidifier</h3>
      <p>GPIO6 &rarr; SSR-25DA &rarr; MIFASOL boiler</p>
    </div>
    <label class="toggle">
      <input type="checkbox" id="humidifierToggle" onchange="toggleActuator('humidifier', this.checked)">
      <span class="slider"></span>
    </label>
  </div>
</div>

<div class="target-section">
  <div class="target-card">
    <label>Target Puck Temp</label>
    <input type="range" id="targetSlider" min="100" max="500" value="300"
           oninput="updateTarget(this.value)">
    <div class="target-val"><span id="targetVal">300</span>&deg;F</div>
  </div>
  <div class="target-card">
    <label>Target Chamber RH (PID)</label>
    <input type="range" id="rhSlider" min="0" max="95" value="50"
           oninput="updateHumidityTarget(this.value)">
    <div class="target-val"><span id="rhTargetVal">50</span>%</div>
    <label style="display:block;margin-top:8px;font-size:13px;font-weight:400">
      <input type="checkbox" id="humAutoToggle" onchange="toggleHumidityAuto(this.checked)">
      Auto (PID drives boiler)
    </label>
  </div>
</div>

<div id="errorBox" class="errors" style="display:none">
  <div class="err" id="errorText"></div>
</div>

<div class="chart-section">
  <div class="chart-card">
    <h3>Temperature</h3>
    <div class="chart-wrap">
      <canvas id="chartTemp"></canvas>
    </div>
  </div>
  <div class="chart-card">
    <h3>Humidity</h3>
    <div class="chart-wrap">
      <canvas id="chartHumid"></canvas>
    </div>
  </div>
  <div class="chart-card">
    <h3>Differential Pressure</h3>
    <div class="chart-wrap">
      <canvas id="chartPressure"></canvas>
    </div>
  </div>
  <div class="chart-card">
    <h3>Weight</h3>
    <div class="chart-wrap">
      <canvas id="chartWeight"></canvas>
    </div>
  </div>
</div>

<script>
// ── Chart setup ──
const timeFmt = v => { let s = parseInt(v); let m = Math.floor(s/60); return m + ':' + String(s%60).padStart(2,'0'); };
const baseOpts = {
  responsive: true, maintainAspectRatio: false, animation: false,
  interaction: { mode: 'index', intersect: false },
  plugins: { legend: { labels: { color: '#d1d5db', font: { size: 11 } } } },
};

const chartTemp = new Chart(document.getElementById('chartTemp').getContext('2d'), {
  type: 'line',
  data: {
    labels: [],
    datasets: [
      { label: 'Puck (°F)', data: [], borderColor: '#f59e0b', borderWidth: 2, pointRadius: 0, tension: 0.3 },
      { label: 'Chamber (°F)', data: [], borderColor: '#3b82f6', borderWidth: 2, pointRadius: 0, tension: 0.3 },
      { label: 'Column (°F)', data: [], borderColor: '#22c55e', borderWidth: 2, pointRadius: 0, tension: 0.3 },
    ]
  },
  options: { ...baseOpts, scales: {
    x: { ticks: { color: '#d1d5db', maxTicksLimit: 10, callback: timeFmt }, grid: { color: '#1f2233' } },
    y: { position: 'left', title: { display: true, text: '°F', color: '#d1d5db' }, ticks: { color: '#d1d5db' }, grid: { color: '#1f2233' } }
  }}
});

const chartHumid = new Chart(document.getElementById('chartHumid').getContext('2d'), {
  type: 'line',
  data: {
    labels: [],
    datasets: [
      { label: 'Chamber RH (%)', data: [], borderColor: '#06b6d4', borderWidth: 2, pointRadius: 0, tension: 0.3 },
      { label: 'Column RH (%)', data: [], borderColor: '#f59e0b', borderWidth: 2, pointRadius: 0, tension: 0.3 },
    ]
  },
  options: { ...baseOpts, scales: {
    x: { ticks: { color: '#d1d5db', maxTicksLimit: 10, callback: timeFmt }, grid: { color: '#1f2233' } },
    y: { position: 'left', title: { display: true, text: '%RH', color: '#d1d5db' }, ticks: { color: '#d1d5db' }, grid: { color: '#1f2233' }, min: 0, max: 100 }
  }}
});

const chartPressure = new Chart(document.getElementById('chartPressure').getContext('2d'), {
  type: 'line',
  data: {
    labels: [],
    datasets: [
      { label: 'Pressure (Pa)', data: [], borderColor: '#a78bfa', borderWidth: 2, pointRadius: 0, tension: 0.3,
        fill: true, backgroundColor: 'rgba(167,139,250,0.1)' },
    ]
  },
  options: { ...baseOpts, scales: {
    x: { ticks: { color: '#d1d5db', maxTicksLimit: 10, callback: timeFmt }, grid: { color: '#1f2233' } },
    y: { position: 'left', title: { display: true, text: 'Pa', color: '#d1d5db' }, ticks: { color: '#d1d5db' }, grid: { color: '#1f2233' } }
  }}
});

const chartWeight = new Chart(document.getElementById('chartWeight').getContext('2d'), {
  type: 'line',
  data: {
    labels: [],
    datasets: [
      { label: 'Weight (g)', data: [], borderColor: '#f472b6', borderWidth: 2, pointRadius: 0, tension: 0.3,
        fill: true, backgroundColor: 'rgba(244,114,182,0.1)' },
    ]
  },
  options: { ...baseOpts, scales: {
    x: { ticks: { color: '#d1d5db', maxTicksLimit: 10, callback: timeFmt }, grid: { color: '#1f2233' } },
    y: { position: 'left', title: { display: true, text: 'g', color: '#d1d5db' }, ticks: { color: '#d1d5db' }, grid: { color: '#1f2233' } }
  }}
});

// ── Polling ──
async function poll() {
  try {
    const r = await fetch('/api/data');
    const d = await r.json();

    document.getElementById('puckF').textContent = d.puck_f.toFixed(1);
    document.getElementById('puckC').textContent = d.puck_c.toFixed(1);
    document.getElementById('chamberF').textContent = d.chamber_f.toFixed(1);
    document.getElementById('chamberC').textContent = d.chamber_c.toFixed(1);
    document.getElementById('rh').textContent = d.humidity.toFixed(1);
    document.getElementById('colF').textContent = d.column_f.toFixed(1);
    document.getElementById('colC').textContent = d.column_c.toFixed(1);
    document.getElementById('colRh').textContent = d.column_humidity.toFixed(1);
    document.getElementById('pa').textContent = d.pressure_pa.toFixed(2);

    document.getElementById('weightG').textContent = d.weight_g.toFixed(3);
    let ss = document.getElementById('scaleStatus');
    if (!d.scale_connected) { ss.textContent = 'Disconnected'; ss.className = 'disconnected'; }
    else if (d.weight_stable) { ss.textContent = 'Stable'; ss.className = 'stable'; }
    else { ss.textContent = 'Unstable'; ss.className = 'unstable'; }

    document.getElementById('heaterToggle').checked = d.heater;
    document.getElementById('pumpToggle').checked = d.pump;
    document.getElementById('pumpCycle').value = d.pump_cycle;
    document.querySelectorAll('.cyc-btn').forEach(b => {
      b.classList.toggle('active', parseInt(b.dataset.cyc) === d.pump_cycle);
    });
    document.getElementById('fanToggle').checked = d.fan;
    document.getElementById('humidifierToggle').checked = d.humidifier;

    let dot = document.getElementById('statusDot');
    let txt = document.getElementById('statusText');
    dot.style.background = '#22c55e';
    let m = Math.floor(d.uptime / 60);
    let s = d.uptime % 60;
    txt.textContent = 'Online · ' + m + ':' + String(s).padStart(2, '0');

    if (d.errors && d.errors.length > 0) {
      document.getElementById('errorBox').style.display = 'block';
      document.getElementById('errorText').textContent = d.errors.join(' | ');
    } else {
      document.getElementById('errorBox').style.display = 'none';
    }
  } catch(e) {
    document.getElementById('statusDot').style.background = '#ef4444';
    document.getElementById('statusText').textContent = 'Disconnected';
  }
}

async function pollHistory() {
  try {
    const r = await fetch('/api/history');
    const h = await r.json();
    const labels = h.map(p => p.t);
    chartTemp.data.labels = labels;
    chartTemp.data.datasets[0].data = h.map(p => p.puck);
    chartTemp.data.datasets[1].data = h.map(p => p.chamber);
    chartTemp.data.datasets[2].data = h.map(p => p.col_f);
    chartTemp.update();
    chartHumid.data.labels = labels;
    chartHumid.data.datasets[0].data = h.map(p => p.rh);
    chartHumid.data.datasets[1].data = h.map(p => p.col_rh);
    chartHumid.update();
    chartPressure.data.labels = labels;
    chartPressure.data.datasets[0].data = h.map(p => p.pa);
    chartPressure.update();
    chartWeight.data.labels = labels;
    chartWeight.data.datasets[0].data = h.map(p => p.wt);
    chartWeight.update();
  } catch(e) {}
}

async function toggleActuator(name, on) {
  await fetch('/api/' + name, {
    method: 'POST', headers: {'Content-Type':'application/json'},
    body: JSON.stringify({on})
  });
}

async function togglePump(on) {
  let cycle = parseInt(document.getElementById('pumpCycle').value);
  await fetch('/api/pump', {
    method: 'POST', headers: {'Content-Type':'application/json'},
    body: JSON.stringify({on, cycle})
  });
}

async function setPumpCycle(val) {
  val = parseInt(val);
  document.getElementById('pumpCycle').value = val;
  document.querySelectorAll('.cyc-btn').forEach(b => {
    b.classList.toggle('active', parseInt(b.dataset.cyc) === val);
  });
  await fetch('/api/pump_cycle', {
    method: 'POST', headers: {'Content-Type':'application/json'},
    body: JSON.stringify({cycle: val})
  });
}

async function tareScale() {
  await fetch('/api/tare', { method: 'POST', headers: {'Content-Type':'application/json'}, body: '{}' });
}

function updateTarget(val) {
  document.getElementById('targetVal').textContent = val;
  fetch('/api/target', {
    method: 'POST', headers: {'Content-Type':'application/json'},
    body: JSON.stringify({target_f: parseFloat(val)})
  });
}

function updateHumidityTarget(val) {
  document.getElementById('rhTargetVal').textContent = val;
  fetch('/api/humidity-target', {
    method: 'POST', headers: {'Content-Type':'application/json'},
    body: JSON.stringify({target_rh: parseFloat(val)})
  });
}

function toggleHumidityAuto(on) {
  fetch('/api/humidity-auto', {
    method: 'POST', headers: {'Content-Type':'application/json'},
    body: JSON.stringify({on: on})
  });
}

setInterval(poll, 1000);
setInterval(pollHistory, 2000);
poll();
pollHistory();
</script>
</body>
</html>"""


@app.route('/')
def index():
    return Response(DASHBOARD_HTML, mimetype='text/html')

@app.route('/api/data')
def api_data():
    return jsonify(state)

@app.route('/api/history')
def api_history():
    with lock:
        return jsonify(list(history))

@app.route('/api/heater', methods=['POST'])
def api_heater():
    on = request.json.get('on', False)
    hw.set_heater(on)
    state['heater'] = on
    return jsonify({'ok': True})

@app.route('/api/pump', methods=['POST'])
def api_pump():
    global pump_cycle_thread
    on = request.json.get('on', False)
    cycle = request.json.get('cycle', state['pump_cycle'])
    state['pump_cycle'] = cycle
    state['pump'] = on
    # Stop any existing cycle thread
    pump_cycle_stop.set()
    if pump_cycle_thread and pump_cycle_thread.is_alive():
        pump_cycle_thread.join(timeout=2)
    if on:
        pump_cycle_stop.clear()
        pump_cycle_thread = threading.Thread(target=pump_cycle_loop, daemon=True)
        pump_cycle_thread.start()
    else:
        hw.set_pump(False)
    return jsonify({'ok': True})

@app.route('/api/pump_cycle', methods=['POST'])
def api_pump_cycle():
    cycle = request.json.get('cycle', 0)
    state['pump_cycle'] = cycle
    # If pump is running, restart with new cycle rate
    if state['pump']:
        global pump_cycle_thread
        pump_cycle_stop.set()
        if pump_cycle_thread and pump_cycle_thread.is_alive():
            pump_cycle_thread.join(timeout=2)
        pump_cycle_stop.clear()
        pump_cycle_thread = threading.Thread(target=pump_cycle_loop, daemon=True)
        pump_cycle_thread.start()
    return jsonify({'ok': True})

@app.route('/api/fan', methods=['POST'])
def api_fan():
    on = request.json.get('on', False)
    hw.set_fan(on)
    state['fan'] = on
    return jsonify({'ok': True})

@app.route('/api/humidifier', methods=['POST'])
def api_humidifier():
    on = request.json.get('on', False)
    hw.set_humidifier(on)
    state['humidifier'] = on
    return jsonify({'ok': True})

@app.route('/api/target', methods=['POST'])
def api_target():
    f = request.json.get('target_f', 300)
    state['target_f'] = float(f)
    return jsonify({'ok': True})

@app.route('/api/tare', methods=['POST'])
def api_tare():
    ok = hw.tare_scale()
    return jsonify({'ok': ok})

@app.route('/api/humidity-target', methods=['POST'])
def api_humidity_target():
    state['target_rh'] = float(request.json.get('target_rh', 50))
    return jsonify({'ok': True})

@app.route('/api/humidity-auto', methods=['POST'])
def api_humidity_auto():
    on = bool(request.json.get('on', False))
    state['humidity_auto'] = on
    if not on:
        hw.set_humidifier(False)
        state['humidifier'] = False
    return jsonify({'ok': True})


def humidity_pid_loop():
    """Closed-loop chamber RH: PID -> slow-PWM the MIFASOL boiler SSR.
    Feedback = chamber SHT41 #1 (state['humidity']). Boiler only ADDS moisture,
    so output clamps 0-100% (drying is passive / via the exhaust fan)."""
    integral = 0.0
    last_err = 0.0
    i_clamp = 100.0 / max(HUM_KI, 1e-6)   # anti-windup: keep KI*integral <= 100
    while True:
        if not state['humidity_auto']:
            integral = 0.0
            last_err = 0.0
            time.sleep(1.0)
            continue
        err = state['target_rh'] - state['humidity']
        if abs(err) <= HUM_DEADBAND:
            duty = 0.0
            integral *= 0.98
        else:
            integral = max(-i_clamp, min(i_clamp, integral + err * HUM_PWM_WINDOW))
            deriv = (err - last_err) / HUM_PWM_WINDOW
            duty = max(0.0, min(100.0, HUM_KP * err + HUM_KI * integral + HUM_KD * deriv))
        last_err = err
        on_time = HUM_PWM_WINDOW * duty / 100.0
        if on_time >= 0.3:
            hw.set_humidifier(True)
            state['humidifier'] = True
            time.sleep(min(on_time, HUM_PWM_WINDOW))
        hw.set_humidifier(False)
        state['humidifier'] = False
        rest = HUM_PWM_WINDOW - on_time
        if rest > 0:
            time.sleep(rest)


# ── Main ────────────────────────────────────────────────────────────

if __name__ == '__main__':
    print("=" * 50)
    print("  HELIOS STEAM GENERATOR — Control System")
    print("=" * 50)
    if MOCK:
        print("  MODE: Mock (no hardware)")
    else:
        print("  MODE: Live hardware")
    print(f"  SHT41 I2C: bus {SHT41_BUS} (software GPIO22/25)")
    print(f"  SDP810 I2C: bus {SDP810_BUS} (hardware GPIO2/3)")
    print(f"  MAX31855 SPI: bus {SPI_BUS}, CE{SPI_DEVICE} (Pin 24=CE0/dead, Pin 26=CE1/active)")
    print(f"  Heater: GPIO{HEATER_PIN}")
    print(f"  Relays: Modbus RTU @ {MODBUS_PORT}")
    print(f"  Scale: RS232 @ {SCALE_PORT}")
    print(f"  Dashboard: http://0.0.0.0:5000")
    print("=" * 50)

    t = threading.Thread(target=sensor_loop, daemon=True)
    t.start()
    threading.Thread(target=humidity_pid_loop, daemon=True).start()

    try:
        app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
    except KeyboardInterrupt:
        pass
    finally:
        hw.shutdown()
        print("\nShutdown complete — all outputs OFF")
