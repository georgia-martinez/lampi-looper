#! /usr/bin/env python3
from pybleno import Bleno
from device_info_service_3 import DeviceInfoService
import time
import socket


class DemoBLEPeripheral():
    def __init__(self):
        self.bleno = Bleno()
        self.info_service = DeviceInfoService('CWRU', 'LAMPI', '123456')

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
                                            self.info_service.uuid,]
                                        )
        else:
            self.bleno.stopAdvertising()

    def onAdvertisingStart(self, error):
        print('on -> advertisingStart: '
              + ('error ' + error if error else 'success'))

        if not error:
            self.bleno.setServices([
                self.info_service,
            ])


def main():

    ble_peripheral = DemoBLEPeripheral()
    ble_peripheral.start()

    while True:
        time.sleep(1)

    print("\nStopping BLE peripheral\n")
    ble_peripheral.stop()


if __name__ == "__main__":
    main()
