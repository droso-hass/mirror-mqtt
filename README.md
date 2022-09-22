# MQTT mir:ror service

This service allows to connect your Violet [mir:ror](https://fr.wikipedia.org/wiki/Mir:ror) to Home-Assistant.

It provides a MQTT tag scanner, a binary sensor indicating the position of the mir:ror and a switch to connect/disconnect the mir:ror (using uhubctl).

MQTT discovery is fully supported, so you just need to start the service for the devices to appear in home-assistant.

## Installation

### Using docker-compose
- Get the docker-compose file of this repo
- Run `docker-compose up -d`

### Using docker
- The image is available [here](https://github.com/droso-hass/mirror-mqtt/pkgs/container/mirror-mqtt)
- Run `docker run -d --device /dev/hidraw0 -e MIRROR_MQTT_HOST="192.168.1.x" --privileged ghcr.io/droso-hass/mirror-mqtt`

### Directly
- Install python3, pip and uhubctl
- Run `pip3 install -r requirements.txt`
- Edit the configurations variables at the top of the file and run `python3 mirror.py`


## Configuration

|Env Var|Variable|Default|Description|
|--|--|--|--|
|MIRROR_ID|ID|mirror1|Unique ID for your mirror|
|MIRROR_USB_HUB|USB_HUB|1-1|id of the usb hub to control|
|MIRROR_USB_PORT|USB_PORT|2|the port on the usb hub to control|
|MIRROR_MQTT_HOST|MQTT_HOST|127.0.0.1|Address of your MQTT server|
|MIRROR_MQTT_PORT|MQTT_PORT|1883|Port of your MQTT server|

## MQTT Topics

|Topic|Messages|Description|
|--|--|--|
|mirror/MIRROR_ID/tag/scan|the id of the scanned tag|fired when a tag is placed on the mir:ror|
|mirror/MIRROR_ID/usb/state|ON/OFF|the status of the usb port (if the mir:ror is connected or not)|
|mirror/MIRROR_ID/usb/set|ON/OFF|to set the status of the usb port|
|mirror/MIRROR_ID/mirror|ON/OFF|the status of the mir:ror (returned or not)|