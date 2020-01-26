#!/usr/local/bin/python3
# coding: utf-8

from . import DOMAIN
from homeassistant.components.switch import SwitchDevice



async def async_setup_platform(hass, config, async_add_entities, discovery_info=None) -> None:

    if discovery_info is None:
        return

    kettler = hass.data[DOMAIN]["kettler"]
    async_add_entities([RedmondSwitch(kettler)])





class RedmondSwitch(SwitchDevice):

    def __init__(self, kettler):
        self._name = 'redmondusebacklight'
        self._icon = 'mdi:globe-light'
        self._kettler = kettler



    @property
    def name(self):
        return self._name

    @property
    def icon(self):
        return self._icon

    @property
    def is_on(self):
        if self._kettler._usebacklight:
            return True
        else:
            return False

    async def async_turn_on(self, **kwargs):
        self._kettler._usebacklight = True
        await self._kettler.modeUpdate()

    async def async_turn_off(self, **kwargs):
        self._kettler._usebacklight = False
        await self._kettler.modeUpdate()
