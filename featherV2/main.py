import cv2
import datetime
import kivy.resources
import numpy as np
import os
# import pyudev
import sys
#import subprocess
import time
import threading

from camera import thermalcameraController, guiController
from components import WarningDialog, WeighDialog
from dotenv import load_dotenv 
from utils import theme, Relay, RS485

from kivy.app import App
from neukivy.app import NeuApp
from kivy.clock import Clock, mainthread
from kivy.core.window import Window
from kivy.factory import Factory
from kivy_garden.graph import LinePlot
from kivy.graphics.texture import Texture
from kivy.properties import BooleanProperty, BoundedNumericProperty, ColorProperty, NumericProperty, StringProperty
from kivy.uix.floatlayout import FloatLayout

load_dotenv()
if os.getenv('IS_PI').lower() in ("true", "1", "yes"):
    Window.maximize()
else:
    Window.size = (600, 977)

if getattr(sys, 'frozen', False):
    # this is a Pyinstaller bundle
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
    finished = False
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

    _guiController = guiController.GuiController(width= 256, height=192)
    _thermalController = thermalcameraController.ThermalCameraController()
    
    def __init__(self, **kwargs):
        super(FeatherInterface, self).__init__(**kwargs)
        # self.capture = cv2.VideoCapture(1)
        Clock.schedule_once(self.connect)
        # Clock.schedule_once(self.check_relay)
        #threading.Thread(target=self.read, daemon=True).start()
        # Clock.schedule_interval(self.update, 1.0/33.0)

    def on_fan_status(self, instance, value):
        pass 
        # self.relay.write(3, self.fan_status)

    def on_hum1_status(self, instance, value):
        pass
        # self.relay.write(1, self.hum1_status)

    def on_hum2_status(self, instance, value):
        pass
        # self.relay.write(2, self.hum2_status)

    def on_heat_status(self, instance, value):
        # self.relay.write(4, self.heat_status)
        pass

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
                self.mode_display = 'Moisture Movement'
            case 'Resistance':
                self.mode_display = 'Moisture Reistance'
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
                    time.sleep(.9)
                except Exception as e:
                    print(e)
                    #self.con_message = 'SENSOR NOT POWERED, MAKE SURE UNIT IS PLUGGED IN'

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
            self.fan_status = False
            self.hum1_status = False
            self.hum2_status = False
            self.heat_status = False

    def proceed(self, *args):
        if self.test_mode == self.test_types[0] or self.test_mode == self.test_types[1]:
            if not self.drying:
                p = Factory.WeighDialog()
                p.finished = False
                p.open()
            else:
                self.restart()
        else:
            self.start_test()

    def start_test(self, *args):
        self.running = not self.running
        if self.running:
            self.finished = False
            self.drying = False
            self.current_time = '00:00:00'
            self.elapsed_time = 0
            self.x_point = 0
            self.total_power = 0
            self.data = []
            self.data_save = []
            self.ids.graph_test.remove_plot(self.plot)
            self.can_save = False
            self.handle_outputs()
            threading.Thread(target=self.update_time, daemon=True).start()

    def restart(self, *args):
        self.running = True
        self.elapsed_time = 0
        self.paused = False
        self.finished = False
        self.handle_outputs()
        threading.Thread(target=self.update_time, daemon=True).start()

    @mainthread
    def plot_data(self, *args):
        try: 
            if self.test_mode == self.test_types[0] or self.test_mode == self.test_types[1]:
                self.data.append((self.x_point, self.current_humd))
                self.data_save.append((self.x_point, self.current_humd, self.current_temp)) 
            else:
                # self.total_power = self.total_power + self.power_data
                self.data.append((self.x_point, self.total_power))
                self.data_save.append((self.x_point, self.total_power, self.current_temp))
            self.plot.points = self.data
            self.ids.graph_test.add_plot(self.plot)
            self.x_point += self.interval
        except Exception as e:
            print(e)
            # self.connected = False
            # self.con_message = 'NOT CONNECTED, PLEASE CLICK CONNECT TO START'

    def update_time(self, *args):
        while self.running:
            if not self.paused:
                self.update_time_label()
            time.sleep(1)

    @mainthread
    def update_time_label(self):
        self.current_time = str(datetime.timedelta(seconds=self.elapsed_time))
        # if self.elapsed_time == self.duration:
        if self.elapsed_time == self.duration * 60:
            self.finished = True 
            self.plot_data()
            self.handle_outputs()
        elif self.elapsed_time % self.interval == 0:
            self.plot_data()
        self.elapsed_time +=1    
        
    @mainthread
    def handle_outputs(self, *args):
        # Moisture Movement
        if self.test_mode == self.test_types[0]:
            if self.finished:
                self.hum2_status = False
                time.sleep(.2)
                self.fan_status = False
                self.running = False
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

        #Moisture Resistance
        if self.test_mode == self.test_types[1]:
            if self.finished:
                if not self.drying:
                    self.hum1_status = False
                    self.paused = True
                    self.drying = True
                    self.running = False
                    # self.x_point = 0
                    p = Factory.WeighDialog()
                    p.finished = False
                    p.open()
                else:
                    self.running = False
                    self.fan_status = False
                    self.drying = False
                    self.finished = True
                    p = Factory.WeighDialog()
                    p.finished = True
                    p.open()
            elif not self.finished: #start humidifier
                if self.drying:
                    self.hum1_status = False
                    time.sleep(.2)
                    self.fan_status = True
                else:
                    self.hum1_status = True
                    time.sleep(.2)
                    self.fan_status = False

        #Dry Thermal
        if self.test_mode == self.test_types[2]:
            if self.finished:
                self.heat_status = False
                self.running = False
                self.can_save = True if self.data_save else False
            elif not self.finished:
                self.heat_status = True
            elif not self.running:
                self.heat_status = False
        #Wet Thermal:
        if self.test_mode == self.test_types[3]:
            if self.finished:
                self.heat_status = False
                time.sleep(.2)
                # self.hum1_status = False
                # time.sleep(.2)
                self.fan_status = True
                self.running = False
                self.can_save = True if self.data_save else False
            elif not self.finished:
                self.heat_status = True
                # time.sleep(.2)
                # self.hum1_status = True
                time.sleep(.2)
                self.fan_status = True
            elif not self.running:
                self.heat_status = False
                time.sleep(.2)
                self.hum1_status = False
                time.sleep(.2)
                self.fan_status = False

    # def save_test(self, *args):
    #     context = pyudev.Context()
    #     for device in context.list_devices(subsystem='block', DEVTYPE='partition'):
    #         if (device.get('ID_USB_DRIVER') == 'usb-storage'):
    #             print ('UUID: {0}'.format(device.get('ID_FS_UUID')))
    #     Factory.SaveDialog().open()
    #     # for device in context.list_devices(subsystem='block', DEVTYPE='disk'):
    #     #     for props in device.properties:
    #     #         if device.get("ID_BUS") == "usb":
    #     #             print(props, device.get(props))

    def update(self, *args):
        if self.capture:
            ret, frame = self.capture.read()
            if ret == True:
                # Split frame into two parts: image data and thermal data
                imdata, thdata = np.array_split(frame, 2)
                
                # Now parse the data from the bottom frame and convert to temp!
                # Grab data from the center pixel...
                _rawTemp = self._thermalController.calculateRawTemperature(thdata)
                _temp = self._thermalController.calculateTemperature(thdata)

                # Calculate minimum temperature
                _minTemp = self._thermalController.calculateMinimumTemperature(thdata)
                
                # Calculate maximum temperature
                _maxTemp = self._thermalController.calculateMaximumTemperature(thdata)

                # Find the average temperature in the frame
                _avgTemp = self._thermalController.calculateAverageTemperature(thdata)
                
                # Draw GUI elements
                heatmap = self._guiController.drawGUI(
                    imdata=imdata,
                    temp=_temp,
                    maxTemp=_maxTemp,
                    minTemp=_minTemp,
                    averageTemp=_avgTemp,
                    isRecording=False,
                    mcol=0,
                    mrow=0,
                    lcol=0,
                    lrow=0)

            buf = heatmap.tobytes()
            texture1 = Texture.create(size=(frame.shape[1], frame.shape[0] * .5), colorfmt='bgr') 
            #if working on RASPBERRY PI, use colorfmt='rgba' here instead, but stick with "bgr" in blit_buffer. 
            texture1.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            texture1.flip_vertical()
            # display image from the texture
            self.ids.camera_display.texture = texture1

class TesterApp(NeuApp):
    def build(self):
        Window.bind(on_request_close=self.on_request_close)
        self.title = 'TEST SYSTEM'
        # The bg_color property should not have an alpha value. This is auto computed
        self.theme_manager.bg_color = (theme.bg_color)
        # Set this to a lighter shade of your bg_color
        self.theme_manager.light_color = (theme.light_color)
        # Set this to a darker shade of your bg_color
        self.theme_manager.dark_color = (theme.dark_color)
        # The text color of your app
        self.theme_manager.text_color = (theme.text_color)
        # Disabled text color of your app
        self.theme_manager.disabled_text_color = (theme.disabled_text_color)
        return FeatherInterface()
    
    def on_request_close(self, *args, **kwargs):
        # Relay.write(1, False)
        # Relay.write(2, False)
        # Relay.write(3, False)
        # Relay.write(4, False)
        pass
    
if __name__ == '__main__':
    TesterApp().run()
