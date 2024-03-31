#!/usr/bin/env python3
import time
import json
import pigpio
import paho.mqtt.client as mqtt
import shelve
import colorsys

from lampi_common import *

MQTT_CLIENT_ID = "lamp_service"
FP_DIGITS = 2
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

        self._setup_db()
        self._client = self._create_broker_client()

    def _setup_db(self):
        self.db = shelve.open("lampi_state", writeback=True)

    def _create_broker_client(self):
        client = mqtt.Client(client_id=MQTT_CLIENT_ID, protocol=MQTT_VERSION)
        # client.will_set(client_state_topic(MQTT_CLIENT_ID), "0",
        #                 qos=2, retain=True)
        client.enable_logger()
        client.on_connect = self.on_connect
        client.message_callback_add(TOPIC_LED_UPDATE, self.on_message_set_config)
        client.on_message = self.default_on_message
        return client

    def serve(self):
        start_time = time.time()
        while True:
            try:
                self._client.connect(MQTT_BROKER_HOST,
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
        self._client.loop_forever()

    def on_connect(self, client, userdata, rc, unknown):
        self._client.subscribe(TOPIC_LED_UPDATE, qos=1)
        self._client.subscribe(TOPIC_UI_UPDATE, qos=1)

    def default_on_message(self, client, userdata, msg):
        print("Received unexpected message on topic " +
              msg.topic + " with payload '" + str(msg.payload) + "'")

    def on_message_set_config(self, client, userdata, msg):
        msg = json.loads(msg.payload.decode('utf-8'))
        self.lampi_driver.change_color(msg["r"], msg["g"], msg["b"])

if __name__ == "__main__":
    lampi = LampiService().serve()
