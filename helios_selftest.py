#!/usr/bin/env python3
"""
HELIOS hardware self-test — run on the Pi to check every subsystem at once.

    ~/helios-env/bin/python3 ~/helios_selftest.py

Re-run after each fix until every line says PASS. IMPORTANT: the main
controller (helios_control.py) silently falls back to MOCK mode (fake data,
scale shows "disconnected") if ANY of the imports below FAIL — so fix the
import section first, then the sensors.
"""
import time

PASS, FAIL = "PASS", "FAIL"
def report(name, ok, detail=""):
    tag = PASS if ok else FAIL
    print(f"  [{tag}] {name:30s} {detail}")

print("=" * 60)
print("  HELIOS SELF-TEST")
print("=" * 60)

# ── 1. Imports (a single failure here = whole app runs in MOCK) ──────
print("\n-- imports (all must PASS or the app mocks everything) --")
imports_ok = True
for mod in ["smbus2", "RPi.GPIO", "spidev", "pymodbus", "serial"]:
    try:
        __import__(mod)
        report(f"import {mod}", True)
    except Exception as e:
        report(f"import {mod}", False, repr(e))
        imports_ok = False
if not imports_ok:
    print("\n  >> Fix the failed import(s) above first — nothing else matters")
    print("  >> until they all pass (that's what forces MOCK mode).")

# ── 2. SHT41 #1 — external chamber (software I2C bus 15) ─────────────
print("\n-- sensors --")
try:
    from smbus2 import SMBus, i2c_msg
    b = SMBus(15)
    b.write_byte(0x44, 0xFD); time.sleep(0.03)
    m = i2c_msg.read(0x44, 6); b.i2c_rdwr(m); d = list(m); b.close()
    t = (d[0] << 8) | d[1]; rh = (d[3] << 8) | d[4]
    c = -45 + 175 * (t / 65535.0); h = -6 + 125 * (rh / 65535.0)
    report("SHT41 #1 chamber (bus15)", True, f"{c*9/5+32:5.1f} F  {h:4.1f}% RH")
except Exception as e:
    report("SHT41 #1 chamber (bus15)", False, repr(e))

# ── 3. SHT41 #2 — in-column (hardware I2C bus 1) ─────────────────────
try:
    from smbus2 import SMBus, i2c_msg
    b = SMBus(1)
    b.write_byte(0x44, 0xFD); time.sleep(0.03)
    m = i2c_msg.read(0x44, 6); b.i2c_rdwr(m); d = list(m); b.close()
    t = (d[0] << 8) | d[1]; rh = (d[3] << 8) | d[4]
    c = -45 + 175 * (t / 65535.0); h = -6 + 125 * (rh / 65535.0)
    report("SHT41 #2 column (bus1)", True, f"{c*9/5+32:5.1f} F  {h:4.1f}% RH")
except Exception as e:
    report("SHT41 #2 column (bus1)", False, repr(e))

# ── 4. SDP810 differential pressure (hardware I2C bus 1) ─────────────
try:
    from smbus2 import SMBus, i2c_msg
    b = SMBus(1)
    b.i2c_rdwr(i2c_msg.write(0x25, [0x36, 0x1E])); time.sleep(0.1)
    m = i2c_msg.read(0x25, 9); b.i2c_rdwr(m); d = list(m); b.close()
    dp = (d[0] << 8) | d[1]
    if dp > 32767: dp -= 65536
    report("SDP810 pressure (bus1)", True, f"{dp/60.0:6.2f} Pa")
except Exception as e:
    report("SDP810 pressure (bus1)", False, repr(e))

# ── 5. MAX31855 puck thermocouple (hardware SPI0 CE1) ───────────────
try:
    import spidev
    spi = spidev.SpiDev(); spi.open(0, 1)
    spi.max_speed_hz = 500000; spi.mode = 0
    raw = spi.xfer2([0, 0, 0, 0]); spi.close()
    val = (raw[0] << 24) | (raw[1] << 16) | (raw[2] << 8) | raw[3]
    if val == 0:
        report("MAX31855 puck (SPI CE1)", False, "all zeros — check power/wiring")
    elif val & 0x10000:
        report("MAX31855 puck (SPI CE1)", False, "TC fault (open/short) — fault bit set")
    else:
        tr = val >> 18
        if tr & 0x2000: tr -= 0x4000
        report("MAX31855 puck (SPI CE1)", True, f"{tr*0.25*9/5+32:5.1f} F")
except Exception as e:
    report("MAX31855 puck (SPI CE1)", False, repr(e))

# ── 6. Scale RS232 (FTDI on /dev/ttyUSB0) ───────────────────────────
try:
    import serial
    s = serial.Serial('/dev/ttyUSB0', 9600, bytesize=8, parity='N',
                      stopbits=1, timeout=2)
    time.sleep(0.4); data = s.read(80); s.close()
    if data:
        report("Scale RS232 (ttyUSB0)", True, f"streaming {data[:14]!r}")
    else:
        report("Scale RS232 (ttyUSB0)", False, "port opens but NO data (TX/RX swap or scale off)")
except Exception as e:
    report("Scale RS232 (ttyUSB0)", False, repr(e))

# ── 7. GPIO heater + humidifier SSR pins (setup only, left LOW) ──────
try:
    import RPi.GPIO as GPIO
    GPIO.setwarnings(False); GPIO.setmode(GPIO.BCM)
    GPIO.setup(5, GPIO.OUT, initial=GPIO.LOW)   # SSR-10 DD heater
    GPIO.setup(6, GPIO.OUT, initial=GPIO.LOW)   # SSR-25DA humidifier
    GPIO.cleanup()
    report("GPIO heater(5)/humid(6)", True, "setup OK, left OFF")
except Exception as e:
    report("GPIO heater(5)/humid(6)", False, repr(e))

# ── 8. Modbus relay (Waveshare RS485 on /dev/ttyAMA0) ───────────────
try:
    from pymodbus.client import ModbusSerialClient
    mb = ModbusSerialClient(port='/dev/ttyAMA0', baudrate=9600,
                            parity='N', stopbits=1, timeout=1)
    ok = mb.connect(); mb.close()
    report("Modbus relay (ttyAMA0)", ok, "connected" if ok else "no connect")
except Exception as e:
    report("Modbus relay (ttyAMA0)", False, repr(e))

print("\n" + "=" * 60)
print("  Re-run after each fix. Green across = ready for a real test run.")
print("=" * 60)
