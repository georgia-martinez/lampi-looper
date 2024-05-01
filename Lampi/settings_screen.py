import lampi_util

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.checkbox import CheckBox
from lampi_common import *


class SettingsScreen(Screen):
    def __init__(self, main_screen=None, **kwargs):
        super(SettingsScreen, self).__init__(**kwargs)

        self.main_screen = main_screen

        layout = BoxLayout(orientation="vertical", padding=5)

        # BPM slider and label
        self.bpm_slider = Slider(min=0, max=200, value=100, step=1, 
                                 value_track=True, value_track_color=[0.5, 0.5, 0.5, 0.5])
        self.bpm_slider.size_hint_y = None
        self.bpm_slider.height = 50

        self.bpm_label = Label()
        self.bpm_label.text = f"BPM: {100}"
        self.bpm_label.color = (0, 0, 0, 1)

        self.bpm_label.size_hint_y = None
        self.bpm_label.height = 20
        self.bpm_slider.bind(value=self.update_bpm)

        layout.add_widget(self.bpm_slider)
        layout.add_widget(self.bpm_label)

        # Time signatures
        time_sigs_layout = GridLayout(cols=2, rows=3, spacing=5)
        self.time_sigs_map = {}

        for time_sig in list(TimeSignature):
            text = Label(text=time_sig.label)
            text.color = (0, 0, 0, 1)

            checkbox = CheckBox()
            checkbox.color = (0, 0, 0, 1)
            checkbox.group = "group"
            checkbox.bind(active=self.update_time_signature)

            self.time_sigs_map[time_sig] = checkbox

            time_sigs_layout.add_widget(text)
            time_sigs_layout.add_widget(checkbox)

        self.time_sigs_map[TimeSignature.FOUR_FOUR].active = True

        layout.add_widget(time_sigs_layout)

        # Network info
        ip_label = Label(text=self.ip_address())
        ip_label.color = (0, 0, 0, 1)

        layout.add_widget(ip_label)

        self.add_widget(layout)

    def update_bpm(self, instance, value):
        bpm = int(value)
        self.bpm_label.text = f"BPM: {bpm}"
        
        self.main_screen.set_bpm(bpm)
        self.main_screen.publish_state_change()

    def update_time_signature(self, checkbox, value):
        if value:
            for time_sig in self.time_sigs_map:
                curr = self.time_sigs_map[time_sig]

                if curr == checkbox:
                    self.main_screen.set_time_signature(time_sig)
                    return


    def ip_address(self):
        interface = "wlan0"
        ipaddr = lampi_util.get_ip_address(interface)
        deviceid = lampi_util.get_device_id()

        return "{}: {}\nDeviceID: {}".format(interface, ipaddr, deviceid)