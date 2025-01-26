"""The lyngdorf_simple integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.discovery import load_platform

# List the platforms that you want to support.
# For your initial PR, limit it to 1 platform.
PLATFORMS: list[Platform] = [Platform.SENSOR]

# TD Create ConfigEntry type alias with API object
# TD Rename type alias and update all entry annotations
# type New_NameConfigEntry = ConfigEntry[MyApi]

_LOGGER = logging.getLogger(__name__)
DOMAIN = "lyngdorf"


def setup(hass: HomeAssistant, config: ConfigEntry) -> bool:
    """Lyngdorf Setup."""
    hass.states.set("lyngdorf_state.my_state", "my_value")

    _LOGGER.info("In Lyngdorf Setup")

    for platform in PLATFORMS:
        load_platform(hass, platform, DOMAIN, {}, {})

    # Return boolean to indicate that initialization was successful.
    return True


# TD Update entry annotation
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up lyngdorf_simple from a config entry."""

    # TD 1. Create API instance
    # TD 2. Validate the API connection (and authentication)
    # TD 3. Store an API object for your platforms to access
    # entry.runtime_data = MyAPI(...)

    # await hass.config_entries.async_forward_entry_setups(entry, _PLATFORMS)

    return True


# TD Update entry annotation
async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # return await hass.config_entries.async_unload_platforms(entry, _PLATFORMS)
    return True
