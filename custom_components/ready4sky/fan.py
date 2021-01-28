#!/usr/local/bin/python3
# coding: utf-8

from . import DOMAIN
from homeassistant.const import CONF_MAC
from homeassistant.components.fan import (
    SUPPORT_SET_SPEED,
    FanEntity
)
from homeassistant.helpers.dispatcher import async_dispatcher_connect



async def async_setup_entry(hass, config_entry, async_add_entities):
    kettler = hass.data[DOMAIN][config_entry.entry_id]
    if kettler._type == 3:
        async_add_entities([RedmondFan(kettler)], True)

        
        
class RedmondFan(FanEntity):

    def __init__(self, kettler):
        self._name = 'Fan ' + kettler._name
        self._icon = 'mdi:fan'
        self._kettler = kettler
        self._ison = False
        self.speeds = ['00', '01', '02', '03', '04', '05', '06']
        self.cur_speed = '00'



    async def async_added_to_hass(self):
        self._handle_update()
        self.async_on_remove(async_dispatcher_connect(self._kettler.hass, 'ready4skyupdate', self._handle_update))

    def _handle_update(self):
        self._ison = False
        self.cur_speed = self._kettler._mode
        if self._kettler._status == '02':
            self._ison = True
        self.schedule_update_ha_state()

    async def async_set_speed(self, speed: str) -> None:
        if speed == '00':
            await self._kettler.async_modeOff()
        else:
            await self._kettler.async_modeFan(speed)
            if not self._ison:
                await self._kettler.async_modeOn()
                
    async def async_turn_on(self, speed: str = None, percentage: int = None, preset_mode: str = None, **kwargs,) -> None:
        if speed is not None:
            self.async_set_speed(speed)
        else:
            await self._kettler.async_modeOn()

    async def async_turn_off(self, **kwargs) -> None:
        await self._kettler.async_modeOff()
            
    
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

    @property
    def speed(self) -> str:
        return self.cur_speed

    @property
    def speed_list(self) -> list:
        return self.speeds

    @property
    def supported_features(self) -> int:
        return SUPPORT_SET_SPEED
    
    @property
    def unique_id(self):
        return f'{DOMAIN}[{self._kettler._mac}][{self._name}]'
