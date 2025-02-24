"""Lyngdorf Processor Media Player Implementation."""

import logging

from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import LyngdorfConfigEntry
from .lyngdorf_processor.lyngdorf_mp import LyngdorfMP

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: LyngdorfConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add Lyngdorf entities from a config_entry."""
    lyngdorf_processor = entry.runtime_data.lyngdorf_processor
    if lyngdorf_processor is None:
        _LOGGER.warning("No processor passed to switch setup")
        return

    entities = [LyngdorfProcessorMediaPlayer(lyngdorf_processor=lyngdorf_processor)]
    async_add_entities(entities, True)


class LyngdorfProcessorMediaPlayer(MediaPlayerEntity):
    """Lyngdorf Processor Media Player."""

    def __init__(self, lyngdorf_processor: LyngdorfMP) -> None:
        """Set up state."""
        self.lyngdorf_processor = lyngdorf_processor
        self._attr_volume_step = 0.005
        # Lyngdorf does not send events when state changes - so need to poll
        self._attr_should_poll = True

    @property
    def supported_features(self) -> MediaPlayerEntityFeature:
        """Flag media player features that are supported."""
        return (
            MediaPlayerEntityFeature.VOLUME_SET
            | MediaPlayerEntityFeature.VOLUME_MUTE
            | MediaPlayerEntityFeature.SELECT_SOURCE
            | MediaPlayerEntityFeature.VOLUME_STEP
            | MediaPlayerEntityFeature.PLAY
            | MediaPlayerEntityFeature.NEXT_TRACK
            | MediaPlayerEntityFeature.PREVIOUS_TRACK
            | MediaPlayerEntityFeature.PAUSE
            | MediaPlayerEntityFeature.TURN_ON
            | MediaPlayerEntityFeature.TURN_OFF
        )

    def select_source(self, source: str) -> None:
        """Select input source from name."""
        _LOGGER.info("Setting source %s", source)
        self.lyngdorf_processor.select_source(source_name=source)

    def mute_volume(self, mute: bool) -> None:
        """Set mute state."""
        self.lyngdorf_processor.mute(mute=mute)

    def set_volume_level(self, volume: float) -> None:
        """Set volume from range (0...1)."""
        db = self._db_from_volume(volume=volume)
        _LOGGER.info("Setting db %d from volume %f", db, volume)
        self.lyngdorf_processor.set_decibels(db)

    def media_play(self) -> None:
        """Play/Pause."""
        self.lyngdorf_processor.play_pause()

    def media_pause(self) -> None:
        """Play/Pause."""
        self.lyngdorf_processor.play_pause()

    def media_next_track(self) -> None:
        """Next track."""
        self.lyngdorf_processor.next()

    def media_previous_track(self) -> None:
        """Previous track."""
        self.lyngdorf_processor.previous()

    def turn_on(self) -> None:
        """Turn processor on."""
        self.lyngdorf_processor.turn_on()

    def turn_off(self) -> None:
        """Turn processor on."""
        self.lyngdorf_processor.turn_off()

    def update(self) -> None:
        """Update latest state from processor."""
        current_state = self.lyngdorf_processor.get_state()
        _LOGGER.info("Current state: %s", str(current_state))
        self._attr_volume_level = self._volume_from_db(current_state.decibels or -999)
        self._attr_is_volume_muted = current_state.mute_status
        self._attr_name = current_state.device_name
        self._attr_source = current_state.source
        self._attr_source_list = current_state.sources
        self._attr_state = (
            MediaPlayerState.ON if current_state.is_on else MediaPlayerState.STANDBY
        )

    @staticmethod
    def _volume_from_db(db: int) -> float:
        """Given a decibel value in the range (-999...0), calculate a volume in the range (0...1)."""
        volume = (100 - (db / 10 * -1)) * 0.01
        _LOGGER.info("Computed volume %f from db %d", volume, db)
        return volume

    @staticmethod
    def _db_from_volume(volume: float) -> int:
        """Given a volume value in the range (0...1), calculate a decibel value in the range (-999...0)."""
        db = int(10 * ((100 - (volume / 0.01)) * -1))
        _LOGGER.info("Computed db %d from volume %f", db, volume)
        return db
