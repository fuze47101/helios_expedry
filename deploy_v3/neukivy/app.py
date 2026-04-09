"""
NeuKivy Compatibility Shim — app.py
Replaces the unavailable NeuKivy library.
Provides NeuApp, NeuRoundedButton, NeuCard with standard Kivy rendering.
"""

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ListProperty, NumericProperty
from kivy.lang import Builder
from kivy.factory import Factory


# ── Theme Manager (dummy — matches what main.py expects) ──

class ThemeManager:
    """Stub for NeuKivy's theme_manager. Properties are set by TesterApp.build()."""
    bg_color = (0.34, 0.35, 0.38, 1)
    light_color = (0.54, 0.55, 0.58, 1)
    dark_color = (0.14, 0.15, 0.18, 1)
    text_color = (1, 1, 1, 1)
    disabled_text_color = (0.1, 0.1, 0.1, 1)


# ── NeuApp ──

class NeuApp(App):
    """Drop-in replacement for neukivy.app.NeuApp."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_manager = ThemeManager()


# ── NeuRoundedButton ──

class NeuRoundedButton(Button):
    """
    Drop-in for NeuKivy's neumorphic button.
    Renders as a flat rounded-rect button.
    Existing .kv files set background_color on instances — that still works.
    """
    pass


# ── NeuCard ──

class NeuCard(BoxLayout):
    """
    Drop-in for NeuKivy's neumorphic card container.
    Renders as a dark rounded-rect box.
    Properties comp_color / light_color / dark_color exist for compat but
    only affect the canvas slightly.
    """
    radius = NumericProperty(10)
    comp_color = ListProperty([0, 0, 0, 1])
    light_color = ListProperty([0.54, 0.55, 0.58, 1])
    dark_color = ListProperty([0.14, 0.15, 0.18, 1])


# ── Register in Kivy Factory so .kv files find them ──

Factory.register('NeuRoundedButton', cls=NeuRoundedButton)
Factory.register('NeuCard', cls=NeuCard)


# ── KV styling ──

Builder.load_string('''
#:import dp kivy.metrics.dp
#:import sp kivy.metrics.sp

<NeuRoundedButton>:
    background_normal: ''
    background_color: 0.24, 0.25, 0.28, 1
    color: 1, 1, 1, 1

<NeuCard>:
    canvas.before:
        Color:
            rgba: 0.24, 0.25, 0.28, 1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(self.radius)]
''')
