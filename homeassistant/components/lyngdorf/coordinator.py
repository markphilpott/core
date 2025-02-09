"""Coordinatior for Lyngdorf Processor."""

import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, UPDATE_INTERVAL
from .lyngdorf_processor.lyngdorf_mp import LyngdorfMP
from .lyngdorf_processor.lyngdorf_sensors import LyngdorfSensors

_LOGGER = logging.getLogger(__name__)


class LyngdorfDataUpdateCoordinator(DataUpdateCoordinator[LyngdorfSensors]):
    """Class to manage fetching data from Lyngdorf Processor."""

    def __init__(self, hass: HomeAssistant, lyngdorf: LyngdorfMP) -> None:
        """Initialize."""
        self.lyngdorf = lyngdorf

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
        )

    async def _async_update_data(self) -> LyngdorfSensors:
        """Update data via library."""
        try:
            return self.lyngdorf.async_update()
        except Exception as error:
            raise UpdateFailed(error) from error
