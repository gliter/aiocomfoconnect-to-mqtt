import asyncio
import logging
import os
import sys
import time

from aiocomfoconnect.const import VentilationSpeed, VentilationTemperatureProfile

LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
logger = logging.getLogger('aiocomfoconnect-to-mqtt')
logger.setLevel(LOGLEVEL)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

from aiocomfoconnect import discover_bridges, ComfoConnect
from aiocomfoconnect.__main__ import run_register
from aiocomfoconnect.sensors import SENSORS

from gmqtt import Client as MQTTClient
from gmqtt.mqtt.constants import MQTTv311

COMFO_HOST = os.environ.get('COMFO_HOST')
COMFO_PIN = int(os.environ.get('COMFO_PIN'))
COMFO_APP_ID = os.environ.get('COMFO_APP_ID', "aiocomfoconnect-to-mqtt")
COMFO_APP_UUID = os.environ.get('COMFO_APP_UUID', "00000000000000000000000000001337")

MQTT_CLIENT_ID = os.environ.get('MQTT_CLIENT_ID', "aiocomfoconnect-to-mqtt")
MQTT_HOST = os.environ.get('MQTT_HOST', '127.0.0.1')
MQTT_PORT = int(os.environ.get('MQTT_PORT', 1883))

MQTT_STATS_TOPIC = os.environ.get('MQTT_STATS_TOPIC', 'stat/aeris')
MQTT_CMD_TOPIC = os.environ.get('MQTT_CMD_TOPIC', 'cmnd/aeris')

STOP = asyncio.Event()

SENSOR_TO_CHANNEL = {
    sensor.name: f"{MQTT_STATS_TOPIC}/{sensor.name.lower().replace('_', '-').replace('?', '').replace('(', '').replace(')', '').strip().replace(' ', '-')}"
    for sensor in SENSORS.values()
}


def ask_exit(*args):
    STOP.set()


def mqtt_on_connect(client, flags, rc, properties):
    logger.info('Connected to MQTT client: %s flags: %s, rc: %s, properties %s', client, flags, rc, properties)


def mqtt_on_disconnect(client, packet, exc=None):
    logger.info('Disconnected from MQTT.')
    exit(1)


def mqtt_on_subscribe(client, mid, qos, properties):
    logger.info('Successfully subscribed client: %s, mid: %s, qos: %s, properties: %s', client, mid, qos, properties)


