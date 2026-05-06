import cv2
import datetime
import kivy.resources
import numpy as np
import os
import sys
import subprocess
import time
import threading

# ── Screen rotation (must be before Window import) ──
from kivy.config import Config
Config.set('graphics', 'rotation', '270')
Config.set('graphics', 'fullscreen', 'auto')

from camera import thermalcameraController, guiController
from components import SaveDialog, WarningDialog, WeighDialog, WifiDialog
from utils import theme, Relay, RS485, Scale
from utils.EmailReport import send_test_report
from utils.AtlasUpload import post_test_results

from kivy.app import App
from neukivy.app import NeuApp
from kivy.core.window import Window
from kivy.clock import Clock, mainthread
from kivy.factory import Factory
from kivy_garden.graph import LinePlot
from kivy.graphics.texture import Texture
from kivy.properties import BooleanProperty, BoundedNumericProperty, ColorProperty, NumericProperty, StringProperty
from kivy.uix.floatlayout import FloatLayout

Window.maximize()

if getattr(sys, 'frozen', False):
    kivy.resources.resource_add_path(sys._MEIPASS)
    kivy.resources.resource_add_path(os.path.join(sys._MEIPASS, 'assets'))

class FeatherInterface(FloatLayout):
    button_text = StringProperty('START')
    button_color = ColorProperty(theme.go_color)
    fan_status  = BooleanProperty(False)
    hum1_status = BooleanProperty(False)
    hum2_status = BooleanProperty(False)
    heat_status = BooleanProperty(False)

    can_save = BooleanProperty(False)
    duration = BoundedNumericProperty(10, min=0, max=120)
    endpoint = BoundedNumericProperty(45, min=10, max=90, errorvalue=0)
    interval = BoundedNumericProperty(5, min=5, max=60, errorvalue=5)
    running  = BooleanProperty(False)
    paused   = BooleanProperty(False)
    sw_point = BoundedNumericProperty(50, min=0, max=100)
    finished  = False
    drying = False

    test_types = ['Movement', 'Resistance', 'Dry_Thermal', 'Wet_Thermal']
    test_mode  = StringProperty('Movement')
    mode_display = StringProperty('Moisture Movement')
    icon_file  = kivy.resources.resource_find('ExpeDRY_logo.png')
    x_point    = NumericProperty(0)
    total_power = NumericProperty(0)

    hum1_pin = 20
    hum2_pin = 21
    fan_pin  = 26
    relay = Relay

    humid_sensor = RS485.HumiditySenosr()
    power_sensor = RS485.HumiditySenosr()
    power_data = NumericProperty(0)
    current_temp = NumericProperty(0)
    current_humd = NumericProperty(0)
    current_time = StringProperty('00:00:00')
    data = []
    data_save = []
    plot = LinePlot(line_width=3, color=theme.go_color)
    connected = BooleanProperty(False)

    # ── Scale + Weight tracking ──
    current_weight = NumericProperty(0.0)
    start_weight = NumericProperty(0.0)
    end_weight = NumericProperty(0.0)
    weight_delta = NumericProperty(0.0)
    max_weight = NumericProperty(0.0)
    _start_weight_set = False

    # ── Test setup wizard parameters ──
    wet_time = NumericProperty(10)           # wetting cycle minutes
    dry_time = NumericProperty(10)           # dry cycle minutes
    humidity_setpoint = NumericProperty(60)  # target humidity %
    external_hum = BooleanProperty(True)     # hum1 (relay 1) — external/environmental humidity
    internal_hum = BooleanProperty(True)     # hum2 (relay 2) — internal/direct chamber humidity
    heat_mode = StringProperty('Off')        # Off, Wet Only, Dry Only, Both
    test_phase = StringProperty('IDLE')
    weight_data = []
    weight_plot = LinePlot(line_width=3, color=theme.weight_color)
    scale_connected = BooleanProperty(False)
    dry_back_time = StringProperty('--:--')
    dry_back_seconds = NumericProperty(0)

    _guiController = guiController.GuiController(width=256, height=192)
    _thermalController = thermalcameraController.ThermalCameraController()

    def __init__(self, **kwargs):
        super(FeatherInterface, self).__init__(**kwargs)
        # ── Auto-detect IR camera ──
        self.capture = None
        for dev_idx in range(5):
            cap = cv2.VideoCapture(f'/dev/video{dev_idx}')
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    print(f'[CAMERA] Found at /dev/video{dev_idx} — {frame.shape}')
                    self.capture = cap
                    break
                cap.release()
        if self.capture is None:
            print('[CAMERA] No thermal camera found on /dev/video0-4')
            self.capture = cv2.VideoCapture('/dev/video0')  # fallback

        Clock.schedule_once(self.connect)
        Clock.schedule_once(self.check_relay)
        threading.Thread(target=self.read, daemon=True).start()
        Clock.schedule_interval(self.update, 1.0/33.0)
        # ── Auto-detect scale ──
        self.scale = Scale.Scale()
        if self.scale.connect():
            self.scale_connected = True
            print(f'[SCALE] Connected at {self.scale.port}')
        else:
            print('[SCALE] Not detected')
        # Update weight at 2Hz
        Clock.schedule_interval(self.poll_weight, 0.5)

    def poll_weight(self, *args):
        """Poll latest weight from scale background thread."""
        if self.scale_connected:
            w = self.scale.read()
            self.current_weight = round(w, 3)
            # Only show delta once start_weight has been set (via tare or test start)
            if self._start_weight_set:
                self.weight_delta = round(w - self.start_weight, 3)
            else:
                self.weight_delta = 0.0
            if self.running and w > self.max_weight:
                self.max_weight = w

    def on_fan_status(self, instance, value):
        self.relay.write(3, self.fan_status)

    def on_hum1_status(self, instance, value):
        self.relay.write(1, self.hum1_status)

    def on_hum2_status(self, instance, value):
        self.relay.write(2, self.hum2_status)

    def on_heat_status(self, instance, value):
        self.relay.write(4, self.heat_status)

    def on_running(self, instance, value):
        if self.running:
            self.button_color = theme.stop_color
            self.button_text = 'STOP'
        elif not self.running and not self.paused:
            self.button_color = theme.go_color
            self.button_text = 'START'

    def on_test_mode(self, instance, value):
        match self.test_mode:
            case 'Movement':
                self.mode_display = 'Moisture Movement (Absorption)'
            case 'Resistance':
                self.mode_display = 'Moisture Resistance (Down)'
            case 'Dry_Thermal':
                self.mode_display = 'Dry Thermal'
            case 'Wet_Thermal':
                self.mode_display = 'Wet Thermal'
        self.ids.options.dismiss()

    def check_relay(self, *args):
        self.hum1_status = self.relay.read(1)
        time.sleep(.2)
        self.hum2_status = self.relay.read(2)
        time.sleep(.2)
        self.fan_status = self.relay.read(3)
        time.sleep(.2)
        self.heat_status = self.relay.read(4)

    def connect(self, *args):
        if not self.connected:
            try:
                self.humid_sensor.connect(1)
                self.power_sensor.connect(3)
                self.connected = True
            except Exception as e:
                self.connected = False

    def read(self, *args):
        while App.get_running_app():
            if self.connected:
                try:
                    data = self.humid_sensor.read()
                    time.sleep(.1)
                    power_data = self.power_sensor.read_power()
                    if self.running and self.test_mode != self.test_types[0]:
                        self.total_power = round(self.total_power + (power_data/4184), 3)
                    current_temp = data[0]
                    current_humd = data[1]
                    self.update_labels(current_temp, current_humd, power_data)

                    # ── Humidity setpoint hold during WETTING phase ──
                    if self.running and self.test_phase == 'WETTING':
                        setpoint = getattr(self, 'humidity_setpoint', 60)
                        if current_humd >= setpoint:
                            # Above setpoint — kill humidifiers
                            if self.hum1_status and getattr(self, 'external_hum', True):
                                self.hum1_status = False
                            if self.hum2_status and getattr(self, 'internal_hum', True):
                                self.hum2_status = False
                        else:
                            # Below setpoint — turn humidifiers back on per wizard config
                            if getattr(self, 'external_hum', True) and not self.hum1_status:
                                self.hum1_status = True
                            if getattr(self, 'internal_hum', True) and not self.hum2_status:
                                self.hum2_status = True

                    time.sleep(.9)
                except Exception as e:
                    print(e)

    @mainthread
    def update_labels(self, temp, humd, power, *args):
        self.current_temp = temp
        self.current_humd = humd
        self.power_data = power

    def start(self, *args):
        if self.data_save and not self.running:
            Factory.WarningDialog().open()
        elif not self.running:
            self.proceed()
        else:
            self.running = False
            self.can_save = True if self.data_save else False
            self.test_phase = 'STOPPED'
            self.fan_status = False
            self.hum1_status = False
            self.hum2_status = False
            self.heat_status = False

    def proceed(self, *args):
        if self.drying:
            # Resuming dry-back phase — skip wizard
            self.restart()
        else:
            # Open setup wizard for all test types
            Factory.SetupWizard().open()

    def start_test(self, *args):
        self.running = not self.running
        if self.running:
            self.finished = False
            self.drying = False
            self.current_time = '00:00:00'
            self.elapsed_time = 0
            self.x_point = 0
            self.total_power = 0
            self.max_weight = self.current_weight
            self.data = []
            self.data_save = []
            self.weight_data = []
            self.dry_back_time = '--:--'
            self.dry_back_seconds = 0
            self._wet_seconds = self.wet_time * 60
            self._dry_seconds = self.dry_time * 60
            # Total duration for the full test
            self.duration = self.wet_time + self.dry_time
            # Clear both graphs
            self.ids.graph_test.remove_plot(self.plot)
            self.ids.graph_weight.remove_plot(self.weight_plot)
            self.can_save = False
            self.test_phase = 'WETTING'
            self._apply_phase_outputs()
            threading.Thread(target=self.update_time, daemon=True).start()

    def restart(self, *args):
        """Restart into dry-back phase."""
        self.running = True
        self.elapsed_time = 0
        self.paused = False
        self.finished = False
        self.test_phase = 'DRY BACK'
        self.dry_back_seconds = 0
        self.handle_outputs()
        threading.Thread(target=self.update_time, daemon=True).start()

    @mainthread
    def plot_data(self, *args):
        try:
            if self.test_mode == self.test_types[0] or self.test_mode == self.test_types[1]:
                self.data.append((self.x_point, self.current_humd))
                self.data_save.append((
                    self.x_point,
                    self.current_humd,
                    self.current_temp,
                    self.current_weight,
                    self.weight_delta,
                    self.test_phase
                ))
            else:
                self.data.append((self.x_point, self.total_power))
                self.data_save.append((
                    self.x_point,
                    self.total_power,
                    self.current_temp,
                    self.current_weight,
                    self.weight_delta,
                    self.test_phase
                ))

            # Plot humidity/power on top graph
            self.plot.points = self.data
            self.ids.graph_test.add_plot(self.plot)

            # Plot weight on bottom graph (separate)
            self.weight_data.append((self.x_point, self.current_weight))
            self.weight_plot.points = self.weight_data
            self.ids.graph_weight.add_plot(self.weight_plot)

            self.x_point += self.interval

            # ── Dry-back detection ──
            if self.drying and self.test_phase == 'DRY BACK':
                self.dry_back_seconds += self.interval
                self.dry_back_time = str(datetime.timedelta(seconds=self.dry_back_seconds))
                if self.current_weight <= self.start_weight + 0.05 and self.dry_back_seconds > 0:
                    self.test_phase = 'DRY COMPLETE'

        except Exception as e:
            print(e)

    def update_time(self, *args):
        while self.running:
            if not self.paused:
                self.update_time_label()
            time.sleep(1)

    @mainthread
    def update_time_label(self):
        self.current_time = str(datetime.timedelta(seconds=self.elapsed_time))

        # ── Phase transitions based on wizard timers ──
        total_seconds = self.duration * 60

        # Wet → Dry transition
        if (self.test_phase == 'WETTING'
                and self.elapsed_time >= self._wet_seconds):
            if self._dry_seconds > 0:
                self.test_phase = 'DRYING'
                self._apply_phase_outputs()
            else:
                # No dry cycle — test complete
                self.finished = True
                self.plot_data()
                self._complete_test()
                return

        # Dry cycle ends on timer OR weight return to start
        if self.test_phase == 'DRYING':
            dry_elapsed = self.elapsed_time - self._wet_seconds
            weight_returned = (self._start_weight_set
                               and self.current_weight <= self.start_weight + 0.05)

            if dry_elapsed >= self._dry_seconds or weight_returned:
                self.finished = True
                self.plot_data()
                if weight_returned and dry_elapsed < self._dry_seconds:
                    self.test_phase = 'DRY - WEIGHT RETURN'
                self._complete_test()
                return

        # Test complete (safety fallback)
        if self.elapsed_time >= total_seconds:
            self.finished = True
            self.plot_data()
            self._complete_test()
        elif self.elapsed_time % self.interval == 0:
            self.plot_data()

        self.elapsed_time += 1

    @mainthread
    def _apply_phase_outputs(self):
        """Set relay outputs based on current test_phase and wizard settings."""
        heat_mode = getattr(self, 'heat_mode', 'Off')

        if self.test_phase == 'WETTING':
            # hum1 = external humidity, hum2 = internal humidity
            self.hum1_status = getattr(self, 'external_hum', True)
            time.sleep(0.2)
            self.hum2_status = getattr(self, 'internal_hum', True)
            self.fan_status = False
            # Heat during wet?
            self.heat_status = heat_mode in ('Wet Only', 'Both')

        elif self.test_phase == 'DRYING':
            # All humidifiers OFF, exhaust fan ON
            self.hum1_status = False
            time.sleep(0.2)
            self.hum2_status = False
            time.sleep(0.2)
            self.fan_status = True
            # Heat during dry?
            self.heat_status = heat_mode in ('Dry Only', 'Both')

    @mainthread
    def _complete_test(self):
        """Shut everything down, mark complete, email report, upload to Atlas."""
        self.running = False
        self.hum1_status = False
        self.hum2_status = False
        self.fan_status = False
        self.heat_status = False
        if self.test_phase not in ('DRY - WEIGHT RETURN',):
            self.test_phase = 'COMPLETE'
        self.can_save = True if self.data_save else False

        # ── Send report in background thread ──
        threading.Thread(target=self._send_results, daemon=True).start()

    def _send_results(self):
        """Email report via Resend and upload to Atlas (runs in background)."""
        try:
            # Compute averages from data_save
            avg_temp = 0
            avg_humid = 0
            if self.data_save:
                temps = [d[2] for d in self.data_save if len(d) > 2]
                humids = [d[1] for d in self.data_save if len(d) > 1]
                if temps:
                    avg_temp = sum(temps) / len(temps)
                if humids:
                    avg_humid = sum(humids) / len(humids)

            test_data = {
                'test_mode': self.mode_display,
                'start_weight': self.start_weight,
                'end_weight': self.current_weight,
                'weight_delta': self.weight_delta,
                'max_weight': self.max_weight,
                'avg_temp': avg_temp,
                'avg_humidity': avg_humid,
                'duration_seconds': self.elapsed_time,
                'test_phase': self.test_phase,
                'data_points': self.data_save,
            }
            settings = {
                'wet_time': getattr(self, 'wet_time', 0),
                'dry_time': getattr(self, 'dry_time', 0),
                'humidity_setpoint': getattr(self, 'humidity_setpoint', 0),
                'external_hum': getattr(self, 'external_hum', False),
                'internal_hum': getattr(self, 'internal_hum', False),
                'heat_mode': getattr(self, 'heat_mode', 'Off'),
            }

            # 1. Email report
            print('[REPORT] Sending email...')
            email_result = send_test_report(
                to='andrew@fuzebiotech.com',
                test_data=test_data,
                settings=settings,
            )
            print(f'[REPORT] Email: {email_result}')

            # 2. Upload to Atlas
            print('[REPORT] Uploading to Atlas...')
            atlas_result = post_test_results(
                test_data=test_data,
                settings=settings,
            )
            print(f'[REPORT] Atlas: {atlas_result}')

        except Exception as e:
            print(f'[REPORT] Error sending results: {e}')

    @mainthread
    def handle_outputs(self, *args):
        # Moisture Movement
        if self.test_mode == self.test_types[0]:
            if self.finished:
                self.hum2_status = False
                time.sleep(.2)
                self.fan_status = False
                self.running = False
                self.test_phase = 'COMPLETE'
                self.can_save = True if self.data_save else False
                p = Factory.WeighDialog()
                p.finished = True
                p.open()
            elif not self.finished:
                self.hum2_status = True
                time.sleep(.2)
                self.fan_status = True
            elif not self.running:
                self.hum2_status = False
                time.sleep(.2)
                self.fan_status = False

        # Moisture Resistance
        if self.test_mode == self.test_types[1]:
            if self.finished:
                if not self.drying:
                    self.hum1_status = False
                    self.paused = True
                    self.drying = True
                    self.running = False
                    self.test_phase = 'WET DONE'
                    p = Factory.WeighDialog()
                    p.finished = False
                    p.open()
                else:
                    self.running = False
                    self.fan_status = False
                    self.drying = False
                    self.finished = True
                    self.test_phase = 'COMPLETE'
                    p = Factory.WeighDialog()
                    p.finished = True
                    p.open()
            elif not self.finished:
                if self.drying:
                    self.hum1_status = False
                    time.sleep(.2)
                    self.fan_status = True
                    self.test_phase = 'DRY BACK'
                else:
                    self.hum1_status = True
                    time.sleep(.2)
                    self.fan_status = False
                    self.test_phase = 'WET'

        # Dry Thermal
        if self.test_mode == self.test_types[2]:
            if self.finished:
                self.heat_status = False
                self.running = False
                self.test_phase = 'COMPLETE'
                self.can_save = True if self.data_save else False
            elif not self.finished:
                self.heat_status = True
                self.test_phase = 'HEATING'
            elif not self.running:
                self.heat_status = False

        # Wet Thermal
        if self.test_mode == self.test_types[3]:
            if self.finished:
                self.heat_status = False
                time.sleep(.2)
                self.fan_status = True
                self.running = False
                self.test_phase = 'COMPLETE'
                self.can_save = True if self.data_save else False
            elif not self.finished:
                self.heat_status = True
                time.sleep(.2)
                self.fan_status = True
                self.test_phase = 'WET THERMAL'
            elif not self.running:
                self.heat_status = False
                time.sleep(.2)
                self.hum1_status = False
                time.sleep(.2)
                self.fan_status = False

    def hardware_test(self, *args):
        """Open hardware diagnostic popup with visual checklist."""
        if self.running:
            return
        Factory.HWTestDialog().open()

    def _run_hardware_test(self):
        """Background thread: cycle each component for 15 seconds to verify operation."""
        try:
            # 1. External humidity — 15 sec
            self._hw_test_update('EXT HUMIDITY (1/6) — 15s')
            self.hum1_status = True
            for i in range(15, 0, -1):
                self._hw_test_update(f'EXT HUMIDITY (1/6) — {i}s')
                time.sleep(1)
            self.hum1_status = False
            time.sleep(0.5)

            # 2. Internal humidity — 15 sec
            self._hw_test_update('INT HUMIDITY (2/6) — 15s')
            self.hum2_status = True
            for i in range(15, 0, -1):
                self._hw_test_update(f'INT HUMIDITY (2/6) — {i}s')
                time.sleep(1)
            self.hum2_status = False
            time.sleep(0.5)

            # 3. Exhaust fan — 15 sec
            self._hw_test_update('EXHAUST FAN (3/6) — 15s')
            self.fan_status = True
            for i in range(15, 0, -1):
                self._hw_test_update(f'EXHAUST FAN (3/6) — {i}s')
                time.sleep(1)
            self.fan_status = False
            time.sleep(0.5)

            # 4. Column heat — 15 sec
            self._hw_test_update('COLUMN HEAT (4/6) — 15s')
            self.heat_status = True
            for i in range(15, 0, -1):
                self._hw_test_update(f'COLUMN HEAT (4/6) — {i}s')
                time.sleep(1)
            self.heat_status = False
            time.sleep(0.5)

            # 5. Scale — 15 sec of readings
            self._hw_test_update('SCALE (5/6) — reading...')
            readings = []
            for i in range(15, 0, -1):
                w = self.scale.read() if self.scale_connected else -1
                readings.append(w)
                self._hw_test_update(f'SCALE (5/6) — {w:.3f}g — {i}s')
                time.sleep(1)
            scale_ok = self.scale_connected and len(readings) > 0
            if readings:
                avg_w = sum(readings) / len(readings)
                spread = max(readings) - min(readings)
                self._hw_test_update(f'SCALE: avg={avg_w:.3f}g spread={spread:.3f}g')
            time.sleep(2)

            # 6. Sensors + camera check — 15 sec
            self._hw_test_update('SENSORS + CAM (6/6) — checking...')
            cam_ok = hasattr(self, 'capture') and self.capture.isOpened()
            sensor_ok = self.connected
            for i in range(15, 0, -1):
                t = self.current_temp
                h = self.current_humd
                self._hw_test_update(f'CAM:{"OK" if cam_ok else "FAIL"} T:{t:.1f}C H:{h:.1f}% — {i}s')
                time.sleep(1)

            # Final summary
            results = []
            results.append(f'CAM:{"OK" if cam_ok else "FAIL"}')
            results.append(f'SCALE:{"OK" if scale_ok else "FAIL"}')
            results.append(f'SENSOR:{"OK" if sensor_ok else "FAIL"}')
            self._hw_test_update('DONE — ' + ' '.join(results))
            time.sleep(5)

            self._hw_test_update('IDLE')
        except Exception as e:
            self._hw_test_update(f'ERROR: {e}')

    @mainthread
    def _hw_test_update(self, msg):
        self.test_phase = msg

    def save_test(self, *args):
        Factory.SaveDialog().open()

    def update(self, *args):
        ret, frame = self.capture.read()
        if ret == True:
            imdata, thdata = np.array_split(frame, 2)
            _rawTemp = self._thermalController.calculateRawTemperature(thdata)
            _temp = self._thermalController.calculateTemperature(thdata)
            _minTemp = self._thermalController.calculateMinimumTemperature(thdata)
            _maxTemp = self._thermalController.calculateMaximumTemperature(thdata)
            _avgTemp = self._thermalController.calculateAverageTemperature(thdata)

            heatmap = self._guiController.drawGUI(
                imdata=imdata,
                temp=_temp,
                maxTemp=_maxTemp,
                minTemp=_minTemp,
                averageTemp=_avgTemp,
                isRecording=False,
                mcol=0, mrow=0,
                lcol=0, lrow=0)

        buf = heatmap.tobytes()
        texture1 = Texture.create(size=(frame.shape[1], frame.shape[0] * .5), colorfmt='bgr')
        texture1.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        texture1.flip_vertical()
        self.ids.camera_display.texture = texture1

    def tare_scale(self, *args):
        """Capture current weight as the start/reference weight."""
        if self.scale_connected:
            self.start_weight = round(self.scale.read(), 3)
            self.weight_delta = 0.0
            self._start_weight_set = True

class TesterApp(NeuApp):
    def build(self):
        Window.bind(on_request_close=self.on_request_close)
        self.title = 'ExpeDRY TEST SYSTEM'
        self.theme_manager.bg_color = (theme.bg_color)
        self.theme_manager.light_color = (theme.light_color)
        self.theme_manager.dark_color = (theme.dark_color)
        self.theme_manager.text_color = (theme.text_color)
        self.theme_manager.disabled_text_color = (theme.disabled_text_color)
        return FeatherInterface()

    def on_request_close(self, *args, **kwargs):
        Relay.write(1, False)
        Relay.write(2, False)
        Relay.write(3, False)
        Relay.write(4, False)

if __name__ == '__main__':
    TesterApp().run()
