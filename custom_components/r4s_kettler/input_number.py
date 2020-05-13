#!/usr/local/bin/python3
# coding: utf-8

from . import DOMAIN
from homeassistant.components.input_number import (
    MODE_BOX,
    ATTR_INITIAL,
    ATTR_MIN,
    ATTR_MAX,
    ATTR_STEP,
    InputNumber
)
from homeassistant.const import (
    ATTR_EDITABLE,
    ATTR_MODE,
    TEMP_CELSIUS
)

async def async_setup_entry(hass, config_entry, async_add_entities):
    kettler = hass.data[DOMAIN]["kettler"]
#    if kettler._type == 5:
    async_add_entities([RedmondCookTemp(kettler)], True)





class RedmondCookTemp(InputNumber):

    def __init__(self, kettler):
        self._name = 'Set temperature ' + kettler._name
        self._icon = 'mdi:sync'
        self._kettler = kettler
        self.editable = True
        self._current_value = self._kettler._tgtemp

    @property
    def device_info(self):
        return {
            "connections": {
                ("mac", self._kettler._mac)
            }
        }

    @property
    def name(self):
        return self._name

    @property
    def icon(self):
        return self._icon

    @property
    def available(self):
        return self._kettler._connected

    @property
    def unique_id(self):
        return f'{DOMAIN}[{self._kettler._mac}][{self._name}]'

    @property
    def state_attributes(self):
        return {
            ATTR_INITIAL: self._current_value,
            ATTR_EDITABLE: self.editable,
            ATTR_MIN: self._minimum,
            ATTR_MAX: self._maximum,
            ATTR_STEP: self._step,
            ATTR_MODE: MODE_BOX,
        }

    @property
    def state(self):
        return self._kettler._tgtemp

    @property
    def _step(self) -> int:
        return 5

    @property
    def unit_of_measurement(self):
        return TEMP_CELSIUS

    @property
    def _minimum(self) -> float:
        return 30

    @property
    def _maximum(self) -> float:
        return 180

    async def async_increment(self):
        await self.async_set_value(min(self._current_value + self._step, self._maximum))

    async def async_decrement(self):
        await self.async_set_value(max(self._current_value - self._step, self._minimum))

    async def async_set_value(self, value):
        pass
#        num_value = float(value)
#        if num_value < self._minimum:
#            num_value = self._minimum
#        if num_value > self._maximum:
#            num_value = self._maximum
#        self._kettler.modeTempCook(self._kettler.decToHex(num_value))
