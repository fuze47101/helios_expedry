"""
RS485.py — Modbus RTU Sensor Interface
ExpeDRY FeatherV2

Hardware: RS485 via /dev/serial0 at 9600 baud
  - Humidity/Temp sensor: addr=1, function code 3, registers 0 (temp) & 1 (humidity)
  - Power sensor: addr=3, function code 4, register 3 (power in watts)

Usage:
    from utils import RS485
    humid = RS485.HumiditySenosr()   # note: original typo preserved
    humid.connect(1)
    data = humid.read()              # returns [temp, humidity]
    power = humid.read_power()       # returns watts (float)
"""

import struct
import time

try:
    import serial
    _HAS_SERIAL = True
except ImportError:
    _HAS_SERIAL = False
    print("pyserial not installed — RS485 module running in MOCK mode")

PORT = '/dev/serial0'
BAUD = 9600
TIMEOUT = 1


def _crc16(data: bytes) -> int:
    """Modbus CRC-16 calculation."""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return crc


def _build_request(addr: int, func: int, register: int, count: int = 1) -> bytes:
    """Build a Modbus RTU request frame."""
    frame = struct.pack('>BBHH', addr, func, register, count)
    crc = _crc16(frame)
    frame += struct.pack('<H', crc)
    return frame


class HumiditySenosr:
    """Modbus RTU sensor reader.

    Note: Class name preserves original typo from Mike's code —
    main.py imports RS485.HumiditySenosr() with that exact spelling.
    """

    def __init__(self):
        self.ser = None
        self.address = 1
        self.connected = False
        self._error_logged = False  # suppress repeated error messages

    def connect(self, address: int = 1):
        """Open serial port and set sensor address.

        Args:
            address: Modbus slave address (1 for humidity, 3 for power)
        """
        self.address = address
        if _HAS_SERIAL:
            try:
                if self.ser is None or not self.ser.is_open:
                    self.ser = serial.Serial(
                        PORT,
                        baudrate=BAUD,
                        bytesize=serial.EIGHTBITS,
                        parity=serial.PARITY_NONE,
                        stopbits=serial.STOPBITS_ONE,
                        timeout=TIMEOUT
                    )
                self.connected = True
            except Exception as e:
                print(f"RS485 connect error (addr {address}): {e}")
                self.connected = False
                raise
        else:
            self.connected = True  # mock mode

    def read(self) -> list:
        """Read temperature and humidity from sensor.

        Returns:
            [temperature, humidity] as floats
            Temperature in °C, humidity in %RH
        """
        if not _HAS_SERIAL or not self.connected:
            return [25.0, 50.0]  # mock values

        try:
            # Function code 3: Read Holding Registers
            # Register 0 = temperature (×10), Register 1 = humidity (×10)
            request = _build_request(self.address, 0x03, 0x0000, 2)
            self.ser.reset_input_buffer()
            self.ser.write(request)
            time.sleep(0.1)

            # Response: addr(1) + func(1) + byte_count(1) + data(4) + crc(2) = 9 bytes
            response = self.ser.read(9)
            if len(response) >= 9:
                # Parse two 16-bit registers
                temp_raw = struct.unpack('>H', response[3:5])[0]
                humd_raw = struct.unpack('>H', response[5:7])[0]
                # Sensors typically report ×10 (e.g., 251 = 25.1°C)
                temperature = temp_raw / 10.0
                humidity = humd_raw / 10.0
                return [temperature, humidity]
            else:
                if not self._error_logged:
                    print(f"RS485 sensor addr {self.address}: no response (sensor not connected?)")
                    self._error_logged = True
                return [0.0, 0.0]

        except Exception as e:
            if not self._error_logged:
                print(f"RS485 read error: {e}")
                self._error_logged = True
            return [0.0, 0.0]

    def read_power(self) -> float:
        """Read power from power sensor.

        Returns:
            Power in watts (float)
        """
        if not _HAS_SERIAL or not self.connected:
            return 0.0  # mock value

        try:
            # Function code 4: Read Input Registers
            # Register 3 = power
            request = _build_request(self.address, 0x04, 0x0003, 1)
            self.ser.reset_input_buffer()
            self.ser.write(request)
            time.sleep(0.1)

            # Response: addr(1) + func(1) + byte_count(1) + data(2) + crc(2) = 7 bytes
            response = self.ser.read(7)
            if len(response) >= 7:
                power_raw = struct.unpack('>H', response[3:5])[0]
                return power_raw / 10.0
            else:
                if not self._error_logged:
                    print(f"RS485 power sensor addr {self.address}: no response (sensor not connected?)")
                    self._error_logged = True
                return 0.0

        except Exception as e:
            if not self._error_logged:
                print(f"RS485 power read error: {e}")
                self._error_logged = True
            return 0.0

    def close(self):
        """Close serial port."""
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.connected = False
