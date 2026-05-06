from os import curdir
from os.path import join, dirname

from kivy.app import App
from kivy.lang import Builder
from kivy.properties import BoundedNumericProperty, BooleanProperty
from neukivy.uix.card import NeuCard

curdir = dirname(__file__)
Builder.load_file(join(curdir, 'Test_Settings.kv'))

class Test_Settings(NeuCard):
    duration = BoundedNumericProperty(60, min=0, max=120)
    endpoint = BoundedNumericProperty(45, min=10, max=90, errorvalue=0)
    interval = BoundedNumericProperty(5, min=5, max=60, errorvalue=5)
    running  = BooleanProperty(False)
    settings = ['Duration', 'Interval', 'Switch_Point', 'Endpoint']
    sw_point = BoundedNumericProperty(50, min=0, max=100)    

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()

    def increment_setting(self, setting, direction, increment):
        value = 0
        if direction == '+':
            value = setting + increment
        else: 
            value = setting - increment
        return value

    def adjust_setting(self, setting, direction):
        match setting:
            case 'Duration':
                self.app.root.duration = self.increment_setting(self.app.root.duration, direction, 5)
            case 'Interval':
                self.app.root.interval = self.increment_setting(self.app.root.interval, direction, 5)
            case 'Switch_Point':
                if direction == "-" and self.sw_point - 5 <= self.endpoint: 
                    return
                self.app.root.sw_point = self.increment_setting(self.app.root.sw_point, direction, 5)
            case 'Endpoint':
                if direction == "+" and self.app.root.endpoint + 5 >= self.sw_point:
                    return
                self.app.root.endpoint = self.increment_setting(self.app.root.endpoint, direction, 5)