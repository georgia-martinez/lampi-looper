import pygame
import time

from sound import Sound
from enum import Enum, auto

class LampiGroove:
    def __init__(self):
        self.pause = None
        self.bpm = self.set_bpm(200)
        self.beats_per_measure = 4

        self.groove = [0 for _ in range(self.beats_per_measure ** 2)]

        self.sound_map = {
            0: None,
            1: Sound("hi_hat"),
            2: Sound("snare"),
            3: Sound("tom"),
        }

        pygame.init()

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
                if self.groove[beat] != 0:
                    sound_id = self.groove[beat]
                    self.sound_map[sound_id].play()

                time.sleep(self.pause)

        pygame.quit()

if __name__ == "__main__":
    lampi_groove = LampiGroove()

    lampi_groove.groove = [
        3, 0, 1, 0,
        2, 0, 1, 0,
        3, 0, 1, 0,
        2, 0, 1, 0,
    ]

    lampi_groove.play()