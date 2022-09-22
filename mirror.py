#!/usr/local/bin/python3

import binascii
import json
import os
from threading import Thread
import paho.mqtt.client as mqtt

ID = os.environ.get("MIRROR_ID") or "mirror1"
USB_HUB = os.environ.get("MIRROR_USB_HUB") or "1-1"
USB_PORT = os.environ.get("MIRROR_USB_PORT") or "2"
MQTT_HOST = os.environ.get("MIRROR_MQTT_HOST") or "127.0.0.1"
MQTT_PORT = os.environ.get("MIRROR_MQTT_PORT") or 1883

BASE_TOPIC = f"mirror/{ID}"


class Mirror(Thread):
    def __init__(self, group = None, target = None, name = None, daemon = True, mqtt=None) -> None:
        super().__init__()
        self._client = mqtt
        self._running = True

    def run(self):
        self._mirror = open("/dev/hidraw0", "rb")
        while self._running:
            try:
                data = self._mirror.read(16)
            except:
                break
            if data != b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00':
                if data[0] == 2 and data[1] == 1:
                    tag = binascii.hexlify(data)[4:]
                    self._client.publish(BASE_TOPIC+"/tag/scan", tag)
                elif data[0:2] == b'\x01\x04':
                    self._client.publish(BASE_TOPIC+"/mirror", "ON")
                elif data[0:2] == b'\x01\x05':
                    self._client.publish(BASE_TOPIC+"/mirror", "OFF")

    def stop(self):
        self.running = False
        self._mirror.close()

mirror_thread = None

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.publish(f"homeassistant/tag/{ID}/config", json.dumps({"topic": BASE_TOPIC+"/tag/scan"}), retain=True)
    client.publish(f"homeassistant/switch/{ID}/config", json.dumps({"name": ID, "command_topic": BASE_TOPIC+"/usb/set", "state_topic": BASE_TOPIC+"/usb/state"}), retain=True)
    client.publish(f"homeassistant/binary_sensor/{ID}/config", json.dumps({"name": ID, "device_class": "power", "state_topic": BASE_TOPIC+"/mirror"}), retain=True)
    client.subscribe(BASE_TOPIC+"/usb/set")

    os.system(f"uhubctl -a on -p {USB_PORT} -l {USB_HUB}")
    client.publish(BASE_TOPIC+"/usb/state", "ON")
    global mirror_thread
    mirror_thread = Mirror(daemon=True, mqtt=client)
    mirror_thread.start()

def on_message(client, userdata, msg):
    global mirror_thread
    if msg.topic == BASE_TOPIC+"/usb/set":
        if msg.payload == b"ON":
            mirror_thread = Mirror(daemon=True, mqtt=client)
            mirror_thread.start()
            os.system(f"uhubctl -a on -p {USB_PORT} -l {USB_HUB}")
            client.publish(BASE_TOPIC+"/usb/state", "ON")
        else:
            if mirror_thread:
                mirror_thread.stop()
                mirror_thread.join()
            os.system(f"uhubctl -a off -p {USB_PORT} -l {USB_HUB}")
            client.publish(BASE_TOPIC+"/usb/state", "OFF")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_HOST, int(MQTT_PORT), 60)
client.loop_forever()