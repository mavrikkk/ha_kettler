#!/usr/local/bin/python3
# coding: utf-8

from . import DOMAIN
from homeassistant.helpers.entity import Entity

async def async_setup_entry(hass, config_entry, async_add_entities):
    kettler = hass.data[DOMAIN]["kettler"]
    async_add_entities([RedmondSensor(kettler)], True)

class RedmondSensor(Entity):

    def __init__(self, kettler):
        self._name = 'Sensor ' + kettler._name
        self._icon = 'mdi:sync'
        self._kettler = kettler

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
    def state(self) -> str:
        return self._kettler._time_upd

    @property
    def unique_id(self):
        return f'{DOMAIN}[{self._kettler._mac}][{self._name}]'
