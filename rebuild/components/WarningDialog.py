"""
WarningDialog.py — Unsaved Data Warning
ExpeDRY FeatherV2

Popup shown when user presses START but has unsaved data from a previous test.
Options: Save first, Discard & Start, or Cancel.
"""

from kivy.app import App
from kivy.factory import Factory
from kivy.uix.popup import Popup


class WarningDialog(Popup):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()

    def discard_and_start(self, *args):
        """Discard unsaved data and start new test."""
        root = self.app.root
        root.data_save = []
        root.can_save = False
        self.dismiss()
        root.proceed()

    def save_first(self, *args):
        """Open save dialog, then start new test after save."""
        self.dismiss()
        Factory.SaveDialog().open()
