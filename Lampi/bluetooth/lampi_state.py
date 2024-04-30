from paho.mqtt.client import Client

import json
from collections import defaultdict
from typing import Callable, Optional

TOPIC_UI_UPDATE = "ui_update"

# MQTT_VERSION = paho.mqtt.client.MQTTv311
MQTT_CLIENT_ID = "bluetooth"
MQTT_BROKER_HOST = "localhost"
MQTT_BROKER_PORT = 1883
MQTT_BROKER_KEEP_ALIVE_SECS = 60


def client_state_topic(client_id):
    return 'lamp/connection/{}/state'.format(client_id)


class LampiState():
    def __init__(self):
        self.loop = [0 for _ in range(16)]
        self.bpm = 100

        self._setup_mqtt()

        self.callbacks: Dict[str, List[Callable]] = defaultdict(list)

    def _setup_mqtt(self):
        self.mqtt = Client(client_id=MQTT_CLIENT_ID)
        self.mqtt.enable_logger()
        self.mqtt.will_set(client_state_topic(MQTT_CLIENT_ID), "0", qos=2, retain=True)
        self.mqtt.on_connect = self.on_mqtt_connect
        self.mqtt.connect(MQTT_BROKER_HOST, port=MQTT_BROKER_PORT, keepalive=MQTT_BROKER_KEEP_ALIVE_SECS)
        self.mqtt.loop_start()

    def on(self, event: str, func: Optional[Callable] = None):
        def subscribe(func: Callable):
            if not callable(func):
                raise ValueError("Argument func must be callable.")

            self.callbacks[event].append(func)
            return func

        if func is None:
            return subscribe
            
        subscribe(func)

    def emit(self, event, message):
        for callback in self.callbacks[event]:
            callback(message)

    def set_bpm(self, newBpm):
        if newBpm != self.bpm:
            self.bpm = newBpm
            self.publish_state_change()

    def on_mqtt_connect(self, client, userdata, flags, rc):
        self.mqtt.publish(client_state_topic(MQTT_CLIENT_ID), b"1", qos=2, retain=True)
        self.mqtt.subscribe(TOPIC_UI_UPDATE, qos=1)
        self.mqtt.message_callback_add(TOPIC_UI_UPDATE, self.receive_new_lamp_state)

    def receive_new_lamp_state(self, client, userdata, message):
        new_state = json.loads(message.payload.decode("utf-8"))

        if new_state.get("client", "UNKNOWN") != MQTT_CLIENT_ID:
            print(f"Got new state: {new_state}")

            if new_state["bpm"] != self.bpm:
                self.bpm = new_state["bpm"]
                self.emit("bpmChange", self.bpm)

            # self.loop = new_state.get("loop", [0 for _ in range(16)])
            # self.emit('loopChange', self.loop)

    def publish_state_change(self):
        config = {
            "client": MQTT_CLIENT_ID,
            "loop": self.loop,
            "bpm": self.bpm,
        }

        print(f"Publishing new state: {config}")

        self.mqtt.publish(TOPIC_UI_UPDATE,
                          json.dumps(config).encode('utf-8'), qos=1,
                          retain=True)
