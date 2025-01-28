"""The lyngdorf integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

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
    return True


# TD Update entry annotation
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up lyngdorf from a config entry."""

    return True


# TD Update entry annotation
async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return True
