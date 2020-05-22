#!/usr/local/bin/python3
# coding: utf-8

from . import DOMAIN
from homeassistant.helpers.entity import Entity



async def async_setup_entry(hass, config_entry, async_add_entities):
    kettler = hass.data[DOMAIN]["kettler"]
    async_add_entities([RedmondSensor(kettler)], True)
    if kettler._type == 5:
#        async_add_entities([RedmondSensorTimer(kettler, True)], True)
#        async_add_entities([RedmondSensorTimer(kettler, False)], True)
        async_add_entities([RedmondCooker(kettler)], True)





class RedmondSensor(Entity):

    def __init__(self, kettler):
        self._name = 'Status ' + kettler._name
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
    def state(self):
        if self._kettler._status == '02':
            if self._kettler._mode == '00':
                return 'BOIL'
            if self._kettler._mode == '01':
                return 'HEAT'
            if self._kettler._mode == '03':
                return 'LIGHT'
        return 'OFF'

    @property
    def device_state_attributes(self):
        attributes = {'sync':str(self._kettler._time_upd)}
        return attributes

    @property
    def unique_id(self):
        return f'{DOMAIN}[{self._kettler._mac}][{self._name}]'





class RedmondSensorTimer(Entity):

    def __init__(self, kettler, current):
        self._icon = 'mdi:timer-outline'
        self._kettler = kettler
        self._curr = current
        if not self._curr:
            self._name = 'prog ' + kettler._name
        else:
            self._name = 'curr' + kettler._name

    @property
    def device_info(self):
        return {
            "connections": {
                ("mac", self._kettler._mac)
            }
        }

    @property
    def name(self):
        if not self._curr:
            return 'Timer prog ' + self._kettler._name
        name1 = 'Timer ' + self._kettler._name
        if self._kettler._status == '05':
            name1 = 'Timer ' + self._kettler._name + ' start in '
        if self._kettler._status == '02' or self._kettler._status == '04':
            name1 = 'Timer ' + self._kettler._name + ' stop in '
        return name1

    @property
    def icon(self):
        return self._icon

    @property
    def available(self):
        return self._kettler._connected

    @property
    def state(self):
        if self._curr:
            hr = self._kettler._th
            mn = self._kettler._tm
        else:
            hr = self._kettler._ph
            mn = self._kettler._pm
        return str(hr) + ':' + str(mn)

    @property
    def unique_id(self):
        return f'{DOMAIN}[{self._kettler._mac}][{self._name}]'





class RedmondCooker(Entity):

    def __init__(self, kettler):
        self._icon = 'mdi:book-open'
        self._kettler = kettler
        self._name = 'Status ' + kettler._name

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
    def state(self):
        if self._kettler._status == '00':
            return 'OFF'
        if self._kettler._status == '01':
            return 'PROGRAM'
        if self._kettler._status == '02':
            return 'ON'
        if self._kettler._status == '04':
            return 'HEAT'
        if self._kettler._status == '05':
            return 'DELAYED START'

    @property
    def device_state_attributes(self):
        attributes = {
            'Timer PROG':str(self._kettler._ph)+':'+str(self._kettler._pm),
            'Timer CURR':str(self._kettler._th)+':'+str(self._kettler._tm)}
        return attributes

    @property
    def unique_id(self):
        return f'{DOMAIN}[{self._kettler._mac}][{self._name}]'
