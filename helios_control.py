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
import math
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
EXHAUST_PIN     = 13         # BCM GPIO13 = Pin 33 (hardware PWM1). MOSFET module TRIG/PWM -> WDERR 12V exhaust fan. PWM speed control.
EXHAUST_PWM_HZ  = 1000       # PWM frequency for the exhaust fan MOSFET (raise toward 20k if it buzzes)

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
# Column SHT41 self-heating (sealed cap): the breakout's own heat makes the chip
# read this many °F hot. Corrected PROPERLY — temp is lowered AND RH is recomputed
# at the true air temp via preserved dew point (holds across the range, unlike a
# flat offset). Measure: column-temp minus chamber-temp at steady state, set here.
COLUMN_SELFHEAT_F  = 14.2

def _sht_crc(b0, b1):
    """Sensirion CRC-8 (poly 0x31, init 0xFF) over two data bytes — used to
    reject corrupted SHT41 reads coming over the long, noisy bus-1 cable."""
    crc = 0xFF
    for byte in (b0, b1):
        crc ^= byte
        for _ in range(8):
            crc = ((crc << 1) ^ 0x31) & 0xFF if (crc & 0x80) else (crc << 1) & 0xFF
    return crc


def _selfheat_correct(tc_chip, rh_chip, dT_c):
    """Compensate an SHT41 for sensor self-heating of dT_c °C. The chip's heat
    doesn't change the air's actual moisture, so its dew point is preserved — we
    hold the dew point and recompute RH at the true (cooler) air temperature.
    Physically correct across the whole temperature range, unlike a flat offset."""
    if dT_c == 0:
        return tc_chip, rh_chip
    a, b = 17.625, 243.04
    rh = max(1.0, min(100.0, rh_chip))
    g = math.log(rh / 100.0) + a * tc_chip / (b + tc_chip)
    td = b * g / (a - g)                       # dew point — unaffected by self-heat
    tc_air = tc_chip - dT_c                     # true (cooler) air temp
    rh_air = 100.0 * math.exp(a * td / (b + td) - a * tc_air / (b + tc_air))
    return tc_air, max(0.0, min(100.0, rh_air))
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
    'exhaust': 0,              # exhaust fan PWM speed 0-100% (GPIO13 MOSFET)
    'humidifier': False,
    'standby': False,          # Hot Start: hold the puck warm between tests
    'standby_f': 180.0,        # standby hold temperature (F)
    'target_f': 300.0,
    'target_rh': 50.0,
    'humidity_auto': False,
    'char_running': False,
    'char_phase': 'IDLE',
    'char_mode': '',
    'char_elapsed': 0,
    'char_time_to_target': 0.0,
    'char_peak_rh': 0.0,
    'char_peak_time': 0.0,
    'char_water_gone_time': 0.0,
    'char_target_rh': 80.0,
    'char_csv': '',
    'weight_g': 0.0,
    'weight_stable': False,
    'scale_connected': False,
    'uptime': 0,
    'errors': [],
}
pump_cycle_thread = None
pump_cycle_stop = threading.Event()

