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

DEFAULT_DEVICE = "hci0"
DEFAULT_SCAN_INTERVAL = 60

@config_entries.HANDLERS.register(DOMAIN)
class RedmondKettlerConfigFlow(config_entries.ConfigFlow):

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    def __init__(self):
        self._hci_devices = {}
        self._ble_devices = {}
        self.get_devices()

    async def async_step_user(self, user_input={}):
        if user_input:
            return await self.create_entry_if_valid(user_input)

        return self.show_form()

    def show_form(self, user_input={}, errors={}):
        device = user_input.get(CONF_DEVICE, DEFAULT_DEVICE)
        mac = user_input.get(CONF_MAC)
        password = user_input.get(CONF_PASSWORD)
        scan_interval = user_input.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        SCHEMA = Schema({
            Required(CONF_DEVICE, default=device): In(self._hci_devices),
            Required(CONF_MAC, default=mac): In(self._ble_devices),
            Required(CONF_PASSWORD, default=password): str,
            Optional(CONF_SCAN_INTERVAL, default=scan_interval): int
        })
        return self.async_show_form(
            step_id='user', data_schema=SCHEMA, errors=errors
        )

    async def create_entry_if_valid(self, user_input):
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

        if scan_interval < 30:
            return self.show_form(
                user_input=user_input,
                errors={
                    'base': 'wrong_scan_interval'
                }
            )

        await self.async_set_unique_id(identifier)
        return self.async_create_entry(
            title=mac, data=user_input
        )

    def get_devices(self):
        first_hci = 'hci0'

        byte_output = check_output(['hciconfig'])
        string_output = byte_output.decode('utf-8')
        lines = string_output.splitlines()
        hci_devices = [line.split(':')[0] for line in lines if 'hci' in line]
        self._hci_devices = {line:line for line in hci_devices}
        first_hci = hci_devices[0]

        match_result = search(r'hci([\d]+)', first_hci)
        if match_result is None:
            pass
        else:
            iface = int(match_result.group(1))
            scanner = Scanner(iface=iface)
            self._ble_devices = {device.addr:device.addr for device in scanner.scan(3.0)}
