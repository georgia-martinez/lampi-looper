import time
import json
import sys

from lampi_mixer import LampiMixer
from lampi_common import *


def update_led(sound_id):
    if sound_id == 0:
        LampiMixer.lampi_driver.change_color(0, 0, 0)
    else:
        color = Color.get_color(sound_id)
        r, g, b, _ = color.value

        LampiMixer.lampi_driver.change_color(r, g, b)


if __name__ == "__main__":

    loop = json.loads(sys.argv[1])
    pause_duration = float(sys.argv[2])
    swung = bool(int(sys.argv[3]))

    col_num = 1
    swing_ratio = 0.3

    while True:
        for beat in range(len(loop)):
            sound_id = loop[beat]

            if loop[beat] != 0:
                LampiMixer.sound_map[sound_id].play()

            update_led(sound_id)

            if swung and col_num == 3:
                time.sleep(pause_duration * swing_ratio)
            else:
                time.sleep(pause_duration)

            col_num += 1

            if col_num > 4:
                col_num = 1
