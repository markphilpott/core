"""Support for the Lyngdorf service."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
import logging

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import LyngdorfConfigEntry, LyngdorfDataUpdateCoordinator
from .const import DOMAIN
from .lyngdorf_processor.lyngdorf_sensors import LyngdorfSensors

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class LyngdorfSensorEntityDescription(SensorEntityDescription):
    """A class that describes sensor entities."""

    value: Callable[[LyngdorfSensors], StateType | datetime]


SENSOR_TYPES: tuple[LyngdorfSensorEntityDescription, ...] = (
    LyngdorfSensorEntityDescription(
        key="volume",
        translation_key="volume",
        entity_category=EntityCategory.DIAGNOSTIC,
        value=lambda data: data.volume,
    ),
    LyngdorfSensorEntityDescription(
        key="source",
        translation_key="source",
        entity_category=EntityCategory.DIAGNOSTIC,
        value=lambda data: data.source,
    ),
    LyngdorfSensorEntityDescription(
        key="power_status",
        translation_key="power_status",
        entity_category=EntityCategory.DIAGNOSTIC,
        value=lambda data: data.power_status,
    ),
    LyngdorfSensorEntityDescription(
        key="mute_status",
        translation_key="mute_status",
        entity_category=EntityCategory.DIAGNOSTIC,
        value=lambda data: data.mute_status,
    ),
    LyngdorfSensorEntityDescription(
        key="device_name",
        translation_key="device_name",
        entity_category=EntityCategory.DIAGNOSTIC,
        value=lambda data: data.device_name,
    ),
)

"""
    Do we need this?
    entity_registry = er.async_get(hass)
    old_unique_id = f"{coordinator.lyngdorf.serial.lower()}_b/w_counter"
    if entity_id := entity_registry.async_get_entity_id(
        PLATFORM, DOMAIN, old_unique_id
    ):
        new_unique_id = f"{coordinator.lyngdorf.serial.lower()}_bw_counter"
        _LOGGER.debug(
            "Migrating entity %s from old unique ID '%s' to new unique ID '%s'",
            entity_id,
            old_unique_id,
            new_unique_id,
        )
        entity_registry.async_update_entity(entity_id, new_unique_id=new_unique_id)
"""


async def async_setup_entry(
    hass: HomeAssistant,
    entry: LyngdorfConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add Lyngdorf entities from a config_entry."""
    coordinator = entry.runtime_data

    async_add_entities(
        LyngdorfSensor(coordinator, description)
        for description in SENSOR_TYPES
        if description.value(coordinator.data) is not None
    )


class LyngdorfSensor(CoordinatorEntity[LyngdorfDataUpdateCoordinator], SensorEntity):
    """Define an Lyngdorf sensor."""

    _attr_has_entity_name = True
    entity_description: LyngdorfSensorEntityDescription

    def __init__(
        self,
        coordinator: LyngdorfDataUpdateCoordinator,
        description: LyngdorfSensorEntityDescription,
    ) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._attr_device_info = DeviceInfo(
            # ip_address=f"{coordinator.lyngdorf.ip_address}",
            # port=f"{coordinator.lyngdorf.port}",
            name=coordinator.lyngdorf.name,
            identifiers={(DOMAIN, coordinator.lyngdorf.name)},
            manufacturer="Lyngdorf",
            model="XXXMODEL",  # coordinator.lyngdorf.model,
            sw_version="XXXSWVERSION",  # coordinator.lyngdorf.firmware,
        )
        self._attr_name = description.key
        self._attr_native_value = description.value(coordinator.data)
        self._attr_unique_id = f"{coordinator.lyngdorf.name.lower()}_{description.key}"
        self.entity_description = description

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = self.entity_description.value(self.coordinator.data)
        self.async_write_ha_state()
