#!/usr/bin/env python3
"""
HELIOS Component Test — Quick check all sensors and actuators
Run after rewiring to verify everything is alive on the bus.
"""

import time
import struct
import RPi.GPIO as GPIO
from smbus2 import SMBus, i2c_msg
import spidev

# ─── Config ────────────────────────────────────────────────────────
HEATER_PIN   = 17
I2C_BUS      = 1
SDP810_ADDR  = 0x25
SHT41_ADDR   = 0x44
RELAY_ADDR   = 0x10
PUMP_CHANNEL = 2
SPI_BUS      = 0
SPI_CE       = 0

PASS = "\033[92m PASS \033[0m"
FAIL = "\033[91m FAIL \033[0m"

def main():
    print("=" * 60)
    print("HELIOS Component Test")
    print("=" * 60)
    print()

    bus = SMBus(I2C_BUS)

    # ── 1. I2C Bus Scan ──
    print("1. I2C Bus Scan")
    found = []
    for addr in range(0x03, 0x78):
        try:
            bus.read_byte(addr)
            found.append(hex(addr))
        except:
            pass
    print(f"   Devices found: {', '.join(found) if found else 'NONE'}")
    print(f"   0x25 (SDP810):  {PASS if '0x25' in found else FAIL}")
    print(f"   0x44 (SHT41):   {PASS if '0x44' in found else FAIL}")
    print(f"   0x10 (Relay):   {PASS if '0x10' in found else FAIL}")
    print()

    # ── 2. SHT41 Temperature/Humidity ──
    print("2. SHT41 — Temperature & Humidity")
    try:
        bus.write_byte(SHT41_ADDR, 0x94)  # soft reset
        time.sleep(0.01)
        bus.write_byte(SHT41_ADDR, 0xFD)  # high precision measure
        time.sleep(0.03)
        msg = i2c_msg.read(SHT41_ADDR, 6)
        bus.i2c_rdwr(msg)
        d = list(msg)
        t_raw = (d[0] << 8) | d[1]
        h_raw = (d[3] << 8) | d[4]
        temp_c = -45.0 + 175.0 * (t_raw / 65535.0)
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        rh = max(0, min(100, -6.0 + 125.0 * (h_raw / 65535.0)))
        print(f"   Temp: {temp_f:.1f}°F  ({temp_c:.1f}°C)")
        print(f"   RH:   {rh:.1f}%")
        print(f"   {PASS}")
    except Exception as e:
        print(f"   Error: {e}")
        print(f"   {FAIL}")
    print()

    # ── 3. SDP810 Differential Pressure ──
    print("3. SDP810 — Differential Pressure")
    try:
        # Trigger continuous measurement (mass flow, avg)
        bus.write_i2c_block_data(SDP810_ADDR, 0x36, [0x15])
        time.sleep(0.1)
        msg = i2c_msg.read(SDP810_ADDR, 9)
        bus.i2c_rdwr(msg)
        d = list(msg)
        dp_raw = (d[0] << 8) | d[1]
        if dp_raw > 32767:
            dp_raw -= 65536
        scale = (d[6] << 8) | d[7]
        if scale == 0:
            scale = 60  # default for SDP810-500Pa
        pressure = dp_raw / scale
        print(f"   Raw: {dp_raw}, Scale: {scale}")
        print(f"   Pressure: {pressure:.2f} Pa")
        print(f"   {PASS}")
        # Stop continuous measurement
        bus.write_i2c_block_data(SDP810_ADDR, 0x3F, [0xF9])
    except Exception as e:
        print(f"   Error: {e}")
        print(f"   {FAIL}")
    print()

    # ── 4. MAX31855 Thermocouple ──
    print("4. MAX31855 — Thermocouple (Puck Temp)")
    try:
        spi = spidev.SpiDev()
        spi.open(SPI_BUS, SPI_CE)
        spi.max_speed_hz = 1000000
        spi.mode = 0
        raw = spi.xfer2([0, 0, 0, 0])
        val = (raw[0] << 24) | (raw[1] << 16) | (raw[2] << 8) | raw[3]

        fault = val & 0x01
        if fault:
            faults = []
            if val & 0x04: faults.append("SHORT_VCC")
            if val & 0x02: faults.append("SHORT_GND")
            if val & 0x01 and not (val & 0x06): faults.append("OPEN_CIRCUIT")
            print(f"   FAULT: {', '.join(faults)}")
            print(f"   {FAIL}")
        else:
            tc_raw = (val >> 18) & 0x3FFF
            if tc_raw & 0x2000:
                tc_raw -= 16384
            temp_c = tc_raw * 0.25
            temp_f = temp_c * 9.0 / 5.0 + 32.0
            print(f"   Temp: {temp_f:.1f}°F  ({temp_c:.1f}°C)")
            print(f"   {PASS}")
        spi.close()
    except Exception as e:
        print(f"   Error: {e}")
        print(f"   {FAIL}")
    print()

    # ── 5. Relay HAT (Pump) ──
    print("5. Relay HAT — Pump Control (CH2)")
    try:
        # Read current state
        bus.write_byte_data(RELAY_ADDR, PUMP_CHANNEL, 0xFF)  # ensure OFF
        time.sleep(0.2)
        print(f"   OFF command sent (0xFF)")
        print(f"   Pulse ON for 0.5s...")
        bus.write_byte_data(RELAY_ADDR, PUMP_CHANNEL, 0x00)  # ON
        time.sleep(0.5)
        bus.write_byte_data(RELAY_ADDR, PUMP_CHANNEL, 0xFF)  # OFF
        print(f"   Pump pulsed and stopped")
        print(f"   {PASS}")
    except Exception as e:
        print(f"   Error: {e}")
        print(f"   {FAIL}")
    print()

    # ── 6. Heater SSR (GPIO17) ──
    print("6. Heater SSR — GPIO17")
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(HEATER_PIN, GPIO.OUT, initial=GPIO.LOW)
        print(f"   GPIO17 initialized LOW")
        print(f"   Pulse HIGH for 1s (heater should kick on briefly)...")
        GPIO.output(HEATER_PIN, GPIO.HIGH)
        time.sleep(1.0)
        GPIO.output(HEATER_PIN, GPIO.LOW)
        print(f"   Heater pulsed and stopped")
        print(f"   {PASS}")
        # Don't call GPIO.cleanup() — leaves pin LOW
    except Exception as e:
        print(f"   Error: {e}")
        print(f"   {FAIL}")
    print()

    bus.close()

    print("=" * 60)
    print("Component test complete. Check results above.")
    print("GPIO17 left LOW (heater off). Pump relay left OFF.")
    print("=" * 60)


if __name__ == "__main__":
    main()
