"""Resolve coordinator and integration mode for platform setup."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import HelioZeroCoordinator
from .integration_mode import effective_mode


def get_coordinator(hass: HomeAssistant, entry: ConfigEntry) -> HelioZeroCoordinator:
    coordinator = getattr(entry, "runtime_data", None)
    if coordinator is None:
        coordinator = hass.data[DOMAIN][entry.entry_id]
    return coordinator


def get_effective_mode(hass: HomeAssistant, entry: ConfigEntry, coordinator: HelioZeroCoordinator) -> str:
    device = coordinator.data.get("device") or {}
    uid = device.get("device_uid") if isinstance(device, dict) else None
    return effective_mode(hass, entry, uid)
