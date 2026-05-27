"""Shared coordinator entity helpers."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import HelioZeroCoordinator
from .device_info import build_device_info, entity_unique_id
from .entity_registry import HelioEntitySpec


class HelioZeroEntity(CoordinatorEntity):
    """Base entity bound to registry spec."""

    def __init__(
        self,
        coordinator: HelioZeroCoordinator,
        entry: ConfigEntry,
        spec: HelioEntitySpec,
    ) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self.spec = spec
        self._attr_name = spec.name
        self._attr_unique_id = entity_unique_id(entry, spec.key)

    @property
    def device_info(self):
        return build_device_info(self._entry, self.coordinator)
