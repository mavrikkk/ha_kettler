#!/usr/local/bin/python3
# coding: utf-8

import pexpect
from time import sleep
import time
import colorsys
from datetime import datetime
from textwrap import wrap
import re

from datetime import timedelta
import voluptuous as vol
import logging

from homeassistant.components.water_heater import (WaterHeaterDevice, PLATFORM_SCHEMA, SUPPORT_TARGET_TEMPERATURE, SUPPORT_OPERATION_MODE, STATE_ELECTRIC, ATTR_TEMPERATURE)
from homeassistant.const import (STATE_OFF, TEMP_CELSIUS)
from homeassistant.core import callback
import homeassistant.helpers.config_validation as cv

SCAN_INTERVAL = timedelta(seconds=60)

CONF_MIN_TEMP = 40
CONF_MAX_TEMP = 100
CONF_TARGET_TEMP = 100

REQUIREMENTS = ['pexpect']

CONF_MAC = 'mac'
CONF_KEY = 'key'
CONF_DEV = 'device'

OPERATION_LIST = [STATE_OFF, STATE_ELECTRIC]
SUPPORT_FLAGS_HEATER = (SUPPORT_TARGET_TEMPERATURE | SUPPORT_OPERATION_MODE)

ATTR_TIME_UPD = 'sync_time'

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_MAC): cv.string,
    vol.Required(CONF_KEY): cv.string,
    vol.Required(CONF_DEV): cv.string,
})



async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    mac = config.get(CONF_MAC)
    key = config.get(CONF_KEY)
    device = config.get(CONF_DEV)

    if len(key) != 16:
        _LOGGER.error("key value is empty or wrong")
        return False

    mac_validation = bool(re.match('^' + '[\:\-]'.join(['([0-9a-f]{2})']*6) + '$', mac.lower()))
    if not mac_validation:
        _LOGGER.error("mac value is empty or wrong")
        return False

    async_add_entities([R4S_G200S(mac, key, device)])





class R4S_G200S(WaterHeaterDevice):

    def __init__(self, addr, key, device):
        self._name = 'G200S'
        self._mac = addr
        self._key = key
        self._device = device

        self._icon = 'mdi:kettle'
        self._avialible = False
        self._is_on = False
        self._heatorboil = '' #may be  '' or 'b' - boil or 'h' - heat to temp
        self._temp = 0

        self._is_busy = False
        self._is_auth = False
        self._status = '' #may be '' or '00' - OFF or '02' - ON
        self._mode = '' #may be  '' or '00' - boil or '01' - heat to temp or '03' - backlight
        self._time_upd = '00:00'
        self._iter = 0 # int counter

        self._tgtemp = CONF_TARGET_TEMP
        self.child = None



    async def async_added_to_hass(self):
        await self.firstConnect()

    ### for HASS
    @property
    def supported_features(self):
        return SUPPORT_FLAGS_HEATER

#    @property
#    def available(self):
#        return self._avialible

    @property
    def temperature_unit(self):
        return TEMP_CELSIUS

    @property
    def current_temperature(self):
        return self._temp

    @property
    def target_temperature(self):
        return self._tgtemp

    @property
    def target_temperature_step(self):
        return 5

    @property
    def current_operation(self):
        if self._is_on:
            return STATE_ELECTRIC
        return STATE_OFF

    @property
    def operation_list(self):
        return OPERATION_LIST

    async def async_set_operation_mode(self, operation_mode):
        if operation_mode == STATE_ELECTRIC:
            if self._temp is None:
                return
            if self._tgtemp is None:
                return
            if self._tgtemp == 100:
                await self.modeOn()
            else:
                await self.modeOn("01", self.decToHex(self._tgtemp))
        elif operation_mode == STATE_OFF:
            await self.modeOff()

    async def async_set_temperature(self, **kwargs):
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is None:
            return
        self._tgtemp = temperature
        await self.async_set_operation_mode(STATE_ELECTRIC)

#    @property
#    def is_on(self):
#        return self._is_on

    @property
    def min_temp(self):
        return CONF_MIN_TEMP

    @property
    def max_temp(self):
        return CONF_MAX_TEMP

    @property
    def name(self):
        return self._name

    @property
    def should_poll(self):
        return True

    @property
    def icon(self):
        return self._icon

    @property
    def device_state_attributes(self):
        attrs = {}
        attrs[ATTR_TIME_UPD] = str(self._time_upd)
        return attrs

    async def async_update(self):
        await self.modeUpdate()



    ### additional methods
    def iterase(self): # counter
        self._iter+=1
        if self._iter >= 100: self._iter = 0

    def hexToDec(self, chr):
        return int(str(chr), 16)

    def decToHex(self, num):
        char = str(hex(int(num))[2:])
        if len(char) < 2:
            char = '0' + char
        return char



