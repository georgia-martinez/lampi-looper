import platform
import json
import pigpio
import lampi.lampi_util

from enum import Enum
from math import fabs
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.properties import NumericProperty, AliasProperty, BooleanProperty
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.label import Label
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

        print(Color.GRAY.value)

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

class GridLayoutExample(GridLayout):
    def __init__(self, **kwargs):
        super(GridLayoutExample, self).__init__(**kwargs)
        self.cols = 4
        self.spacing = 5

        for i in range(16):
            btn = BeatButton(background_color=(1, 1, 1, 1))
            self.add_widget(btn)

class LampiApp(App):

    gpio17_pressed = BooleanProperty(False)
    popup_opened = BooleanProperty(False)

    def build(self):
        return GridLayoutExample()

    def on_start(self):
        self.set_up_GPIO_and_network_status_popup()

    def set_up_GPIO_and_network_status_popup(self):
        self.pi = pigpio.pi()
        self.pi.set_mode(17, pigpio.INPUT)
        self.pi.set_pull_up_down(17, pigpio.PUD_UP)
        Clock.schedule_interval(self._poll_GPIO, 0.05)
        self.network_status_popup = self._build_network_status_popup()
        self.network_status_popup.bind(on_open=self.update_popup_ip_address)

    def _build_network_status_popup(self):
        return Popup(title='Network Status',
                     content=Label(text='IP ADDRESS WILL GO HERE'),
                     size_hint=(1, 1), auto_dismiss=False)

    def update_popup_ip_address(self, instance):
        interface = "wlan0"
        ipaddr = lampi.lampi_util.get_ip_address(interface)
        deviceid = lampi.lampi_util.get_device_id()
        msg = "{}: {}\nDeviceID: {}".format(interface, ipaddr, deviceid)
        instance.content.text = msg

    def on_gpio17_pressed(self, instance, value):
        if value:
            if not self.popup_opened:
                self.network_status_popup.open()
                self.popup_opened = True
            else:
                self.network_status_popup.dismiss()
                self.popup_opened = False

    def _poll_GPIO(self, dt):
        self.gpio17_pressed = not self.pi.read(17)
