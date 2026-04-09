"""
SaveDialog.py — Save Test Data to USB Drive
ExpeDRY FeatherV2

Popup dialog that detects mounted USB drives, lets user pick one,
and saves the test CSV data to it.
"""

import csv
import datetime
import os
import subprocess

from os.path import join, dirname

from kivy.app import App
from kivy.lang import Builder
from kivy.properties import ListProperty, StringProperty
from kivy.uix.popup import Popup
from utils import theme

curdir = dirname(__file__)
Builder.load_file(join(curdir, 'SaveDialog.kv'))


class SaveDialog(Popup):
    drives = ListProperty([])
    status = StringProperty('Scanning for USB drives...')
    selected_drive = StringProperty('')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()

    def on_open(self, *args):
        """Scan for USB drives on open."""
        self.scan_drives()

    def scan_drives(self):
        """Find mounted USB storage devices."""
        self.drives = []
        try:
            # Check /media/<user>/ for mounted USB drives
            media_path = '/media'
            if os.path.exists(media_path):
                for user_dir in os.listdir(media_path):
                    user_path = os.path.join(media_path, user_dir)
                    if os.path.isdir(user_path):
                        for drive in os.listdir(user_path):
                            drive_path = os.path.join(user_path, drive)
                            if os.path.ismount(drive_path):
                                self.drives.append(drive_path)

            # Also check /mnt
            mnt_path = '/mnt'
            if os.path.exists(mnt_path):
                for d in os.listdir(mnt_path):
                    dp = os.path.join(mnt_path, d)
                    if os.path.ismount(dp):
                        self.drives.append(dp)

            if self.drives:
                self.selected_drive = self.drives[0]
                self.status = f'Found {len(self.drives)} drive(s)'
            else:
                self.status = 'No USB drive found. Insert drive and retry.'
        except Exception as e:
            self.status = f'Error scanning: {e}'

    def save(self, *args):
        """Save test data CSV to selected drive."""
        if not self.selected_drive:
            self.status = 'No drive selected'
            return

        root = self.app.root
        if not root.data_save:
            self.status = 'No test data to save'
            return

        try:
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            mode = root.test_mode.lower()
            filename = f'expedry_{mode}_{timestamp}.csv'
            filepath = os.path.join(self.selected_drive, filename)

            with open(filepath, 'w', newline='') as f:
                writer = csv.writer(f)
                # Header
                if root.test_mode in ['Movement', 'Resistance']:
                    writer.writerow([
                        'Time(s)', 'Humidity(%)', 'Temp(C)',
                        'Weight(g)', 'Delta(g)', 'Phase'
                    ])
                else:
                    writer.writerow([
                        'Time(s)', 'Power(Cal)', 'Temp(C)',
                        'Weight(g)', 'Delta(g)', 'Phase'
                    ])
                # Data rows
                for row in root.data_save:
                    writer.writerow(row)

                # Metadata footer
                writer.writerow([])
                writer.writerow(['Test Mode', root.mode_display])
                writer.writerow(['Duration (min)', root.duration])
                writer.writerow(['Interval (sec)', root.interval])
                writer.writerow(['Start Weight (g)', root.start_weight])
                writer.writerow(['End Weight (g)', root.end_weight])
                writer.writerow(['Max Weight (g)', root.max_weight])

            self.status = f'Saved: {filename}'
            root.can_save = False
            # Auto-dismiss after brief pause
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: self.dismiss(), 1.5)

        except Exception as e:
            self.status = f'Save failed: {e}'
