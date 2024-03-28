import pygame
import time
import json
import paho.mqtt.client as mqtt

from paho.mqtt.client import Client
from enum import Enum, auto
from lampi_app import Color
from lampi_common import *

class SoundFile():
    mixer = pygame.mixer
    mixer.init()

    def __init__(self, sound_name):
        sound_file = os.path.join(os.getcwd(), "Lampi/sounds", sound_name + ".WAV")
        self.sound = Sound.mixer.Sound(sound_file)

    def play(self):
        self.sound.play()

class LampiMixer:
    def __init__(self):
        self.pause = None
        self.bpm = self.set_bpm(100)
        self.beats_per_measure = 4

        self.loop = [0 for _ in range(self.beats_per_measure ** 2)]

        self.sound_map = {
            0: None,
            1: SoundFile("hi_hat"),
            2: SoundFile("snare"),
            3: SoundFile("tom"),
        }

        pygame.init()

        # MQTT
        self.mqtt = Client(client_id="lampi_mixer")
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

            for beat in range(len(self.loop)):
                sound_id = self.loop[beat]

                if self.loop[beat] != 0:
                    self.sound_map[sound_id].play()
                
                self.update_led(sound_id)

                time.sleep(self.pause)

        pygame.quit()

    def update_led(self, sound_id):
        if sound_id == 0:
            msg = self.led_update_msg(0, 0, 0)
        else:
            color = Color.get_color(sound_id)
            r, g, b, _ = color.value

            msg = self.led_update_msg(r, g, b)

        self.mqtt.publish(TOPIC_LED_UPDATE, json.dumps(msg).encode('utf-8'), qos=1)

    def led_update_msg(self, r, g, b):
        return {"r": r, "g": g, "b": b}

if __name__ == "__main__":
    mixer = LampiMixer()

    mixer.loop = [
        3, 0, 1, 0,
        2, 0, 1, 0,
        3, 0, 1, 0,
        2, 0, 1, 0,
    ]

    mixer.play()