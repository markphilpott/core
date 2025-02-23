"""The Lyngdorf Processor component."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .coordinator import LyngdorfDataUpdateCoordinator
from .lyngdorf_processor.lyngdorf_mp import LyngdorfMP

PLATFORMS = [Platform.MEDIA_PLAYER]

type LyngdorfConfigEntry = ConfigEntry[LyngdorfDataUpdateCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: LyngdorfConfigEntry) -> bool:
    """Set up Lyngdorf Processor from a config entry."""
    name = entry.data[CONF_NAME]
    host = entry.data[CONF_HOST]
    port = entry.data[CONF_PORT]

    try:
        lyngdorf_mp = LyngdorfMP(name, host, port)
        lyngdorf_mp.connect()
    except Exception as error:
        raise ConfigEntryNotReady from error

    coordinator = LyngdorfDataUpdateCoordinator(hass, lyngdorf_mp)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: LyngdorfConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
