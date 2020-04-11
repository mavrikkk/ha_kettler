#!/usr/local/bin/python3
# coding: utf-8

from . import DOMAIN

from homeassistant.components.water_heater import (
    WaterHeaterDevice,
    SUPPORT_TARGET_TEMPERATURE,
    SUPPORT_OPERATION_MODE,
    STATE_ELECTRIC,
    ATTR_TEMPERATURE
)
from homeassistant.const import (
    STATE_UNKNOWN,
    STATE_OFF,
    TEMP_CELSIUS
)

OPERATION_LIST = [STATE_OFF, STATE_ELECTRIC]
SUPPORT_FLAGS_HEATER = (SUPPORT_TARGET_TEMPERATURE | SUPPORT_OPERATION_MODE)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Setup sensor platform."""
    kettler = hass.data[DOMAIN]["kettler"]

    async_add_entities([RedmondWaterHeater(kettler)], True)


class RedmondWaterHeater(WaterHeaterDevice):

    def __init__(self, kettler):
        self._name = 'Kettle'
        self._icon = 'mdi:kettle'
        self._kettler = kettler

    @property
    def device_info(self):
        return {
            "connections": {
                ("mac", self._kettler._mac)
            }
        }

    ### for HASS
    @property
    def supported_features(self):
        return SUPPORT_FLAGS_HEATER

    @property
    def available(self):
        return self._kettler._connected

    @property
    def temperature_unit(self):
        return TEMP_CELSIUS

    @property
    def current_temperature(self):
        return self._kettler._temp

    @property
    def target_temperature(self):
        return self._kettler._tgtemp

    @property
    def target_temperature_step(self):
        return 5

    @property
    def current_operation(self):
        if self._kettler._mode == '00' or self._kettler._mode == '01':
            if self._kettler._status == '02':
                return STATE_ELECTRIC
        return STATE_OFF

    @property
    def operation_list(self):
        return OPERATION_LIST

    async def async_set_operation_mode(self, operation_mode):
        lightIsOn = self._kettler.theLightIsOn()
        if operation_mode == STATE_ELECTRIC:
            if self._kettler._temp is None:
                return
            if self._kettler._tgtemp is None:
                return
            if self._kettler._tgtemp == 100:
                if lightIsOn:
                    await self._kettler.stopNightColor()
                await self._kettler.modeOn()
            else:
                if lightIsOn:
                    await self._kettler.stopNightColor()
                await self._kettler.modeOn("01", self._kettler.decToHex(self._kettler._tgtemp))
        elif operation_mode == STATE_OFF:
            await self._kettler.modeOff()

    async def async_set_temperature(self, **kwargs):
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is None:
            return
        self._kettler._tgtemp = temperature
        await self.async_set_operation_mode(STATE_ELECTRIC)

    @property
    def min_temp(self):
        return self._kettler._mntemp

    @property
    def max_temp(self):
        return self._kettler._mxtemp

    @property
    def name(self):
        return self._name

    @property
    def icon(self):
        return self._icon

    @property
    def unique_id(self):
        return f'{DOMAIN}[{self._kettler._mac}][{self._name}]'
