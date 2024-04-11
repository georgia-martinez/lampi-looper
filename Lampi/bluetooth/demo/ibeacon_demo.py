#! /usr/bin/env python3
from pybleno import Bleno
import sys
import signal
import time


uuid = 'B9407F30-F5F8-466E-AFF9-25556B57FE6D'  # Estimote iBeacon UUID
major = 0
minor = 0
measuredPower = -59


class DemoiBeacon():
    def __init__(self):
        self.bleno = Bleno()
        self.bleno.on('stateChange', self.onStateChange)
        self.bleno.on('advertisingStart', self.onAdvertisingStart)

    def start(self):
        self.bleno.start()

    def stop(self):
        self.bleno.stopAdvertising()
        self.bleno.disconnect()

    def onStateChange(self, state):
        print('on -> stateChange: ' + state)

        if (state == 'poweredOn'):
            self.bleno.startAdvertisingIBeacon(
                uuid,
                major,
                minor,
                measuredPower,
            )
        else:
            self.bleno.stopAdvertising()

    def onAdvertisingStart(self, error):
        print('on -> advertisingStart: '
              + ('error ' + error if error else 'success'))


def main():
    ibeacon = DemoiBeacon()
    ibeacon.start()

    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
