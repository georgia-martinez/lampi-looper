from pybleno import BlenoPrimaryService
from on_off_characteristic import OnOffCharacteristic
from hsv_characteristic import HSVCharacteristic
from brightness_characteristic import BrightnessCharacteristic

from lampi_state import LampiState


class LampiService(BlenoPrimaryService):
    uuid = '0001A7D3-D8A4-4FEA-8174-1736E808C066'

    def __init__(self):
        self.lampi_state = LampiState()

        BlenoPrimaryService.__init__(self, {
            'uuid': self.uuid,
            'characteristics': [
                HSVCharacteristic(self.lampi_state),
                BrightnessCharacteristic(self.lampi_state),
                OnOffCharacteristic(self.lampi_state)
            ]
        })
        print("Started Lamp Service")
