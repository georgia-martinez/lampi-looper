#!/usr/bin/env python3
import time
import json
import pigpio
import paho.mqtt.client as mqtt
import shelve
import colorsys

from lampi_mixer import LampiMixer
from lampi_common import *

MQTT_CLIENT_ID = "lampi_service"
MAX_STARTUP_WAIT_SECS = 10.0


class LampiDriver(object):
    PIN_R = 19
    PIN_G = 26
    PIN_B = 13
    PINS = [PIN_R, PIN_G, PIN_B]

    def __init__(self):
        self._gpio = pigpio.pi()
        for color_pin in PINS:
            self._gpio.set_mode(color_pin, pigpio.OUTPUT)
            self._gpio.set_PWM_dutycycle(color_pin, 0)
            self._gpio.set_PWM_frequency(color_pin, 1000)
            self._gpio.set_PWM_range(color_pin, 1000)

    def change_color(self, r, g, b):
        self._gpio.write(PIN_R, r)
        self._gpio.write(PIN_G, g)
        self._gpio.write(PIN_B, b)


class LampiService(object):

    def __init__(self):
        self.lampi_driver = LampiDriver()
        self.lampi_driver.change_color(0, 0, 0) # turn off

        self.lampi_mixer = LampiMixer()

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
        # client.will_set(client_state_topic(MQTT_CLIENT_ID), "0",
        #                 qos=2, retain=True)
        client.enable_logger()
        client.on_connect = self.on_connect

        client.message_callback_add(TOPIC_LED_UPDATE, self.change_led_color)
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
        self.client.subscribe(TOPIC_LED_UPDATE, qos=1)
        self.client.subscribe(TOPIC_UI_UPDATE, qos=1)

    def change_led_color(self, client, userdata, msg):
        msg = json.loads(msg.payload.decode('utf-8'))
        self.lampi_driver.change_color(msg["r"], msg["g"], msg["b"])

     def update_db(self, client, userdata, msg):
        msg = json.loads(msg.payload.decode('utf-8'))

        if msg["client"] == MQTT_CLIENT_ID:
            return

        self.db["loop"] = msg["loop"]
        self.db["bpm"] = msg["bpm"]

        self.db.sync()

if __name__ == "__main__":
    lampi = LampiService().serve()
