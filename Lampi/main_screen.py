import json
import lampi_util
import paho.mqtt.client as mqtt
import subprocess
import time
import signal
import os

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.properties import BooleanProperty
from kivy.uix.screenmanager import Screen

from paho.mqtt.client import Client
from lampi_mixer import LampiMixer
from lampi_common import *

MQTT_CLIENT_ID = "lampi_app"

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


class MainScreen(Screen):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)

        self.pause_duration = self.set_bpm(100)
        self.time_signature = TimeSignature.FOUR_FOUR

        self.play_flag = False
        self.play_process = None

        self.build()
        self.client = self.create_client()

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
        self.clear_widgets()
        self.reset_loop(publish=False)

        layout = BoxLayout(orientation="vertical", padding=5)

        self.button_grid = GridLayout(rows=self.time_signature.numerator,
                                      cols=self.time_signature.denominator, 
                                      spacing=5)
        self.buttons = []

        for i in range(self.time_signature.numerator * self.time_signature.denominator):
            btn = BeatButton(i)
            btn.bind(on_press=self.on_beat_button_press)
            
            self.button_grid.add_widget(btn)
            self.buttons.append(btn)

        layout.add_widget(self.button_grid)
        self.add_widget(layout)

    def reset_loop(self, publish=True):
        self.loop = [0 for _ in range(self.time_signature.numerator * self.time_signature.denominator)]
        
        if publish:
            self.publish_state_change()

    def set_bpm(self, bpm):
        self.bpm = bpm

        if bpm != 0:
            self.pause_duration = 0.25 * (60 / bpm)
        else:
            self.pause_duration = 0

    def set_time_signature(self, time_sig):
        self.time_signature = time_sig
        self.build()

    def update_buttons(self):
        for i, btn in zip(self.loop, self.buttons):
            btn.set_color(i)

    def on_beat_button_press(self, instance):
        instance.toggle_color()
        self.loop[instance.id] = instance.curr_color.id()
        self.publish_state_change()

    def publish_state_change(self):
        msg = self.ui_update_msg(self.loop, self.bpm)        

        self.client.publish(TOPIC_UI_UPDATE, json.dumps(msg).encode('utf-8'), qos=1)

    def ui_update_msg(self, loop, bpm):
        return {"client": MQTT_CLIENT_ID, "loop": loop, "bpm": bpm} 

    def toggle_play(self):
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

    def clear(self):
        for btn in self.buttons:
            btn.reset_color()
        
        self.reset_loop()