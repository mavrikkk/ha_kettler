
#!/usr/local/bin/python3
# coding: utf-8

from re import search
from bluepy import btle
import binascii
import asyncio
from functools import partial

from time import sleep
import time
from datetime import datetime
from textwrap import wrap
import logging

from random import seed
from random import randint

from datetime import timedelta
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import async_track_time_interval, async_call_later
import homeassistant.util.color as color_util
from homeassistant.const import (
    CONF_DEVICE,
    CONF_MAC,
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL
)

from .r4sconst import SUPPORTED_DEVICES

CONF_USE_BACKLIGHT = 'use_backlight'

CONF_MIN_TEMP = 40
CONF_MAX_TEMP = 100
CONF_TARGET_TEMP = 100

_LOGGER = logging.getLogger(__name__)

SUPPORTED_DOMAINS = ["water_heater", "sensor", "light", "switch", "fan"]

DOMAIN = "ready4sky"

async def async_setup(hass, config):
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry):

    config = config_entry.data

    mac = config.get(CONF_MAC)
    device = config.get(CONF_DEVICE)
    password = config.get(CONF_PASSWORD)
    scan_delta = timedelta(seconds=config.get(CONF_SCAN_INTERVAL))
    backlight = config.get(CONF_USE_BACKLIGHT)

    kettler = RedmondKettler(hass, mac, password, device, backlight)
    
    seed(1)
    valueR = randint(5, 10)
    await asyncio.sleep(valueR)
    
    try:
        await kettler.async_firstConnect()
        if not kettler._connected:
            _LOGGER.error("Connection error")
            return False
    except:
        _LOGGER.error("Connect to %s through device %s failed", mac, device)
        return False

    hass.data[DOMAIN][config_entry.entry_id] = kettler
    
    device_registry = await dr.async_get_registry(hass)
    device_registry.async_get_or_create(
        config_entry_id=config_entry.entry_id,
        identifiers={(DOMAIN, config_entry.unique_id)},
        connections={(dr.CONNECTION_NETWORK_MAC, mac)},
        manufacturer="Redmond",
        name="Ready4Sky",
    )
    
    async_track_time_interval(hass, hass.data[DOMAIN][config_entry.entry_id].async_update, scan_delta)

    for component in SUPPORTED_DOMAINS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(config_entry, component)
        )

    return True



async def async_unload_entry(hass:HomeAssistant, entry:ConfigEntry):
    try:
        for component in SUPPORTED_DOMAINS:
            await hass.config_entries.async_forward_entry_unload(entry, component)
        hass.data[DOMAIN].pop(entry.entry_id)
    except ValueError:
        pass
    return True





class BTLEConnection(btle.DefaultDelegate):

    def __init__(self, mac):
        btle.DefaultDelegate.__init__(self)
        self._conn = None
        self._mac = mac
        self._callbacks = {}

    def __enter__(self, i=0):
        try:
            self.__exit__(None, None, None)
            self._conn = btle.Peripheral(deviceAddr=self._mac, addrType=btle.ADDR_TYPE_RANDOM)
            self._conn.withDelegate(self)
        except:
            i=i+1
            if i<5:
                return self.__enter__(i)
            else:
                _LOGGER.error('unable to connect to device')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self._conn.disconnect()
        except:
            pass
        self._conn = None

    def handleNotification(self, handle, data):
        if handle in self._callbacks:
            self._callbacks[handle](data)

    @property
    def mac(self):
        return self._mac

    def set_callback(self, handle, function):
        self._callbacks[handle] = function

    def make_request(self, handle, value, with_response=True):
        answ = False
        try:
            self._conn.writeCharacteristic(handle, value, withResponse=with_response)
            self._conn.waitForNotifications(2.0)
            answ = True
        except:
            pass
        return answ



