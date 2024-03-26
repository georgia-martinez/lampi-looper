import pygame
import os
import time

class Sound():
    def __init__(self, mixer, sound_name, color):
        self.mixer = mixer
        sound_file = os.path.join("Lampi/lampi/sounds", sound_name + ".wav")
        self.sound = pygame.mixer.Sound(sound_file)
        self.color = color

    def play(self):
        self.sound.play()