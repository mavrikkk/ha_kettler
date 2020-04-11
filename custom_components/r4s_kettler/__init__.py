"""Support for Redmond Kettler G200S"""

#!/usr/local/bin/python3
# coding: utf-8

import pexpect
from time import sleep
import time
from datetime import datetime
from textwrap import wrap
import logging

from datetime import timedelta

from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import async_track_time_interval
import homeassistant.util.color as color_util
from homeassistant.const import (
    CONF_DEVICE,
    CONF_MAC,
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL
)

CONF_MIN_TEMP = 40
CONF_MAX_TEMP = 100
CONF_TARGET_TEMP = 100

REQUIREMENTS = ['pexpect']

_LOGGER = logging.getLogger(__name__)

SUPPORTED_DOMAINS = ["water_heater", "sensor", "light", "switch"]

DOMAIN = "r4s_kettler"

async def async_setup(hass, config):
    return True

async def async_setup_entry(hass, config_entry):
    hass.data[DOMAIN] = {}

    config = config_entry.data

    mac = config.get(CONF_MAC)
    device = config.get(CONF_DEVICE)
    password = config.get(CONF_PASSWORD)
    scan_delta = timedelta(
        seconds=config.get(CONF_SCAN_INTERVAL)
    )

    device_registry = await dr.async_get_registry(hass)
    device_registry.async_get_or_create(
        config_entry_id=config_entry.entry_id,
        connections={(dr.CONNECTION_NETWORK_MAC, mac)},
        name="SkyKettle",
        model="G200S",
        manufacturer="Redmond"
    )

    kettler = hass.data[DOMAIN]["kettler"] = RedmondKettler(
        hass,
        mac,
        password,
        device
    )
    try:
        await kettler.firstConnect()
    except:
        _LOGGER.warning(
            "Connect to Kettler %s through device %s failed", mac, device)

    async_track_time_interval(hass, kettler.async_update, scan_delta)
    for domain in SUPPORTED_DOMAINS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(config_entry, domain)
        )

    return True


async def async_remove_entry(hass, entry):
    """Unload a config entry."""
    try:
        for domain in SUPPORTED_DOMAINS:
            await hass.config_entries.async_forward_entry_unload(entry, domain)
    except ValueError:
        pass