class RedmondKettler:

    def __init__(self, hass, addr, key, device, backlight):
        self.hass = hass
        self._mac = addr
        self._key = key
        self._device = device
        self._use_backlight = backlight
        self._type = 1
        self._name = 'redmond sky'
        self._mntemp = CONF_MIN_TEMP
        self._mxtemp = CONF_MAX_TEMP
        self._tgtemp = CONF_TARGET_TEMP
        self._temp = 0
        self._time_upd = '00:00'
        self._boiltime = '80'
        self._rgb1 = '0000ff'
        self._rgb2 = 'ff0000'
        self._rand = '5e'
        self._mode = '00' # '00' - boil, '01' - heat to temp, '03' - backlight  for cooker 00 - heat after cook   01 - off after cook        for fan 00-06 - speed 
        self._status = '00' #may be '00' - OFF or '02' - ON         for cooker 00 - off   01 - setup program   02 - on  04 - heat   05 - delayed start
        self._iter = 0
        self._prog = '00' #  program
        self._sprog = '00' # subprogram
        self._ph = 0 #  program hours
        self._pm = 0 #  program min
        self._th = 0 #  timer hours
        self._tm = 0 #  timer min
        self._ion = '00' # 00 - off   01 - on
        self._connected = False
        self._conn = BTLEConnection(self._mac)
        self._conn.set_callback(11, self.handle_notification)



    def handle_notification(self, data):
        s = binascii.b2a_hex(data).decode("utf-8")
        arr = [s[x:x+2] for x in range (0, len(s), 2)]
        if arr[2] == 'ff': ### sendAuth
            if self._type == 0 or self._type == 1 or self._type == 3 or self._type == 4 or self._type == 5:
                if arr[3] == '01':
                    self._connected = True
                else:
                    self._connected = False
            if self._type == 2:
                if arr[3] == '02':
                    self._connected = True
                else:
                    self._connected = False
        if arr[2] == '03'  or arr[2] == '04'  or arr[2] == '05' or arr[2] == '6e'  or arr[2] == '37' or arr[2] == '32' or arr[2] == '33': ### sendOn    sendOff    sendMode    sendSync   sendUseBacklight   sendSetLights   sendGetLights
            pass
        if arr[2] == '06': ### sendStatus
            if self._type == 0:
                self._temp = self.hexToDec(str(arr[13]))
                self._status = str(arr[11])
                self._mode = str(arr[3])
                tgtemp = str(arr[5])
                if tgtemp != '00':
                    self._tgtemp = self.hexToDec(tgtemp)
                else:
                    self._tgtemp = 100
            if self._type == 1 or self._type == 2:
                self._temp = self.hexToDec(str(arr[8]))
                self._status = str(arr[11])
                self._mode = str(arr[3])
                tgtemp = str(arr[5])
                if tgtemp != '00':
                    self._tgtemp = self.hexToDec(tgtemp)
                else:
                    self._tgtemp = 100
            if self._type == 3:
                self._status = str(arr[11])
                self._mode = str(arr[5])
                self._ion = str(arr[14])
            if self._type == 4:
                self._status = str(arr[11])
                self._mode = str(arr[3])
            if self._type == 5:
                self._prog = str(arr[3])
                self._sprog = str(arr[4])
                self._temp = self.hexToDec(str(arr[5]))
                self._tgtemp = self.hexToDec(str(arr[5]))
                self._ph = self.hexToDec(str(arr[6]))
                self._pm = self.hexToDec(str(arr[7]))
                self._th = self.hexToDec(str(arr[8]))
                self._tm = self.hexToDec(str(arr[9]))
                self._mode = str(arr[10])
                self._status = str(arr[11])
            async_dispatcher_send(self.hass, 'ready4skyupdate')

    def calcMidColor(self, rgb1, rgb2):
        try:
            hs1 = self.rgbhex_to_hs(rgb1)
            hs2 = self.rgbhex_to_hs(rgb2)
            hmid = int((hs1[0]+hs2[0])/2)
            smid = int((hs1[1]+hs2[1])/2)
            hsmid = (hmid,smid)
            rgbmid = self.hs_to_rgbhex(hsmid)
        except:
            rgbmid = '00ff00'
        return rgbmid

    def rgbhex_to_hs(self, rgbhex):
        rgb = color_util.rgb_hex_to_rgb_list(rgbhex)
        return color_util.color_RGB_to_hs(*rgb)

    def hs_to_rgbhex(self, hs):
        rgb = color_util.color_hs_to_RGB(*hs)
        return color_util.color_rgb_to_hex(*rgb)

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



    def sendResponse(self, conn):
        answ = False
        str2b = binascii.a2b_hex(bytes('0100', 'utf-8'))
        if conn.make_request(12, str2b):
            answ = True
        return answ

    def sendAuth(self,conn):
        answ = False
        str2b = binascii.a2b_hex(bytes('55' + self.decToHex(self._iter) + 'ff' + self._key + 'aa', 'utf-8'))
        if conn.make_request(14, str2b):
            self.iterase()
            answ = True
        return answ

    def sendOn(self,conn):
        answ = False
        if self._type == 0:
            answ = True
        if self._type == 1 or self._type == 2 or self._type == 3 or self._type == 4 or self._type == 5:
            str2b = binascii.a2b_hex(bytes('55' + self.decToHex(self._iter) + '03aa', 'utf-8'))
            if conn.make_request(14, str2b):
                self.iterase()
                answ = True
        return answ

    def sendOff(self,conn):
        answ = False
        str2b = binascii.a2b_hex(bytes('55' + self.decToHex(self._iter) + '04aa', 'utf-8'))
        if conn.make_request(14, str2b):
            self.iterase()
            answ = True
        return answ

    def sendSync(self, conn, timezone = 4):
        answ = False
        if self._type == 0 or self._type == 3 or self._type == 4 or self._type == 5:
            answ = True
        if self._type == 1 or self._type == 2:
            if self._use_backlight:
                tmz_hex_list = wrap(str(self.decToHex(timezone*60*60)), 2)
                tmz_str = ''
                for i in reversed(tmz_hex_list):
                    tmz_str+=i
                timeNow_list = wrap(str(self.decToHex(time.mktime(datetime.now().timetuple()))), 2)
                timeNow_str = ''
                for i in reversed(timeNow_list):
                    timeNow_str+=i
                str2b = binascii.a2b_hex(bytes('55' + self.decToHex(self._iter) + '6e' + timeNow_str + tmz_str + '0000aa', 'utf-8'))
                if conn.make_request(14, str2b):
                    self.iterase()
                    answ = True
            else:
                answ = True
        return answ

    def sendStat(self,conn):
        answ = True
        return answ

    def sendStatus(self,conn):
        answ = False
        str2b = binascii.a2b_hex(bytes('55' + self.decToHex(self._iter) + '06aa', 'utf-8'))
        if conn.make_request(14, str2b):
            self.iterase()
            answ = True
        return answ

    def sendMode(self, conn, mode, temp):   # 00 - boil 01 - heat to temp 03 - backlight (boil by default)    temp - in HEX
        answ = False
        if self._type == 3 or self._type == 4 or self._type == 5:
            return True
        if self._type == 0:
            str2b = binascii.a2b_hex(bytes('55' + self.decToHex(self._iter) + '05' + mode + '00' + temp + '00aa', 'utf-8'))
        if self._type == 1 or self._type == 2:
            str2b = binascii.a2b_hex(bytes('55' + self.decToHex(self._iter) + '05' + mode + '00' + temp + '00000000000000000000800000aa', 'utf-8'))
        if conn.make_request(14, str2b):
            self.iterase()
            answ = True
        return answ

    def sendModeCook(self, conn, prog, sprog, temp, hours, minutes, dhours, dminutes, heat): #
        answ = False
        if self._type == 5:
            str2b = binascii.a2b_hex(bytes('55' + self.decToHex(self._iter) + '05' + prog + sprog + temp + hours + minutes + dhours + dminutes + heat + 'aa', 'utf-8'))
            if conn.make_request(14, str2b):
                self.iterase()
                answ = True
        else:
            answ  = True
        return answ

    def sendTimerCook(self, conn, hours, minutes): #
        answ = False
        if self._type == 5:
            str2b = binascii.a2b_hex(bytes('55' + self.decToHex(self._iter) + '0c' + hours + minutes + 'aa', 'utf-8'))
            if conn.make_request(14, str2b):
                self.iterase()
                answ = True
        else:
            answ  = True
        return answ

    def sendTempCook(self, conn, temp): #temp in HEX or speed 00-06
        answ = False
        if self._type == 3 or self._type == 5:
            str2b = binascii.a2b_hex(bytes('55' + self.decToHex(self._iter) + '0b' + temp + 'aa', 'utf-8'))
            if conn.make_request(14, str2b):
                self.iterase()
                answ = True
        else:
            answ  = True
        return answ

    def sendIonCmd(self, conn, onoff): #00-off 01-on
        answ = False
        if self._type == 3:
            str2b = binascii.a2b_hex(bytes('55' + self.decToHex(self._iter) + '1b' + onoff + 'aa', 'utf-8'))
            if conn.make_request(14, str2b):
                self.iterase()
                answ = True
        else:
            answ  = True
        return answ

    def sendAfterSpeed(self, conn):
        answ = False
        if self._type == 3:
            str2b = binascii.a2b_hex(bytes('55' + self.decToHex(self._iter) + '0900aa', 'utf-8'))
            if conn.make_request(14, str2b):
                self.iterase()
                answ = True
        else:
            answ  = True
        return answ

    def sendUseBackLight(self, conn):
        answ = False
        if self._type == 0 or self._type == 3 or self._type == 4 or self._type == 5:
            answ = True
        if self._type == 1 or self._type == 2:
            onoff="00"
            if self._use_backlight:
                onoff="01"
            str2b = binascii.a2b_hex(bytes('55' + self.decToHex(self._iter) + '37c8c8' + onoff + 'aa', 'utf-8'))
            if conn.make_request(14, str2b):
                self.iterase()
                answ = True
        return answ

    def sendSetLights(self, conn, boilOrLight = '01', rgb1 = '0000ff'): # 00 - boil light    01 - backlight
        answ = False
        if self._type == 0 or self._type == 2 or self._type == 3 or self._type == 4 or self._type == 5:
            answ = True
        if self._type == 1:
            rgb_mid = rgb1
            rgb2 = rgb1
            if boilOrLight == "00":
                scale_light = ['28', '46', '64']
            else:
                scale_light = ['00', '32', '64']
            str2b = binascii.a2b_hex(bytes('55' + self.decToHex(self._iter) + '32' + boilOrLight + scale_light[0] + self._rand + rgb1 + scale_light[1] + self._rand + rgb_mid + scale_light[2] + self._rand + rgb2 + 'aa', 'utf-8'))
            if conn.make_request(14, str2b):
                self.iterase()
                answ = True
        return answ



