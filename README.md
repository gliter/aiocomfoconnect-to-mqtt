# Aiocomfoconnect to MQTT

This is a bridge between [aicomfoconnect](https://github.com/michaelarnauts/aiocomfoconnect) and MQTT topic.

## Running as script

```shell
export COMFO_HOST=10.0.0.2
export COMFO_PIN=<comfo pin>
export MQTT_HOST=10.0.0.1
python main.py
```

## Building docker image

```shell
docker build -t literg/aiocomfoconnect-to-mqtt:0.1.0 .
```

## Publishing docker image

```shell
docker push literg/aiocomfoconnect-to-mqtt:0.1.0
```

## Running as docker image

```shell
docker run -e COMFO_HOST=10.0.0.2 -e COMFO_PIN=<comfo pin> -e MQTT_HOST=10.0.0.1  literg/aiocomfoconnect-to-mqtt:0.1.0
```

## Sensor channels

Sensors are mapped to MQTT channels that are prepend with `MQTT_STATS_TOPIC = os.environ.get('MQTT_STATS_TOPIC', 'stat/aeris')`

```python
{
  'Device State': 'stat/aeris/device-state',
  'Changing filters': 'stat/aeris/changing-filters',
  'sensor_33': 'stat/aeris/sensor-33',
  'sensor_37': 'stat/aeris/sensor-37',
  'Operating Mode': 'stat/aeris/operating-mode',
  'sensor_53': 'stat/aeris/sensor-53',
  'Supply Fan Mode': 'stat/aeris/supply-fan-mode',
  'Exhaust Fan Mode': 'stat/aeris/exhaust-fan-mode',
  'Fan Speed': 'stat/aeris/fan-speed',
  'Bypass Activation State': 'stat/aeris/bypass-activation-state',
  'Temperature Profile Mode': 'stat/aeris/temperature-profile-mode',
  'Fan Speed Next Change': 'stat/aeris/fan-speed-next-change',
  'Bypass Next Change': 'stat/aeris/bypass-next-change',
  'sensor_85': 'stat/aeris/sensor-85',
  'Supply Fan Next Change': 'stat/aeris/supply-fan-next-change',
  'Exhaust Fan Next Change': 'stat/aeris/exhaust-fan-next-change',
  'Exhaust Fan Duty': 'stat/aeris/exhaust-fan-duty',
  'Supply Fan Duty': 'stat/aeris/supply-fan-duty',
  'Exhaust Fan Flow': 'stat/aeris/exhaust-fan-flow',
  'Supply Fan Flow': 'stat/aeris/supply-fan-flow',
  'Exhaust Fan Speed': 'stat/aeris/exhaust-fan-speed',
  'Supply Fan Speed': 'stat/aeris/supply-fan-speed',
  'Power Usage': 'stat/aeris/power-usage',
  'Power Usage (year)': 'stat/aeris/power-usage-year',
  'Power Usage (total)': 'stat/aeris/power-usage-total',
  'Preheater Power Usage (year)': 'stat/aeris/preheater-power-usage-year',
  'Preheater Power Usage (total)': 'stat/aeris/preheater-power-usage-total',
  'Preheater Power Usage': 'stat/aeris/preheater-power-usage',
  'RF Pairing Mode': 'stat/aeris/rf-pairing-mode',
  'Days remaining to replace the filter': 'stat/aeris/days-remaining-to-replace-the-filter',
  'Device Temperature Unit': 'stat/aeris/device-temperature-unit',
  'Running Mean Outdoor Temperature (RMOT)': 'stat/aeris/running-mean-outdoor-temperature-rmot',
  'Heating Season is active': 'stat/aeris/heating-season-is-active',
  'Cooling Season is active': 'stat/aeris/cooling-season-is-active',
  'Target Temperature': 'stat/aeris/target-temperature',
  'Avoided Heating Power Usage': 'stat/aeris/avoided-heating-power-usage',
  'Avoided Heating Power Usage (year)': 'stat/aeris/avoided-heating-power-usage-year',
  'Avoided Heating Power Usage (total)': 'stat/aeris/avoided-heating-power-usage-total',
  'Avoided Cooling Power Usage': 'stat/aeris/avoided-cooling-power-usage',
  'Avoided Cooling Power Usage (year)': 'stat/aeris/avoided-cooling-power-usage-year',
  'Avoided Cooling Power Usage (total)': 'stat/aeris/avoided-cooling-power-usage-total',
  'sensor_219': 'stat/aeris/sensor-219',
  'Outdoor Air Temperature (?)': 'stat/aeris/outdoor-air-temperature',
  'Supply Air Temperature': 'stat/aeris/supply-air-temperature',
  'Device Airflow Unit': 'stat/aeris/device-airflow-unit',
  'Sensor based ventilation mode': 'stat/aeris/sensor-based-ventilation-mode',
  'Fan Speed (modulated)': 'stat/aeris/fan-speed-modulated',
  'Bypass State': 'stat/aeris/bypass-state',
  'frostprotection_unbalance': 'stat/aeris/frostprotection-unbalance',
  'Airflow constraints': 'stat/aeris/airflow-constraints',
  'Extract Air Temperature': 'stat/aeris/extract-air-temperature',
  'Exhaust Air Temperature': 'stat/aeris/exhaust-air-temperature',
  'Outdoor Air Temperature': 'stat/aeris/outdoor-air-temperature',
  'Supply Air Temperature (?)': 'stat/aeris/supply-air-temperature',
  'Extract Air Humidity': 'stat/aeris/extract-air-humidity',
  'Exhaust Air Humidity': 'stat/aeris/exhaust-air-humidity',
  'Outdoor Air Humidity': 'stat/aeris/outdoor-air-humidity',
  'Outdoor Air Humidity (after preheater)': 'stat/aeris/outdoor-air-humidity-after-preheater',
  'Supply Air Humidity': 'stat/aeris/supply-air-humidity',
  'sensor_321': 'stat/aeris/sensor-321',
  'sensor_325': 'stat/aeris/sensor-325',
  'sensor_337': 'stat/aeris/sensor-337',
  'Bypass Override': 'stat/aeris/bypass-override',
  'sensor_341': 'stat/aeris/sensor-341',
  'Analog Input 1': 'stat/aeris/analog-input-1',
  'Analog Input 2': 'stat/aeris/analog-input-2',
  'Analog Input 3': 'stat/aeris/analog-input-3',
  'Analog Input 4': 'stat/aeris/analog-input-4',
  'sensor_384': 'stat/aeris/sensor-384',
  'sensor_386': 'stat/aeris/sensor-386',
  'sensor_400': 'stat/aeris/sensor-400',
  'sensor_401': 'stat/aeris/sensor-401',
  'sensor_402': 'stat/aeris/sensor-402',
  'ComfoFond Outdoor Air Temperature': 'stat/aeris/comfofond-outdoor-air-temperature',
  'ComfoFond Ground Temperature': 'stat/aeris/comfofond-ground-temperature',
  'ComfoFond GHE State Percentage': 'stat/aeris/comfofond-ghe-state-percentage',
  'ComfoFond GHE Present': 'stat/aeris/comfofond-ghe-present',
  'ComfoCool State': 'stat/aeris/comfocool-state',
  'sensor_785': 'stat/aeris/sensor-785',
  'ComfoCool Condensor Temperature': 'stat/aeris/comfocool-condensor-temperature'
}
```

## Command channels

Available command channels are described here:

```python

MQTT_CMD_TOPIC = os.environ.get('MQTT_CMD_TOPIC', 'cmnd/aeris')

self.cmnd_to_function_mapping = {
# auto / manual
MQTT_CMD_TOPIC + '/mode': lambda value: self.comfoconnect.set_mode(value),
# away / low / medium / high
MQTT_CMD_TOPIC + '/speed': lambda value: self.comfoconnect.set_speed(value),
# auto / off
MQTT_CMD_TOPIC + '/comfocool': lambda value: self.comfoconnect.set_comfocool_mode(value),
# warm / normal / cool
MQTT_CMD_TOPIC + '/temperature-profile': lambda value: self.comfoconnect.set_temperature_profile(value),
# seconds
MQTT_CMD_TOPIC + '/bypass': lambda value: self.comfoconnect.set_bypass('auto' if int(value) == 0 else 'on', int(value)),
# seconds
MQTT_CMD_TOPIC + '/boost': lambda value: self.comfoconnect.set_boost(False if int(value) == 0 else True, int(value)),
}
```

## Dev notes

### Zero value

It sometimes takes longer time to initialize temperature and humidity sensors and 0 would be reported.
As workaround for these sensors 0 value will always be omitted.

### Reconnect

Sometimes we are loosing connection with ComfoNET. `aiocomfoconnect` lib provides no handlers for this.
As workaround, we are periodically checking when was last update to sensor values. If this exceeds 15 seconds
reconnect will be done.