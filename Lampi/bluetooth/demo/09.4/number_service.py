from pybleno import BlenoPrimaryService, Characteristic, Descriptor
from number_state import NumberState
import struct


class NumberCharacteristic(Characteristic):
    def __init__(self, number_state):
        Characteristic.__init__(self, {
            'uuid': '7a4b0001-999f-4717-b63a-066e06971f59',
            'properties': ['read', 'write', 'notify'],
            'value': None,
            'descriptors': [
                Descriptor({
                    'uuid': '2901',
                    'value': bytes("Some Number", 'utf-8')
                }),
                Descriptor({
                    'uuid': '2904',
                    # Presentation Format fields are:
                    # Format      1 octet :  0x04 - unsigned 8-bit integer
                    # Exponent    1 octet :  0x00
                    # Unit        2 octets:  0x2700 - unitless
                    # Name Space  1 octet :  0x01 - Bluetooth SIG
                    # Description 2 octets:  0x0000 - blank
                    'value': struct.pack("<BBHBH", 0x01, 0x00,
                                         0x2700, 0x01, 0x0000)
                })

            ]
        })
        self.number_state = number_state
        self.updateValueCallback = None
        self.number_state.on('numberChange', self.handle_number_change)

    def _encode_some_number(self):
        return struct.pack("<B", self.number_state.number)

    def onReadRequest(self, offset, callback):
        if offset:
            callback(Characteristic.RESULT_ATTR_NOT_LONG, None)
        else:
            data = self._encode_some_number()
            callback(Characteristic.RESULT_SUCCESS, data)

    def onWriteRequest(self, data, offset, withoutResponse, callback):
        if offset:
            callback(Characteristic.RESULT_ATTR_NOT_LONG)
        elif len(data) != 1:
            callback(Characteristic.RESULT_INVALID_ATTRIBUTE_LENGTH)
        else:
            print(f'Writing SomeNumber {data}')
            self.number_state.number = struct.unpack("<B", data)[0]
            callback(Characteristic.RESULT_SUCCESS)

    def handle_number_change(self, newValue):
        print("Handling SomeNumber change")
        if self.updateValueCallback:
            data = self._encode_some_number()
            self.updateValueCallback(data)


class SomeNumberService(BlenoPrimaryService):
    uuid = '7a4bbfe6-999f-4717-b63a-066e06971f59'

    def __init__(self):
        self.number_state = NumberState()

        BlenoPrimaryService.__init__(self, {
            'uuid': self.uuid,
            'characteristics': [
                NumberCharacteristic(self.number_state)
            ]
        })