# common cmd
    def sendResponse(self):
        answ = False
        try:
            self.child.sendline("char-write-cmd 0x000c 0100") #send packet to receive messages in future
            self.child.expect(r'\[LE\]>')
            answ = True
        except:
            answ = False
            _LOGGER.error('error sendResponse')
        return answ

    def sendAuth(self):
        answer = False
        try:
            self.child.sendline("char-write-req 0x000e 55" + self.decToHex(self._iter) + "ff" + self._key + "aa") #send authorise key
            self.child.expect("value: ") # wait for response
            self.child.expect("\r\n") # wait for end string
            connectedStr = self.child.before[0:].decode("utf-8") # answer from device
            answ = connectedStr.split()[3] # parse: 00 - no   01 - yes
            if answ == '01':
                answer = True
            self.child.expect(r'\[LE\]>')
            self.iterase()
        except:
            answer = False
            _LOGGER.error('error sendAuth')
        return answer

    def sendOn(self):
        answ = False
        try:
            self.child.sendline("char-write-req 0x000e 55" + self.decToHex(self._iter) + "03aa") # ON
            self.child.expect("value: ")
            self.child.expect("\r\n")
            self.child.expect(r'\[LE\]>')
            self.iterase()
            answ = True
        except:
            answ = False
            _LOGGER('error sendOn')
        return answ

    def sendOff(self):
        answ = False
        try:
            self.child.sendline("char-write-req 0x000e 55" + self.decToHex(self._iter) + "04aa") # OFF
            self.child.expect("value: ")
            self.child.expect("\r\n")
            self.child.expect(r'\[LE\]>')
            self.iterase()
            answ = True
        except:
            answ = False
            _LOGGER.error('error sendOff')
        return answ

    def sendSync(self, timezone = 4):
        answ = False
        try:
            tmz_hex_list = wrap(str(self.decToHex(timezone*60*60)), 2)
            tmz_str = ''
            for i in reversed(tmz_hex_list):
                tmz_str+=i
            timeNow_list = wrap(str(self.decToHex(time.mktime(datetime.now().timetuple()))), 2)
            timeNow_str = ''
            for i in reversed(timeNow_list):
                timeNow_str+=i
            self.child.sendline("char-write-req 0x000e 55" + self.decToHex(self._iter) + "6e" + timeNow_str + tmz_str + "0000aa")
            self.child.expect("value: ")
            self.child.expect("\r\n")
            self.child.expect(r'\[LE\]>')
            self.iterase()
            answ = True
        except:
            answ = False
            _LOGGER.error('error sendSync')
        return answ

    def sendStat(self):
        answ = False
        try:
            self.child.sendline("char-write-req 0x000e 55" + self.decToHex(self._iter) + "4700aa")
            self.child.expect("value: ")
            self.child.expect("\r\n")
            statusStr = self.child.before[0:].decode("utf-8")
            self._Watts = self.hexToDec(str(statusStr.split()[11] + statusStr.split()[10] + statusStr.split()[9])) # in Watts
            self._alltime = round(self._Watts/2200, 1) # in hours
            self.child.expect(r'\[LE\]>')
            self.iterase()
            self.child.sendline("char-write-req 0x000e 55" + self.decToHex(self._iter) + "5000aa")
            self.child.expect("value: ")
            self.child.expect("\r\n")
            statusStr = self.child.before[0:].decode("utf-8")
            self._times = self.hexToDec(str(statusStr.split()[7] + statusStr.split()[6]))
            self.child.expect(r'\[LE\]>')
            self.iterase()
            answ = True
        except:
            answ = False
            _LOGGER.error('error sendStat')
        return answ

    def sendStatus(self):
        answ = False
        try:
            self.child.sendline("char-write-req 0x000e 55" + self.decToHex(self._iter) + "06aa") # status of device
            self.child.expect("value: ")
            self.child.expect("\r\n")
            statusStr = self.child.before[0:].decode("utf-8") # answer from device example 55 xx 06 00 00 00 00 01 2a 1e 00 00 00 00 00 00 80 00 00 aa
            answer = statusStr.split()
            self._status = str(answer[11])
            self._temp = self.hexToDec(str(answer[8]))
            self._mode = str(answer[3])
            tgtemp = str(answer[5])
            if tgtemp != '00':
                self._tgtemp = self.hexToDec(tgtemp)
            else:
                self._tgtemp = 100
            if self._mode == '00':
                self._heatorboil = 'b'
            elif self._mode == '01':
                self._heatorboil = 'h'
            else:
                self._heatorboil = ''
            if self._status == '02' and self._heatorboil != '':
                self._is_on = True
            else:
                self._is_on = False
            self.child.expect(r'\[LE\]>')
            self.iterase()
            answ = True
        except:
            answ = False
            _LOGGER.error('error sendStatus')
        return answ

    def sendMode(self, mode, temp):   # 00 - boil 01 - heat to temp 03 - backlight (boil by default)    temp - in HEX
        answ = False
        try:
            self.child.sendline("char-write-req 0x000e 55" + self.decToHex(self._iter) + "05" + mode + "00" + temp + "00000000000000000000800000aa") # set Properties
            self.child.expect("value: ")
            self.child.expect("\r\n")
            self.child.expect(r'\[LE\]>')
            self.iterase()
            answ = True
        except:
            answ = False
            _LOGGER.error('error sendMode')
        return answ

    def sendUseBackLight(self, onoff="01"):
        answ = False
        try:
            self.child.sendline("char-write-req 0x000e 55" + self.decToHex(self._iter) + "37c8c8" + onoff + "aa") #  onoff: 00 - off, 01 - on
            self.child.expect("value: ")
            self.child.expect("\r\n")
            self.child.expect(r'\[LE\]>')
            self.iterase()
            answ = True
        except:
            answ = False
            _LOGGER.error('error sendUseBaclLight')
        return answ

    def sendSetLights(self, rand, boilOrLight = "00", rgb1 = '0000ff', rgb2 = 'ff0000', bright = ""): # 00 - boil light    01 - backlight
        answ = False
        try:
            if boilOrLight == "00":
                scale_light = ['28', '46', '64']
            else:
                scale_light = ['00', '32', '64']
            if rgb1 == '0000ff' and rgb2 == 'ff0000': # hardcoded to reduce calc time
                rgb_mid = '00ff00'
            else:
                rgb_mid = self.calcMiddleColor(rgb1, rgb2)
            self.child.sendline("char-write-req 0x000e 55" + self.decToHex(self._iter) + "32" + boilOrLight + scale_light[0] + rand + rgb1 + scale_light[1] + rand + rgb_mid + scale_light[2] + rand + rgb2 + "aa")
            self.child.expect("value: ")
            self.child.expect("\r\n")
            self.child.expect(r'\[LE\]>')
            self.iterase()
            answ = True
        except:
            answ = False
            _LOGGER.error('error sendSetLights')
        return answ

