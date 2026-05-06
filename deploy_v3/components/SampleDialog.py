"""
SampleDialog.py — Pre-test sample placement and stabilization
ExpeDRY FeatherV2

Flow:
  1. Shows "Place sample on scale" with live weight readout
  2. Detects sample placed (weight increases > 0.5g above baseline)
  3. Waits for weight to stabilize (readings within 0.05g for 3 seconds)
  4. Shows stable weight, auto-tares, and enables START
"""

from os.path import join, dirname

from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import (
    BooleanProperty, NumericProperty, StringProperty
)
from kivy.uix.popup import Popup

curdir = dirname(__file__)
Builder.load_file(join(curdir, 'SampleDialog.kv'))


class SampleDialog(Popup):
    # Live weight display
    live_weight = NumericProperty(0.0)
    weight_text = StringProperty('0.000 g')
    status_text = StringProperty('Place sample on scale...')
    status_color = StringProperty('FFFFFF')  # hex for label color

    # State machine
    sample_detected = BooleanProperty(False)
    sample_stable = BooleanProperty(False)
    can_start = BooleanProperty(False)

    # Internal
    _baseline = 0.0
    _stable_readings = []
    _stable_start = 0  # clock ticks of stable readings

    # Thresholds
    DETECT_THRESHOLD = 0.5    # grams above baseline to detect sample
    STABLE_TOLERANCE = 0.05   # grams — max spread for "stable"
    STABLE_SECONDS = 3        # how many seconds of stable readings required

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        root = self.app.root
        # Grab current weight as baseline (empty scale)
        if root.scale_connected:
            self._baseline = root.current_weight
        else:
            self._baseline = 0.0
        self._stable_readings = []
        self._stable_start = 0
        # Poll weight at 4Hz
        self._poll_event = Clock.schedule_interval(self._poll, 0.25)

    def _poll(self, dt):
        root = self.app.root
        if not root.scale_connected:
            self.status_text = 'Scale not connected!'
            self.status_color = 'FF4444'
            return

        w = root.current_weight
        self.live_weight = w
        self.weight_text = f'{w:.3f} g'

        if not self.sample_detected:
            # Phase 1: waiting for sample
            delta = w - self._baseline
            if delta > self.DETECT_THRESHOLD:
                self.sample_detected = True
                self._stable_readings = []
                self._stable_start = 0
                self.status_text = 'Sample detected — stabilizing...'
                self.status_color = 'FFB833'  # yellow/orange
            else:
                self.status_text = f'Place sample on scale...  ({w:.3f} g)'
                self.status_color = 'FFFFFF'

        elif not self.sample_stable:
            # Phase 2: waiting for stability
            self._stable_readings.append(w)
            # Keep last N readings (STABLE_SECONDS * 4Hz)
            window = self.STABLE_SECONDS * 4
            if len(self._stable_readings) > window:
                self._stable_readings = self._stable_readings[-window:]

            if len(self._stable_readings) >= window:
                spread = max(self._stable_readings) - min(self._stable_readings)
                if spread <= self.STABLE_TOLERANCE:
                    # Stable!
                    self.sample_stable = True
                    self.can_start = True
                    self.status_text = f'Stable at {w:.3f} g — Ready to start'
                    self.status_color = '44CC66'  # green
                else:
                    self.status_text = f'Stabilizing...  spread: {spread:.3f} g'
                    self.status_color = 'FFB833'
            else:
                remaining = (window - len(self._stable_readings)) / 4
                self.status_text = f'Stabilizing... {remaining:.1f}s'
                self.status_color = 'FFB833'

        # If sample was detected but then removed (weight drops back to baseline)
        if self.sample_detected and not self.sample_stable:
            if w < self._baseline + self.DETECT_THRESHOLD * 0.5:
                self.sample_detected = False
                self._stable_readings = []
                self.status_text = 'Sample removed — place sample on scale...'
                self.status_color = 'FF4444'

    def start_test(self):
        """Tare the scale at current stable weight and start the test."""
        self._poll_event.cancel()
        root = self.app.root
        root.tare_scale()
        self.dismiss()
        root.start_test()

    def cancel(self):
        """Cancel — go back to main screen without starting."""
        self._poll_event.cancel()
        self.dismiss()

    def on_dismiss(self):
        """Ensure polling stops on any dismiss."""
        if self._poll_event:
            self._poll_event.cancel()
