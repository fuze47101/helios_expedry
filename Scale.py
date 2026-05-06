"""
Scale.py — Bonvoisin RS232 Scale Interface
Drop-in utility for the FeatherV2 ExpeDRY app.

The scale streams weight continuously over RS232 at ~10 readings/sec.
Format: "   0.260\n\r" (space-padded, grams)

Usage:
    from utils.Scale import Scale
    scale = Scale()
    scale.connect()          # opens /dev/ttyUSB0
    weight = scale.read()    # returns float in grams
    scale.tare()             # sends tare command
    scale.close()
"""

import serial
import threading
import time


class Scale:
    PORT = '/dev/ttyUSB0'
    BAUD = 9600
    BYTESIZE = 8
    PARITY = 'N'
    STOPBITS = 1
    TIMEOUT = 2

    def __init__(self, port=None):
        self.port = port or self.PORT
        self.ser = None
        self.connected = False
        self.current_weight = 0.0
        self.stable = False
        self._running = False
        self._thread = None

    def connect(self):
        """Open serial connection to scale."""
        try:
            self.ser = serial.Serial(
                self.port,
                baudrate=self.BAUD,
                bytesize=self.BYTESIZE,
                parity=self.PARITY,
                stopbits=self.STOPBITS,
                timeout=self.TIMEOUT
            )
            self.connected = True
            self._running = True
            self._thread = threading.Thread(target=self._read_loop, daemon=True)
            self._thread.start()
            return True
        except Exception as e:
            print(f"Scale connection failed: {e}")
            self.connected = False
            return False

    def _read_loop(self):
        """Continuously read weight from the streaming scale."""
        while self._running and self.ser and self.ser.is_open:
            try:
                line = self.ser.readline().decode('ascii', errors='ignore').strip()
                if line:
                    weight = self._parse_weight(line)
                    if weight is not None:
                        self.current_weight = weight
            except Exception as e:
                print(f"Scale read error: {e}")
                time.sleep(0.1)

    def _parse_weight(self, line):
        """Parse weight value from scale output.

        Handles formats:
            '   0.260'        -> 0.260
            '  12.345 g'      -> 12.345
            'ST,  12.345 g'   -> 12.345 (with stability indicator)
        """
        try:
            # Remove any non-numeric prefix (stability indicators etc)
            cleaned = line.replace('ST,', '').replace('US,', '')
            cleaned = cleaned.replace('g', '').replace('oz', '')
            cleaned = cleaned.replace('ct', '').replace('ozt', '')
            cleaned = cleaned.strip()
            return float(cleaned)
        except ValueError:
            return None

    def read(self):
        """Get the most recent weight reading in grams."""
        return self.current_weight

    def tare(self):
        """Send tare/zero command to scale."""
        if self.ser and self.ser.is_open:
            try:
                self.ser.write(b'T\r\n')
            except Exception as e:
                print(f"Tare failed: {e}")

    def close(self):
        """Close the serial connection."""
        self._running = False
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.connected = False

    @staticmethod
    def find_port():
        """Auto-detect scale port by scanning /dev/ttyUSB*."""
        import glob
        ports = glob.glob('/dev/ttyUSB*')
        for port in ports:
            try:
                s = serial.Serial(port, 9600, timeout=1)
                time.sleep(0.5)
                data = s.read(s.in_waiting or 50)
                s.close()
                if data:
                    # If we got data, this is probably the scale
                    return port
            except:
                continue
        return None
