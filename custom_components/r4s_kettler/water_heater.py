#!/usr/local/bin/python3
# coding: utf-8

from . import DOMAIN

import voluptuous as vol

from homeassistant.components.water_heater import (
    WaterHeaterDevice,
    SUPPORT_TARGET_TEMPERATURE,
    SUPPORT_OPERATION_MODE,
    STATE_ELECTRIC,
    ATTR_TEMPERATURE
)
from homeassistant.const import (
    STATE_UNKNOWN,
    STATE_OFF,
    TEMP_CELSIUS
)
from homeassistant.helpers import entity_platform

OPERATION_LIST = [STATE_OFF, STATE_ELECTRIC]
SUPPORT_FLAGS_HEATER = (SUPPORT_TARGET_TEMPERATURE | SUPPORT_OPERATION_MODE)

COOKER_PROGRAMS = {
    'rice':['01', '00', '64', '00', '23'],
    'slow_cooking':['02', '00', '61', '03', '00'],
    'pilaf':['03', '00', '6e', '01', '00'],
    'frying_vegetables':['04', '01', 'b4', '00', '12',],
    'frying_fish':['04', '02', 'b4', '00', '0c'],
    'frying_meat':['04', '03', 'b4', '00', '0f'],
    'stewing_vegetables':['05', '01', '64', '00', '28',],
    'stewing_fish':['05', '02', '64', '00', '23'],
    'stewing_meat':['05', '03', '64', '01', '00'],
    'pasta':['06', '00', '64', '00', '08'],
    'milk_porridge':['07', '00', '5f', '00', '23'],
    'soup':['08', '00', '63', '01', '00'],
    'yogurt':['09', '00', '28', '08', '00'],
    'baking':['0a', '00', '91', '00', '2d'],
    'steam_vegetables':['0b', '01', '64', '00', '1e'],
    'steam_fish':['0b', '02', '64', '00', '19'],
    'steam_meat':['0b', '03', '64', '00', '28'],
    'hot':['0с', '00', '64', '00', '28']}
COOKER_OPERATION_LIST = [program for program,value in COOKER_PROGRAMS.items()]
COOKER_OPERATION_LIST.append(STATE_OFF)



async def async_setup_entry(hass, config_entry, async_add_entities):
    kettler = hass.data[DOMAIN]["kettler"]
    if kettler._type == 0 or kettler._type == 1 or kettler._type == 2:
        async_add_entities([RedmondWaterHeater(kettler)], True)
    if kettler._type == 5:
        async_add_entities([RedmondCooker(kettler)], True)
        platform = entity_platform.current_platform.get()
        platform.async_register_entity_service("set_timer",{vol.Required("hours"): vol.All(vol.Coerce(int), vol.Range(min=0, max=23)), vol.Required("minutes"): vol.All(vol.Coerce(int), vol.Range(min=0, max=59))},"async_set_timer",)
        platform.async_register_entity_service("set_manual_program",{vol.Required("prog"): vol.All(vol.Coerce(int), vol.Range(min=0, max=12)), vol.Required("subprog"): vol.All(vol.Coerce(int), vol.Range(min=0, max=3)),vol.Required("temp"): vol.All(vol.Coerce(int), vol.Range(min=30, max=180)), vol.Required("hours"): vol.All(vol.Coerce(int), vol.Range(min=0, max=23)),vol.Required("minutes"): vol.All(vol.Coerce(int), vol.Range(min=0, max=59)), vol.Required("dhours"): vol.All(vol.Coerce(int), vol.Range(min=0, max=23)),vol.Required("dminutes"): vol.All(vol.Coerce(int), vol.Range(min=0, max=59)), vol.Required("heat"): vol.All(vol.Coerce(int), vol.Range(min=0, max=1))},"async_set_manual_program",)



