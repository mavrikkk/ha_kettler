from . import DOMAIN
from datetime import timedelta
from homeassistant import config_entries
from homeassistant.const import (
    CONF_DEVICE,
    CONF_MAC,
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL
)

from bluepy.btle import Scanner
from re import search
from subprocess import check_output
from re import match as matches
from voluptuous import Schema, Required, Optional, In

CONF_USE_BACKLIGHT = 'use_backlight'

DEFAULT_DEVICE = "hci0"
DEFAULT_SCAN_INTERVAL = 30
DEFAULT_USE_BACKLIGHT = True

#@config_entries.HANDLERS.register(DOMAIN)
class RedmondKettlerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    def __init__(self):
        self._hci_devices = {}
        self._ble_devices = {}
        self._use_backlight = {True:True, False:False}
        self.get_devices()
        self.data = {}

    async def async_step_user(self, user_input={}):
        if user_input:
            return await self.check_valid(user_input)
        return self.show_form()

    async def async_step_info(self, user_input={}):
        return await self.create_entryS()

    def show_form(self, user_input={}, errors={}):
        device = user_input.get(CONF_DEVICE, DEFAULT_DEVICE)
        mac = user_input.get(CONF_MAC)
        password = user_input.get(CONF_PASSWORD)
        scan_interval = user_input.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        backlight = user_input.get(CONF_USE_BACKLIGHT, DEFAULT_USE_BACKLIGHT)
        SCHEMA = Schema({
            Required(CONF_DEVICE, default=device): In(self._hci_devices),
            Required(CONF_MAC, default=mac): In(self._ble_devices),
            Required(CONF_PASSWORD, default=password): str,
            Optional(CONF_SCAN_INTERVAL, default=scan_interval): int,
            Optional(CONF_USE_BACKLIGHT, default=backlight): In(self._use_backlight)
        })
        return self.async_show_form(
            step_id='user', data_schema=SCHEMA, errors=errors
        )

    def show_form_info(self):
        return self.async_show_form(step_id='info')

    async def create_entryS(self):
        mac = self.data.get(CONF_MAC)
        identifier = f'{DOMAIN}[{mac}]'
        await self.async_set_unique_id(identifier)
        return self.async_create_entry(
            title=mac, data=self.data
        )

    async def check_valid(self, user_input):
        mac = user_input.get(CONF_MAC)
        password = user_input.get(CONF_PASSWORD)
        scan_interval = user_input.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        identifier = f'{DOMAIN}[{mac}]'
        if identifier in self._async_current_ids():
            return self.async_abort(reason='already_configured')

        if len(password) != 16:
            return self.show_form(
                user_input=user_input,
                errors={
                    'base': 'wrong_password'
                }
            )

        if scan_interval < 10 or scan_interval > 300:
            return self.show_form(
                user_input=user_input,
                errors={
                    'base': 'wrong_scan_interval'
                }
            )
        self.data = user_input
        return self.show_form_info()

    def get_devices(self):
        first_hci = 'hci0'
        try:
            byte_output = check_output(['hciconfig'])
            string_output = byte_output.decode('utf-8')
            lines = string_output.splitlines()
            hci_devices = [line.split(':')[0] for line in lines if 'hci' in line]
            self._hci_devices = {line:line for line in hci_devices}
            first_hci = hci_devices[0]
        except:
            self._hci_devices = {'hci0':'hci0'}
        try:
            match_result = search(r'hci([\d]+)', first_hci)
            if match_result is None:
                pass
            else:
                iface = int(match_result.group(1))
                scanner = Scanner(iface=iface)
                self._ble_devices = {str(device.addr):str(device.getValueText(9))+','+str(device.addr) for device in scanner.scan(3.0)}
        except:
            pass
