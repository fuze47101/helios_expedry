"""
SetupWizard.py — Test Setup Wizard for ExpeDRY
Step-through popup that configures test parameters before starting.

Hardware mapping:
  hum1 (relay 1) — External humidity (environmental)
  hum2 (relay 2) — Internal humidity (direct/chamber)
  fan  (relay 3) — Exhaust fan (drying)
  heat (relay 4) — Column heater

Test types:
  Movement     — How much moisture fabric absorbs (weight gain over time)
  Resistance   — How well down resists moisture penetration
  Dry Thermal  — Thermal performance dry
  Wet Thermal  — Thermal performance wet

Test flow:
  WETTING CYCLE — humidifiers hold target humidity setpoint, fan OFF
  DRY CYCLE     — humidifiers OFF, exhaust fan ON
                  Ends on timer OR weight return to start (whichever first)
  Column heat   — configurable per phase
"""

from os.path import join, dirname

from kivy.app import App
from kivy.factory import Factory
from kivy.lang import Builder
from kivy.properties import (
    BooleanProperty, NumericProperty, StringProperty, ListProperty
)
from kivy.uix.popup import Popup

curdir = dirname(__file__)
Builder.load_file(join(curdir, 'SetupWizard.kv'))


HEAT_MODES = ['Off', 'Wet Only', 'Dry Only', 'Both']

# Default settings per test mode
MODE_DEFAULTS = {
    'Movement': {
        'wet_time': 10, 'humidity_setpoint': 60,
        'external_hum': True, 'internal_hum': True,
        'dry_time': 10, 'heat_mode_index': 0,
    },
    'Resistance': {
        'wet_time': 10, 'humidity_setpoint': 60,
        'external_hum': True, 'internal_hum': False,
        'dry_time': 10, 'heat_mode_index': 0,
    },
    'Dry_Thermal': {
        'wet_time': 0, 'humidity_setpoint': 60,
        'external_hum': False, 'internal_hum': False,
        'dry_time': 10, 'heat_mode_index': 2,  # Dry Only
    },
    'Wet_Thermal': {
        'wet_time': 10, 'humidity_setpoint': 60,
        'external_hum': True, 'internal_hum': True,
        'dry_time': 10, 'heat_mode_index': 3,  # Both
    },
}


