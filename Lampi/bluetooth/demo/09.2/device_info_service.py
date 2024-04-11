from pybleno import BlenoPrimaryService, Characteristic, Descriptor
import struct


class DeviceInfoService(BlenoPrimaryService):
    uuid = '180a'

    def __init__(self, manufacturer, model, serial):
        BlenoPrimaryService.__init__(self, {
            'uuid': self.uuid,
            'characteristics': [
            ]
        })