TEST_DATA_DIR = os.path.expanduser('~/helios/data')
PUMP_ML_PER_S = 1.667        # calibrated continuous pump rate (DripRateTest.xlsx)
DRY_PUCK_F = 245.0           # water-gone mark: puck pins ~212F while boiling, spikes past this when dry
MAX_PUCK_F = 290.0           # dry-puck safety: cut heat once it runs this hot (water long gone)
char_thread = None
char_stop = threading.Event()
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

        # Exhaust fan — software PWM on GPIO13 via plain digital output (rpi-lgpio
        # hardware PWM doesn't drive the pin on Pi 5; GPIO.output is proven to work).
        GPIO.setup(EXHAUST_PIN, GPIO.OUT, initial=GPIO.LOW)
        self._exhaust_duty = 0.0
        self._exhaust_run = True
        threading.Thread(target=self._exhaust_pwm_loop, daemon=True).start()

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
        try:
            self.bus_sdp810.write_byte(SHT41_COL_ADDR, 0xFD)
            time.sleep(0.03)
            msg = i2c_msg.read(SHT41_COL_ADDR, 6)
            self.bus_sdp810.i2c_rdwr(msg)
            d = list(msg)
            # Reject corrupted reads from the long bus-1 cable via Sensirion CRC.
            if _sht_crc(d[0], d[1]) != d[2] or _sht_crc(d[3], d[4]) != d[5]:
                raise ValueError("SHT41 column CRC fail")
            t = (d[0] << 8) | d[1]
            h = (d[3] << 8) | d[4]
            c = -45.0 + 175.0 * (t / 65535.0)
            rh = max(0, min(100, -6.0 + 125.0 * (h / 65535.0)))
            self._last_col = (c, c * 9 / 5 + 32, rh)
            return self._last_col
        except Exception:
            # bad read (CRC fail or I/O error) — hold last good instead of garbage
            return getattr(self, '_last_col', (23.0, 73.4, 40.0))

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

    # ── Exhaust fan (software PWM via MOSFET on GPIO13) ───────────────
    def set_exhaust(self, pct):
        self._exhaust_duty = max(0.0, min(100.0, float(pct)))

    def _exhaust_pwm_loop(self):
        period = 1.0 / 100.0      # 100 Hz software PWM (fine for a fan)
        while self._exhaust_run:
            d = self._exhaust_duty
            if d <= 0:
                GPIO.output(EXHAUST_PIN, GPIO.LOW);  time.sleep(period); continue
            if d >= 100:
                GPIO.output(EXHAUST_PIN, GPIO.HIGH); time.sleep(period); continue
            on = period * d / 100.0
            GPIO.output(EXHAUST_PIN, GPIO.HIGH); time.sleep(on)
            GPIO.output(EXHAUST_PIN, GPIO.LOW);  time.sleep(period - on)

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
        self._exhaust_duty = 0.0
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
            cc, crh = _selfheat_correct(cc, crh, COLUMN_SELFHEAT_F / 1.8)
            crh = max(0.0, min(100.0, crh + COLUMN_RH_OFFSET))
            cf = cc * 9 / 5 + 32
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
    padding: 8px 16px;
    display: flex; justify-content: space-between; align-items: center;
  }
  header h1 {
    font-size: 17px; font-weight: 700; letter-spacing: 2px;
    color: var(--accent);
  }
  header .status {
    font-size: 15px; color: var(--dim);
  }
  header .status .dot {
    display: inline-block; width:8px; height:8px; border-radius:50%;
    background: var(--green); margin-right:6px; vertical-align: middle;
  }
  /* ===== compact single-screen layout ===== */
  .grid {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 8px; padding: 8px 12px;
  }
  .card {
    background: var(--card); border: 1px solid var(--border);
    border-radius: 10px; padding: 8px 10px;
  }
  .card .label {
    font-size: 10px; text-transform: uppercase; letter-spacing: 0.6px;
    color: var(--dim); margin-bottom: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  }
  .card .value {
    font-size: 26px; font-weight: 700; font-variant-numeric: tabular-nums;
    line-height: 1.05;
  }
  .card .unit {
    font-size: 14px; font-weight: 400; color: var(--dim); margin-left: 3px;
  }
  .card .sub {
    font-size: 10px; color: var(--dim); margin-top: 2px;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  }
  /* two-column body: charts left, controls+test right; sensors stay pinned on top */
  .main {
    display: grid;
    grid-template-columns: 1.25fr 1fr;
    gap: 10px; padding: 0 12px 10px;
    align-items: start;
  }
  .main > .chart-section { grid-column: 1; grid-row: 1 / 3; }
  .main > .controls      { grid-column: 2; grid-row: 1; }
  .main > .target-section{ grid-column: 2; grid-row: 2; }
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
    display: grid; grid-template-columns: 1fr 1fr;
    gap: 8px; padding: 0;
  }
  .controls > .ctrl-card[style*="flex-wrap"] { grid-column: 1 / -1; }  /* wide cards span full width */
  .ctrl-card {
    background: var(--card); border: 1px solid var(--border);
    border-radius: 10px; padding: 10px 12px;
    display: flex; justify-content: space-between; align-items: center;
  }
  .ctrl-card .info h3 {
    font-size: 14px; font-weight: 600; margin-bottom: 2px;
  }
  .ctrl-card .info p {
    font-size: 11px; color: var(--dim);
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
    padding: 0;
  }
  .target-card {
    background: var(--card); border: 1px solid var(--border);
    border-radius: 10px; padding: 10px 12px; margin-bottom: 8px;
    display: flex; align-items: center; gap: 14px; flex-wrap: wrap;
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
    padding: 0;
    display: grid; grid-template-columns: 1fr 1fr; gap: 8px;
  }
  .chart-card {
    background: var(--card); border: 1px solid var(--border);
    border-radius: 10px; padding: 8px 12px;
  }
  .chart-card h3 {
    font-size: 12px; font-weight: 600; color: var(--dim);
    text-transform: uppercase; letter-spacing: 0.6px;
    margin-bottom: 4px;
  }
  .chart-wrap {
    position: relative; height: 150px;
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

<div class="main">
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
  <div class="ctrl-card">
    <div class="info">
      <h3>Hot Start</h3>
      <p>Pre-warm &amp; hold puck <input id="standbyTarget" type="number" value="180" onchange="setStandbyTarget(this.value)" style="width:52px;font-size:13px;padding:3px;background:#252836;color:var(--text);border:1px solid var(--border);border-radius:5px;">&deg;F</p>
    </div>
    <label class="toggle">
      <input type="checkbox" id="standbyToggle" onchange="toggleStandby(this.checked)">
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
    <div style="display:flex;gap:8px;flex-wrap:wrap;width:100%;margin-top:10px;">
      <span style="font-size:13px;opacity:.85;width:100%;">Timed continuous run (pump-volume calibration):</span>
      <button class="cyc-btn" onclick="pumpTimed(10)">RUN 10s</button>
      <button class="cyc-btn" onclick="pumpTimed(20)">RUN 20s</button>
      <button class="cyc-btn" onclick="pumpTimed(30)">RUN 30s</button>
    </div>
  </div>
  <div class="ctrl-card">
    <div class="info">
      <h3>Circulation Fan</h3>
      <p>Modbus CH4 &bull; chamber mixing</p>
    </div>
    <label class="toggle">
      <input type="checkbox" id="fanToggle" onchange="toggleActuator('fan', this.checked)">
      <span class="slider"></span>
    </label>
  </div>
  <div class="ctrl-card" style="flex-wrap:wrap;">
    <div class="info" style="width:100%;display:flex;justify-content:space-between;align-items:center;">
      <div><h3>Exhaust Fan</h3><p>GPIO13 PWM &bull; MOSFET &bull; venting</p></div>
      <div style="font-size:22px;font-weight:700;color:var(--accent);"><span id="exhaustVal">0</span>%</div>
    </div>
    <input type="range" min="0" max="100" value="0" id="exhaustSlider" oninput="setExhaust(this.value)"
           style="width:100%;height:22px;margin-top:8px;">
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
  <div class="ctrl-card" style="flex-wrap:wrap;">
    <div class="info" style="width:100%;margin-bottom:10px;">
      <h3>Characterization Test</h3>
      <p>Boil a water charge (or drip onto a hot puck) — logs time-to-target RH to CSV</p>
    </div>
    <div style="display:flex;gap:18px;flex-wrap:wrap;width:100%;align-items:center;">
      <label style="font-size:16px;">Mode
        <select id="charMode" onchange="charFields()" style="margin-left:8px;font-size:19px;padding:10px;border-radius:8px;">
          <option value="boil">Boil charge</option>
          <option value="drip">Drip on hot puck</option>
          <option value="driphold">Drip &rarr; hold RH</option>
        </select>
      </label>
      <label id="charChargeLbl" style="font-size:16px;">Charge&nbsp;s <input id="charCharge" type="number" value="30" style="width:90px;font-size:19px;padding:10px;"></label>
      <label style="font-size:16px;">Target&nbsp;RH% <input id="charTarget" type="number" value="80" style="width:90px;font-size:19px;padding:10px;"></label>
      <label style="font-size:16px;">Timeout&nbsp;min <input id="charTimeout" type="number" value="15" style="width:90px;font-size:19px;padding:10px;"></label>
    </div>
    <label style="font-size:16px;width:100%;margin-top:12px;display:flex;align-items:center;gap:10px;">
      <input type="checkbox" id="charStopAtTarget" style="width:26px;height:26px;">
      Cut heat at target RH (leave OFF to run to full dry-out &amp; record the humidity peak)
    </label>
    <div id="charDripRow" style="display:none;gap:18px;flex-wrap:wrap;width:100%;align-items:center;margin-top:12px;background:#15171f;padding:12px;border-radius:8px;">
      <span style="font-size:14px;opacity:.85;width:100%;">Drip mode only: after the puck preheats, pulse the pump on/off onto the hot puck.</span>
      <label style="font-size:16px;">on&nbsp;s <input id="charDripOn" type="number" value="1" style="width:74px;font-size:19px;padding:10px;"></label>
      <label style="font-size:16px;">off&nbsp;s <input id="charDripOff" type="number" value="10" style="width:74px;font-size:19px;padding:10px;"></label>
      <label style="font-size:16px;">repeats <input id="charDripCount" type="number" value="20" style="width:74px;font-size:19px;padding:10px;"></label>
      <label style="font-size:16px;">preheat&nbsp;&deg;F <input id="charPreheat" type="number" value="200" style="width:84px;font-size:19px;padding:10px;"></label>
    </div>
    <div id="charHoldRow" style="display:none;gap:18px;flex-wrap:wrap;width:100%;align-items:center;margin-top:12px;background:#15171f;padding:12px;border-radius:8px;">
      <span style="font-size:14px;opacity:.85;width:100%;">Drip&rarr;hold: preheat the puck, drip onto it to climb to Target RC%, then hold by auto-modulating drip rate + puck heat. (Uses Target RH% &amp; Timeout above.)</span>
      <label style="font-size:16px;">preheat&nbsp;&deg;F <input id="charHoldPreheat" type="number" value="212" style="width:84px;font-size:19px;padding:10px;"></label>
      <label style="font-size:16px;">hold puck&nbsp;&deg;F <input id="charPuckHold" type="number" value="240" style="width:84px;font-size:19px;padding:10px;"></label>
      <label style="font-size:16px;">drip pulse&nbsp;ms <input id="charDripMs" type="number" value="200" style="width:84px;font-size:19px;padding:10px;"></label>
      <label style="font-size:16px;">climb every&nbsp;s <input id="charClimbInt" type="number" value="2" style="width:74px;font-size:19px;padding:10px;"></label>
      <label style="font-size:16px;">fan
        <select id="charFanMode" style="margin-left:6px;font-size:19px;padding:10px;border-radius:8px;">
          <option value="continuous">continuous</option>
          <option value="cycle">cycle</option>
          <option value="off">off</option>
        </select>
      </label>
      <label style="font-size:16px;">fan on&nbsp;s <input id="charFanOn" type="number" value="30" style="width:74px;font-size:19px;padding:10px;"></label>
      <label style="font-size:16px;">fan off&nbsp;s <input id="charFanOff" type="number" value="30" style="width:74px;font-size:19px;padding:10px;"></label>
    </div>
    <div style="width:100%;display:flex;gap:12px;margin-top:16px;">
      <button onclick="charStart()" style="flex:2;padding:20px;border-radius:10px;background:var(--green);color:#000;border:none;font-size:19px;font-weight:700;cursor:pointer;">Start Test</button>
      <button onclick="charStop()" style="flex:1;padding:20px;border-radius:10px;background:var(--red);color:#fff;border:none;font-size:19px;font-weight:700;cursor:pointer;">Stop</button>
      <button onclick="charDownload()" style="flex:1;padding:20px;border-radius:10px;background:#334155;color:#fff;border:none;font-size:19px;font-weight:700;cursor:pointer;">Save CSV</button>
    </div>
    <div id="charStatus" style="width:100%;margin-top:14px;font-size:18px;font-weight:700;">Idle</div>
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

    var cs = document.getElementById('charStatus');
    if (cs) {
      var hit80 = d.char_time_to_target > 0
        ? (d.char_target_rh + '% @ ' + d.char_time_to_target.toFixed(0) + 's')
        : (d.char_target_rh + '% not reached');
      var pk = 'peak ' + d.char_peak_rh.toFixed(0) + '%'
        + (d.char_peak_time > 0 ? (' @ ' + d.char_peak_time.toFixed(0) + 's') : '');
      var wg = d.char_water_gone_time > 0
        ? (' • dry @ ' + d.char_water_gone_time.toFixed(0) + 's') : ' • not yet dry';
      if (d.char_running) {
        cs.textContent = d.char_phase + ' • ' + d.char_elapsed + 's • RH '
          + d.humidity.toFixed(0) + '% • ' + hit80 + ' • ' + pk + wg;
      } else if (d.char_phase && d.char_phase !== 'IDLE') {
        cs.textContent = 'DONE • ' + hit80 + ' • ' + pk + wg;
      }
    }

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
    var sb = document.getElementById('standbyToggle'); if (sb) sb.checked = d.standby;
    var exv = document.getElementById('exhaustVal'); if (exv) exv.textContent = Math.round(d.exhaust);
    var exs = document.getElementById('exhaustSlider');
    if (exs && document.activeElement !== exs) exs.value = d.exhaust;

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

function pumpTimed(s) {
  fetch('/api/pump_timed', {
    method: 'POST', headers: {'Content-Type':'application/json'},
    body: JSON.stringify({seconds: s})
  });
}

function setExhaust(v) {
  document.getElementById('exhaustVal').textContent = v;
  fetch('/api/exhaust', {method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({pct: parseFloat(v)})});
}
function toggleStandby(on) {
  let t = parseFloat(document.getElementById('standbyTarget').value);
  fetch('/api/standby', {method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({on: on, target_f: t})});
}
function setStandbyTarget(v) {
  fetch('/api/standby', {method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({on: document.getElementById('standbyToggle').checked, target_f: parseFloat(v)})});
}

function charFields() {
  var m = document.getElementById('charMode').value;
  document.getElementById('charDripRow').style.display = (m === 'drip') ? 'flex' : 'none';
  document.getElementById('charHoldRow').style.display = (m === 'driphold') ? 'flex' : 'none';
  document.getElementById('charChargeLbl').style.display = (m === 'boil') ? '' : 'none';
}
function charStart() {
  let cfg = {
    mode: document.getElementById('charMode').value,
    charge_s: parseFloat(document.getElementById('charCharge').value),
    target_rh: parseFloat(document.getElementById('charTarget').value),
    timeout_min: parseFloat(document.getElementById('charTimeout').value),
    stop_at_target: document.getElementById('charStopAtTarget').checked,
    drip_on: parseFloat(document.getElementById('charDripOn').value),
    drip_off: parseFloat(document.getElementById('charDripOff').value),
    drip_count: parseInt(document.getElementById('charDripCount').value),
    preheat_f: parseFloat(document.getElementById('charPreheat').value),
    hold_preheat_f: parseFloat(document.getElementById('charHoldPreheat').value),
    puck_hold_f: parseFloat(document.getElementById('charPuckHold').value),
    drip_ms: parseFloat(document.getElementById('charDripMs').value),
    climb_int: parseFloat(document.getElementById('charClimbInt').value),
    fan_mode: document.getElementById('charFanMode').value,
    fan_on_s: parseFloat(document.getElementById('charFanOn').value),
    fan_off_s: parseFloat(document.getElementById('charFanOff').value)
  };
  fetch('/api/char/start', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(cfg)})
    .then(r => r.json()).then(d => { if (!d.ok) alert(d.err || 'could not start'); });
}
function charStop() {
  fetch('/api/char/stop', {method:'POST', headers:{'Content-Type':'application/json'}, body:'{}'});
}
function charDownload() { window.open('/api/char/download', '_blank'); }

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
    return Response(DASHBOARD_HTML, mimetype='text/html',
                    headers={'Cache-Control': 'no-store, no-cache, must-revalidate, max-age=0',
                             'Pragma': 'no-cache', 'Expires': '0'})

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