### composite methods
    def startNightColor(self, i=0):
        answ = False
        try:
            with self._conn as conn:
                if self.sendResponse(conn):
                    if self.sendAuth(conn):
                        offed = False
                        if self._status == '02':
                            if self.sendOff(conn):
                                offed = True
                        else:
                            offed = True
                        if offed:
                            if self.sendSetLights(conn, '01', self._rgb1):
                                if self.sendMode(conn, '03', '00'):
                                    if self.sendOn(conn):
                                        if self.sendStatus(conn):
                                            self._time_upd = time.strftime("%H:%M")
                                            answ = True
        except:
            pass
        if not answ:
            i=i+1
            if i<5:
                answ = self.startNightColor(i)
            else:
                _LOGGER.warning('five attempts of startNightColor failed')
        return answ

    async def async_startNightColor(self):
        await self.hass.async_add_executor_job(self.startNightColor)

    def modeOn(self, mode = "00", temp = "00", i=0):
        answ = False
        try:
            with self._conn as conn:
                if self.sendResponse(conn):
                    if self.sendAuth(conn):
                        offed = False
                        if self._status == '02':
                            if self.sendOff(conn):
                                offed = True
                        else:
                            offed = True
                        if offed:
                            if self.sendMode(conn, mode, temp):
                                if self.sendOn(conn):
                                    if self.sendStatus(conn):
                                        self._time_upd = time.strftime("%H:%M")
                                        answ = True
        except:
            pass
        if not answ:
            i=i+1
            if i<5:
                answ = self.modeOn(mode,temp,i)
            else:
                _LOGGER.warning('five attempts of modeOn failed')
        return answ

    async def async_modeOn(self, mode = "00", temp = "00"):
        await self.hass.async_add_executor_job(partial(self.modeOn, mode, temp, 0))

    def modeOnCook(self, prog, sprog, temp, hours, minutes, dhours='00', dminutes='00', heat = '01', i=0):
        answ = False
        try:
            with self._conn as conn:
                if self.sendResponse(conn):
                    if self.sendAuth(conn):
                        offed = False
                        if self._status != '00':
                            if self.sendOff(conn):
                                offed = True
                        else:
                            offed = True
                        if offed:
                            if self.sendModeCook(conn, prog, sprog, temp, hours, minutes, dhours, dminutes, heat):
                                if self.sendOn(conn):
                                    if self.sendStatus(conn):
                                        self._time_upd = time.strftime("%H:%M")
                                        answ = True
        except:
            pass
        if not answ:
            i=i+1
            if i<5:
                answ = self.modeOnCook(prog, sprog, temp, hours, minutes, dhours, dminutes, heat, i)
            else:
                _LOGGER.warning('five attempts of modeOn failed')
        return answ

    async def async_modeOnCook(self, prog, sprog, temp, hours, minutes, dhours='00', dminutes='00', heat = '01'):
        await self.hass.async_add_executor_job(partial(self.modeOnCook, prog, sprog, temp, hours, minutes, dhours, dminutes, heat, 0))

    def modeTempCook(self, temp, i=0):
        answ = False
        try:
            with self._conn as conn:
                if self.sendResponse(conn):
                    if self.sendAuth(conn):
                        if self.sendTempCook(conn, temp):
                            if self.sendStatus(conn):
                                self._time_upd = time.strftime("%H:%M")
                                answ = True
        except:
            pass
        if not answ:
            i=i+1
            if i<5:
                answ = self.modeTempCook(temp, i)
            else:
                _LOGGER.warning('five attempts of modeTempCook failed')
        return answ

    async def async_modeTempCook(self, temp):
        await self.hass.async_add_executor_job(partial(self.modeTempCook, temp, 0))

    def modeFan(self, speed, i=0):
        answ = False
        try:
            with self._conn as conn:
                if self.sendResponse(conn):
                    if self.sendAuth(conn):
                        if self.sendTempCook(conn, speed):
                            if self.sendAfterSpeed(conn):
                                if self._status == '00':
                                    answ1 = self.sendOn(conn)
                                if self.sendStatus(conn):
                                    self._time_upd = time.strftime("%H:%M")
                                    answ = True
        except:
            pass
        if not answ:
            i=i+1
            if i<5:
                answ = self.modeFan(speed, i)
            else:
                _LOGGER.warning('five attempts of modeFan failed')
        return answ

    async def async_modeFan(self, speed):
        await self.hass.async_add_executor_job(partial(self.modeFan, speed, 0))

    def modeIon(self, onoff, i=0):
        answ = False
        try:
            with self._conn as conn:
                if self.sendResponse(conn):
                    if self.sendAuth(conn):
                        if self.sendIonCmd(conn, onoff):
                            if self.sendStatus(conn):
                                self._time_upd = time.strftime("%H:%M")
                                answ = True
        except:
            pass
        if not answ:
            i=i+1
            if i<5:
                answ = self.modeIon(onoff, i)
            else:
                _LOGGER.warning('five attempts of modeIon failed')
        return answ

    async def async_modeIon(self, onoff):
        await self.hass.async_add_executor_job(partial(self.modeIon, onoff, 0))

    def modeTimeCook(self, hours, minutes, i=0):
        answ = False
        try:
            with self._conn as conn:
                if self.sendResponse(conn):
                    if self.sendAuth(conn):
                        if self.sendTimerCook(conn, hours, minutes):
                            if self.sendStatus(conn):
                                self._time_upd = time.strftime("%H:%M")
                                answ = True
        except:
            pass
        if not answ:
            i=i+1
            if i<5:
                answ = self.modeTimeCook(hours, minutes, i)
            else:
                _LOGGER.warning('five attempts of modeTimeCook failed')
        return answ

    async def async_modeTimeCook(self, hours, minutes):
        await self.hass.async_add_executor_job(partial(self.modeTimeCook, hours, minutes, 0))

    def modeOff(self, i=0):
        answ = False
        try:
            with self._conn as conn:
                if self.sendResponse(conn):
                    if self.sendAuth(conn):
                        if self.sendOff(conn):
                            if self.sendStatus(conn):
                                self._time_upd = time.strftime("%H:%M")
                                answ = True
        except:
            pass
        if not answ:
            i=i+1
            if i<5:
                answ = self.modeOff(i)
            else:
                _LOGGER.warning('five attempts of modeOff failed')
        return answ

    async def async_modeOff(self):
        await self.hass.async_add_executor_job(self.modeOff)

    def firstConnect(self, i=0):
        self.findType()
        iter = 0
        self._connected = False
        answ = False
        try:
            with self._conn as conn:
                while iter < 10:  # 10 attempts to auth
                    if self.sendResponse(conn):
                        if self.sendAuth(conn):
                            break
                    sleep(1)
                    iter+=1
                if self._connected:
                    if self.sendUseBackLight(conn):
                        if self.sendSync(conn):
                            if self.sendStatus(conn):
                                self._time_upd = time.strftime("%H:%M")
                                answ = True
        except:
            pass
        if not answ:
            i=i+1
            if i<5:
                self.firstConnect(i)
            else:
                _LOGGER.warning('five attempts of firstConnect failed')

    async def async_firstConnect(self):
        await self.hass.async_add_executor_job(self.firstConnect)

    def findType(self):
        #try:
        match_result = search(r'hci([\d]+)', self._device)
        if match_result is None:
            pass
        else:
            iface = int(match_result.group(1))
            scanner = btle.Scanner(iface=iface)
            ble_devices = {device.addr:str(device.getValueText(9)) for device in scanner.scan(3.0)}
            dev_name = ble_devices.get(self._mac, 'None')
            self._type = SUPPORTED_DEVICES.get(dev_name, 1)
            if dev_name != 'None':
                self._name = dev_name
        #except:
            #_LOGGER.error('unable to know the type of device...use default')

    def modeUpdate(self, i=0):
        answ = False
        try:
            with self._conn as conn:
                if self.sendResponse(conn):
                    if self.sendAuth(conn):
                        if self.sendSync(conn):
                            if self.sendStatus(conn):
                                self._time_upd = time.strftime("%H:%M")
                                answ = True
        except:
            pass
        if not answ:
            i=i+1
            if i<5:
                answ = self.modeUpdate(i)
            else:
                _LOGGER.warning('five attempts of modeUpdate failed')
        return answ

    async def async_modeUpdate(self):
        await self.hass.async_add_executor_job(self.modeUpdate)

    async def async_update(self, now, **kwargs) -> None:
        await self.async_modeUpdate()