### composite methods
    def connect(self):
        if self._is_busy:
            self.disconnect()
        try:
            self.child = pexpect.spawn("gatttool --adapter=" + self._device + " -I -t random -b " + self._mac, ignore_sighup=False)
            self.child.expect(r'\[LE\]>', timeout=3)
            self.child.sendline("connect")
            self.child.expect(r'Connection successful.*\[LE\]>', timeout=3)
        except:
            _LOGGER.error('error connect')

    def disconnect(self):
        if self.child != None:
            self.child.sendline("exit")
        self._is_busy = False
        self._is_auth = False
        self._heatorboil = ''
        self._status = ''
        self._mode = ''
        self.child = None

    async def modeOn(self, mode = "00", temp = "00"):
        if not self._is_busy:
            self._is_busy = True
            answ = False
            self.connect()
            try:
                if self.sendResponse():
                    if self.sendAuth():
                        if self.sendMode(mode, temp):
                            if self.sendOn():
                                if self.sendStatus():
                                    answ = True
            except:
                _LOGGER.error('error modeOn')
            self.disconnect()
            return answ
        else:
            _LOGGER.info('device is busy now')
            return False

    async def modeOff(self):
        if not self._is_busy:
            self._is_busy = True
            answ = False
            self.connect()
            try:
                if self.sendResponse():
                    if self.sendAuth():
                        if self.sendOff():
                            if self.sendStatus():
                                answ = True
            except:
                _LOGGER.error('error modeOff')
            self.disconnect()
            return answ
        else:
            _LOGGER.info('device is busy now')
            return False

    async def firstConnect(self):
        self._is_busy = True
        iter = 0
        self.connect()
        try:
            while iter < 5:  # 5 attempts to auth
                answer = False
                if self.sendResponse():
                    if self.sendAuth():
                        answer = True
                        break
                sleep(1)
                iter+=1
            if answer:
                self._is_auth = True
                self._avialible = True
                if self.sendUseBackLight():
                    if self.sendSetLights('5e'):
                        if self.sendSync():
                            if self.sendStatus():
                                self._time_upd = time.strftime("%H:%M")
            else:
                self._is_auth = False
                self._avialible = False
                _LOGGER.error('error first connect')
        except:
            _LOGGER.error('error first connect')
        self.disconnect()

    async def modeUpdate(self):
        if not self._is_busy:
            self._is_busy = True
            answ = False
            self.connect()
            try:
                if self.sendResponse():
                    if self.sendAuth():
                        if self.sendSync():
                            if self.sendStatus():
                                self._time_upd = time.strftime("%H:%M")
                                answ = True
            except:
                _LOGGER.error('error update')
            self.disconnect()
            return answ
        else:
            _LOGGER.info('device is busy now')
            return False
