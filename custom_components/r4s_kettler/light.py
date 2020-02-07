#!/usr/local/bin/python3
# coding: utf-8

from . import DOMAIN
from homeassistant.components.light import (ATTR_RGB_COLOR, ATTR_HS_COLOR, SUPPORT_COLOR, Light, )



async def async_setup_platform(hass, config, async_add_entities, discovery_info=None) -> None:

    if discovery_info is None:
        return

    kettler = hass.data[DOMAIN]["kettler"]
    async_add_entities([RedmondLight(kettler)])





class RedmondLight(Light):

    def __init__(self, kettler):
        self._name = 'redmondlight'
        self._hs = (0,0)
        self._icon = 'mdi:lightbulb'
        self._kettler = kettler
        self._hs = self._kettler.rgbhex_to_hs(self._kettler._rgb1)

    @property
    def name(self):
        return self._name

    @property
    def icon(self):
        return self._icon

    @property
    def is_on(self):
        return self._kettler.theLightIsOn()

    @property
    def available(self):
        return self._kettler._connected

    @property
    def hs_color(self):
        return self._hs

    @property
    def supported_features(self):
        return SUPPORT_COLOR

    async def async_turn_on(self, **kwargs):
        if ATTR_HS_COLOR in kwargs:
            self._hs = kwargs[ATTR_HS_COLOR]
        self._kettler._rgb1 = self._kettler.hs_to_rgbhex(self._hs)
        if self._kettler.theKettlerIsOn():
            await self._kettler.modeOff()
        await self._kettler.startNightColor()

    async def async_turn_off(self, **kwargs):
        await self._kettler.stopNightColor()