class RedmondWaterHeater(WaterHeaterDevice):

    def __init__(self, kettler):
        self._name = 'Kettle ' + kettler._name
        self._icon = 'mdi:kettle'
        self._kettler = kettler

    @property
    def device_info(self):
        return {
            "connections": {
                ("mac", self._kettler._mac)
            }
        }

    ### for HASS
    @property
    def supported_features(self):
        return SUPPORT_FLAGS_HEATER

    @property
    def available(self):
        return self._kettler._connected

    @property
    def temperature_unit(self):
        return TEMP_CELSIUS

    @property
    def current_temperature(self):
        return self._kettler._temp

    @property
    def target_temperature(self):
        return self._kettler._tgtemp

    @property
    def device_state_attributes(self):
        data = {"target_temp_step": 5}
        return data

    @property
    def current_operation(self):
        if self._kettler._mode == '00' or self._kettler._mode == '01':
            if self._kettler._status == '02':
                return STATE_ELECTRIC
        return STATE_OFF

    @property
    def operation_list(self):
        return OPERATION_LIST

    async def async_set_operation_mode(self, operation_mode):
        if operation_mode == STATE_ELECTRIC:
            if self._kettler._temp is None:
                return
            if self._kettler._tgtemp is None:
                return
            if self._kettler._tgtemp == 100:
                await self._kettler.modeOn()
            else:
                await self._kettler.modeOn("01", self._kettler.decToHex(self._kettler._tgtemp))
        elif operation_mode == STATE_OFF:
            await self._kettler.modeOff()

    async def async_set_temperature(self, **kwargs):
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is None:
            return
        self._kettler._tgtemp = temperature
        await self.async_set_operation_mode(STATE_ELECTRIC)

    @property
    def min_temp(self):
        return self._kettler._mntemp

    @property
    def max_temp(self):
        return self._kettler._mxtemp

    @property
    def name(self):
        return self._name

    @property
    def icon(self):
        return self._icon

    @property
    def unique_id(self):
        return f'{DOMAIN}[{self._kettler._mac}][{self._name}]'





class RedmondCooker(WaterHeaterDevice):

    def __init__(self, kettler):
        self._name = 'Cooker ' + kettler._name
        self._icon = 'mdi:chef-hat'
        self._kettler = kettler

    @property
    def device_info(self):
        return {
            "connections": {
                ("mac", self._kettler._mac)
            }
        }

    ### for HASS
    @property
    def supported_features(self):
        return SUPPORT_FLAGS_HEATER

    @property
    def available(self):
        return self._kettler._connected

    @property
    def temperature_unit(self):
        return TEMP_CELSIUS

    @property
    def current_temperature(self):
        return self._kettler._tgtemp

    @property
    def target_temperature(self):
        return self._kettler._tgtemp

    @property
    def device_state_attributes(self):
        data = {"target_temp_step": 5}
        return data

    @property
    def operation_list(self):
        return COOKER_OPERATION_LIST

    @property
    def current_operation(self):
        if self._kettler._status == '02' or self._kettler._status == '04' or self._kettler._status == '05':
            for key,value in COOKER_PROGRAMS.items():
                if value[0] == self._kettler._prog:
                    return key
        return STATE_OFF

    async def async_set_operation_mode(self, operation_mode):
        if operation_mode == STATE_OFF:
            await self._kettler.modeOff()
        else:
            program = COOKER_PROGRAMS[operation_mode]
            await self._kettler.modeOnCook(program[0],program[1],program[2],program[3],program[4])

    async def async_set_manual_program(self, program={}):
        if program == {}:
            return
        try:
            prog = self._kettler.decToHex(program['prog'])
            subprog = self._kettler.decToHex(program['subprog'])
            temp = self._kettler.decToHex(program['temp'])
            hours = self._kettler.decToHex(program['hours'])
            minutes = self._kettler.decToHex(program['minutes'])
            dhours = self._kettler.decToHex(program['dhours'])
            dminutes = self._kettler.decToHex(program['dminutes'])
            heat = self._kettler.decToHex(program['heat'])
            await self._kettler.modeOnCook(prog,subprog,temp,hours,minutes,dhours,dminutes,heat)
        except:
            pass

    async def async_set_timer(self, timer={}):
        if timer == {}:
            return
        try:
            hours = self._kettler.decToHex(timer['hours'])
            minutes = self._kettler.decToHex(timer['minutes'])
            await self._kettler.modeTimeCook(hours,minutes)
        except:
            pass

    async def async_set_temperature(self, **kwargs):
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is None:
            return
        self._kettler._tgtemp = temperature
        await self._kettler.modeTempCook(temperature)

    @property
    def min_temp(self):
        return 30

    @property
    def max_temp(self):
        return 180

    @property
    def name(self):
        return self._name

    @property
    def icon(self):
        return self._icon

    @property
    def unique_id(self):
        return f'{DOMAIN}[{self._kettler._mac}][{self._name}]'
