from pybleno import Characteristic, Descriptor
from lampi_state import LampiState

import array
import struct


class HSVCharacteristic(Characteristic):
    def __init__(self, lampi_state: LampiState):
        Characteristic.__init__(self, {
            'uuid': '0002A7D3-D8A4-4FEA-8174-1736E808C066',
            'properties': ['read', 'write', 'notify'],
            'value': None,
            'descriptors': [
                Descriptor({
                    'uuid': '2901',
                    'value': bytes("HSV", 'utf-8')
                }),
                Descriptor({
                    'uuid': '2904',
                    # Presentation Format fields are:
                    # Format      1 octet :  0x07 - unsigned 24-bit value
                    # Exponent    1 octet :  0x00
                    # Unit        2 octets:  0x2700 - unitless
                    # Name Space  1 octet :  0x01 - Bluetooth SIG
                    # Description 2 octets:  0x0000 - blank
                    'value': struct.pack("<BBHBH", 0x07, 0x00,
                                         0x2700, 0x01, 0x0000)
                })
            ]
        })

        self.updateValueCallback = None

        self.lampi_state = lampi_state
        self.lampi_state.on('hsvChange', self.handle_hsv_change)

# region BLE Read/Write
    def onReadRequest(self, offset, callback):
        if offset:
            callback(Characteristic.RESULT_ATTR_NOT_LONG, None)
        else:
            data = struct.pack("<BBB",
                               int(self.lampi_state.hue * 0xff),
                               int(self.lampi_state.saturation * 0xff),
                               0x00)
            callback(Characteristic.RESULT_SUCCESS, data)

    def onWriteRequest(self, data, offset, withoutResponse, callback):
        if offset:
            callback(Characteristic.RESULT_ATTR_NOT_LONG)
        elif len(data) != 3:
            callback(Characteristic.RESULT_INVALID_ATTRIBUTE_LENGTH)
        else:
            new_hue = data[0] / 0xff
            new_saturation = data[1] / 0xff
            print(f'New hue: {new_hue} sat: {new_saturation}')
            self.lampi_state.setHSV(new_hue, new_saturation)
            callback(Characteristic.RESULT_SUCCESS)

    def handle_hsv_change(self, newValue):
        print(f"Handling HSV change: {newValue}")
        if self.updateValueCallback:
            data = struct.pack("<BBB",
                               int(self.lampi_state.hue * 0xff),
                               int(self.lampi_state.saturation * 0xff),
                               0x00)
            self.updateValueCallback(data)

# endregion
