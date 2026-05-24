"""Vacation switch via REST."""

from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
import aiohttp

from .const import CONF_API_TOKEN, DOMAIN
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
        host = self._entry.data["host"].rstrip("/")
        token = self._entry.data.get(CONF_API_TOKEN) or None
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        async with aiohttp.ClientSession() as session:
            async with session.patch(
                f"{host}/api/v1/config",
                json={"vacation_enabled": enabled},
                headers=headers,
                timeout=10,
            ) as resp:
                resp.raise_for_status()
        await self.coordinator.async_request_refresh()

    async def async_turn_on(self, **kwargs) -> None:
        await self._patch(True)

    async def async_turn_off(self, **kwargs) -> None:
        await self._patch(False)
