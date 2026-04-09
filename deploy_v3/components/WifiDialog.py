"""
WifiDialog.py — WiFi Settings for ExpeDRY Test System
Scan, connect, and show WiFi status from the touchscreen.
Uses nmcli on Raspberry Pi (NetworkManager).
"""

import subprocess

from os.path import join, dirname

from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import BooleanProperty, ListProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup

curdir = dirname(__file__)
Builder.load_file(join(curdir, 'WifiDialog.kv'))


class WifiDialog(Popup):
    networks = ListProperty([])
    selected_ssid = StringProperty('')
    status_text = StringProperty('Scanning...')
    is_connected = BooleanProperty(False)
    current_ssid = StringProperty('--')
    current_ip = StringProperty('--')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()

    def on_open(self, *args):
        """Scan WiFi and get current status on open."""
        self._get_current_connection()
        Clock.schedule_once(lambda dt: self.scan(), 0.3)

    def _get_current_connection(self):
        """Get current WiFi SSID and IP."""
        try:
            result = subprocess.run(
                ['nmcli', '-t', '-f', 'GENERAL.CONNECTION', 'device', 'show', 'wlan0'],
                capture_output=True, text=True, timeout=5
            )
            for line in result.stdout.strip().split('\n'):
                if 'CONNECTION' in line:
                    ssid = line.split(':')[-1].strip()
                    if ssid and ssid != '--':
                        self.current_ssid = ssid
                        self.is_connected = True
                    else:
                        self.current_ssid = '--'
                        self.is_connected = False
        except Exception:
            self.current_ssid = '--'
            self.is_connected = False

        # Get IP
        try:
            result = subprocess.run(
                ['hostname', '-I'],
                capture_output=True, text=True, timeout=5
            )
            ip = result.stdout.strip().split()[0] if result.stdout.strip() else '--'
            self.current_ip = ip
        except Exception:
            self.current_ip = '--'

    def on_networks(self, instance, value):
        """Populate the network list UI when networks change."""
        if not hasattr(self, 'ids') or 'network_list' not in self.ids:
            return
        network_list = self.ids.network_list
        network_list.clear_widgets()
        from utils import theme
        for net in self.networks:
            row = BoxLayout(orientation='horizontal', size_hint_y=None, height=55, spacing=10)
            btn = Button(
                text=net['ssid'],
                font_size=20,
                bold=True,
                background_color=theme.dark_color,
                background_normal='',
                size_hint_x=1,
            )
            ssid = net['ssid']
            btn.bind(on_release=lambda b, s=ssid: self._select_network(s))
            sig_color = theme.go_color if int(net.get('signal', '0') or '0') > 50 else theme.dry_color
            sig = Label(
                text=net.get('signal', '0') + '%',
                font_size=16, bold=True, color=sig_color,
                size_hint_x=None, width=55
            )
            lock = Label(
                text='L' if net.get('security') else '',
                font_size=14, size_hint_x=None, width=30
            )
            row.add_widget(btn)
            row.add_widget(sig)
            row.add_widget(lock)
            network_list.add_widget(row)

    def _select_network(self, ssid):
        """Select a network and connect with password from input."""
        self.selected_ssid = ssid
        password = ''
        if 'wifi_password' in self.ids:
            password = self.ids.wifi_password.text.strip()
        self.connect(ssid, password)

    def scan(self, *args):
        """Scan for available WiFi networks."""
        self.status_text = 'Scanning...'
        self.networks = []
        try:
            subprocess.run(
                ['nmcli', 'dev', 'wifi', 'rescan'],
                capture_output=True, timeout=10
            )
        except Exception:
            pass
        # Wait 2 sec for scan to complete, then fetch results (non-blocking)
        Clock.schedule_once(self._fetch_networks, 2.0)

    def _fetch_networks(self, dt):
        """Fetch the network list after rescan completes."""
        try:
            result = subprocess.run(
                ['nmcli', '-t', '-f', 'SSID,SIGNAL,SECURITY', 'dev', 'wifi', 'list'],
                capture_output=True, text=True, timeout=10
            )
            seen = set()
            nets = []
            for line in result.stdout.strip().split('\n'):
                if not line.strip():
                    continue
                parts = line.split(':')
                if len(parts) >= 2:
                    security = parts[-1].strip() if len(parts) >= 3 else ''
                    signal = parts[-2].strip() if len(parts) >= 3 else parts[-1].strip()
                    ssid = ':'.join(parts[:-2]).strip() if len(parts) >= 3 else parts[0].strip()
                    if ssid and ssid not in seen:
                        seen.add(ssid)
                        nets.append({
                            'ssid': ssid,
                            'signal': signal,
                            'security': security
                        })
            nets.sort(key=lambda x: int(x['signal']) if x['signal'].isdigit() else 0, reverse=True)
            self.networks = nets
            self.status_text = f'Found {len(nets)} network(s)'
        except subprocess.TimeoutExpired:
            self.status_text = 'Scan timed out — try again'
        except Exception as e:
            self.status_text = f'Scan error: {e}'

    def connect(self, ssid, password=''):
        """Connect to a WiFi network using nmcli connection profiles.
        Uses 'nmcli c add' + 'nmcli c up' instead of 'nmcli dev wifi connect'
        to avoid WPA2/WPA3 mixed-mode 'key-mgmt missing' errors.
        """
        self.status_text = f'Connecting to {ssid}...'
        try:
            # Clean up any existing connection profile with this name
            con_name = f'expedry-{ssid.replace(" ", "_")}'
            subprocess.run(
                ['nmcli', 'c', 'delete', con_name],
                capture_output=True, timeout=10
            )
            # Create connection profile
            cmd = [
                'nmcli', 'c', 'add', 'type', 'wifi',
                'ifname', 'wlan0', 'con-name', con_name,
                'ssid', ssid
            ]
            if password:
                cmd += ['--', 'wifi-sec.key-mgmt', 'wpa-psk',
                        'wifi-sec.psk', password]
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=15
            )
            if result.returncode != 0:
                err = result.stderr.strip() or result.stdout.strip()
                self.status_text = f'Failed: {err[:60]}'
                return
            # Activate the connection
            result = subprocess.run(
                ['nmcli', 'c', 'up', con_name],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                self.status_text = f'Connected to {ssid}'
                self.is_connected = True
                self.current_ssid = ssid
                Clock.schedule_once(lambda dt: self._get_current_connection(), 3)
            else:
                err = result.stderr.strip() or result.stdout.strip()
                self.status_text = f'Failed: {err[:60]}'
        except subprocess.TimeoutExpired:
            self.status_text = 'Connection timed out'
        except Exception as e:
            self.status_text = f'Error: {e}'

    def disconnect(self, *args):
        """Disconnect from current WiFi."""
        try:
            subprocess.run(
                ['nmcli', 'dev', 'disconnect', 'wlan0'],
                capture_output=True, timeout=10
            )
            self.is_connected = False
            self.current_ssid = '--'
            self.current_ip = '--'
            self.status_text = 'Disconnected'
        except Exception as e:
            self.status_text = f'Error: {e}'
