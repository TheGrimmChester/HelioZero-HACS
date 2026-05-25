"""Site max routed power via REST."""

from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import HelioZeroCoordinator
from .device_info import build_device_info, entity_unique_id


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> None:
    coordinator: HelioZeroCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([HelioZeroMaxRoutedNumber(coordinator, entry)])


class HelioZeroMaxRoutedNumber(CoordinatorEntity, NumberEntity):
    _attr_name = "Max routed power (W)"
    _attr_native_min_value = 0
    _attr_native_max_value = 20000
    _attr_native_step = 100
    _attr_mode = NumberMode.BOX

    def __init__(self, coordinator: HelioZeroCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = entity_unique_id(entry, "max_routed_w")

    @property
    def device_info(self) -> DeviceInfo:
        return build_device_info(self._entry, self.coordinator)

    @property
    def native_value(self) -> float:
        cfg = self.coordinator.data.get("config") or {}
        return float(cfg.get("max_routed_w") or 0)

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.async_patch_config({"max_routed_w": int(value)})
        await self.coordinator.async_request_refresh()
