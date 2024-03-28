import pygame
import os
import time

class Sound():
    mixer = pygame.mixer
    mixer.init()

    def __init__(self, sound_name):
        sound_file = os.path.join(os.getcwd(), "Lampi/sounds", sound_name + ".WAV")
        self.sound = Sound.mixer.Sound(sound_file)

    def play(self):
        self.sound.play()