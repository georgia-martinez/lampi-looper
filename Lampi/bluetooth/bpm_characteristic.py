from pybleno import Characteristic, Descriptor
from lampi_state import LampiState

import array
import struct


class BpmCharacteristic(Characteristic):

    MAX_BPM = 200

    def __init__(self, lampi_state: LampiState):
        Characteristic.__init__(self, {
            'uuid': '0002A7D3-D8A4-4FEA-8174-1736E808C066',
            'properties': ['read', 'write', 'notify'],
            'value': None,
            'descriptors': [
                Descriptor({
                    'uuid': '2901',
                    'value': bytes("BPM", 'utf-8')
                }),
                Descriptor({
                    'uuid': '2904',
                    # Presentation Format fields are:
                    # Format      1 octet :  0x04 - unsigned 8-bit value
                    # Exponent    1 octet :  0x00
                    # Unit        2 octets:  0x2700 - unitless
                    # Name Space  1 octet :  0x01 - Bluetooth SIG
                    # Description 2 octets:  0x0000 - blank
                    'value': struct.pack("<BBHBH", 0x04, 0x00,
                                         0x2700, 0x01, 0x0000)
                })
            ]
        })

        self.updateValueCallback = None

        self.lampi_state = lampi_state
        self.lampi_state.on("bpmChange", self.handle_bpm_change)

    def onReadRequest(self, offset, callback):
        if offset:
            callback(Characteristic.RESULT_ATTR_NOT_LONG, None)
        else:
            data = struct.pack("<B", int(self.lampi_state.bpm * 255 / self.MAX_BPM))
            callback(Characteristic.RESULT_SUCCESS, data)

    def onWriteRequest(self, data, offset, withoutResponse, callback):
        if offset:
            callback(Characteristic.RESULT_ATTR_NOT_LONG)

        elif len(data) != 1:
            callback(Characteristic.RESULT_INVALID_ATTRIBUTE_LENGTH)

        else:
            new_bpm = data[0]
            print(f"New BPM: {new_bpm}")

            self.lampi_state.set_bpm(new_bpm)
            callback(Characteristic.RESULT_SUCCESS)

    def handle_bpm_change(self, newValue):
        print(f"Handling bpm change: {newValue}")
        if self.updateValueCallback:
            data = struct.pack("<B", int(self.lampi_state.bpm * 255 / self.MAX_BPM))
            self.updateValueCallback(data)
