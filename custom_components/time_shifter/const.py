"""Constants for the Time Shifter integration."""

DOMAIN = "time_shifter"
VERSION = "0.3.0"

# Configuration keys
CONF_SOURCE_ENTITY = "source_entity"
CONF_OFFSET_HOURS = "offset_hours"
CONF_PREFETCH_INTERVAL = "prefetch_interval"
CONF_BUFFER_SECONDS = "buffer_seconds"

# Defaults
DEFAULT_PREFETCH_INTERVAL = 5  # minutes
DEFAULT_BUFFER_SECONDS = 60  # 1 minute
DEFAULT_OFFSET_HOURS = 1  # 1 hour


def format_offset_label(offset_hours: float) -> str:
    """Format offset for names / entity ids (e.g. 1 or 1.5)."""
    value = float(offset_hours)
    if value.is_integer():
        return str(int(value))
    return str(value)


def shifted_entity_object_id(source_entity: str, offset_hours: float) -> str:
    """Build object_id: <source_object_id>_<N>_hours_ago."""
    source_object_id = source_entity.split(".", 1)[-1]
    label = format_offset_label(offset_hours).replace(".", "_")
    return f"{source_object_id}_{label}_hours_ago"


def shifted_friendly_name(source_name: str, offset_hours: float) -> str:
    """Build friendly name: <source name> <N> hours ago."""
    return f"{source_name} {format_offset_label(offset_hours)} hours ago"
