"""The Time Shifter integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import (
    CONF_BUFFER_SECONDS,
    CONF_OFFSET_HOURS,
    CONF_PREFETCH_INTERVAL,
    CONF_SOURCE_ENTITY,
    DEFAULT_BUFFER_SECONDS,
    DEFAULT_OFFSET_HOURS,
    DEFAULT_PREFETCH_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]

type TimeShifterConfigEntry = ConfigEntry


async def async_setup_entry(hass: HomeAssistant, entry: TimeShifterConfigEntry) -> bool:
    """Set up Time Shifter from a config entry."""
    _LOGGER.debug("Setting up Time Shifter integration for entry: %s", entry.entry_id)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: TimeShifterConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.debug("Unloading Time Shifter integration for entry: %s", entry.entry_id)
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Migrate old config entry to the current version."""
    _LOGGER.debug(
        "Migrating Time Shifter config entry from version %s", entry.version
    )

    if entry.version > 3:
        _LOGGER.error(
            "Unable to migrate Time Shifter entry from version %s", entry.version
        )
        return False

    data = dict(entry.data)
    options: dict[str, Any] = dict(entry.options)
    version = entry.version

    if version < 2:
        for key, default in (
            (CONF_OFFSET_HOURS, DEFAULT_OFFSET_HOURS),
            (CONF_PREFETCH_INTERVAL, DEFAULT_PREFETCH_INTERVAL),
            (CONF_BUFFER_SECONDS, DEFAULT_BUFFER_SECONDS),
        ):
            if key in data:
                options[key] = data.pop(key)
            elif key not in options:
                options[key] = default
        version = 2

    if version < 3:
        # Drop custom sensor_name; name/entity_id are generated from source + offset.
        data = {CONF_SOURCE_ENTITY: data[CONF_SOURCE_ENTITY]}
        version = 3

    hass.config_entries.async_update_entry(
        entry,
        data=data,
        options=options,
        version=version,
    )
    _LOGGER.info("Migrated Time Shifter config entry to version %s", version)
    return True
