"""Type definitions for Lyngdorf Processor."""

from dataclasses import dataclass


@dataclass(frozen=True)
class LyngdorfSensors:
    """Lyngdorf Sensors class."""

    decibels: int | None = None
    source: str | None = None
    sources: list[str] | None = None
    is_on: bool | None = None
    mute_status: bool | None = None
    device_name: str | None = None
