"""Vacation switch via REST."""

from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import HelioZeroCoordinator
from .device_info import build_device_info, entity_unique_id


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> None:
    coordinator: HelioZeroCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([HelioZeroVacationSwitch(coordinator, entry)])


class HelioZeroVacationSwitch(CoordinatorEntity, SwitchEntity):
    _attr_name = "Vacation mode"

    def __init__(self, coordinator: HelioZeroCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = entity_unique_id(entry, "vacation")

    @property
    def device_info(self) -> DeviceInfo:
        return build_device_info(self._entry, self.coordinator)

    @property
    def is_on(self) -> bool:
        cfg = self.coordinator.data.get("config") or {}
        return bool(cfg.get("vacation_enabled"))

    async def _patch(self, enabled: bool) -> None:
        await self.coordinator.async_patch_config({"vacation_enabled": enabled})
        await self.coordinator.async_request_refresh()

    async def async_turn_on(self, **kwargs) -> None:
        await self._patch(True)

    async def async_turn_off(self, **kwargs) -> None:
        await self._patch(False)
