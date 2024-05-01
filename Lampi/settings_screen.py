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

BLACK = (0, 0, 0, 1)

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
        self.bpm_label.color = BLACK

        self.bpm_label.size_hint_y = None
        self.bpm_label.height = 20
        self.bpm_slider.bind(value=self.update_bpm)

        layout.add_widget(self.bpm_slider)
        layout.add_widget(self.bpm_label)

        # Time signatures
        grid_layout = GridLayout(cols=2, rows=4, spacing=5)
        self.time_sigs_map = {}

        for time_sig in list(TimeSignature):
            text = Label(text=time_sig.label, color=BLACK)

            checkbox = CheckBox(group="group", color=BLACK)
            checkbox.bind(active=self.update_time_signature)

            self.time_sigs_map[time_sig] = checkbox

            grid_layout.add_widget(text)
            grid_layout.add_widget(checkbox)

        self.time_sigs_map[TimeSignature.FOUR_FOUR].active = True

        swing_text = Label(text="Swing", color=BLACK)
        
        swing_checkbox = CheckBox(color=BLACK)
        swing_checkbox.bind(active=self.toggle_swing)

        grid_layout.add_widget(swing_text)
        grid_layout.add_widget(swing_checkbox)

        layout.add_widget(grid_layout)

        # Network info
        ip_label = Label(text=self.ip_address())
        ip_label.color = BLACK

        layout.add_widget(ip_label)

        self.add_widget(layout)

    def update_bpm(self, instance, value):
        bpm = int(value)
        self.bpm_label.text = f"BPM: {bpm}"
        
        self.main_screen.set_bpm(bpm)

    def update_time_signature(self, checkbox, value):
        if value:
            for time_sig in self.time_sigs_map:
                curr = self.time_sigs_map[time_sig]

                if curr == checkbox:
                    self.main_screen.set_time_signature(time_sig)
                    return

    def toggle_swing(self, checkbox, value):
        self.main_screen.swung = not self.main_screen.swung

    def ip_address(self):
        interface = "wlan0"
        ipaddr = lampi_util.get_ip_address(interface)
        deviceid = lampi_util.get_device_id()

        return "{}: {}\nDeviceID: {}".format(interface, ipaddr, deviceid)