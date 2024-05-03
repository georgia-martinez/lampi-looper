import pigpio
import colorsys

PIN_R = 19
PIN_G = 26
PIN_B = 13
PINS = [PIN_R, PIN_G, PIN_B]


class LampiDriver(object):
    def __init__(self):
        self._gpio = pigpio.pi()
        for color_pin in PINS:
            self._gpio.set_mode(color_pin, pigpio.OUTPUT)
            self._gpio.set_PWM_dutycycle(color_pin, 0)
            self._gpio.set_PWM_frequency(color_pin, 1000)
            self._gpio.set_PWM_range(color_pin, 1000)

    def change_color(self, r, g, b):
        self._gpio.write(PIN_R, r)
        self._gpio.write(PIN_G, g)
        self._gpio.write(PIN_B, b)
