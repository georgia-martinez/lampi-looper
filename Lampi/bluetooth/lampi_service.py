from pybleno import BlenoPrimaryService
from loop_characteristic import LoopCharacteristic
from bpm_characteristic import BpmCharacteristic

from lampi_state import LampiState


class LampiService(BlenoPrimaryService):
    uuid = '0001A7D3-D8A4-4FEA-8174-1736E808C066'

    def __init__(self):
        self.lampi_state = LampiState()

        BlenoPrimaryService.__init__(self, {
            'uuid': self.uuid,
            'characteristics': [
                BpmCharacteristic(self.lampi_state),
                LoopCharacteristic(self.lampi_state),
            ]
        })
        print("Started Lamp Service")