@app.route('/api/exhaust', methods=['POST'])
def api_exhaust():
    pct = float((request.json or {}).get('pct', 0))
    pct = max(0.0, min(100.0, pct))
    state['exhaust'] = pct
    hw.set_exhaust(pct)
    return jsonify({'ok': True, 'exhaust': pct})

@app.route('/api/standby', methods=['POST'])
def api_standby():
    j = request.json or {}
    state['standby'] = bool(j.get('on', not state['standby']))
    if 'target_f' in j:
        state['standby_f'] = float(j['target_f'])
    if not state['standby'] and not state['char_running']:
        hw.set_heater(False); state['heater'] = False   # turning Hot Start off cools down
    return jsonify({'ok': True, 'standby': state['standby'], 'standby_f': state['standby_f']})

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

@app.route('/api/pump_timed', methods=['POST'])
def api_pump_timed():
    secs = float(request.json.get('seconds', 10))
    def _run():
        # stop any pulse cycle, run pump continuously for `secs`, then off
        pump_cycle_stop.set()
        hw.set_pump(True); state['pump'] = True
        time.sleep(secs)
        hw.set_pump(False); state['pump'] = False
    threading.Thread(target=_run, daemon=True).start()
    return jsonify({'ok': True, 'seconds': secs})

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


def standby_loop():
    """Hot Start: when 'standby' is on AND no characterization test is running,
    bang-bang the cartridge heater to hold the puck near standby_f (default 180F)
    so a test can start hot instead of waiting ~7 min from cold. Yields the heater
    to a running test, then resumes holding when the test ends."""
    while True:
        if state.get('standby') and not state['char_running']:
            pf = state['puck_f']
            tgt = state.get('standby_f', 180.0)
            if pf < tgt - 5 and not state['heater']:
                hw.set_heater(True); state['heater'] = True
            elif pf > tgt + 5 and state['heater']:
                hw.set_heater(False); state['heater'] = False
        time.sleep(2.0)


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
        # RH well ABOVE target: the boiler can't remove moisture, so VENT with the
        # PWM exhaust fan (GPIO13), ramped by how far over we are, until back near target.
        if err < -HUM_DEADBAND:
            hw.set_humidifier(False); state['humidifier'] = False
            ex = max(40.0, min(100.0, 40.0 + 12.0 * (-err)))   # 40% just-over -> 100% way-over
            hw.set_exhaust(ex); state['exhaust'] = ex
            integral *= 0.9
            last_err = err
            time.sleep(HUM_PWM_WINDOW)
            continue
        hw.set_exhaust(0); state['exhaust'] = 0
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


