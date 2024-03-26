import pygame
import time

from sound import Sound
from enum import Enum, auto

class Color(Enum):
    RED = auto()
    BLUE = auto()
    GREEN = auto()
    YELLOW = auto()

class LampiGroove:
    def __init__(self):
        self.pause = None
        self.bpm = self.set_bpm(100)
        self.time_signature = 4

        self.groove = [0 for _ in range(self.time_signature)]

        mixer = pygame.mixer
        mixer.init()

        self.sound_map = {
            0: None,
            1: Sound(mixer, "hi_hat", Color.YELLOW),
            2: Sound(mixer, "snare", Color.RED),
            3: Sound(mixer, "tom", Color.BLUE),
        }

        pygame.init()

    def set_bpm(self, bpm):
        self.bpm = bpm
        self.pause = 0.25 * (60 / bpm) 

    def play(self):
        # Main loop to play the bass drum sound at quarter note intervals
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Play the bass drum sound on each quarter note
            for beat in range(len(self.groove)):
                if self.groove[beat] != 0:
                    self.sound_map[self.groove[beat]].play()

                time.sleep(self.pause)

        # Clean up resources
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