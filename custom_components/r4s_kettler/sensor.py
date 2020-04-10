#!/usr/local/bin/python3
# coding: utf-8

from . import DOMAIN
from homeassistant.helpers.entity import Entity

ATTR_WATTS = 'energy spent'
ATTR_ALLTIME = 'time working'
ATTR_TIMES = 'amount of starts'
ATTR_WATTS_MEASURE = 'kW * h'
ATTR_ALLTIME_MEASURE = 'h'
ATTR_TIMES_MEASURE = 'times'

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Setup sensor platform."""
    kettler = hass.data[DOMAIN]["kettler"]

    async_add_entities([RedmondSensor(kettler)], True)

class RedmondSensor(Entity):

    def __init__(self, kettler):
        self._name = 'redmondsensors'
        self._icon = 'mdi:sync'
        self._kettler = kettler

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
    def device_state_attributes(self):
        attrs = {}
        attrs[ATTR_WATTS] = str(round(self._kettler._Watts/1000, 2)) + " " + ATTR_WATTS_MEASURE
        attrs[ATTR_ALLTIME] = str(self._kettler._alltime) + " " + ATTR_ALLTIME_MEASURE
        attrs[ATTR_TIMES] = str(self._kettler._times) + " " + ATTR_TIMES_MEASURE
        return attrs

    @property
    def state(self) -> str:
        return self._kettler._time_upd

    @property
    def unique_id(self):
        return f'{DOMAIN}[{self._kettler._mac}][{self._name}]'