# ── Characterization test runner ────────────────────────────────────

def char_runner(cfg):
    """Automated puck-humidity characterization. BOIL mode: pump a water charge
    into the cup, heat, time how long to reach target chamber RH. DRIP mode:
    preheat the puck dry, then pulse drips onto the hot puck. Logs every second
    to CSV with a summary footer (time-to-target, peak RH, charge volume)."""
    mode = cfg.get('mode', 'boil')
    target = float(cfg.get('target_rh', 80))
    timeout_s = float(cfg.get('timeout_min', 15)) * 60.0
    charge_s = float(cfg.get('charge_s', 30))
    drip_on = float(cfg.get('drip_on', 1))
    drip_off = float(cfg.get('drip_off', 10))
    drip_count = int(cfg.get('drip_count', 20))
    preheat_f = float(cfg.get('preheat_f', 200))
    stop_at_target = bool(cfg.get('stop_at_target', False))
    # driphold params: climb to target then closed-loop hold via drip rate + puck heat
    hold_preheat_f = float(cfg.get('hold_preheat_f', 212))
    puck_hold_f = float(cfg.get('puck_hold_f', 240))
    drip_ms = float(cfg.get('drip_ms', 200))
    climb_int = float(cfg.get('climb_int', 2))
    fan_mode = cfg.get('fan_mode', 'continuous')   # 'off' | 'continuous' | 'cycle'
    fan_on_s = float(cfg.get('fan_on_s', 30))
    fan_off_s = float(cfg.get('fan_off_s', 30))
    charge_ml = charge_s * PUMP_ML_PER_S

    state['humidity_auto'] = False        # don't let the PID fight the test
    os.makedirs(TEST_DATA_DIR, exist_ok=True)
    ts = time.strftime('%Y%m%d_%H%M%S')
    path = os.path.join(TEST_DATA_DIR, f"char_{mode}_{int(charge_s)}s_{ts}.csv")
    state.update({'char_running': True, 'char_mode': mode, 'char_phase': 'START',
                  'char_target_rh': target, 'char_elapsed': 0, 'char_time_to_target': 0.0,
                  'char_peak_rh': 0.0, 'char_peak_time': 0.0, 'char_water_gone_time': 0.0,
                  'char_csv': path})

    t0 = time.time()
    ttt = [0.0]          # time-to-target (list so the nested fn can write it)
    peak = [0.0]; peak_t = [0.0]; water_gone = [0.0]
    hold = {'n': 0, 'sum': 0.0, 'min': 999.0, 'max': 0.0}   # driphold quality stats
    f = None
    try:
        f = open(path, 'w')
        f.write(f"# Helios characterization  mode={mode}  started={ts}\n")
        f.write(f"# charge={charge_s}s = {charge_ml:.1f} mL @ {PUMP_ML_PER_S} mL/s   target_rh={target}%\n")
        if mode == 'drip':
            f.write(f"# drip {drip_on}s on / {drip_off}s off x{drip_count}, preheat puck to {preheat_f} F\n")
        f.write(f"# notes={cfg.get('notes','')}\n")
        f.write("elapsed_s,phase,puck_f,chamber_f,chamber_rh,column_f,column_rh,pressure_pa,weight_g\n")

        def step(phase):
            now = time.time() - t0
            rh = state['humidity']
            pf = state['puck_f']
            if rh > peak[0]:
                peak[0] = rh; peak_t[0] = now
                state['char_peak_rh'] = round(rh, 1); state['char_peak_time'] = round(now, 1)
            # DRY-OUT off PUCK TEMP (not the RH curve): puck is pinned ~212F while water boils,
            # then spikes once the last water is gone. Heat phases only (skip preheat/charge).
            if water_gone[0] == 0.0 and phase in ('HEAT', 'DRIP-ON', 'DRIP-OFF') and pf > DRY_PUCK_F:
                water_gone[0] = now; state['char_water_gone_time'] = round(now, 1)
            if ttt[0] == 0.0 and rh >= target:
                ttt[0] = now; state['char_time_to_target'] = round(now, 1)
            state['char_elapsed'] = int(now)
            state['char_phase'] = phase
            f.write(f"{now:.1f},{phase},{state['puck_f']},{state['chamber_f']},"
                    f"{state['humidity']},{state['column_f']},{state['column_humidity']},"
                    f"{state['pressure_pa']},{state['weight_g']}\n")
            f.flush()

        def run_for(phase, dur):
            end = time.time() + dur
            while time.time() < end and not char_stop.is_set():
                step(phase); time.sleep(1.0)

        if mode == 'boil':
            hw.set_pump(True); state['pump'] = True
            run_for('CHARGE', charge_s)
            hw.set_pump(False); state['pump'] = False
            hw.set_heater(True); state['heater'] = True
            hend = time.time() + max(0.0, timeout_s - charge_s)
            while time.time() < hend and not char_stop.is_set():
                step('HEAT')
                if stop_at_target and ttt[0] > 0.0:   # hit target → stop heating
                    break
                if state['puck_f'] > MAX_PUCK_F:       # puck spiked = water gone & dry: cut heat (safety)
                    hw.set_heater(False); state['heater'] = False
                    run_for('FALLOFF', max(0.0, hend - time.time()))  # keep logging the RH falloff
                    break
                time.sleep(1.0)
        elif mode == 'driphold':
            # Preheat puck dry, drip onto it to climb to target, then HOLD the setpoint
            # by modulating drip frequency (pump) while bang-banging puck heat.
            pulse_s = max(0.05, drip_ms / 1000.0)
            if fan_mode == 'continuous':
                hw.set_fan(True); state['fan'] = True
            hw.set_heater(True); state['heater'] = True
            ph_end = t0 + timeout_s
            while state['puck_f'] < hold_preheat_f and time.time() < ph_end and not char_stop.is_set():
                step('PREHEAT'); time.sleep(1.0)
            hold_reached = [False]
            last_drip = 0.0
            while time.time() < (t0 + timeout_s) and not char_stop.is_set():
                rh = state['humidity']; pf = state['puck_f']
                # circulation fan: cycle on/off to mix the chamber (continuous handled above)
                if fan_mode == 'cycle':
                    want = ((time.time() - t0) % (fan_on_s + fan_off_s)) < fan_on_s
                    if want != state['fan']:
                        hw.set_fan(want); state['fan'] = want
                # heater bang-bang: keep puck hot enough to flash drops instantly
                if pf < puck_hold_f - 8:
                    hw.set_heater(True); state['heater'] = True
                elif pf > puck_hold_f + 8:
                    hw.set_heater(False); state['heater'] = False
                # drip-rate control: faster when far below target, off when above
                err = target - rh
                if   err > 4:    interval = climb_int        # far below: full drip rate
                elif err > 2:    interval = climb_int * 2     # approaching: ease off early
                elif err > 0.3:  interval = climb_int * 5     # just under: light top-up only
                else:            interval = 1e9               # at/above setpoint: STOP dripping
                if rh >= target:
                    hold_reached[0] = True
                phase = 'HOLD' if hold_reached[0] else 'CLIMB'
                if (time.time() - last_drip) >= interval and pf >= hold_preheat_f:
                    hw.set_pump(True); state['pump'] = True
                    time.sleep(pulse_s)
                    hw.set_pump(False); state['pump'] = False
                    last_drip = time.time()
                # active vent: above setpoint -> PWM exhaust pulls RH back onto target
                if err < -0.5:
                    ex = max(35.0, min(100.0, 35.0 + 18.0 * (-err)))
                    hw.set_exhaust(ex); state['exhaust'] = ex
                elif state['exhaust']:
                    hw.set_exhaust(0); state['exhaust'] = 0
                if hold_reached[0]:
                    hold['n'] += 1; hold['sum'] += rh
                    hold['min'] = min(hold['min'], rh); hold['max'] = max(hold['max'], rh)
                step(phase)
                time.sleep(1.0)
        else:  # drip
            hw.set_heater(True); state['heater'] = True
            ph_end = time.time() + timeout_s
            while state['puck_f'] < preheat_f and time.time() < ph_end and not char_stop.is_set():
                step('PREHEAT'); time.sleep(1.0)
            for _ in range(drip_count):
                if char_stop.is_set() or (time.time() - t0) > timeout_s:
                    break
                hw.set_pump(True); state['pump'] = True
                run_for('DRIP-ON', drip_on)
                hw.set_pump(False); state['pump'] = False
                run_for('DRIP-OFF', drip_off)
    except Exception as e:
        print(f"char_runner error: {e}")
    finally:
        hw.set_heater(False); state['heater'] = False
        hw.set_pump(False); state['pump'] = False
        hw.set_fan(False); state['fan'] = False
        hw.set_exhaust(0); state['exhaust'] = 0
        if f:
            try:
                reached = 'yes' if ttt[0] else 'no'
                f.write(f"# SUMMARY  reached_{int(target)}pct={reached}  time_to_target_s={ttt[0]:.1f}  "
                        f"peak_rh={peak[0]:.1f}  peak_time_s={peak_t[0]:.1f}  "
                        f"water_gone_s={water_gone[0]:.1f}  charge_ml={charge_ml:.1f}\n")
                if hold['n'] > 0:
                    f.write(f"# HOLD  setpoint={int(target)}pct  mean_rh={hold['sum']/hold['n']:.1f}  "
                            f"min={hold['min']:.1f}  max={hold['max']:.1f}  hold_seconds={hold['n']}\n")
                f.close()
            except Exception:
                pass
        state['char_phase'] = 'STOPPED' if char_stop.is_set() else 'DONE'
        state['char_running'] = False


