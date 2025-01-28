"""Config flow for Lyngdorf."""

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.helpers import config_validation as cv

from .const import DEFAULT_TCP_PORT, DOMAIN

_LOGGER = logging.getLogger(__name__)


class ExampleConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Example config flow."""

    # The schema version of the entries that it creates
    # Home Assistant will call your migrate method if the version changes
    _LOGGER.info("IN FLOW")
    VERSION = 1
    MINOR_VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Manage the options."""

        _LOGGER.info("Config flow async step init")

        settings_schema = vol.Schema(
            {
                vol.Required(CONF_HOST, default="192.168.1.71"): cv.string,
                vol.Optional(CONF_PORT, default=DEFAULT_TCP_PORT): cv.port,
            }
        )

        if user_input is None:
            return self.async_show_form(step_id="init", data_schema=settings_schema)

        return self.async_create_entry(title="", data=user_input)

    async def async_step_init(
        self, user_input: dict[str, str] | None = None
    ) -> ConfigFlowResult:
        """Handle the step of the form."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): cv.string,
                    vol.Optional(CONF_PORT, default=DEFAULT_TCP_PORT): cv.port,
                }
            ),
        )
