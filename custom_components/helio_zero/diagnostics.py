"""Diagnostics panel (H10 thin)."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN


async def async_get_config_entry_diagnostics(hass: HomeAssistant, entry: ConfigEntry) -> dict:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    device = coordinator.data.get("device") or {}
    if not isinstance(device, dict):
        device = {}
    return {
        "host": entry.data.get("host"),
        "router_name": device.get("router_name"),
        "device_uid": device.get("device_uid"),
        "firmware_version": device.get("firmware_version"),
        "last_update_success": coordinator.last_update_success,
        "data_keys": list(coordinator.data.keys()),
    }
