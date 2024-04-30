from pybleno import Characteristic, Descriptor
from lampi_state import LampiState

import array
import struct


class LoopCharacteristic(Characteristic):
    def __init__(self, lampi_state: LampiState):
        Characteristic.__init__(self, {
            'uuid': '0003A7D3-D8A4-4FEA-8174-1736E808C066',
            'properties': ['read', 'write', 'notify'],
            'value': None,
            'descriptors': [
                Descriptor({
                    'uuid': '2901',
                    'value': "Loop".encode('utf-8')
                }),
            ]
        })

        self.updateValueCallback = None

        self.lampi_state = lampi_state
        self.lampi_state.on("loopChange", self.handle_loop_change)

    def encode_loop(self, array):
        return ''.join([format(x, 'x') for x in array]).encode("utf-8")

    def decode_loop(self, data):
        return data

    def onReadRequest(self, offset, callback):
        if offset:
            callback(Characteristic.RESULT_ATTR_NOT_LONG, None)
        else:
            data = struct.pack("<16B", *self.lampi_state.loop)
            callback(Characteristic.RESULT_SUCCESS, data)

    def onWriteRequest(self, data, offset, withoutResponse, callback):
        new_loop = list(struct.unpack("<16B", data[0]))
        print(f"New loop: {new_loop}")

        self.lampi_state.set_loop(new_loop)
        callback(Characteristic.RESULT_SUCCESS)

    def handle_loop_change(self, newValue):
        print(f"Handling loop change: {newValue}")
        if self.updateValueCallback:
            data = struct.pack("<16B", *self.lampi_state.loop)
            self.updateValueCallback(data)

# endregion
