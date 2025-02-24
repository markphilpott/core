"""Type represenging a Lyngdorf MP40 or MP60 processor."""

import logging
import re
import socket
import threading

logging.basicConfig(format="%(threadName)s:%(message)s")
_LOGGER = logging.getLogger(__name__)


class HostUnreachable(Exception):
    """Exception thrown when the processor cannot be contacted."""

    def __init__(self, host: str) -> None:
        """Create the exception."""
        self.host = host


class LyngdorfMPRawInterface:
    """Class to interact with LyngdorfMP amp."""

    def __init__(self, ip_address: str, port: int) -> None:
        """Store connection details."""
        self.ip_address = ip_address
        self.port = port
        # Only make one call to the processor at at time
        self._processor_lock = threading.Lock()
        self._processor_socket = self._get_socket()

    def _send_command(self, command: str) -> None:
        """Send command to processor."""
        if not command.startswith("!"):
            command = "!" + command

        _LOGGER.info("Sending command '%s'", command)

        if not command.endswith("\r"):
            command = command + "\r"

        encoded_command = command.encode("utf-8")
        self._processor_socket.send(encoded_command)

    def _get_response(self) -> str:
        """Get response from processor."""
        response = self._processor_socket.recv(1024).decode("utf-8").rstrip()
        _LOGGER.info("Received response '%s'", response)
        return response

    def _get_socket(self) -> socket.socket:
        """Open socket with processor."""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.ip_address, self.port))
        return s

    def command_with_response(self, command: str | None) -> str:
        """Send command if supplied, then fetch response."""
        with self._processor_lock:
            if command:
                self._send_command(command)
            return self._get_response()

    def command_without_response(self, command: str) -> None:
        """Send command which does not have response."""
        with self._processor_lock:
            self._send_command(command)

    def get_numeric_parameter_response(self, command: str) -> int:
        """For a response of the form !VOL(42) return 42."""
        response = self.command_with_response(command)
        return int(re.findall(r"-?\d+", response)[0])

    def get_quoted_text_parameter_response(self, command: str) -> str:
        """For response of the form '!SRC(4)"DVD"' return 'DVD'."""
        response = self.command_with_response(command)
        match = re.search(r"\"(.+)\"", response)
        return (
            match.group(1)
            if match
            else "ERROR - " + response + " did not match text parameter response"
        )

    def get_round_bracket_text_parameter_response(self, command: str) -> str:
        """For response of the form '!SRC(DEVICE NAME) return 'DEVICE NAME'."""
        response = self.command_with_response(command)
        match = re.search(r"\((.+)\)", response)
        return (
            match.group(1)
            if match
            else "ERROR - "
            + response
            + " did not match round bracket parameter response"
        )

    def get_text_response(self, command: str | None) -> str:
        """Get raw response."""
        return self.command_with_response(command)
