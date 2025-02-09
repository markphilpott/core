"""Type represenging a Lyngdorf MP40 or MP60 processor."""

import logging
import re
import socket

from .lyngdorf_sensors import LyngdorfSensors

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

    def _get_socket(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.ip_address, self.port))
        return s

    @staticmethod
    def _send_command(command: str, s: socket.socket):
        if not command.startswith("!"):
            command = "!" + command

        if not command.endswith("\r"):
            command = command + "\r"

        encoded_command = command.encode("utf-8")

        _LOGGER.info("Sending command %s", encoded_command)
        s.send(encoded_command)

    @staticmethod
    def _get_response(s: socket.socket):
        response = s.recv(1024).decode("utf-8").rstrip()
        _LOGGER.info("Received response %s", response)
        return response

    def _command_with_response(self, command) -> str:
        with self._get_socket() as s:
            self._send_command(command, s)
            return self._get_response(s)

    def _command_without_response(self, command):
        with self._get_socket() as s:
            self._send_command(command, s)

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

    def get_power_status(self):
        """Get power state of processor."""
        response = self._get_numeric_parameter_response("POWER?")
        if response == 0:
            return "STANDBY"
        if response == 1:
            return "ON"
        return "UNKNOWN POWER STATE"

    def get_is_mute(self):
        """Get mute status - 'ON' or 'OFF'."""
        response = self._get_text_response("!MUTE?")
        if response == "!MUTEON":
            return "ON"
        if response == "!MUTEOFF":
            return "OFF"
        return f"Unknown Mute response {response}"

    def test_ping(self):
        """Send a ping and check the response."""
        ping_response = self._get_text_response("PING?")
        _LOGGER.info("Equal?? %s", ping_response == "!PONG")
        return ping_response

    def get_volume(self) -> float:
        """Get current volume."""
        return self._get_numeric_parameter_response("!VOL?") / 10

    def get_current_source_id(self) -> int:
        """Get current source id."""
        return self._get_numeric_parameter_response("!SRC?")

    def get_current_source_name(self) -> str:
        """Get current source name."""
        current_source_id = self.get_current_source_id()
        return self._get_quoted_text_parameter_response(f"!SRC({current_source_id})?")

    def get_device_name(self) -> str:
        """Get device name."""
        return self._get_round_bracket_text_parameter_response("!DEVICE?")

    def connect(self) -> None:
        """Connect to processor."""
        if not self.test_ping():
            raise HostUnreachable("Ping failed")

    def async_update(self) -> LyngdorfSensors:
        """Get current state of processor."""
        return LyngdorfSensors(
            volume=self.get_volume(),
            source=self.get_current_source_name(),
            power_status=self.get_power_status(),
            mute_status=self.get_is_mute(),
            device_name=self.get_device_name(),
        )
