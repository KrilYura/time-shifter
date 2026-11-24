"""Constants for the Time Shifter integration."""

DOMAIN = "time_shifter"
VERSION = "0.2.0"

# Configuration keys
CONF_SOURCE_ENTITY = "source_entity"
CONF_OFFSET_HOURS = "offset_hours"
CONF_PREFETCH_INTERVAL = "prefetch_interval"
CONF_BUFFER_SECONDS = "buffer_seconds"
CONF_SENSOR_NAME = "sensor_name"

# Defaults
DEFAULT_PREFETCH_INTERVAL = 5  # minutes
DEFAULT_BUFFER_SECONDS = 60  # 1 minute
DEFAULT_OFFSET_HOURS = 1  # 1 hour
