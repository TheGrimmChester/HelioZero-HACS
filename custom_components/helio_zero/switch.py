"""Switches (vacation, actions) via REST."""

from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .entity import HelioZeroEntity
from .entity_registry import entities_for_mode, read_binary_value
from .platform_setup import get_coordinator, get_effective_mode


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> None:
    coordinator = get_coordinator(hass, entry)
    mode = get_effective_mode(hass, entry, coordinator)
    specs = entities_for_mode(coordinator.data, mode, platform="switch")
    async_add_entities([HelioZeroSwitch(coordinator, entry, spec) for spec in specs])


class HelioZeroSwitch(HelioZeroEntity, SwitchEntity):
    @property
    def is_on(self) -> bool | None:
        return read_binary_value(self.coordinator.data, self.spec.key)

    async def async_turn_on(self, **kwargs) -> None:
        await self._set(True)

    async def async_turn_off(self, **kwargs) -> None:
        await self._set(False)

    async def _set(self, on: bool) -> None:
        if self.spec.key == "vacation":
            await self.coordinator.async_patch_config({"vacation_enabled": on})
        elif self.spec.action_index is not None:
            await self.coordinator.async_post_action_override(
                self.spec.action_index, "on" if on else "off"
            )
        await self.coordinator.async_request_refresh()
