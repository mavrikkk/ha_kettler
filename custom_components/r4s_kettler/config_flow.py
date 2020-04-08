from . import DOMAIN
from datetime import timedelta
from homeassistant import config_entries
from homeassistant.const import (
    CONF_DEVICE,
    CONF_MAC,
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL
)

from re import match as matches
import voluptuous as vol

DEFAULT_DEVICE = 'hci0'
DEFAULT_SCAN_INTERVAL = 60

@config_entries.HANDLERS.register(DOMAIN)
class RedmondKettlerConfigFlow(config_entries.ConfigFlow):

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(self, user_input={}):
        if user_input:
            return await self.create_entry_if_valid(user_input)

        return self.show_form()

    def show_form(self, user_input={}, errors={}):
        device = user_input.get(CONF_DEVICE, DEFAULT_DEVICE)
        mac = user_input.get(CONF_MAC)
        password = user_input.get(CONF_PASSWORD)
        scan_interval = user_input.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        SCHEMA = vol.Schema({
            vol.Required(CONF_DEVICE, default=device): str,
            vol.Required(CONF_MAC, default=mac): str,
            vol.Required(CONF_PASSWORD, default=password): str,
            vol.Optional(CONF_SCAN_INTERVAL, default=scan_interval): int
        })
        return self.async_show_form(
            step_id='user', data_schema=SCHEMA, errors=errors
        )

    async def create_entry_if_valid(self, user_input):
        mac = user_input.get(CONF_MAC)
        password = user_input.get(CONF_PASSWORD)
        identifier = f'{DOMAIN}[{mac}]'
        if identifier in self._async_current_ids():
            return self.async_abort(reason='already_configured')

        mac_pattern = '^' + '[\:\-]'.join(['([0-9a-f]{2})']*6) + '$'
        if not matches(mac_pattern, mac.lower()):
            return self.show_form(
                user_input=user_input,
                errors={
                    'base': 'wrong_mac'
                }
            )

        if len(password) != 16:
            return self.show_form(
                user_input=user_input,
                errors={
                    'base': 'wrong_password'
                }
            )

        await self.async_set_unique_id(identifier)
        return self.async_create_entry(
            title=mac, data=user_input
        )
