"""Binary sensors from REST telemetry."""

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .entity import HelioZeroEntity
from .entity_registry import entities_for_mode, read_binary_value
from .platform_setup import get_coordinator, get_effective_mode


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> None:
    coordinator = get_coordinator(hass, entry)
    mode = get_effective_mode(hass, entry, coordinator)
    specs = entities_for_mode(coordinator.data, mode, platform="binary_sensor")
    async_add_entities([HelioZeroBinarySensor(coordinator, entry, spec) for spec in specs])


class HelioZeroBinarySensor(HelioZeroEntity, BinarySensorEntity):
    @property
    def is_on(self) -> bool | None:
        return read_binary_value(self.coordinator.data, self.spec.key)
