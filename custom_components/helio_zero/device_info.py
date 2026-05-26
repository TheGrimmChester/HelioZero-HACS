"""Shared device registry and entity unique_id helpers."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN

if TYPE_CHECKING:
    from .coordinator import HelioZeroCoordinator


def entity_unique_id(entry: ConfigEntry, key: str) -> str:
    """Per-config-entry unique_id so multiple routers do not collide."""
    return f"{entry.entry_id}_{key}"


def _device_payload(coordinator: HelioZeroCoordinator) -> dict:
    device = coordinator.data.get("device")
    return device if isinstance(device, dict) else {}


def build_device_info(
    entry: ConfigEntry, coordinator: "HelioZeroCoordinator"
) -> DeviceInfo:
    """Device registry entry using live router metadata from the coordinator."""
    device = _device_payload(coordinator)
    name = (device.get("router_name") or "").strip() or "HelioZero"
    info = DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name=name,
        manufacturer="HelioZero",
        model="PV excess router",
        configuration_url=coordinator.host,
    )
    fw = device.get("firmware_version")
    if fw:
        info["sw_version"] = str(fw)
    uid = device.get("device_uid")
    if uid:
        info["serial_number"] = str(uid)
    return info


def title_from_public(body: dict, host: str) -> str:
    """Config entry title from /api/v1/public (setup before first coordinator poll)."""
    device = body.get("device")
    if isinstance(device, dict):
        name = (device.get("router_name") or "").strip()
        if name:
            return name
    return f"HelioZero ({host})"
