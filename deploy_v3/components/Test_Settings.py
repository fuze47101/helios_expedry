"""
Test_Settings.py — Test Configuration Widget
ExpeDRY FeatherV2

Provides input fields for test parameters:
  - Duration (minutes)
  - Interval (seconds between data points)
  - Endpoint (target humidity %)
  - Switchover point (for resistance tests)

Properties are bound from FeatherInterface in tester.kv.
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.properties import BooleanProperty, BoundedNumericProperty, NumericProperty


class Test_Settings(BoxLayout):
    duration = NumericProperty(10)
    endpoint = NumericProperty(45)
    interval = NumericProperty(5)
    running = BooleanProperty(False)
    sw_point = NumericProperty(50)
