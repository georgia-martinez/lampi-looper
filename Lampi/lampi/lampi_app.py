import platform
import json
import pigpio
import lampi.lampi_util

from enum import Enum
from math import fabs
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.properties import NumericProperty, AliasProperty, BooleanProperty
from kivy.clock import Clock
from paho.mqtt.client import Client
from lamp_common import *

class Color(Enum):
    GRAY = (0.5, 0.5, 0.5, 1)
    RED = (1, 0, 0, 1)
    GREEN = (0, 1, 0, 1)
    BLUE = (0, 0, 1, 1)

class BeatButton(Button):
    def __init__(self, **kwargs):
        super(BeatButton, self).__init__(**kwargs)

        self.colors = [
            Color.GRAY,
            Color.RED,
            Color.GREEN,
            Color.BLUE,
        ]

        self.color_id = 0
        self.curr_color = Color.GRAY
        self._toggle_color()

    def on_press(self):
        if self.color_id != len(self.colors) - 1:
            self.color_id += 1
        else:
            self.color_id = 0

        self._toggle_color()

    def _toggle_color(self):
        new_color = self.colors[self.color_id]

        self.background_color = new_color.value
        self.curr_color = new_color

class MainLayout(BoxLayout):
    def __init__(self, **kwargs):
        super(MainLayout, self).__init__(**kwargs)
        
        self.orientation = 'vertical'

        # Adding the bpm slider
        self.bpm_slider = Slider(min=0, max=200, value=100, step=1)
        self.bpm_slider.size_hint_y = None
        self.bpm_slider.height = 50

        self.bpm_label = Label()
        self.update_bpm_label(None, self.bpm_slider.value)

        self.bpm_label.size_hint_y = None
        self.bpm_label.height = 20
        self.bpm_slider.bind(value=self.update_bpm_label)

        self.add_widget(self.bpm_slider)
        self.add_widget(self.bpm_label)

        # Adding the button grid
        self.button_grid = GridLayout(cols=4, spacing=5)

        for i in range(16):
            btn = BeatButton()
            self.button_grid.add_widget(btn)

        self.add_widget(self.button_grid)

    def update_bpm_label(self, instance, value):
        self.bpm_label.text = f"BPM: {int(value)}"

class LampiApp(App):

    network_button_pressed = BooleanProperty(False)
    network_popup_open = BooleanProperty(False)

    def build(self):
        return MainLayout()

    def on_start(self):
        self.set_up_network_popup()

    def set_up_network_popup(self):
        self.pi = pigpio.pi()
        self.pi.set_mode(17, pigpio.INPUT)
        self.pi.set_pull_up_down(17, pigpio.PUD_UP)
        Clock.schedule_interval(self._poll_GPIO, 0.05)
        self.network_popup = self._build_network_popup()
        self.network_popup.bind(on_open=self.update_popup_ip_address)

    def _build_network_popup(self):
        return Popup(title='Network Status',
                     content=Label(text='IP ADDRESS WILL GO HERE'),
                     size_hint=(1, 1), auto_dismiss=False)

    def update_popup_ip_address(self, instance):
        interface = "wlan0"
        ipaddr = lampi.lampi_util.get_ip_address(interface)
        deviceid = lampi.lampi_util.get_device_id()

        msg = "{}: {}\nDeviceID: {}".format(interface, ipaddr, deviceid)
        instance.content.text = msg

    def on_network_button_pressed(self, instance, value):
        if value:
            if not self.network_popup_open:
                self.network_popup.open()
                self.network_popup_open = True
            else:
                self.network_popup.dismiss()
                self.network_popup_open = False

    def _poll_GPIO(self, dt):
        self.network_button_pressed = not self.pi.read(17) # gpio17 is the rightmost button