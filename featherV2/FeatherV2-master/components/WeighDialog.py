from os import curdir, path
from os.path import join, dirname

from kivy.app import App
from kivy.lang import Builder
from kivy.properties import BooleanProperty
from kivy.uix.popup import Popup

curdir = dirname(__file__)
Builder.load_file(join(curdir, 'WeighDialog.kv'))

class WeighDialog(Popup):
    finished = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()

    def start(self, *args):
        print(self.finished)
        if not self.finished:
            self.app.root.start_test()
        self.dismiss()