#!/usr/bin/env python3

import platform
import json
import pigpio
import lampi_util
import paho.mqtt.client as mqtt
import subprocess
import time
import signal
import os

from math import fabs
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.properties import BooleanProperty
from kivy.clock import Clock
from paho.mqtt.client import Client
from lampi_mixer import LampiMixer
from lampi_common import *

class BeatButton(Button):

    def __init__(self, id, **kwargs):
        super(BeatButton, self).__init__(**kwargs)

        self.id = id

        self.colors = [
            Color.GRAY,
            Color.BLUE,
            Color.GREEN,
            Color.RED,
        ]

        self.reset_color()

    def toggle_color(self):
        if self.color_id != len(self.colors) - 1:
            self.color_id += 1
        else:
            self.color_id = 0

        self.set_color(self.color_id)

    def reset_color(self):
        self.color_id = 0
        self.curr_color = Color.GRAY
        self.set_color(self.color_id)

    def set_color(self, color_id):
        self.color_id = color_id
        new_color = self.colors[color_id]

        self.background_color = new_color.value
        self.curr_color = new_color

MQTT_CLIENT_ID = "lampi_app"

class LampiApp(App):

    PLAY_PIN = 27 
    CLEAR_PIN = 23 
    NETWORK_PIN = 17

    play_button_pressed = BooleanProperty(False)
    clear_button_pressed = BooleanProperty(False)
    network_button_pressed = BooleanProperty(False)

    network_popup_open = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.pause_duration = self.set_pause_duration(100)
        self.beats_per_measure = 4

        self.loop = [0 for _ in range(self.beats_per_measure ** 2)]

        self.setup_face_buttons()
        self.setup_network_popup()

        self.play_flag = False
        self.play_process = None

    def create_client(self):
        client = mqtt.Client(client_id=MQTT_CLIENT_ID)
        client.enable_logger()
        client.connect(MQTT_BROKER_HOST, port=MQTT_BROKER_PORT, keepalive=MQTT_BROKER_KEEP_ALIVE_SECS)
        client.on_connect = self.on_connect
        client.message_callback_add(TOPIC_UI_UPDATE, self.update_ui)
        client.loop_start()

        return client

    def on_connect(self, client, userdata, rc, unknown):
        self.client.subscribe(TOPIC_UI_UPDATE, qos=0)

    def update_ui(self, client, userdata, msg):
        msg = json.loads(msg.payload.decode('utf-8'))

        if msg["client"] == MQTT_CLIENT_ID:
            return

        self.loop = msg["loop"]
        # self.update_bpm(msg["bpm"])

        self.update_buttons()

    def build(self):
        layout = BoxLayout(orientation="vertical")

        # Adding the bpm slider and label
        self.bpm_slider = Slider(min=0, max=200, value=100, step=1)
        self.bpm_slider.size_hint_y = None
        self.bpm_slider.height = 50

        self.bpm_label = Label()
        self.bpm_label.text = f"BPM: {100}"
        self.set_pause_duration(100)

        self.bpm_label.size_hint_y = None
        self.bpm_label.height = 20
        self.bpm_slider.bind(value=self.update_bpm_label)

        layout.add_widget(self.bpm_slider)
        layout.add_widget(self.bpm_label)

        # Adding the button grid
        self.button_grid = GridLayout(cols=4, spacing=5)
        self.buttons = []

        for i in range(16):
            btn = BeatButton(i)
            btn.bind(on_press=self.on_beat_button_press)
            
            self.button_grid.add_widget(btn)
            self.buttons.append(btn)

        layout.add_widget(self.button_grid)

        self.client = self.create_client()

        return layout

    def reset_loop(self):
        self.loop = [0 for _ in range(16)]
        self.publish_state_change()

    def set_pause_duration(self, bpm):
        self.bpm = bpm
        self.pause_duration = 0.25 * (60 / bpm)

    def update_buttons(self):
        for i, btn in zip(self.loop, self.buttons):
            btn.set_color(i)

    def update_bpm_label(self, instance, value):
        self.update_bpm(value)

    def update_bpm(self, value):
        bpm = int(value)

        self.bpm_label.text = f"BPM: {bpm}"
        self.set_pause_duration(bpm)

        self.publish_state_change()

    def on_beat_button_press(self, instance):
        instance.toggle_color()
        self.loop[instance.id] = instance.curr_color.id()
        self.publish_state_change()

    def publish_state_change(self):
        bpm_val = ''.join(filter(str.isdigit, self.bpm_label.text))
        msg = self.ui_update_msg(self.loop, bpm_val)        

        self.client.publish(TOPIC_UI_UPDATE, json.dumps(msg).encode('utf-8'), qos=0)

    def ui_update_msg(self, loop, bpm):
        return {"client": MQTT_CLIENT_ID, "loop": loop, "bpm": bpm}

    def setup_face_buttons(self):
        self.pi = pigpio.pi()

        self.pi.set_mode(self.PLAY_PIN, pigpio.INPUT)
        self.pi.set_pull_up_down(self.PLAY_PIN, pigpio.PUD_UP)        

        self.pi.set_mode(self.CLEAR_PIN, pigpio.INPUT)
        self.pi.set_pull_up_down(self.CLEAR_PIN, pigpio.PUD_UP)

        self.pi.set_mode(self.NETWORK_PIN, pigpio.INPUT)
        self.pi.set_pull_up_down(self.NETWORK_PIN, pigpio.PUD_UP)  

    def on_play_button_pressed(self, instance, value):
        if value: 
            if self.play_flag:
                os.kill(self.play_process.pid, signal.SIGTERM)
                self.play_process.wait()
                LampiMixer.lampi_driver.change_color(0, 0, 0)

            else:
                command = [
                    "python3", 
                    "/home/pi/lampi-looper/Lampi/playback.py", 
                    json.dumps(self.loop),
                    str(self.pause_duration)
                ]
                self.play_process = subprocess.Popen(command)

            self.play_flag = not self.play_flag

    def on_clear_button_pressed(self, instance, value):
        if value:      
            for btn in self.buttons:
                btn.reset_color()
            
            self.reset_loop()

    def setup_network_popup(self):
        Clock.schedule_interval(self._poll_GPIO, 0.05)

        self.network_popup = self.build_network_popup()
        self.network_popup.bind(on_open=self.update_popup_ip_address)

    def build_network_popup(self):
        return Popup(title='Network Status',
                     content=Label(text='IP ADDRESS WILL GO HERE'),
                     size_hint=(1, 1), auto_dismiss=False)

    def update_popup_ip_address(self, instance):
        interface = "wlan0"
        ipaddr = lampi_util.get_ip_address(interface)
        deviceid = lampi_util.get_device_id()

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
        self.play_button_pressed = not self.pi.read(self.PLAY_PIN)       # button 1
        self.clear_button_pressed = not self.pi.read(self.CLEAR_PIN)     # button 2
        self.network_button_pressed = not self.pi.read(self.NETWORK_PIN) # button 4

if __name__ == "__main__":
    LampiApp().run()