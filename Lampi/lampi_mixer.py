#!/usr/bin/env python3

import pygame
import time
import json
import os
import paho.mqtt.client as mqtt
import pigpio
import colorsys
import threading

from paho.mqtt.client import Client
from enum import Enum, auto
from lampi_driver import LampiDriver
from lampi_common import *


class SoundFile():
    mixer = pygame.mixer
    mixer.init()

    def __init__(self, sound_name):
        sound_file = os.path.join(
            "/home/pi/lampi-looper/Lampi/sounds/",
            sound_name + ".WAV")
        self.sound = SoundFile.mixer.Sound(sound_file)

    def play(self):
        self.sound.play()


class LampiMixer:

    lampi_driver = LampiDriver()
    lampi_driver.change_color(0, 0, 0)  # turn off

    sound_map = {
        0: None,
        1: SoundFile("tom"),
        2: SoundFile("snare"),
        3: SoundFile("hi_hat"),
    }
