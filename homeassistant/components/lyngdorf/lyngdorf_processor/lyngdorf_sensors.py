"""Type definitions for Lyngdorf Processor."""

from dataclasses import dataclass


@dataclass(frozen=True)
class LyngdorfSensors:
    """Lyngdorf Sensors class."""

    volume: float | None = None
    source: str | None = None
    power_status: str | None = None
    mute_status: str | None = None
    device_name: str | None = None
