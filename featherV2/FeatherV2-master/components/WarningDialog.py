from os import curdir
from os.path import join, dirname

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.popup import Popup

curdir = dirname(__file__)
Builder.load_file(join(curdir, 'WarningDialog.kv'))

class WarningDialog(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()

    def start(self, *args):
        self.app.root.proceed()
        self.dismiss()
