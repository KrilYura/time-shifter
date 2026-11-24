"""Config flow for Time Shifter integration."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlowWithReload,
)
from homeassistant.core import callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers import selector

from .const import (
    CONF_BUFFER_SECONDS,
    CONF_OFFSET_HOURS,
    CONF_PREFETCH_INTERVAL,
    CONF_SOURCE_ENTITY,
    DEFAULT_BUFFER_SECONDS,
    DEFAULT_OFFSET_HOURS,
    DEFAULT_PREFETCH_INTERVAL,
    DOMAIN,
    format_offset_label,
)


def _options_schema(
    defaults: dict[str, Any] | None = None,
) -> vol.Schema:
    """Build the options schema with optional defaults."""
    defaults = defaults or {}
    return vol.Schema(
        {
            vol.Required(
                CONF_OFFSET_HOURS,
                default=defaults.get(CONF_OFFSET_HOURS, DEFAULT_OFFSET_HOURS),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=0.01,
                    max=168,
                    step=0.1,
                    mode=selector.NumberSelectorMode.BOX,
                    unit_of_measurement="hours",
                )
            ),
            vol.Optional(
                CONF_PREFETCH_INTERVAL,
                default=defaults.get(
                    CONF_PREFETCH_INTERVAL, DEFAULT_PREFETCH_INTERVAL
                ),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=1,
                    max=60,
                    step=1,
                    mode=selector.NumberSelectorMode.BOX,
                    unit_of_measurement="minutes",
                )
            ),
            vol.Optional(
                CONF_BUFFER_SECONDS,
                default=defaults.get(CONF_BUFFER_SECONDS, DEFAULT_BUFFER_SECONDS),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=0,
                    max=300,
                    step=1,
                    mode=selector.NumberSelectorMode.BOX,
                    unit_of_measurement="seconds",
                )
            ),
        }
    )


def _validate_options(user_input: dict[str, Any]) -> dict[str, str]:
    """Validate option values; return field -> error key map."""
    errors: dict[str, str] = {}
    if user_input.get(CONF_OFFSET_HOURS, DEFAULT_OFFSET_HOURS) <= 0:
        errors[CONF_OFFSET_HOURS] = "offset_must_be_positive"
    if user_input.get(CONF_PREFETCH_INTERVAL, DEFAULT_PREFETCH_INTERVAL) <= 0:
        errors[CONF_PREFETCH_INTERVAL] = "prefetch_must_be_positive"
    if user_input.get(CONF_BUFFER_SECONDS, DEFAULT_BUFFER_SECONDS) < 0:
        errors[CONF_BUFFER_SECONDS] = "buffer_must_be_non_negative"
    return errors


class TimeShifterConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Time Shifter."""

    VERSION = 3

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            entity_id = user_input[CONF_SOURCE_ENTITY]
            entity_registry = er.async_get(self.hass)

            if not entity_registry.async_get(entity_id):
                if self.hass.states.get(entity_id) is None:
                    errors[CONF_SOURCE_ENTITY] = "entity_not_found"

            errors.update(_validate_options(user_input))

            if not errors:
                await self.async_set_unique_id(f"{entity_id}_shifted")
                self._abort_if_unique_id_configured()

                offset_hours = user_input[CONF_OFFSET_HOURS]
                return self.async_create_entry(
                    title=f"{entity_id} ({format_offset_label(offset_hours)} hours ago)",
                    data={
                        CONF_SOURCE_ENTITY: entity_id,
                    },
                    options={
                        CONF_OFFSET_HOURS: offset_hours,
                        CONF_PREFETCH_INTERVAL: user_input.get(
                            CONF_PREFETCH_INTERVAL, DEFAULT_PREFETCH_INTERVAL
                        ),
                        CONF_BUFFER_SECONDS: user_input.get(
                            CONF_BUFFER_SECONDS, DEFAULT_BUFFER_SECONDS
                        ),
                    },
                )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_SOURCE_ENTITY): selector.EntitySelector(
                    selector.EntitySelectorConfig()
                ),
            }
        ).extend(_options_schema().schema)

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> TimeShifterOptionsFlow:
        """Get the options flow for this handler."""
        return TimeShifterOptionsFlow()


class TimeShifterOptionsFlow(OptionsFlowWithReload):
    """Handle options flow for Time Shifter."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the options."""
        errors: dict[str, str] = {}

        if user_input is not None:
            errors = _validate_options(user_input)
            if not errors:
                return self.async_create_entry(data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=self.add_suggested_values_to_schema(
                _options_schema(),
                self.config_entry.options,
            ),
            errors=errors,
        )
