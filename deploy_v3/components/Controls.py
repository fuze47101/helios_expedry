"""
Controls.py — Relay Toggle Controls Widget
ExpeDRY FeatherV2

Provides on/off toggle switches for the 4 relay channels:
  - External Humidifier (ch1)
  - Internal Humidifier (ch2)
  - Fan (ch3)
  - Heater (ch4)

Used in tester.kv as <Controls> widget inside the main layout.
Properties are bound to FeatherInterface's relay status properties.
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.properties import BooleanProperty


class Controls(BoxLayout):
    fan_status = BooleanProperty(False)
    hum1_status = BooleanProperty(False)
    hum2_status = BooleanProperty(False)
    heat_status = BooleanProperty(False)
