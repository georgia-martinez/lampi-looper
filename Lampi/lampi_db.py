#!/usr/bin/env python3

import time
import json
import paho.mqtt.client as mqtt
import shelve

from lampi_common import *

MQTT_CLIENT_ID = "lampi_db"
MAX_STARTUP_WAIT_SECS = 10.0


class LampiDB(object):
    def __init__(self):
        self.setup_db()
        self.client = self.create_client()

    def setup_db(self):
        self.db = shelve.open("lampi_state", writeback=True)

        if "loop" not in self.db:
            self.db["loop"] = [0 for _ in range(16)]

        if "bpm" not in self.db:
            self.db["bpm"] = 100

        self.db.sync()

    def create_client(self):
        client = mqtt.Client(client_id=MQTT_CLIENT_ID, protocol=MQTT_VERSION)
        client.enable_logger()
        client.on_connect = self.on_connect

        client.message_callback_add(TOPIC_UI_UPDATE, self.update_db)

        return client

    def serve(self):
        start_time = time.time()
        while True:
            try:
                self.client.connect(MQTT_BROKER_HOST,
                                     port=MQTT_BROKER_PORT,
                                     keepalive=MQTT_BROKER_KEEP_ALIVE_SECS)
                print("Connnected to broker")
                break

            except ConnectionRefusedError as e:
                current_time = time.time()
                delay = current_time - start_time

                if (delay) < MAX_STARTUP_WAIT_SECS:
                    print("Error connecting to broker; delaying and "
                          "will retry; delay={:.0f}".format(delay))
                    time.sleep(1)
                else:
                    raise e

        self.client.loop_forever()

    def on_connect(self, client, userdata, rc, unknown):
        self.client.subscribe(TOPIC_UI_UPDATE, qos=0)
        self.publish_state_change()

    def update_db(self, client, userdata, msg):
        msg = json.loads(msg.payload.decode('utf-8'))

        if msg["client"] == MQTT_CLIENT_ID:
            return

        self.db["loop"] = msg["loop"]
        self.db["bpm"] = msg["bpm"]

        self.db.sync()

    def publish_state_change(self):
        msg = {
            "client": MQTT_CLIENT_ID, 
            "loop": self.db["loop"], 
            "bpm": int(self.db["bpm"])
        }

        self.client.publish(TOPIC_UI_UPDATE, json.dumps(msg).encode('utf-8'), qos=1, retain=True)

if __name__ == "__main__":
    lampi_db = LampiDB().serve()
