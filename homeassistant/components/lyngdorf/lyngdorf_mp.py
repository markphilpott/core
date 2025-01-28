"""Type represenging a Lyngdorf MP40 or MP60 processor."""

import re
from socket import socket

from .const import DEFAULT_TCP_PORT


class HostUnreachable(Exception):
    """Exception thrown when the processor cannot be contacted."""

    def __init__(self, host: str) -> None:
        """Create the exception."""
        self.host = host


class LyngdorfMP:
    """Class to interact with LyngdorfMP amp."""

    def __init__(self, ip_address: str, tcp_port: int = DEFAULT_TCP_PORT) -> None:
        """Store the ip address and port of the Lyngdorf."""
        self.ip_address = ip_address
        self.tcp_port = tcp_port

    def _get_socket(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(self.ip_address, self.tcp_port)
        return s

    @staticmethod
    def _send_command(command: str, s: socket):
        if not command.startswith("!"):
            command = "!" + command

        if not command.endswith("\r"):
            command = command + "\r"

        s.send(command.encode("utf-8"))

    @staticmethod
    def _get_response(s: socket):
        return s.recv(1024).decode("utf-8")

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

    def _get_text_parameter_response(self, command):
        response = self._command_with_response(command)
        return re.search(r"\((.*?)\)", response).group(1)

    def _get_text_response(self, command):
        response = self._command_with_response(command)
        return re.findall(r"[^!]+", response)[0]

    def get_power_state(self):
        """Get power state of processor."""
        response = self._get_numeric_parameter_response("POWER?")
        if response == 0:
            return "STANDBY"
        if response == 1:
            return "ON"
        return "UNKNOWN POWER STATE"

    def test_ping(self):
        """Send a ping and check the response."""
        return self._get_text_response("PING?") == "!PONG"

    async def connect(self) -> None:
        """Connect to processor."""
        if not await self.test_ping():
            raise HostUnreachable("Ping failed")
