#!/usr/local/bin/python3
# coding: utf-8

from . import DOMAIN
from homeassistant.components.light import (ATTR_RGB_COLOR, ATTR_HS_COLOR, SUPPORT_COLOR, Light, )
import homeassistant.util.color as color_util



async def async_setup_platform(hass, config, async_add_entities, discovery_info=None) -> None:

    if discovery_info is None:
        return

    kettler = hass.data[DOMAIN]["kettler"]
    async_add_entities([RedmondLight(kettler)])





class RedmondLight(Light):

    def __init__(self, kettler):
        self._name = 'redmondlight'
        self._icon = 'mdi:floor-lamp'
        self._hs = (0, 0)
        self._kettler = kettler
        self.rgbhex_to_hs()



    def rgbhex_to_hs(self):
        rgbhex = self._kettler._rgb
        rgb = color_util.rgb_hex_to_rgb_list(rgbhex)
        self._hs = color_util.color_RGB_to_hs(*rgb)

    def hs_to_rgbhex(self):
        rgb = color_util.color_hs_to_RGB(*self._hs)
        rgbhex = color_util.color_rgb_to_hex(*rgb)
        return rgbhex

    @property
    def name(self):
        return self._name

    @property
    def icon(self):
        return self._icon

    @property
    def is_on(self):
        if self._kettler._avialible and self._kettler._status == '02' and self._kettler._mode == '03':
            return True
        else:
            return False

    @property
    def hs_color(self):
        return self._hs

    @property
    def supported_features(self):
        return SUPPORT_COLOR

    async def async_turn_on(self, **kwargs):
        if ATTR_HS_COLOR in kwargs:
            self._hs = kwargs[ATTR_HS_COLOR]
        self._kettler._rgb = self.hs_to_rgbhex()
        kettlerIsOn = self._kettler.theKettlerIsOn()
        if kettlerIsOn:
            await self._kettler.modeOff()
        await self._kettler.startNightColor(self._kettler._rgb)

    async def async_turn_off(self, **kwargs):
        await self._kettler.stopNightColor()
