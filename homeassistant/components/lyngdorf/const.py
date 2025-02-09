"""Constants for the lyngdorf integration."""

from datetime import timedelta
from typing import Final

DOMAIN: Final = "lyngdorf"

# Default port for Lyngdorf Processor
DEFAULT_PORT = 84

CONF_LYNDORF = "conf_lyngdorf"

UPDATE_INTERVAL = timedelta(seconds=5)
