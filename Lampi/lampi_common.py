import paho.mqtt.client
from enum import Enum

class Color(Enum):
    GRAY = (0.5, 0.5, 0.5, 1)
    BLUE = (0, 0, 1, 1)
    GREEN = (0, 1, 0, 1)
    RED = (1, 0, 0, 1)

    def id(self):
        return list(Color).index(self)

    @classmethod
    def get_color(cls, color_id):
        return list(cls)[color_id]

DEVICE_ID_FILENAME = '/sys/class/net/eth0/address'

# MQTT Topic Names
TOPIC_UI_UPDATE = "ui_update"

# MQTT Broker Connection info
MQTT_VERSION = paho.mqtt.client.MQTTv311
MQTT_BROKER_HOST = "localhost"
MQTT_BROKER_PORT = 1883
MQTT_BROKER_KEEP_ALIVE_SECS = 60