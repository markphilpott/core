"""Setup code."""

import logging
import re
import socket

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import UnitOfSoundPressure
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

_LOGGER = logging.getLogger(__name__)


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up of Volume button."""
    _LOGGER.info("Adding Volume Entity")
    add_entities([LyngdorfVolume()], True)


class LyngdorfVolume(SensorEntity):
    """Volume entity."""

    _attr_has_entity_name = True

    def __init__(self):
        """Init."""
        self._ip = "192.168.1.71"
        self._port = 84
        self._buffer_size = 1024

        _LOGGER.info("In volume init")

    @property
    def name(self):
        """Name."""
        return "Current Volume"

    @property
    def state(self):
        """Get current volume."""
        _LOGGER.info("Getting volume")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as lyngdorf_socket:
            lyngdorf_socket.connect((self._ip, self._port))
            lyngdorf_socket.send(b"!VOL?\r")
            response = lyngdorf_socket.recv(self._buffer_size).decode("utf-8")
            return int(re.findall(r"\-?\d+", response)[0]) / 10

    @property
    def unit_of_measurement(self):
        """Unit."""
        return UnitOfSoundPressure.DECIBEL
