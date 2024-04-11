#! /usr/bin/env python3

from pybleno import Bleno
from device_info_service import DeviceInfoService
from lampi_service import LampiService
import sys
import signal
import time
import socket

DEVICE_ID_FILENAME = '/sys/class/net/eth0/address'


def get_device_id():
    mac_addr = open(DEVICE_ID_FILENAME).read().strip()
    return mac_addr.replace(':', '')


class LampiBLEPeripheral():
    def __init__(self):
        self.bleno = Bleno()
        self.info_service = DeviceInfoService('CWRU', 'LAMPI',
                                              get_device_id())
        self.lampi_service = LampiService()

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
            self.bleno.startAdvertising(socket.gethostname(),
                                        [
                                            self.info_service.uuid,
                                            self.lampi_service.uuid]
                                        )
        else:
            self.bleno.stopAdvertising()

    def onAdvertisingStart(self, error):
        print('on -> advertisingStart: ' +
              ('error ' + error if error else 'success'))

        if not error:
            self.bleno.setServices([
                self.info_service,
                self.lampi_service
            ])


stopflag = False


def main():
    def on_exit(*args, **kwargs):
        global stopflag
        stopflag = True

    signal.signal(signal.SIGTERM, on_exit)
    signal.signal(signal.SIGINT, on_exit)

    ble_peripheral = LampiBLEPeripheral()
    ble_peripheral.start()

    while not stopflag:
        time.sleep(1)

    print("\nStopping BLE peripheral\n")
    ble_peripheral.stop()


if __name__ == "__main__":
    if __name__ == '__main__':
        sys.exit(main())
