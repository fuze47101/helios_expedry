"""
HWTestDialog.py — Hardware Diagnostic Popup for ExpeDRY
Shows a live checklist as each component is tested with PASS/FAIL results.
"""

from os.path import join, dirname

from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import StringProperty, ListProperty, BooleanProperty
from kivy.uix.popup import Popup

import threading
import time

curdir = dirname(__file__)
Builder.load_file(join(curdir, 'HWTestDialog.kv'))


class HWTestDialog(Popup):
    line1 = StringProperty('[ ]  External Humidity')
    line2 = StringProperty('[ ]  Internal Humidity')
    line3 = StringProperty('[ ]  Exhaust Fan')
    line4 = StringProperty('[ ]  Column Heat')
    line5 = StringProperty('[ ]  Scale')
    line6 = StringProperty('[ ]  Temp/Humidity Sensor')
    line7 = StringProperty('[ ]  IR Camera')
    status_text = StringProperty('Press RUN to start diagnostics')
    is_running = BooleanProperty(False)
    is_done = BooleanProperty(False)

    # Colors per line: white=pending, green=pass, red=fail, yellow=testing
    color1 = ListProperty([0.6, 0.6, 0.6, 1])
    color2 = ListProperty([0.6, 0.6, 0.6, 1])
    color3 = ListProperty([0.6, 0.6, 0.6, 1])
    color4 = ListProperty([0.6, 0.6, 0.6, 1])
    color5 = ListProperty([0.6, 0.6, 0.6, 1])
    color6 = ListProperty([0.6, 0.6, 0.6, 1])
    color7 = ListProperty([0.6, 0.6, 0.6, 1])

    YELLOW = [1, 0.8, 0, 1]
    GREEN = [0.2, 0.9, 0.3, 1]
    RED = [1, 0.2, 0.2, 1]
    GRAY = [0.6, 0.6, 0.6, 1]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()

    def run_test(self):
        if self.is_running:
            return
        self.is_running = True
        self.is_done = False
        # Reset all lines
        for i in range(1, 8):
            setattr(self, f'color{i}', list(self.GRAY))
        threading.Thread(target=self._run, daemon=True).start()

    def _set(self, line_num, text, color):
        """Update a line from background thread (schedules on main thread)."""
        def _do(dt):
            setattr(self, f'line{line_num}', text)
            setattr(self, f'color{line_num}', list(color))
        Clock.schedule_once(_do, 0)

    def _status(self, text):
        def _do(dt):
            self.status_text = text
        Clock.schedule_once(_do, 0)

    def _run(self):
        root = self.app.root
        passed = 0
        total = 7

        # ── 1. External Humidity (hum1, relay 1) ──
        self._set(1, '[>>]  External Humidity — TESTING...', self.YELLOW)
        self._status('Testing external humidity relay...')
        try:
            root.hum1_status = True
            time.sleep(3)
            root.hum1_status = False
            time.sleep(0.5)
            self._set(1, '[OK]  External Humidity — PASS', self.GREEN)
            passed += 1
        except Exception as e:
            self._set(1, f'[XX]  External Humidity — FAIL: {e}', self.RED)

        # ── 2. Internal Humidity (hum2, relay 2) ──
        self._set(2, '[>>]  Internal Humidity — TESTING...', self.YELLOW)
        self._status('Testing internal humidity relay...')
        try:
            root.hum2_status = True
            time.sleep(3)
            root.hum2_status = False
            time.sleep(0.5)
            self._set(2, '[OK]  Internal Humidity — PASS', self.GREEN)
            passed += 1
        except Exception as e:
            self._set(2, f'[XX]  Internal Humidity — FAIL: {e}', self.RED)

        # ── 3. Exhaust Fan (relay 3) ──
        self._set(3, '[>>]  Exhaust Fan — TESTING...', self.YELLOW)
        self._status('Testing exhaust fan relay...')
        try:
            root.fan_status = True
            time.sleep(3)
            root.fan_status = False
            time.sleep(0.5)
            self._set(3, '[OK]  Exhaust Fan — PASS', self.GREEN)
            passed += 1
        except Exception as e:
            self._set(3, f'[XX]  Exhaust Fan — FAIL: {e}', self.RED)

        # ── 4. Column Heat (relay 4) ──
        self._set(4, '[>>]  Column Heat — TESTING...', self.YELLOW)
        self._status('Testing column heat relay...')
        try:
            root.heat_status = True
            time.sleep(3)
            root.heat_status = False
            time.sleep(0.5)
            self._set(4, '[OK]  Column Heat — PASS', self.GREEN)
            passed += 1
        except Exception as e:
            self._set(4, f'[XX]  Column Heat — FAIL: {e}', self.RED)

        # ── 5. Scale ──
        self._set(5, '[>>]  Scale — TESTING...', self.YELLOW)
        self._status('Reading scale...')
        try:
            if root.scale_connected:
                readings = []
                for _ in range(5):
                    readings.append(root.scale.read())
                    time.sleep(0.5)
                avg = sum(readings) / len(readings)
                spread = max(readings) - min(readings)
                if spread < 1.0:
                    self._set(5, f'[OK]  Scale — PASS  ({avg:.3f}g, spread {spread:.3f}g)', self.GREEN)
                    passed += 1
                else:
                    self._set(5, f'[!!]  Scale — UNSTABLE  ({avg:.3f}g, spread {spread:.3f}g)', self.RED)
            else:
                self._set(5, '[XX]  Scale — FAIL (not connected)', self.RED)
        except Exception as e:
            self._set(5, f'[XX]  Scale — FAIL: {e}', self.RED)

        # ── 6. Temp/Humidity Sensor ──
        self._set(6, '[>>]  Temp/Humidity Sensor — TESTING...', self.YELLOW)
        self._status('Reading temp/humidity sensor...')
        try:
            time.sleep(2)
            t = root.current_temp
            h = root.current_humd
            if root.connected and (t != 0 or h != 0):
                self._set(6, f'[OK]  Sensor — PASS  ({t:.1f}°C, {h:.1f}% RH)', self.GREEN)
                passed += 1
            elif root.connected:
                self._set(6, f'[!!]  Sensor — CONNECTED but reading 0', self.YELLOW)
            else:
                self._set(6, '[XX]  Sensor — FAIL (not connected)', self.RED)
        except Exception as e:
            self._set(6, f'[XX]  Sensor — FAIL: {e}', self.RED)

        # ── 7. IR Camera ──
        self._set(7, '[>>]  IR Camera — TESTING...', self.YELLOW)
        self._status('Checking IR camera...')
        try:
            time.sleep(1)
            cam_ok = hasattr(root, 'capture') and root.capture.isOpened()
            if cam_ok:
                self._set(7, '[OK]  IR Camera — PASS', self.GREEN)
                passed += 1
            else:
                self._set(7, '[XX]  IR Camera — FAIL (not detected)', self.RED)
        except Exception as e:
            self._set(7, f'[XX]  IR Camera — FAIL: {e}', self.RED)

        # ── Summary ──
        if passed == total:
            self._status(f'ALL SYSTEMS GO — {passed}/{total} passed')
        else:
            self._status(f'ISSUES FOUND — {passed}/{total} passed, {total - passed} failed')

        def _done(dt):
            self.is_running = False
            self.is_done = True
        Clock.schedule_once(_done, 0)
