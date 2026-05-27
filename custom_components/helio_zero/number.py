"""Numbers (max routed, triac target) via REST."""

from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .entity import HelioZeroEntity
from .entity_registry import entities_for_mode, read_snapshot_key
from .platform_setup import get_coordinator, get_effective_mode


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> None:
    coordinator = get_coordinator(hass, entry)
    mode = get_effective_mode(hass, entry, coordinator)
    specs = entities_for_mode(coordinator.data, mode, platform="number")
    async_add_entities([HelioZeroNumber(coordinator, entry, spec) for spec in specs])


class HelioZeroNumber(HelioZeroEntity, NumberEntity):
    _attr_mode = NumberMode.BOX

    def __init__(self, coordinator, entry, spec):
        super().__init__(coordinator, entry, spec)
        self._attr_native_unit_of_measurement = spec.native_unit
        self._attr_native_min_value = spec.min_value
        self._attr_native_max_value = spec.max_value
        self._attr_native_step = spec.step or 1

    @property
    def native_value(self) -> float | None:
        if self.spec.key == "max_routed_w":
            cfg = self.coordinator.data.get("config") or {}
            return float(cfg.get("max_routed_w") or 0)
        val = read_snapshot_key(self.coordinator.data, self.spec.key)
        if val is None and self.spec.key == "triac_target":
            val = read_snapshot_key(self.coordinator.data, "triac_open_percent")
        return float(val) if val is not None else None

    async def async_set_native_value(self, value: float) -> None:
        if self.spec.key == "max_routed_w":
            await self.coordinator.async_patch_config({"max_routed_w": int(value)})
        elif self.spec.key == "triac_target":
            await self.coordinator.async_post_triac_override(str(int(value)))
        await self.coordinator.async_request_refresh()
