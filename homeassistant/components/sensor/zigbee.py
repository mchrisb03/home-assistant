"""
homeassistant.components.sensor.zigbee
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Contains functionality to use a ZigBee device as a sensor.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/sensor.zigbee/

"""
import logging
from binascii import hexlify

from homeassistant.core import JobPriority
from homeassistant.const import TEMP_CELCIUS
from homeassistant.helpers.entity import Entity
from homeassistant.components import zigbee


DEPENDENCIES = ["zigbee"]
_LOGGER = logging.getLogger(__name__)


def setup_platform(hass, config, add_entities, discovery_info=None):
    """
    Uses the 'type' config value to work out which type of ZigBee sensor we're
    dealing with and instantiates the relevant classes to handle it.
    """
    typ = config.get("type", "").lower()
    if not typ:
        _LOGGER.exception(
            "Must include 'type' when configuring a ZigBee sensor.")
        return
    try:
        sensor_class, config_class = TYPE_CLASSES[typ]
    except KeyError:
        _LOGGER.exception("Unknown ZigBee sensor type: %s", typ)
        return
    add_entities([sensor_class(hass, config_class(config))])


class ZigBeeTemperatureSensor(Entity):
    """ Allows usage of an XBee Pro as a temperature sensor. """
    def __init__(self, hass, config):
        self._config = config
        self._temp = None
        # Get initial state
        hass.pool.add_job(
            JobPriority.EVENT_STATE, (self.update_ha_state, True))

    @property
    def name(self):
        return self._config.name

    @property
    def state(self):
        return self._temp

    @property
    def unit_of_measurement(self):
        return TEMP_CELCIUS

    def update(self, *args):
        try:
            self._temp = zigbee.DEVICE.get_temperature(self._config.address)
        except zigbee.ZIGBEE_TX_FAILURE:
            _LOGGER.warning(
                "Transmission failure when attempting to get sample from "
                "ZigBee device at address: %s", hexlify(self._config.address))
        except zigbee.ZIGBEE_EXCEPTION as exc:
            _LOGGER.exception(
                "Unable to get sample from ZigBee device: %s", exc)


# This must be below the classes to which it refers.
TYPE_CLASSES = {
    "temperature": (ZigBeeTemperatureSensor, zigbee.ZigBeeConfig),
    "analog": (zigbee.ZigBeeAnalogIn, zigbee.ZigBeeAnalogInConfig)
}
