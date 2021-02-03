#!/usr/local/bin/python3
# coding: utf-8

from . import DOMAIN

#from homeassistant.util.percentage import (
#    ordered_list_item_to_percentage,
#    percentage_to_ordered_list_item,
#)

from homeassistant.const import CONF_MAC
from homeassistant.components.fan import (
    SUPPORT_SET_SPEED,
    FanEntity
)
from homeassistant.helpers.dispatcher import async_dispatcher_connect

#ORDERED_NAMED_FAN_SPEEDS = ['01', '02', '03', '04', '05', '06']  # off is not included



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
        #self._perc = 0
        self._speed = '01'



    async def async_added_to_hass(self):
        self._handle_update()
        self.async_on_remove(async_dispatcher_connect(self._kettler.hass, 'ready4skyupdate', self._handle_update))

    def _handle_update(self):
        self._ison = False
        if self._kettler._mode == '00':
            self._speed = '01'
        else:
            self._speed = self._kettler._mode
#        if self._kettler._mode == '00' or self._kettler._status == '00':
#            self._perc = 0
#        else:
#            self._perc = ordered_list_item_to_percentage(ORDERED_NAMED_FAN_SPEEDS, self._kettler._mode)
        if self._kettler._status == '02':
            self._ison = True
        self.schedule_update_ha_state()

#    async def async_set_percentage(self, percentage: int) -> None:
#        if percentage == 0:
#            await self.async_turn_off()
#        else:
#            speed = percentage_to_ordered_list_item(ORDERED_NAMED_FAN_SPEEDS, percentage)
#            await self._kettler.async_modeFan(speed)
       
    async def async_set_speed(self, speed: str) -> None:
        if speed == '00':
            await self._kettler.async_modeOff()
        else:
            await self._kettler.async_modeFan(speed)
            
    async def async_turn_on(self, speed: str = None, percentage: int = None, preset_mode: str = None, **kwargs,) -> None:
        if speed is not None:
            await self.async_set_speed(speed)
        else:
            await self.async_set_speed('01')
#        if percentage is not None:
#            await self.async_set_percentage(percentage)
#        else:
#            await self.async_set_percentage(0)

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
    def speed(self):
        return self._speed
    
    @property
    def speed_list(self):
        return ['01', '02', '03', '04', '05', '06']
    
#    @property
#    def percentage(self) -> int:
#        return self._perc

    @property
    def supported_features(self) -> int:
        return SUPPORT_SET_SPEED
    
    @property
    def unique_id(self):
        return f'{DOMAIN}[{self._kettler._mac}][{self._name}]'
