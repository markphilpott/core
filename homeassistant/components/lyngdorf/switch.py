"""Send commands to Lyngdorf Processor for changing volume, source etc."""

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import DiscoveryInfoType

from . import LyngdorfMP

_LOGGER = logging.getLogger(__name__)


def async_setup_entry(
    hass: HomeAssistant,
    config: ConfigEntry,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Lyngdorf switch platform setup."""
    lyngdorf = config.runtime_data.lyngdorf
    if lyngdorf is None:
        _LOGGER.warning("No processor passed to switch setup")
        return

    entities = [LyngdorfPowerSwitch(lyngdorf=lyngdorf)]
    add_entities(entities, True)


class LyngdorfPowerSwitch(SwitchEntity):
    """Lyngdorf power switch."""

    def __init__(self, lyngdorf: LyngdorfMP) -> None:
        """Set up power switch."""
        self.lyngdorf = lyngdorf
        self._attr_unique_id = f"{self.lyngdorf.name.lower()}_power_switch"

    @property
    def name(self) -> str:
        """Switch name."""
        return f"{self.lyngdorf.name} Power Switch"

    def log_registration(self) -> None:
        """Log registration."""
        _LOGGER.debug(
            "Registered LyngdorfPowerSwitch integration with Home Assistant for Lyngdord %s",
            self.lyngdorf.name,
        )

    @property
    def is_on(self) -> bool:
        """Return true if Lyngdorf is on."""
        return self.lyngdorf.get_power_status() == "ON"

    def turn_on(self, **kwargs: Any) -> None:
        """Turn on Lyngdorf."""
        self.lyngdorf.turn_on()
        self._attr_is_on = True

    def turn_off(self, **kwargs: Any) -> None:
        """Turn off Lyngdorf."""
        self.lyngdorf.turn_off()
        self._attr_is_on = False
