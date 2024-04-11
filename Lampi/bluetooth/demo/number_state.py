from paho.mqtt.client import Client
from collections import defaultdict
from typing import Callable, Optional
import json

# MQTT constants
MQTT_CLIENT_ID = "bemo_bt"
MQTT_BROKER_HOST = "localhost"
MQTT_BROKER_PORT = 1883
MQTT_BROKER_KEEP_ALIVE_SECS = 60
TOPIC_NUMBER_NOTIFICATION = 'number/changed'
TOPIC_NUMBER_SET = 'number/set'


class NumberState():
    def __init__(self):
        self._number = 0

        self.callbacks: Dict[str, List[Callable]] = defaultdict(list)

        self._setup_mqtt()

    def _setup_mqtt(self):
        self.mqtt = Client(client_id=MQTT_CLIENT_ID)
        self.mqtt.on_connect = self._on_mqtt_connect
        self.mqtt.connect(MQTT_BROKER_HOST, port=MQTT_BROKER_PORT,
                          keepalive=MQTT_BROKER_KEEP_ALIVE_SECS)
        self.mqtt.loop_start()

    def _on_mqtt_connect(self, client, userdata, flags, rc):
        self.mqtt.message_callback_add(TOPIC_NUMBER_NOTIFICATION,
                                       self._receive_new_number_state)
        self.mqtt.subscribe(TOPIC_NUMBER_NOTIFICATION, qos=1)

    def _receive_new_number_state(self, client, userdata, message):
        new_state = json.loads(message.payload.decode('utf-8'))

        print(f"Got new state: {new_state}")

        if new_state.get('number', 0) != self._number:
            self._number = new_state.get('number', 0)
            self.emit('numberChange', self.number)

    # event handler registration
    def on(self, event: str, func: Optional[Callable] = None):
        def subscribe(func: Callable):
            if not callable(func):
                raise ValueError("Argument func must be callable.")
            self.callbacks[event].append(func)
            return func
        if func is None:
            return subscribe
        subscribe(func)

    # generate (emit) events
    def emit(self, event, message):
        for callback in self.callbacks[event]:
            callback(message)

    @property
    def number(self):
        return self._number

    @number.setter
    def number(self, new_value):
        if new_value != self._number:
            if new_value >= 0xff:
                new_value = 0
            self._number = new_value
            self._publish_state_change()

    def _publish_state_change(self):
        msg = {'number': self._number}
        self.mqtt.publish(TOPIC_NUMBER_SET,
                          json.dumps(msg).encode('utf-8'), qos=1)
