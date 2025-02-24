"""Type represenging a Lyngdorf MP40 or MP60 processor."""

import logging

from .lyngdorf_mp_raw_interface import LyngdorfMPRawInterface
from .lyngdorf_sensors import LyngdorfSensors

logging.basicConfig(format="%(threadName)s:%(message)s")
_LOGGER = logging.getLogger(__name__)


class HostUnreachable(Exception):
    """Exception thrown when the processor cannot be contacted."""

    def __init__(self, host: str) -> None:
        """Create the exception."""
        self.host = host


class LyngdorfMP:
    """Class to interact with LyngdorfMP amp."""

    def __init__(
        self, name: str, processor_raw_interface: LyngdorfMPRawInterface
    ) -> None:
        """Store the specifics of the Lyngdorf."""
        self.name = name
        self.processor_raw_interface = processor_raw_interface

    def turn_on(self) -> None:
        """Turn on processor."""
        self.processor_raw_interface.command_without_response("POWERONMAIN")

    def turn_off(self) -> None:
        """Turn off processor."""
        self.processor_raw_interface.command_without_response("POWEROFFMAIN")

    def is_on(self) -> bool:
        """Whether the processor is currently on."""
        return (
            self.processor_raw_interface.get_numeric_parameter_response("POWER?") == 1
        )

    def get_is_mute(self) -> bool:
        """Get mute status - 'ON' or 'OFF'."""
        response = self.processor_raw_interface.get_text_response("!MUTE?")
        if response == "!MUTEON":
            return True
        return False

    def mute(self, mute: bool) -> None:
        """Set mute state."""
        command = "MUTEON" if mute else "MUTEOFF"
        self.processor_raw_interface.command_without_response(command=command)

    def unmute(self) -> None:
        """Engage mute."""
        self.processor_raw_interface.command_without_response("MUTEOFF")

    def test_ping(self):
        """Send a ping and check the response."""
        ping_response = self.processor_raw_interface.get_text_response("PING?")
        _LOGGER.info("Equal?? %s", ping_response == "!PONG")
        return ping_response

    def get_decibels(self) -> int:
        """Get current decibels."""
        return self.processor_raw_interface.get_numeric_parameter_response("!VOL?")

    def set_decibels(self, decibels: int) -> None:
        """Set decibels."""
        self.processor_raw_interface.command_without_response(f"!VOL({decibels})")

    def get_current_source_id(self) -> int:
        """Get current source id."""
        return self.processor_raw_interface.get_numeric_parameter_response("!SRC?")

    def get_current_source_name(self) -> str:
        """Get current source name."""
        return self._get_source_name(self.get_current_source_id())

    def _get_source_name(self, source_id) -> str:
        """Get name of given source."""
        return self.processor_raw_interface.get_quoted_text_parameter_response(
            f"!SRC({source_id})?"
        )

    def select_source(self, source_name: str) -> None:
        """Select source given the name."""
        source_index = self.get_available_source_names().index(source_name)
        _LOGGER.info("Source %s has index %d", source_name, source_index)
        self.processor_raw_interface.command_without_response(f"!SRC({source_index})")

    def play_pause(self) -> None:
        """Press Play button."""
        self.processor_raw_interface.command_without_response("!PLAY")

    def next(self) -> None:
        """Press Next button."""
        self.processor_raw_interface.command_without_response("!NEXT")

    def previous(self) -> None:
        """Press Previous button."""
        self.processor_raw_interface.command_without_response("!PREV")

    def get_available_source_names(self) -> list[str]:
        """Get list of available sources."""
        # '!SRC(0)"SHIELD"\r!SRC(1)"PC"\r!SRC(2)"NOW TV"\r!SRC(3)"MUSIC"'
        number_of_available_sources = (
            self.processor_raw_interface.get_numeric_parameter_response("!SRCS?")
        )
        # Command !SRCS? has two responses - first the count of sources, then the list of sources.
        # This means we must call 'get response' twice.
        sources_string = self.processor_raw_interface.get_text_response(None)
        _LOGGER.info("Sources text list '%s'", sources_string)
        available_sources = sources_string.split('"')[1::2]
        _LOGGER.info(
            "Found Sources %s.  Expected %d Actual %d",
            available_sources,
            number_of_available_sources,
            len(available_sources),
        )
        return available_sources

    def get_device_name(self) -> str:
        """Get device name."""
        return self.processor_raw_interface.get_round_bracket_text_parameter_response(
            "!DEVICE?"
        )

    def connect(self) -> None:
        """Connect to processor."""
        if not self.test_ping():
            raise HostUnreachable("Ping failed")

    def get_state(self) -> LyngdorfSensors:
        """Get current state of processor."""
        return LyngdorfSensors(
            decibels=self.get_decibels(),
            source=self.get_current_source_name(),
            sources=self.get_available_source_names(),
            is_on=self.is_on(),
            mute_status=self.get_is_mute(),
            device_name=self.get_device_name(),
        )
