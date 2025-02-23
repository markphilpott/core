"""Type represenging a Lyngdorf MP40 or MP60 processor."""

import logging
import re
import socket
import threading

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

    def __init__(self, name: str, ip_address: str, port: int) -> None:
        """Store the specifics of the Lyngdorf."""
        self.name = name
        self.ip_address = ip_address
        self.port = port
        # Only make one call to the processor at at time
        self._processor_lock = threading.Lock()
        self._processor_socket = self._get_socket()

    def _send_command(self, command: str):
        if not command.startswith("!"):
            command = "!" + command

        _LOGGER.info("Sending command '%s'", command)

        if not command.endswith("\r"):
            command = command + "\r"

        encoded_command = command.encode("utf-8")
        self._processor_socket.send(encoded_command)

    def _get_response(self):
        response = self._processor_socket.recv(1024).decode("utf-8").rstrip()
        _LOGGER.info("Received response %s", response)
        return response

    def _get_socket(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.ip_address, self.port))
        return s

    def _command_with_response(self, command: str) -> str:
        with self._processor_lock:
            _LOGGER.info("%s calling %s", threading.get_ident(), command)
            self._send_command(command)
            response = self._get_response()
            _LOGGER.info(
                "%s called %s and got response %s",
                threading.get_ident(),
                command,
                response,
            )
            return response

    def _command_without_response(self, command):
        with self._processor_lock:
            self._send_command(command)

    def _get_numeric_parameter_response(self, command):
        response = self._command_with_response(command)
        return int(re.findall(r"-?\d+", response)[0])

    def _get_quoted_text_parameter_response(self, command):
        """For response of the form '!SRC(4)"DVD"' return 'DVD'."""
        response = self._command_with_response(command)
        return re.search(r"\"(.+)\"", response).group(1)

    def _get_round_bracket_text_parameter_response(self, command):
        """For response of the form '!SRC(DEVICE NAME) return 'DEVICE NAME'."""
        response = self._command_with_response(command)
        return re.search(r"\((.+)\)", response).group(1)

    def _get_text_response(self, command):
        return self._command_with_response(command)

    def get_power_status(self) -> str:
        """Get power state of processor."""
        response = self._get_numeric_parameter_response("POWER?")
        if response == 0:
            return "STANDBY"
        if response == 1:
            return "ON"
        return "UNKNOWN POWER STATE"

    def turn_on(self) -> None:
        """Turn on processor."""
        self._command_without_response("POWERONMAIN")

    def turn_off(self) -> None:
        """Turn off processor."""
        self._command_without_response("POWEROFFMAIN")

    def is_on(self) -> bool:
        """Whether the processor is currently on."""
        return self.get_power_status() == "ON"

    def get_is_mute(self) -> bool:
        """Get mute status - 'ON' or 'OFF'."""
        response = self._get_text_response("!MUTE?")
        if response == "!MUTEON":
            return True
        return False

    def mute(self, mute: bool) -> None:
        """Set mute state."""
        command = "MUTEON" if mute else "MUTEOFF"
        self._command_without_response(command=command)

    def unmute(self) -> None:
        """Engage mute."""
        self._command_without_response("MUTEOFF")

    def test_ping(self):
        """Send a ping and check the response."""
        ping_response = self._get_text_response("PING?")
        _LOGGER.info("Equal?? %s", ping_response == "!PONG")
        return ping_response

    def get_decibels(self) -> int:
        """Get current decibels."""
        return self._get_numeric_parameter_response("!VOL?")

    def set_decibels(self, decibels: int) -> None:
        """Set decibels."""
        self._command_without_response(f"!VOL({decibels})")

    def get_current_source_id(self) -> int:
        """Get current source id."""
        return self._get_numeric_parameter_response("!SRC?")

    def get_current_source_name(self) -> str:
        """Get current source name."""
        return self._get_source_name(self.get_current_source_id())

    def _get_source_name(self, source_id) -> str:
        """Get name of given source."""
        return self._get_quoted_text_parameter_response(f"!SRC({source_id})?")

    def select_source(self, source_name: str) -> None:
        """Select source given the name."""
        source_index = self.get_available_source_names().index(source_name)
        _LOGGER.info("Source %s has index %d", source_name, source_index)
        self._command_without_response(f"!SRC({source_index})")

    def get_available_source_names(self) -> list[str]:
        """Get list of available sources."""
        # '!SRC(0)"SHIELD"\r!SRC(1)"PC"\r!SRC(2)"NOW TV"\r!SRC(3)"MUSIC"'
        number_of_available_sources = self._get_numeric_parameter_response("!SRCS?")
        # switch to this string instead of multiple calls
        # sources = self._get_response()
        available_sources = [
            self._get_source_name(i) for i in range(number_of_available_sources)
        ]
        _LOGGER.info("Found Sources %s", available_sources)
        return available_sources

    def get_device_name(self) -> str:
        """Get device name."""
        return self._get_round_bracket_text_parameter_response("!DEVICE?")

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
            power_status=self.get_power_status(),
            mute_status=self.get_is_mute(),
            device_name=self.get_device_name(),
        )