class RedmondKettler:

    def __init__(self, hass, addr, key, device):
        self.hass = hass
        self._mac = addr
        self._key = key
        self._device = device
        self._mntemp = CONF_MIN_TEMP
        self._mxtemp = CONF_MAX_TEMP
        self._tgtemp = CONF_TARGET_TEMP
        self._temp = 0
        self._Watts = 0
        self._alltime = 0
        self._times = 0
        self._time_upd = '00:00'
        self._boiltime = '80'
        self._rgb1 = '0000ff'
        self._rgb2 = 'ff0000'
        self._rand = '5e'
        self._mode = '00' # '00' - boil, '01' - heat to temp, '03' - backlight
        self._status = '00' #may be '00' - OFF or '02' - ON
        self._usebacklight = True
        self._hold = False
        self._iter = 0
        self._connected = False
        self._is_busy = False
        self.child = None



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

    def theLightIsOn(self):
        if self._status == '02' and self._mode == '03':
            return True
        return False

    def theKettlerIsOn(self):
        if self._status == '02':
            if self._mode == '00' or self._mode == '01':
                return True
        return False

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



    async def async_update(self, now, **kwargs) -> None:
        try:
            await self.modeUpdate()
        except:
            _LOGGER.warning("Update failed")
            return
        async_dispatcher_send(self.hass, DOMAIN)



    def sendResponse(self):
        answ = False
        try:
            self.child.sendline("char-write-cmd 0x000c 0100") #send packet to receive messages in future
            self.child.expect(r'\[LE\]>')
            answ = True
        except:
            answ = False
            _LOGGER.error('error subscription')
        return answ

    def sendAuth(self):
        answer = False
        try:
            self.child.sendline("char-write-req 0x000e 55" + self.decToHex(self._iter) + "ff" + self._key + "aa") #send authorise key
            self.child.expect("value: ") # wait for response
            self.child.expect("\r\n") # wait for end string
            connectedStr = self.child.before[0:].decode("utf-8") # answer from device
            answ = connectedStr.split()[3] # parse: 00 - no   01 - yes
            self.child.expect(r'\[LE\]>')
            if answ == '01':
                answer = True
            self.iterase()
        except:
            answer = False
            _LOGGER.error('error auth')
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
            _LOGGER('error mode ON')
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
            _LOGGER.error('error mode OFF')
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
            _LOGGER.error('error sync time')
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
            _LOGGER.error('error get statistic')
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
            self.child.expect(r'\[LE\]>')
            self.iterase()
            answ = True
        except:
            answ = False
            _LOGGER.error('error get status')
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
            _LOGGER.error('error set mode')
        return answ

    def sendUseBackLight(self, use = True):
        answ = False
        onoff="00"
        if use:
            onoff="01"
        try:
            self.child.sendline("char-write-req 0x000e 55" + self.decToHex(self._iter) + "37c8c8" + onoff + "aa") #  onoff: 00 - off, 01 - on
            self.child.expect("value: ")
            self.child.expect("\r\n")
            self.child.expect(r'\[LE\]>')
            self.iterase()
            answ = True
        except:
            answ = False
            _LOGGER.error('error set use backlight')
        return answ

    def sendGetLights(self, boilOrLight = "01"): # night light by default
        answ = False
        try:
            self.child.sendline("char-write-req 0x000e 55" + self.decToHex(self._iter) + "33" + boilOrLight + "aa") # status of lights
            self.child.expect("value: ")
            self.child.expect("\r\n")
            statusStr = self.child.before[0:].decode("utf-8") # answer from device example 55 xx 06 00 00 00 00 01 2a 1e 00 00 00 00 00 00 80 00 00 aa
            answer = statusStr.split()
            self._rand = str(answer[5])
            if boilOrLight == '01':
                self._rgb1 = str(answer[6]) + str(answer[7]) + str(answer[8])
                self._rgb2 = str(answer[16]) + str(answer[17]) + str(answer[18])
            self.child.expect(r'\[LE\]>')
            self.iterase()
            answ = True
        except:
            answ = False
            _LOGGER.error('error get lights')
        return answ

    def sendSetLights(self, boilOrLight = '00', rgb1 = '0000ff', rgb2 = 'ff0000'): # 00 - boil light    01 - backlight
        answ = False
        try:
            if rgb1 == '0000ff' and rgb2 == 'ff0000':
                rgb_mid = '00ff00'
            else:
                rgb_mid = self.calcMidColor(rgb1,rgb2)
            if boilOrLight == "00":
                scale_light = ['28', '46', '64']
            else:
                scale_light = ['00', '32', '64']
            self.child.sendline("char-write-req 0x000e 55" + self.decToHex(self._iter) + "32" + boilOrLight + scale_light[0] + self._rand + rgb1 + scale_light[1] + self._rand + rgb_mid + scale_light[2] + self._rand + rgb2 + "aa")
            self.child.expect("value: ")
            self.child.expect("\r\n")
            self.child.expect(r'\[LE\]>')
            self.iterase()
            answ = True
        except:
            answ = False
            _LOGGER.error('error set colors of light')
        return answ

