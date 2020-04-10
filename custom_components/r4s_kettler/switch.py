#!/usr/local/bin/python3
# coding: utf-8

from . import DOMAIN
from homeassistant.components.switch import SwitchDevice

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Setup sensor platform."""
    kettler = hass.data[DOMAIN]["kettler"]

    async_add_entities([
        RedmondSwitchAuthorize(kettler),
        RedmondSwitchBacklight(kettler),
        RedmondSwitchHold(kettler)
    ], True)

class RedmondSwitchBacklight(SwitchDevice):

    def __init__(self, kettler):
        self._name = 'redmondusebacklight'
        self._icon = 'mdi:floor-lamp'
        self._kettler = kettler

    @property
    def name(self):
        return self._name

    @property
    def icon(self):
        return self._icon

    @property
    def is_on(self):
        return self._kettler._usebacklight

    @property
    def available(self):
        return self._kettler._connected

    async def async_turn_on(self, **kwargs):
        self._kettler._usebacklight = True
        await self._kettler.modeUpdate()

    async def async_turn_off(self, **kwargs):
        self._kettler._usebacklight = False
        await self._kettler.modeUpdate()

    @property
    def unique_id(self):
        return f'{DOMAIN}[{self._kettler._mac}][{self._name}]'



class RedmondSwitchHold(SwitchDevice):

    def __init__(self, kettler):
        self._name = 'redmondhold'
        self._icon = 'mdi:car-brake-hold'
        self._kettler = kettler

    @property
    def name(self):
        return self._name

    @property
    def icon(self):
        return self._icon

    @property
    def is_on(self):
        return self._kettler._hold

    @property
    def available(self):
        return self._kettler._connected

    async def async_turn_on(self, **kwargs):
        self._kettler._hold = True
        await self._kettler.modeUpdate()

    async def async_turn_off(self, **kwargs):
        self._kettler._hold = False
        await self._kettler.modeUpdate()

    @property
    def unique_id(self):
        return f'{DOMAIN}[{self._kettler._mac}][{self._name}]'




class RedmondSwitchAuthorize(SwitchDevice):

    def __init__(self, kettler):
        self._name = 'redmondauthorize'
        self._icon = 'mdi:bluetooth-connect'
        self._kettler = kettler

    @property
    def name(self):
        return self._name

    @property
    def icon(self):
        return self._icon

    @property
    def is_on(self):
        return self._kettler._connected

    @property
    def available(self):
        return True

    async def async_turn_on(self, **kwargs):
        if not self._kettler._connected:
            await self._kettler.firstConnect()

    async def async_turn_off(self, **kwargs):
        pass

    @property
    def unique_id(self):
        return f'{DOMAIN}[{self._kettler._mac}][{self._name}]'
