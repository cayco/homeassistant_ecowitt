"""Support for Ecowitt Weather Stations."""
import logging
import homeassistant.util.dt as dt_util

from . import EcowittEntity, async_add_ecowitt_entities
from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from .const import (
    DOMAIN,
    TYPE_SENSOR,
    SENSOR_TYPES,
    REG_ENTITIES,
    NEW_ENTITIES,
    SIGNAL_ADD_ENTITIES,
)

from homeassistant.const import (
    STATE_UNKNOWN,
    DEVICE_CLASS_TIMESTAMP,
    DEVICE_CLASS_BATTERY,
    PERCENTAGE,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Add sensors if new."""

    _LOGGER.warning("called async_setup_entry in sensor")

    def add_entities(discovery_info=None):
        _LOGGER.warning("called add_entities in sensor")
        _LOGGER.warning(discovery_info)
        async_add_ecowitt_entities(hass, entry, EcowittSensor,
                                   SENSOR_DOMAIN, async_add_entities,
                                   discovery_info)

    signal = f"{SIGNAL_ADD_ENTITIES}_{SENSOR_DOMAIN}"
    async_dispatcher_connect(hass, signal, add_entities)
    add_entities(hass.data[DOMAIN][entry.entry_id][REG_ENTITIES][TYPE_SENSOR])


class EcowittSensor(EcowittEntity):

    def __init__(self, hass, entry, key, name, dc, uom, icon):
        """Initialize the sensor."""
        super().__init__(hass, entry, key, name)
        self._icon = icon
        self._uom = uom
        self._dc = dc

    @property
    def state(self):
        """Return the state of the sensor."""
        _LOGGER.warning("sensor: request for " + self._key)
        if self._key in self._ws.last_values:
            # The lightning time is reported in UTC, hooray.
            if self._dc == DEVICE_CLASS_TIMESTAMP:
                return dt_util.as_local(
                    dt_util.utc_from_timestamp(self._ws.last_values[self._key])
                ).isoformat()
            if self._dc == DEVICE_CLASS_BATTERY and self._uom == PERCENTAGE:
                return self._ws.last_values[self._key] * 20.0
            return self._ws.last_values[self._key]
        _LOGGER.warning("Sensor %s not in last update, check range or battery",
                        self._key)
        return STATE_UNKNOWN

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._uom

    @property
    def icon(self):
        """Return the icon to use in the fronend."""
        return self._icon

    @property
    def device_class(self):
        """Return the device class."""
        return self._dc
