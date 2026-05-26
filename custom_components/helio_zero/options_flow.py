"""Options flow for integration mode and poll interval."""

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import (
    CONF_INTEGRATION_MODE,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
    MODE_COMPANION,
    MODE_REST_ONLY,
)


class HelioZeroOptionsFlow(config_entries.OptionsFlow):
    async def async_step_init(self, user_input=None) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        entry = self.config_entry
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_INTEGRATION_MODE,
                        default=entry.options.get(CONF_INTEGRATION_MODE, MODE_COMPANION),
                    ): vol.In([MODE_REST_ONLY, MODE_COMPANION]),
                    vol.Optional(
                        CONF_SCAN_INTERVAL,
                        default=entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
                    ): vol.All(vol.Coerce(int), vol.Range(min=MIN_SCAN_INTERVAL, max=MAX_SCAN_INTERVAL)),
                }
            ),
        )