class SetupWizard(Popup):
    # Parameters
    wet_time = NumericProperty(10)           # wetting cycle minutes
    humidity_setpoint = NumericProperty(60)   # target humidity %
    external_hum = BooleanProperty(True)     # hum1 — external/environmental
    internal_hum = BooleanProperty(True)     # hum2 — internal/chamber
    dry_time = NumericProperty(10)           # dry cycle minutes
    heat_mode_index = NumericProperty(0)     # index into HEAT_MODES

    # Wizard state
    step = NumericProperty(0)
    step_title = StringProperty('')
    step_description = StringProperty('')
    step_value = StringProperty('')
    step_count = NumericProperty(7)  # 6 config + 1 confirm
    is_numeric_step = BooleanProperty(True)
    is_toggle_step = BooleanProperty(False)
    is_cycle_step = BooleanProperty(False)
    toggle_value = BooleanProperty(False)

    steps = ListProperty([
        {
            'title': 'Wetting Cycle Time',
            'desc': 'How long to run humidity before drying.',
            'unit': 'min',
            'prop': 'wet_time',
            'min': 0, 'max': 120, 'increment': 1,
        },
        {
            'title': 'Humidity Setpoint',
            'desc': 'Target % — system holds by cycling humidifiers.',
            'unit': '%',
            'prop': 'humidity_setpoint',
            'min': 20, 'max': 99, 'increment': 5,
        },
        {
            'title': 'External Humidity',
            'desc': 'Environmental moisture from outside the chamber.',
            'prop': 'external_hum',
            'toggle': True,
        },
        {
            'title': 'Internal Humidity',
            'desc': 'Direct moisture inside the chamber.',
            'prop': 'internal_hum',
            'toggle': True,
        },
        {
            'title': 'Dry Cycle Time',
            'desc': 'Exhaust fan ON. Ends on timer or weight return.',
            'unit': 'min',
            'prop': 'dry_time',
            'min': 0, 'max': 120, 'increment': 1,
        },
        {
            'title': 'Column Heat',
            'desc': 'When should the column heater run?',
            'prop': 'heat_mode_index',
            'cycle': True,
        },
        {
            'title': 'Confirm Settings',
            'desc': '',
            'confirm': True,
        },
    ])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        # Load defaults for the selected test mode
        mode = self.app.root.test_mode
        defaults = MODE_DEFAULTS.get(mode, {})
        for key, val in defaults.items():
            setattr(self, key, val)
        self._update_display()

    def _update_display(self):
        s = self.steps[self.step]
        self.step_title = s['title']

        # Set step-type flags for KV layout switching
        self.is_numeric_step = not s.get('toggle') and not s.get('cycle') and not s.get('confirm')
        self.is_toggle_step = bool(s.get('toggle'))
        self.is_cycle_step = bool(s.get('cycle'))

        if s.get('confirm'):
            heat = HEAT_MODES[self.heat_mode_index]
            ext = 'ON' if self.external_hum else 'OFF'
            int_h = 'ON' if self.internal_hum else 'OFF'
            dry_end = 'timer or weight return'
            self.step_description = ''
            self.step_value = (
                f'Wet: {int(self.wet_time)} min @ {int(self.humidity_setpoint)}%\n'
                f'  External: {ext}  |  Internal: {int_h}\n'
                f'Dry: {int(self.dry_time)} min ({dry_end})\n'
                f'Heat: {heat}'
            )
        elif s.get('toggle'):
            self.step_description = s['desc']
            val = getattr(self, s['prop'])
            self.toggle_value = val
            self.step_value = 'ON' if val else 'OFF'
        elif s.get('cycle'):
            self.step_description = s['desc']
            self.step_value = HEAT_MODES[self.heat_mode_index]
        else:
            self.step_description = s['desc']
            val = getattr(self, s['prop'])
            self.step_value = f'{int(val)} {s["unit"]}'

    def _adjust(self, amount):
        """Adjust current step value by amount (+/-)."""
        s = self.steps[self.step]
        if s.get('confirm'):
            return
        if s.get('toggle'):
            val = getattr(self, s['prop'])
            setattr(self, s['prop'], not val)
        elif s.get('cycle'):
            direction = 1 if amount > 0 else -1
            self.heat_mode_index = (self.heat_mode_index + direction) % len(HEAT_MODES)
        else:
            val = getattr(self, s['prop'])
            new_val = max(s['min'], min(val + amount, s['max']))
            setattr(self, s['prop'], new_val)
        self._update_display()

    def set_toggle(self, value):
        """Explicitly set a boolean step to True or False."""
        s = self.steps[self.step]
        if s.get('toggle'):
            setattr(self, s['prop'], value)
            self._update_display()

    def increment(self):
        self._adjust(1)

    def decrement(self):
        self._adjust(-1)

    def increment_big(self):
        s = self.steps[self.step]
        if s.get('toggle') or s.get('cycle') or s.get('confirm'):
            self._adjust(1)
        else:
            self._adjust(5)

    def decrement_big(self):
        s = self.steps[self.step]
        if s.get('toggle') or s.get('cycle') or s.get('confirm'):
            self._adjust(-1)
        else:
            self._adjust(-5)

    def next_step(self):
        if self.step < self.step_count - 1:
            self.step += 1
            self._update_display()
        else:
            self._start_test()

    def prev_step(self):
        if self.step > 0:
            self.step -= 1
            self._update_display()

    def _start_test(self):
        """Apply settings to the app, then open sample placement dialog."""
        root = self.app.root

        # Store wizard parameters
        root.wet_time = self.wet_time
        root.humidity_setpoint = self.humidity_setpoint
        root.external_hum = self.external_hum
        root.internal_hum = self.internal_hum
        root.dry_time = self.dry_time
        root.heat_mode = HEAT_MODES[self.heat_mode_index]

        # Total duration
        root.duration = self.wet_time + self.dry_time

        self.dismiss()

        # Open sample placement dialog — it will tare and start when ready
        Factory.SampleDialog().open()
