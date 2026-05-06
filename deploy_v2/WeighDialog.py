from kivy.app import App
from kivy.clock import Clock
from kivy.properties import BooleanProperty, NumericProperty, StringProperty
from kivy.uix.popup import Popup
from utils import theme


class WeighDialog(Popup):
    finished = BooleanProperty(False)
    live_weight = NumericProperty(0.0)
    status_text = StringProperty('PLACE SAMPLE ON SCALE')
    stable = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        self._readings = []
        self._poll = None

    def on_open(self, *args):
        """Start polling weight when dialog opens."""
        # Tare scale on open
        root = self.app.root
        if root.scale_connected:
            root.scale.tare()
            self.status_text = 'TARING...'
            Clock.schedule_once(self._start_polling, 1.5)
        else:
            self.status_text = 'SCALE NOT CONNECTED'
            self._start_polling(0)

    def _start_polling(self, *args):
        self.status_text = 'PLACE SAMPLE ON SCALE'
        self._poll = Clock.schedule_interval(self._update_weight, 0.3)

    def _update_weight(self, *args):
        root = self.app.root
        if root.scale_connected:
            w = root.scale.read()
            self.live_weight = round(w, 3)
            self._readings.append(w)
            # Keep last 8 readings for stability check
            if len(self._readings) > 8:
                self._readings.pop(0)
            # Stable if last 8 readings within 0.01g of each other
            if len(self._readings) >= 8:
                spread = max(self._readings) - min(self._readings)
                if spread < 0.01:
                    self.stable = True
                    self.status_text = 'WEIGHT STABLE'
                else:
                    self.stable = False
                    self.status_text = 'STABILIZING...'

    def tare(self, *args):
        """Manual tare button."""
        root = self.app.root
        if root.scale_connected:
            root.scale.tare()
            self.status_text = 'TARING...'
            self._readings = []
            Clock.schedule_once(lambda dt: setattr(self, 'status_text', 'PLACE SAMPLE ON SCALE'), 1.5)

    def start(self, *args):
        """Capture weight and proceed with test."""
        root = self.app.root
        if not self.finished:
            # Capture start weight
            root.start_weight = self.live_weight
            root.weight_delta = 0.0
            if root.drying:
                root.proceed()
            else:
                root.start_test()
        else:
            # Capture end weight
            root.end_weight = self.live_weight
        self._stop_polling()
        self.dismiss()

    def _stop_polling(self):
        if self._poll:
            self._poll.cancel()
            self._poll = None

    def on_dismiss(self, *args):
        self._stop_polling()