### composite methods
    def connect(self):
        answ = False
        if self._is_busy:
            self.disconnect()
        try:
            self._is_busy = True
            self.child = pexpect.spawn("gatttool --adapter=" + self._device + " -I -t random -b " + self._mac, ignore_sighup=False)
            self.child.expect(r'\[LE\]>', timeout=1)
            self.child.sendline("connect")
            self.child.expect(r'Connection successful.*\[LE\]>', timeout=1)
            self._is_busy = False
            answ = True
        except:
            _LOGGER.error('error connect')
        return answ

    def disconnect(self):
        self._is_busy = True
        if self.child != None:
            self.child.sendline("exit")
        self.child = None
        self._is_busy = False

    def reset(self):
        self._is_busy = True
        if self.child != None:
            self.child.sendline("exit")
        self._connected = False
        self._tgtemp = CONF_TARGET_TEMP
        self._temp = 0
        self._Watts = 0
        self._alltime = 0
        self._times = 0
        self._time_upd = '00:00'
        self._boiltime = '80'
        self._rgb1 = '0000ff'
        self._rgb2 = 'ff0000'
        self._rand = '5e'
        self._iter = 0
        self._mode = '00'
        self._status = '00'
        self._usebacklight = True
        self._hold = False
        self.child = None
        self._is_busy = False

    async def readNightColor(self):
        return self.sendGetLights()

    async def startNightColor(self):
        if not self._is_busy:
            self._is_busy = True
            answ = False
            try:
                if self.connect():
                    if self.sendResponse():
                        if self.sendAuth():
                            if self.sendSetLights('01', self._rgb1, self._rgb1):
                                if self.sendMode('03', '00'):
                                    if self.sendOn():
                                        if self.sendStatus():
                                            answ = True
            except:
                _LOGGER.error('error composite writeNightColor')
                self.reset()
            self.disconnect()
            return answ
        else:
            _LOGGER.info('device is busy now')
            return False

    async def stopNightColor(self):
        await self.modeOff()

    async def modeOn(self, mode = "00", temp = "00"):
        if not self._is_busy:
            self._is_busy = True
            answ = False
            try:
                if self.connect():
                    if self.sendResponse():
                        if self.sendAuth():
                            if self.sendMode(mode, temp):
                                if self.sendOn():
                                    if self.sendStatus():
                                        answ = True
            except:
                _LOGGER.error('error composite modeOn')
                self.reset()
            self.disconnect()
            return answ
        else:
            _LOGGER.info('device is busy now')
            return False

    async def modeOff(self):
        if not self._is_busy:
            self._is_busy = True
            answ = False
            try:
                if self.connect():
                    if self.sendResponse():
                        if self.sendAuth():
                            if self.sendOff():
                                if self.sendStatus():
                                    answ = True
            except:
                _LOGGER.error('error composite modeOff')
                self.reset()
            self.disconnect()
            return answ
        else:
            _LOGGER.info('device is busy now')
            return False

    async def firstConnect(self):
        self._is_busy = True
        iter = 0
        answ = False
        try:
            if self.connect():
                while iter < 10:  # 10 attempts to auth
                    answer = False
                    if self.sendResponse():
                        if self.sendAuth():
                            answer = True
                            break
                    sleep(1)
                    iter+=1
                if answer:
                    if self.sendUseBackLight(self._usebacklight):
                        if self.sendSetLights():
                            if self.sendSync():
                                if self.sendStat():
                                    if self.sendStatus():
                                        self._time_upd = time.strftime("%H:%M")
                                        answ = True
        except:
            _LOGGER.error('error first connect')
            self.reset()
        if answ:
            self._connected = True
            self.disconnect()
        else:
            _LOGGER.error('error first connect')
            self.reset()

    async def modeUpdate(self):
        if not self._is_busy:
            self._is_busy = True
            answ = False
            try:
                if self.connect():
                    if self.sendResponse():
                        if self.sendAuth():
                            if self.sendUseBackLight(self._usebacklight):
                                if self.sendSync():
                                    if self.sendStat():
                                        if self.sendStatus():
                                            self._time_upd = time.strftime("%H:%M")
                                            answ = True
            except:
                _LOGGER.error('error update')
                self.reset()
            self.disconnect()
            if self._mode == '01' and self._status == '02' and self._temp >= self._tgtemp and self._hold == False:
                self.modeOff()
            return answ
        else:
            _LOGGER.info('device is busy now')
            return False
