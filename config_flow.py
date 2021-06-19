import logging

import voluptuous as vol
import traceback

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from .api import BWTPerlaApi
from .const import (
    CONF_CODE,
    CONF_HOST,
    CONF_SYNC_INTERVAL,
    DEFAULT_SYNC_INTERVAL,
    DOMAIN,
    PLATFORMS,
)

_LOGGER = logging.getLogger(__name__)


class BWTPerlaFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        self._errors = {}

    async def async_step_user(self, user_input=None):
        self._errors = {}

        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            valid = await self._test_credentials(
                user_input[CONF_HOST], user_input[CONF_CODE]
            )
            if valid:
                return self.async_create_entry(
                    title=user_input[CONF_HOST], data=user_input
                )
            else:
                self._errors["base"] = "auth"

            return await self._show_config_form(user_input)

        return await self._show_config_form(user_input)

    async def _show_config_form(self, user_input):  # pylint: disable=unused-argument
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {vol.Required(CONF_HOST): str, vol.Required(CONF_CODE): str}
            ),
            errors=self._errors,
        )

    async def _test_credentials(self, host, code):
        try:
            api = BWTPerlaApi(host, code)
            await self.hass.async_add_executor_job(api.get_data)
            return True
        except Exception as ex:  # pylint: disable=broad-except
            _LOGGER.error(
                f"{DOMAIN} Exception in login : %s - traceback: %s",
                ex,
                traceback.format_exc(),
            )
        return False

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return BWTPerlaOptionsFlowHandler(config_entry)


class BWTPerlaOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry
        self.options = dict(config_entry.options)

    async def async_step_init(self, user_input=None):  # pylint: disable=unused-argument
        return await self.async_step_user()

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            self.options.update(user_input)
            return await self._update_options()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_SYNC_INTERVAL,
                        default=self.options.get(
                            CONF_SYNC_INTERVAL, DEFAULT_SYNC_INTERVAL
                        ),
                    ): vol.All(vol.Coerce(int))
                }
            ),
        )

    async def _update_options(self):
        return self.async_create_entry(
            title=self.config_entry.data.get(CONF_SYNC_INTERVAL), data=self.options
        )
