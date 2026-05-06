from os import curdir
from os.path import join, dirname

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.properties import StringProperty

curdir = dirname(__file__)
Builder.load_file(join(curdir, 'SettingsDialog.kv'))

class SettingsDialog(Popup):
    error_message = StringProperty('')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()

    def connect_humid(self):
        pass
    
    def connect_power(self):
        pass

    def connect_relay(self):
        pass
