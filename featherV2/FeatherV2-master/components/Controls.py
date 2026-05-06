from os import curdir
from os.path import join, dirname

from kivy.app import App
from kivy.lang import Builder
from kivy.properties import BooleanProperty
from neukivy.uix.card import NeuCard

curdir = dirname(__file__)
Builder.load_file(join(curdir, 'Controls.kv'))

class Controls(NeuCard):
    fan_status  = BooleanProperty(False)
    hum1_status = BooleanProperty(False)
    hum2_status = BooleanProperty(False)
    heat_status = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()

    def toggle_output(self, output, *args):
        match output:
            case 'humidifier1':
                self.app.root.hum1_status = not self.app.root.hum1_status
            case 'humidifier2':
                self.app.root.hum2_status = not self.app.root.hum2_status
            case 'fan':
                self.app.root.fan_status = not self.app.root.fan_status
            case 'heater':
                self.app.root.heat_status = not self.app.root.heat_status