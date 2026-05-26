"""Meter source select via REST config."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .entity import HelioZeroEntity
from .entity_registry import entities_for_mode
from .platform_setup import get_coordinator, get_effective_mode

SOURCE_OPTIONS = [
    "linky",
    "shelly",
    "jsy",
    "external",
    "pmqtt",
    "brute",
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> None:
    coordinator = get_coordinator(hass, entry)
    mode = get_effective_mode(hass, entry, coordinator)
    specs = entities_for_mode(coordinator.data, mode, platform="select")
    async_add_entities([HelioZeroSourceSelect(coordinator, entry, spec) for spec in specs])


class HelioZeroSourceSelect(HelioZeroEntity, SelectEntity):
    _attr_options = SOURCE_OPTIONS

    @property
    def current_option(self) -> str | None:
        cfg = self.coordinator.data.get("config") or {}
        src = cfg.get("source")
        return str(src).lower() if src else None

    async def async_select_option(self, option: str) -> None:
        await self.coordinator.async_patch_config({"source": option})
        await self.coordinator.async_request_refresh()
