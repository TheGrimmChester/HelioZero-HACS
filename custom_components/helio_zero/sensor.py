"""Sensors from REST telemetry snapshot."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .entity import HelioZeroEntity
from .entity_registry import entities_for_mode, read_snapshot_key
from .platform_setup import get_coordinator, get_effective_mode


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> None:
    coordinator = get_coordinator(hass, entry)
    mode = get_effective_mode(hass, entry, coordinator)
    specs = entities_for_mode(coordinator.data, mode, platform="sensor")
    async_add_entities([HelioZeroSensor(coordinator, entry, spec) for spec in specs])


class HelioZeroSensor(HelioZeroEntity, SensorEntity):
    def __init__(self, coordinator, entry, spec):
        super().__init__(coordinator, entry, spec)
        self._attr_device_class = spec.device_class
        self._attr_state_class = spec.state_class
        self._attr_native_unit_of_measurement = spec.native_unit

    @property
    def native_value(self):
        return read_snapshot_key(self.coordinator.data, self.spec.key)