class Bridge:
    def __init__(self):
        self.mqtt_client = None
        self.comfoconnect : ComfoConnect = None
        self.last_update = None
        self._loop = asyncio.get_running_loop()

        self.speed_map = {
            0: VentilationSpeed.AWAY,
            1: VentilationSpeed.LOW,
            2: VentilationSpeed.MEDIUM,
            3: VentilationSpeed.HIGH,
        }

        self.temperature_profile_map = {
            0: VentilationTemperatureProfile.NORMAL,
            1: VentilationTemperatureProfile.COOL,
            2: VentilationTemperatureProfile.WARM,
        }

        self.cmnd_to_function_mapping = {
            # auto / manual
            MQTT_CMD_TOPIC + '/mode': lambda value: self.get_comfoconnect().set_mode(value),
            # 0 - away / 1 - low / 2 - medium / 3 - high
            MQTT_CMD_TOPIC + '/speed': lambda value: self.get_comfoconnect().set_speed(self.speed_map[int(value)]),
            # auto / off
            MQTT_CMD_TOPIC + '/comfocool': lambda value: self.get_comfoconnect().set_comfocool_mode(value),
            # 0 - normal / 1 - cool / 2 - warm
            MQTT_CMD_TOPIC + '/temperature-profile': lambda value: self.get_comfoconnect().set_temperature_profile(self.temperature_profile_map[int(value)]),
            # seconds
            MQTT_CMD_TOPIC + '/bypass': lambda value: self.get_comfoconnect().set_bypass('auto' if int(value) == 0 else 'on', int(value)),
            # seconds
            MQTT_CMD_TOPIC + '/boost': lambda value: self.get_comfoconnect().set_boost(False if int(value) == 0 else True, int(value)),
        }

    async def connect_to_mqtt(self):
        self.mqtt_client = MQTTClient("client-id")
        self.mqtt_client.on_connect = mqtt_on_connect
        self.mqtt_client.on_disconnect = mqtt_on_disconnect
        self.mqtt_client.on_subscribe = mqtt_on_subscribe
        await self.mqtt_client.connect(host=MQTT_HOST, port=MQTT_PORT, version=MQTTv311)

        async def mqtt_on_message(client, topic, payload, qos, properties):
            decoded_payload = payload.decode()
            logger.info('Received MQTT msg. Topic: %s, payload: %s', topic, decoded_payload)
            await self.cmnd_to_function_mapping[topic](decoded_payload)

        self.mqtt_client.on_message = mqtt_on_message

    async def register_to_comfo(self):
        bridges = await discover_bridges(host=COMFO_HOST)
        if len(bridges) == 0:
            logger.error("Could not found ComfoConnect using IP %s", COMFO_HOST)
        logger.info('Discovered bridges %s', bridges)
        bridge = bridges[0]

        await run_register(host=COMFO_HOST, uuid=COMFO_APP_UUID, name=COMFO_APP_ID, pin=COMFO_PIN)

        self.bridge_uid = bridge.uuid

    async def connect_to_comfo(self):

        def sensor_callback(sensor, value):
            self.last_update = time.time()
            channel = SENSOR_TO_CHANNEL[sensor.name]
            logger.debug("Received update from sensor: %s value %s. Sending to channel %s", sensor.name, value, channel)
            if value != 0 or not (channel.endswith('air-temperature') or channel.endswith('humidity')):
                self.mqtt_client.publish(channel, value)

        self.comfoconnect = ComfoConnect(COMFO_HOST, self.bridge_uid, sensor_callback=sensor_callback, sensor_delay=5)
        await self.comfoconnect.connect(COMFO_APP_UUID)

        logger.info("Connected to comfoconnect %s", self.comfoconnect)

        for key in SENSORS:
            await self.comfoconnect.register_sensor(SENSORS[key])

        for topic in  self.cmnd_to_function_mapping.keys():
            logger.info('Subscribing to MQTT topic %s', topic)
            self.mqtt_client.subscribe(topic, qos=0)

    async def disconnect_from_comfo(self):
        await self.comfoconnect.disconnect()

    async def start_reconnect_loop(self):
        async def _reconnect_loop():
            while True:
                last_update_delta = (time.time() - self.last_update) if self.last_update is not None else 'Unknown'
                logger.info("Seconds since last update %s", last_update_delta)
                logger.info("Is connected? %s", self.get_comfoconnect().is_connected())
                await asyncio.sleep(10)
                try:
                    await self.get_comfoconnect().cmd_time_request()
                except Exception as e:
                    logger.error("Error whiele sending keepalive %s", e)
                if self.last_update and time.time() - self.last_update > 15:
                    logger.warning('No update since %s. Reconnecting', last_update_delta)
                    try:
                        await self.disconnect_from_comfo()
                    except Exception as e:
                        logger.error("Error while disconnecting. %s", e)
                    try:
                        await self.connect_to_comfo()
                    except Exception as e:
                        logger.error("Error while reconnecting. %s", e)

        await self._loop.create_task(_reconnect_loop())

    def get_comfoconnect(self):
        return self.comfoconnect


async def main():
    bridge = Bridge()

    await bridge.register_to_comfo()
    await bridge.connect_to_mqtt()
    await bridge.connect_to_comfo()

    await bridge.start_reconnect_loop()

    await STOP.wait()
    await bridge.mqtt_client.disconnect()
    await bridge.comfoconnect.disconnect()


if __name__ == "__main__":


    logger.info('Sensor to channel mapping: %s', SENSOR_TO_CHANNEL)

    asyncio.run(main())
