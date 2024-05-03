import paho.mqtt.client
from enum import Enum


class Color(Enum):
    GRAY = (0.5, 0.5, 0.5, 0.4)
    BLUE = (0, 0, 1, 0.7)
    GREEN = (0, 1, 0, 0.7)
    RED = (1, 0, 0, 0.7)

    def id(self):
        return list(Color).index(self)

    @classmethod
    def get_color(cls, color_id):
        return list(cls)[color_id]


class TimeSignature(Enum):
    THREE_FOUR = (3, 4, "3/4")
    FOUR_FOUR = (4, 4, "4/4")
    FIVE_FOUR = (5, 4, "5/4")

    def __init__(self, numerator, denominator, label):
        self._numerator = numerator
        self._denominator = denominator
        self._label = label

    @property
    def numerator(self):
        return self._numerator

    @property
    def denominator(self):
        return self._denominator

    @property
    def label(self):
        return self._label


DEVICE_ID_FILENAME = '/sys/class/net/eth0/address'

# MQTT Topic Names
TOPIC_UI_UPDATE = "ui_update"

# MQTT Broker Connection info
MQTT_VERSION = paho.mqtt.client.MQTTv311
MQTT_BROKER_HOST = "localhost"
MQTT_BROKER_PORT = 1883
MQTT_BROKER_KEEP_ALIVE_SECS = 60
