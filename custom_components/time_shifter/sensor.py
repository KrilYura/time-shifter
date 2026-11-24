"""Sensor platform for Time Shifter integration."""
from __future__ import annotations

from datetime import datetime, timedelta
import logging
from typing import Any

from homeassistant.components import history
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.core import HomeAssistant, State
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.util import dt as dt_util

from . import TimeShifterConfigEntry
from .const import (
    CONF_BUFFER_SECONDS,
    CONF_OFFSET_HOURS,
    CONF_PREFETCH_INTERVAL,
    CONF_SOURCE_ENTITY,
    DEFAULT_BUFFER_SECONDS,
    DEFAULT_OFFSET_HOURS,
    DEFAULT_PREFETCH_INTERVAL,
    shifted_entity_object_id,
    shifted_friendly_name,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: TimeShifterConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Time Shifter sensor from a config entry."""
    source_entity = config_entry.data[CONF_SOURCE_ENTITY]
    options = config_entry.options

    offset_hours = options.get(CONF_OFFSET_HOURS, DEFAULT_OFFSET_HOURS)
    prefetch_interval = options.get(
        CONF_PREFETCH_INTERVAL, DEFAULT_PREFETCH_INTERVAL
    )
    buffer_seconds = options.get(CONF_BUFFER_SECONDS, DEFAULT_BUFFER_SECONDS)

    _LOGGER.debug(
        "Setting up shifted sensor for %s with offset=%s hours, "
        "prefetch=%s min, buffer=%s sec",
        source_entity,
        offset_hours,
        prefetch_interval,
        buffer_seconds,
    )

    async_add_entities(
        [
            TimeShiftedSensor(
                hass,
                config_entry.entry_id,
                source_entity,
                offset_hours,
                prefetch_interval,
                buffer_seconds,
            )
        ],
        update_before_add=True,
    )


class TimeShiftedSensor(SensorEntity):
    """Representation of a time-shifted sensor."""

    _attr_should_poll = False
    _attr_icon = "mdi:clock-time-four-outline"

    def __init__(
        self,
        hass: HomeAssistant,
        entry_id: str,
        source_entity: str,
        offset_hours: float,
        prefetch_interval: int,
        buffer_seconds: int,
    ) -> None:
        """Initialize the sensor."""
        self.hass = hass
        self._entry_id = entry_id
        self._source_entity = source_entity
        self._offset_hours = offset_hours
        self._prefetch_interval = prefetch_interval
        self._buffer_seconds = buffer_seconds

        self._state_cache: list[tuple[datetime, State]] = []
        self._unsub_prefetch = None

        source_state = hass.states.get(source_entity)
        source_name = (
            source_state.name
            if source_state and source_state.name
            else source_entity.split(".", 1)[-1]
        )

        # Name: "<source name> N hours ago"
        # entity_id: sensor.<source_object_id>_N_hours_ago
        self._attr_name = shifted_friendly_name(source_name, offset_hours)
        self._attr_unique_id = f"{entry_id}_shifted"
        self.entity_id = f"sensor.{shifted_entity_object_id(source_entity, offset_hours)}"

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added to hass."""
        await super().async_added_to_hass()

        registry = er.async_get(self.hass)
        source = registry.async_get(self._source_entity)
        if source and source.device_id and self.registry_entry:
            registry.async_update_entity(
                self.entity_id, device_id=source.device_id
            )

        self._unsub_prefetch = async_track_time_interval(
            self.hass,
            self._async_prefetch_states,
            timedelta(minutes=self._prefetch_interval),
        )

        await self._async_prefetch_states(None)

    async def async_will_remove_from_hass(self) -> None:
        """Run when entity will be removed from hass."""
        if self._unsub_prefetch:
            self._unsub_prefetch()
            self._unsub_prefetch = None

    async def _async_prefetch_states(self, now: datetime | None) -> None:
        """Prefetch historical states for the upcoming interval."""
        try:
            current_time = dt_util.utcnow()

            offset_delta = timedelta(hours=self._offset_hours)
            prefetch_delta = timedelta(minutes=self._prefetch_interval)
            buffer_delta = timedelta(seconds=self._buffer_seconds)

            start_time = current_time - offset_delta
            end_time = start_time + prefetch_delta + buffer_delta

            _LOGGER.debug(
                "Prefetching states for %s from %s to %s (offset=%s hours)",
                self._source_entity,
                start_time,
                end_time,
                self._offset_hours,
            )

            states_dict = await self.hass.async_add_executor_job(
                history.get_significant_states,
                self.hass,
                start_time,
                end_time,
                [self._source_entity],
                None,
                True,  # include_start_time_state
            )

            states = states_dict.get(self._source_entity, [])

            if states:
                self._state_cache = [
                    (state.last_updated, state) for state in states
                ]
                self._state_cache.sort(key=lambda x: x[0])

                _LOGGER.debug(
                    "Prefetched %d states for %s",
                    len(self._state_cache),
                    self._source_entity,
                )
            else:
                _LOGGER.warning(
                    "No historical states found for %s in time range %s to %s",
                    self._source_entity,
                    start_time,
                    end_time,
                )

            self.async_write_ha_state()

        except Exception:
            _LOGGER.exception(
                "Error prefetching states for %s", self._source_entity
            )

    def _get_shifted_state(self) -> State | None:
        """Get the state at the shifted time."""
        if not self._state_cache:
            return None

        current_time = dt_util.utcnow()
        shifted_time = current_time - timedelta(hours=self._offset_hours)

        for timestamp, state in reversed(self._state_cache):
            if timestamp <= shifted_time:
                return state

        return self._state_cache[0][1]

    def _source_attr(self, key: str) -> Any | None:
        """Return an attribute from the live source entity if available."""
        source_state = self.hass.states.get(self._source_entity)
        if source_state and source_state.attributes:
            return source_state.attributes.get(key)
        return None

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        shifted_state = self._get_shifted_state()
        if shifted_state:
            return shifted_state.state
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        shifted_state = self._get_shifted_state()
        attributes: dict[str, Any] = {
            "source_entity": self._source_entity,
            "offset_hours": self._offset_hours,
            "prefetch_interval_minutes": self._prefetch_interval,
            "buffer_seconds": self._buffer_seconds,
            "cache_size": len(self._state_cache),
        }

        if shifted_state:
            if shifted_state.attributes:
                attributes["source_attributes"] = dict(shifted_state.attributes)

            attributes["shifted_timestamp"] = (
                shifted_state.last_updated.isoformat()
            )

            current_time = dt_util.utcnow()
            actual_shift = current_time - shifted_state.last_updated
            attributes["actual_shift_seconds"] = actual_shift.total_seconds()

        return attributes

    @property
    def device_class(self) -> SensorDeviceClass | str | None:
        """Return device class from source entity if available."""
        return self._source_attr("device_class")

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return unit of measurement from source entity if available."""
        return self._source_attr("unit_of_measurement")

    @property
    def icon(self) -> str | None:
        """Return icon from source entity if available, else default."""
        return self._source_attr("icon") or self._attr_icon

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return len(self._state_cache) > 0
