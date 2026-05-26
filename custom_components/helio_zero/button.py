"""Buttons (republish discovery)."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .entity import HelioZeroEntity
from .entity_registry import entities_for_mode
from .platform_setup import get_coordinator, get_effective_mode


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> None:
    coordinator = get_coordinator(hass, entry)
    mode = get_effective_mode(hass, entry, coordinator)
    specs = entities_for_mode(coordinator.data, mode, platform="button")
    async_add_entities([HelioZeroButton(coordinator, entry, spec) for spec in specs])


class HelioZeroButton(HelioZeroEntity, ButtonEntity):
    async def async_press(self) -> None:
        await self.coordinator.async_post_mqtt_discover()
        await self.coordinator.async_request_refresh()
