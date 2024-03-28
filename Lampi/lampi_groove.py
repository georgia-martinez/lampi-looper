import pygame
import time
import json
import paho.mqtt.client as mqtt

from paho.mqtt.client import Client
from sound import Sound
from enum import Enum, auto
from lampi_common import *
from lampi_app import Color

class LampiGroove:
    def __init__(self):
        self.pause = None
        self.bpm = self.set_bpm(100)
        self.beats_per_measure = 4

        self.groove = [0 for _ in range(self.beats_per_measure ** 2)]

        self.sound_map = {
            0: None,
            1: Sound("hi_hat"),
            2: Sound("snare"),
            3: Sound("tom"),
        }

        pygame.init()

        # MQTT
        self.mqtt = Client(client_id="lampi_groove")
        self.mqtt.enable_logger()
        self.mqtt.connect(MQTT_BROKER_HOST, port=MQTT_BROKER_PORT, keepalive=MQTT_BROKER_KEEP_ALIVE_SECS)
        self.mqtt.loop_start()

    def set_bpm(self, bpm):
        self.bpm = bpm
        self.pause = 0.25 * (60 / bpm) 

    def play(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            for beat in range(len(self.groove)):
                sound_id = self.groove[beat]

                if self.groove[beat] != 0:
                    self.sound_map[sound_id].play()
                
                self.update_led(sound_id)

                time.sleep(self.pause)

        pygame.quit()

    def update_led(self, sound_id):
        if sound_id == 0:
            msg = {"r": 0, "g": 0, "b": 0}
        else:
            color = Color.get_color(sound_id)
            r, g, b, _ = color.value

            msg = {"r": r, "g": g, "b": b}

        self.mqtt.publish(TOPIC_LED_UPDATE, json.dumps(msg).encode('utf-8'), qos=1)

if __name__ == "__main__":
    lampi_groove = LampiGroove()

    lampi_groove.groove = [
        3, 0, 1, 0,
        2, 0, 1, 0,
        3, 0, 1, 0,
        2, 0, 1, 0,
    ]

    lampi_groove.play()