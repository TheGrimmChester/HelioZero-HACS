"""Diagnostics panel."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .integration_mode import effective_mode


def _redact(entry: ConfigEntry) -> dict:
    return {
        "host": entry.data.get("host"),
        "has_token": bool(entry.data.get("api_token")),
        "integration_mode": entry.options.get("integration_mode"),
        "scan_interval": entry.options.get("scan_interval"),
    }


async def async_get_config_entry_diagnostics(hass: HomeAssistant, entry: ConfigEntry) -> dict:
    coordinator = getattr(entry, "runtime_data", None) or hass.data[DOMAIN][entry.entry_id]
    device = coordinator.data.get("device") or {}
    if not isinstance(device, dict):
        device = {}
    uid = device.get("device_uid")
    mode = effective_mode(hass, entry, uid)
    diag = coordinator.data.get("measurements", {}).get("diagnostics", {})
    return {
        **_redact(entry),
        "effective_mode": mode,
        "router_name": device.get("router_name"),
        "device_uid": uid,
        "firmware_version": device.get("firmware_version"),
        "last_update_success": coordinator.last_update_success,
        "measurements_diagnostics": diag if isinstance(diag, dict) else {},
        "snapshot_keys": list((coordinator.data.get("snapshot") or {}).keys()),
    }
