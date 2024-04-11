#! /usr/bin/env python3
from paho.mqtt.client import Client
import json
import time

MAX_NUMBER = 0xff

# MQTT constants
MQTT_CLIENT_ID = "demo_bt"
MQTT_BROKER_HOST = "localhost"
MQTT_BROKER_PORT = 1883
MQTT_BROKER_KEEP_ALIVE_SECS = 60
TOPIC_NUMBER_NOTIFICATION = 'number/changed'
TOPIC_NUMBER_SET = 'number/set'


class NumberMQTTService:

    def __init__(self):
        self._number = 0

        self._setup_mqtt()

    def _setup_mqtt(self):
        self.mqtt = Client(client_id=MQTT_CLIENT_ID)
        self.mqtt.on_connect = self._on_mqtt_connect
        self.mqtt.connect(MQTT_BROKER_HOST, port=MQTT_BROKER_PORT,
                          keepalive=MQTT_BROKER_KEEP_ALIVE_SECS)
        self.mqtt.loop_start()

    def _on_mqtt_connect(self, client, userdata, flags, rc):
        self.mqtt.message_callback_add(TOPIC_NUMBER_SET,
                                       self._receive_new_number_request)
        self.mqtt.subscribe(TOPIC_NUMBER_SET, qos=1)

    def _receive_new_number_request(self, client, userdata, message):
        new_state = json.loads(message.payload.decode('utf-8'))
        if new_state['number'] <= MAX_NUMBER:
            self._number = new_state['number']
        else:
            print(f"Received {new_state['number']} too large!")

    def _publish_number_state(self):
        msg = {'number': self._number}
        self.mqtt.publish(TOPIC_NUMBER_NOTIFICATION,
                          json.dumps(msg).encode('utf-8'), qos=1)

    @property
    def number(self):
        return self._number

    @number.setter
    def number(self, new_value):
        if new_value != self._number:
            if new_value >= 0xff:
                new_value = 0
            self._number = new_value
            # publish updated value
            self._publish_number_state()


def main():
    number_service = NumberMQTTService()

    while True:
        number_service.number = number_service.number + 1
        time.sleep(1)


if __name__ == "__main__":
    main()