@app.route('/api/char/start', methods=['POST'])
def api_char_start():
    global char_thread
    if state['char_running']:
        return jsonify({'ok': False, 'err': 'A characterization test is already running'})
    char_stop.clear()
    char_thread = threading.Thread(target=char_runner, args=(request.json or {},), daemon=True)
    char_thread.start()
    return jsonify({'ok': True})

@app.route('/api/char/stop', methods=['POST'])
def api_char_stop():
    char_stop.set()
    try:                                  # always kill outputs, even if no test loop is live
        hw.set_heater(False); state['heater'] = False
        hw.set_pump(False); state['pump'] = False
    except Exception:
        pass
    return jsonify({'ok': True})

@app.route('/api/char/download')
def api_char_download():
    import glob
    files = sorted(glob.glob(os.path.join(TEST_DATA_DIR, 'char_*.csv')), key=os.path.getmtime)
    if not files:
        return "no characterization CSV yet", 404
    fn = files[-1]
    return Response(open(fn).read(), mimetype='text/csv',
                    headers={'Content-Disposition': f'attachment; filename={os.path.basename(fn)}'})


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
    threading.Thread(target=standby_loop, daemon=True).start()

    try:
        app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
    except KeyboardInterrupt:
        pass
    finally:
        hw.shutdown()
        print("\nShutdown complete — all outputs OFF")
