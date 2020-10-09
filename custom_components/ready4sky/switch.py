#!/usr/local/bin/python3
# coding: utf-8

from . import DOMAIN

from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.dispatcher import async_dispatcher_connect



async def async_setup_entry(hass, config_entry, async_add_entities):
    kettler = hass.data[DOMAIN]["kettler"]
    if kettler._type == 4:
        async_add_entities([RedmondSwitch(kettler)], True)

class RedmondSwitch(SwitchEntity):

    def __init__(self, kettler):
        self._name = 'Switch ' + kettler._name
        self._icon = 'mdi:lightbulb'
        self._kettler = kettler
        self._ison = False



    async def async_added_to_hass(self):
        self._handle_update()
        self.async_on_remove(async_dispatcher_connect(self._kettler.hass, 'ready4skyupdate', self._handle_update))

    def _handle_update(self):
        self._ison = False
        if self._kettler._status == '02' and self._kettler._mode == '03':
            self._ison = True
        self.schedule_update_ha_state()

    @property
    def device_info(self):
        return {
            "connections": {
                ("mac", self._kettler._mac)
            }
        }

    @property
    def should_poll(self):
        return False

    @property
    def name(self):
        return self._name

    @property
    def icon(self):
        return self._icon

    @property
    def is_on(self):
        return self._ison

    @property
    def available(self):
        return True

    async def async_turn_on(self, **kwargs):
        await self._kettler.async_modeOn()

    async def async_turn_off(self, **kwargs):
        await self._kettler.async_modeOff()

    @property
    def unique_id(self):
        return f'{DOMAIN}[{self._kettler._mac}][{self._name}]'
