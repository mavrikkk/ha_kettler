#!/usr/local/bin/python3
# coding: utf-8

from . import DOMAIN
from homeassistant.const import CONF_MAC
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.dispatcher import async_dispatcher_connect



async def async_setup_entry(hass, config_entry, async_add_entities):
    kettler = hass.data[DOMAIN][config_entry.entry_id]
    if kettler._type == 0 or kettler._type == 1 or kettler._type == 2 or kettler._type == 3 or kettler._type == 4:
        async_add_entities([RedmondSensor(kettler)], True)
    if kettler._type == 5:
        async_add_entities([RedmondCooker(kettler)], True)





class RedmondSensor(Entity):

    def __init__(self, kettler):
        self._kettler = kettler
        self._name = 'Status ' + self._kettler._name
        self._icon = 'mdi:sync'
        self._state = ''
        self._sync = ''

    async def async_added_to_hass(self):
        self._handle_update()
        self.async_on_remove(async_dispatcher_connect(self._kettler.hass, 'ready4skyupdate', self._handle_update))

    def _handle_update(self):
        self._state = 'OFF'
        if self._kettler._status == '02':
            if self._kettler._type == 3 or self._kettler._type == 4:
                self._state = 'ON'
            else:
                if self._kettler._mode == '00':
                    self._state = 'BOIL'
                if self._kettler._mode == '01':
                    self._state = 'HEAT'
                if self._kettler._mode == '03':
                    self._state = 'LIGHT'
        self._sync = str(self._kettler._time_upd)
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
    def available(self):
        return True

    @property
    def state(self):
        return self._state

    @property
    def device_state_attributes(self):
        attributes = {'sync':self._sync}
        return attributes

    @property
    def unique_id(self):
        return f'{DOMAIN}[{self._kettler._mac}][{self._name}]'





class RedmondCooker(Entity):

    def __init__(self, kettler):
        self._icon = 'mdi:book-open'
        self._kettler = kettler
        self._name = 'Status ' + kettler._name
        self._state = ''
        self._sync = ''
        self._timer_prog = ''
        self._timer_curr = ''

    async def async_added_to_hass(self):
        self._handle_update()
        self.async_on_remove(async_dispatcher_connect(self._kettler.hass, 'ready4skyupdate', self._handle_update))

    def _handle_update(self):
        self._state = 'OFF'
        if self._kettler._status == '01':
            self._state = 'PROGRAM'
        if self._kettler._status == '02':
            self._state = 'ON'
        if self._kettler._status == '04':
            self._state = 'HEAT'
        if self._kettler._status == '05':
            self._state = 'DELAYED START'
        self._sync = str(self._kettler._time_upd)
        self._timer_prog = str(self._kettler._ph)+':'+str(self._kettler._pm)
        self._timer_curr = str(self._kettler._th)+':'+str(self._kettler._tm)
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
    def available(self):
        return True

    @property
    def state(self):
        return self._state

    @property
    def device_state_attributes(self):
        attributes = {
            'sync':str(self._sync),
            'Timer PROG':self._timer_prog,
            'Timer CURR':self._timer_curr}
        return attributes

    @property
    def unique_id(self):
        return f'{DOMAIN}[{self._kettler._mac}][{self._name}]'
