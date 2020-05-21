#!/usr/local/bin/python3
# coding: utf-8

from . import DOMAIN

from homeassistant.components.light import (
    ATTR_RGB_COLOR,
    ATTR_HS_COLOR,
    SUPPORT_COLOR,
    Light
)

async def async_setup_entry(hass, config_entry, async_add_entities):
    kettler = hass.data[DOMAIN]["kettler"]
    if kettler._type == 1:
        async_add_entities([RedmondLight(kettler)], True)

class RedmondLight(Light):

    def __init__(self, kettler):
        self._name = 'Light ' + kettler._name
        self._hs = (0,0)
        self._icon = 'mdi:lightbulb'
        self._kettler = kettler
        self._hs = self._kettler.rgbhex_to_hs(self._kettler._rgb1)

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
    def is_on(self):
        if self._kettler._status == '02' and self._kettler._mode == '03':
            return True
        return False

    @property
    def available(self):
        return self._kettler._connected

    @property
    def hs_color(self):
        return self._kettler.rgbhex_to_hs(self._kettler._rgb1)

    @property
    def supported_features(self):
        return SUPPORT_COLOR

    async def async_turn_on(self, **kwargs):
        if ATTR_HS_COLOR in kwargs:
            self._hs = kwargs[ATTR_HS_COLOR]
        self._kettler._rgb1 = self._kettler.hs_to_rgbhex(self._hs)
        await self._kettler.async_startNightColor()

    async def async_turn_off(self, **kwargs):
        await self._kettler.async_modeOff()

    @property
    def unique_id(self):
        return f'{DOMAIN}[{self._kettler._mac}][{self._name}]'
