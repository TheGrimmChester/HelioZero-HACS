"""MQTT discovery parity registry for rest_only HACS entities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from homeassistant.const import (
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfPower,
    UnitOfTemperature,
)

from .integration_mode import entity_enabled_for_mode


@dataclass(frozen=True)
class HelioEntitySpec:
    key: str
    platform: str
    name: str
    companion_allowed: bool = False
    capability: str | None = None
    device_class: str | None = None
    state_class: str | None = None
    native_unit: str | None = None
    min_value: float | None = None
    max_value: float | None = None
    step: float | None = None
    action_index: int | None = None


def _on_off(value: Any) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    return str(value).upper() == "ON"


def _snapshot(data: dict[str, Any]) -> dict[str, Any]:
    snap = data.get("snapshot")
    return snap if isinstance(snap, dict) else {}


def _measurements(data: dict[str, Any]) -> dict[str, Any]:
    m = data.get("measurements")
    return m if isinstance(m, dict) else {}


def _diagnostics(data: dict[str, Any]) -> dict[str, Any]:
    m = _measurements(data)
    d = m.get("diagnostics")
    return d if isinstance(d, dict) else {}


def _state(data: dict[str, Any]) -> dict[str, Any]:
    s = data.get("state")
    return s if isinstance(s, dict) else {}


def _status(data: dict[str, Any]) -> dict[str, Any]:
    s = _state(data).get("status")
    return s if isinstance(s, dict) else {}


# Entity key -> (measurements section, field) for CH2 REST parity with nested /measurements JSON.
_SECOND_CHANNEL_MEASUREMENT_KEYS: dict[str, tuple[str, str]] = {
    "second_active_import_w": ("second", "active_import_w"),
    "second_active_export_w": ("second", "active_export_w"),
    "second_voltage_v": ("raw_meter", "voltage_second_v"),
    "second_current_a": ("raw_meter", "current_second_a"),
    "second_power_factor": ("raw_meter", "pf_second"),
    "second_energy_import_wh": ("second", "energy_total_import_wh"),
    "second_energy_export_wh": ("second", "energy_total_export_wh"),
    "second_day_energy_import_wh": ("second", "energy_day_import_wh"),
    "second_day_energy_export_wh": ("second", "energy_day_export_wh"),
    "mains_frequency_hz": ("raw_meter", "freq_hz"),
}


def _read_second_channel_from_measurements(
    measurements: dict[str, Any], key: str
) -> Any:
    mapping = _SECOND_CHANNEL_MEASUREMENT_KEYS.get(key)
    if not mapping:
        return None
    section, field = mapping
    block = measurements.get(section) or {}
    if not isinstance(block, dict):
        return None
    return block.get(field)


def read_snapshot_key(data: dict[str, Any], key: str) -> Any:
    snap = _snapshot(data)
    if key in snap:
        return snap[key]
    diag = _diagnostics(data)
    if key in diag:
        return diag[key]
    st = _status(data)
    if key in st:
        return st[key]
    state = _state(data)
    if key in state:
        return state[key]
    m = _measurements(data)
    if key in m:
        return m[key]
    raw = m.get("raw_meter") or {}
    if key in raw:
        return raw[key]
    house = m.get("house") or {}
    if key == "house_net_power_w":
        if raw.get("house_net_power_w") is not None:
            return raw.get("house_net_power_w")
        return house.get("grid_net_w")
    if key in house:
        return house[key]
    second = m.get("second") or {}
    if key in second:
        return second[key]
    return _read_second_channel_from_measurements(m, key)


def _triac_channel_present(data: dict[str, Any]) -> bool:
    raw = _measurements(data).get("raw_meter") or {}
    if not isinstance(raw, dict):
        raw = {}
    return (
        _snapshot(data).get("second_voltage_v") is not None
        or (_measurements(data).get("second") or {}).get("active_import_w") is not None
        or raw.get("voltage_second_v") is not None
    )


CAPABILITY_CHECKS: dict[str, Callable[[dict[str, Any]], bool]] = {
    "triac_channel": _triac_channel_present,
    "temperature": lambda d: (_state(d).get("temperature_c") or _snapshot(d).get("temperature_c")) is not None,
    "linky": lambda d: _measurements(d).get("linky_tariff") is not None
    or _snapshot(d).get("linky_ltarf") is not None,
    "tempo": lambda d: _snapshot(d).get("rte_today") is not None,
}


def capability_enabled(data: dict[str, Any], cap: str | None) -> bool:
    if not cap:
        return True
    if cap == "action":
        return True
    check = CAPABILITY_CHECKS.get(cap)
    return check(data) if check else True


def iter_action_specs(data: dict[str, Any]) -> list[HelioEntitySpec]:
    cfg = data.get("actions_config") or {}
    actions = cfg.get("actions") if isinstance(cfg, dict) else None
    if not isinstance(actions, list):
        return []
    specs: list[HelioEntitySpec] = []
    for idx, ch in enumerate(actions):
        if idx == 0:
            continue
        if not isinstance(ch, dict):
            continue
        title = str(ch.get("title") or ch.get("name") or f"Action {idx}")
        specs.append(
            HelioEntitySpec(
                key=f"action_{idx}",
                platform="switch",
                name=title,
                capability="action",
                action_index=idx,
            )
        )
    return specs


STATIC_ENTITIES: tuple[HelioEntitySpec, ...] = (
    HelioEntitySpec(
        key="republish_discovery",
        platform="button",
        name="Republish MQTT discovery",
        companion_allowed=True,
    ),
    HelioEntitySpec(
        key="house_net_power_w",
        platform="sensor",
        name="House net power",
        native_unit=UnitOfPower.WATT,
        device_class="power",
        state_class="measurement",
    ),
    HelioEntitySpec(
        key="house_active_import_w",
        platform="sensor",
        name="House active import",
        native_unit=UnitOfPower.WATT,
        device_class="power",
        state_class="measurement",
    ),
    HelioEntitySpec(
        key="house_active_export_w",
        platform="sensor",
        name="House active export",
        native_unit=UnitOfPower.WATT,
        device_class="power",
        state_class="measurement",
    ),
    HelioEntitySpec(
        key="house_voltage_v",
        platform="sensor",
        name="House voltage",
        native_unit=UnitOfElectricPotential.VOLT,
        device_class="voltage",
        state_class="measurement",
    ),
    HelioEntitySpec(
        key="house_current_a",
        platform="sensor",
        name="House current",
        native_unit=UnitOfElectricCurrent.AMPERE,
        device_class="current",
        state_class="measurement",
    ),
    HelioEntitySpec(
        key="house_power_factor",
        platform="sensor",
        name="House power factor",
        device_class="power_factor",
        state_class="measurement",
    ),
    HelioEntitySpec(
        key="house_energy_import_wh",
        platform="sensor",
        name="House energy import",
        native_unit=UnitOfEnergy.WATT_HOUR,
        device_class="energy",
        state_class="total_increasing",
    ),
    HelioEntitySpec(
        key="house_energy_export_wh",
        platform="sensor",
        name="House energy export",
        native_unit=UnitOfEnergy.WATT_HOUR,
        device_class="energy",
        state_class="total_increasing",
    ),
    HelioEntitySpec(
        key="house_day_energy_import_wh",
        platform="sensor",
        name="House day energy import",
        native_unit=UnitOfEnergy.WATT_HOUR,
        device_class="energy",
        state_class="total_increasing",
    ),
    HelioEntitySpec(
        key="house_day_energy_export_wh",
        platform="sensor",
        name="House day energy export",
        native_unit=UnitOfEnergy.WATT_HOUR,
        device_class="energy",
        state_class="total_increasing",
    ),
    HelioEntitySpec(
        key="triac_open_percent",
        platform="sensor",
        name="Triac open",
        native_unit="%",
        state_class="measurement",
    ),
    HelioEntitySpec(
        key="source_health",
        platform="sensor",
        name="Source health",
        state_class="measurement",
        min_value=0,
        max_value=100,
    ),
    HelioEntitySpec(
        key="second_active_import_w",
        platform="sensor",
        name="Second active import",
        native_unit=UnitOfPower.WATT,
        device_class="power",
        state_class="measurement",
        capability="triac_channel",
    ),
    HelioEntitySpec(
        key="second_active_export_w",
        platform="sensor",
        name="Second active export",
        native_unit=UnitOfPower.WATT,
        device_class="power",
        state_class="measurement",
        capability="triac_channel",
    ),
    HelioEntitySpec(
        key="second_voltage_v",
        platform="sensor",
        name="Second voltage",
        native_unit=UnitOfElectricPotential.VOLT,
        device_class="voltage",
        state_class="measurement",
        capability="triac_channel",
    ),
    HelioEntitySpec(
        key="second_current_a",
        platform="sensor",
        name="Second current",
        native_unit=UnitOfElectricCurrent.AMPERE,
        device_class="current",
        state_class="measurement",
        capability="triac_channel",
    ),
    HelioEntitySpec(
        key="second_power_factor",
        platform="sensor",
        name="Second power factor",
        device_class="power_factor",
        state_class="measurement",
        capability="triac_channel",
    ),
    HelioEntitySpec(
        key="second_energy_import_wh",
        platform="sensor",
        name="Second energy import",
        native_unit=UnitOfEnergy.WATT_HOUR,
        device_class="energy",
        state_class="total_increasing",
        capability="triac_channel",
    ),
    HelioEntitySpec(
        key="second_energy_export_wh",
        platform="sensor",
        name="Second energy export",
        native_unit=UnitOfEnergy.WATT_HOUR,
        device_class="energy",
        state_class="total_increasing",
        capability="triac_channel",
    ),
    HelioEntitySpec(
        key="second_day_energy_import_wh",
        platform="sensor",
        name="Second day energy import",
        native_unit=UnitOfEnergy.WATT_HOUR,
        device_class="energy",
        state_class="total_increasing",
        capability="triac_channel",
    ),
    HelioEntitySpec(
        key="second_day_energy_export_wh",
        platform="sensor",
        name="Second day energy export",
        native_unit=UnitOfEnergy.WATT_HOUR,
        device_class="energy",
        state_class="total_increasing",
        capability="triac_channel",
    ),
    HelioEntitySpec(
        key="mains_frequency_hz",
        platform="sensor",
        name="Mains frequency",
        native_unit=UnitOfFrequency.HERTZ,
        device_class="frequency",
        state_class="measurement",
        capability="triac_channel",
    ),
    HelioEntitySpec(
        key="temperature_c",
        platform="sensor",
        name="Temperature",
        native_unit=UnitOfTemperature.CELSIUS,
        device_class="temperature",
        state_class="measurement",
        capability="temperature",
    ),
    HelioEntitySpec(
        key="tariff_code",
        platform="sensor",
        name="Tariff code",
        capability="linky",
    ),
    HelioEntitySpec(
        key="linky_ltarf",
        platform="sensor",
        name="Linky tariff option",
        capability="linky",
    ),
    HelioEntitySpec(
        key="rte_today",
        platform="sensor",
        name="RTE today",
        capability="tempo",
    ),
    HelioEntitySpec(
        key="rte_tomorrow",
        platform="sensor",
        name="RTE tomorrow",
        capability="tempo",
    ),
    HelioEntitySpec(key="adc_clipping", platform="binary_sensor", name="ADC clipping"),
    HelioEntitySpec(
        key="regulation_hunting", platform="binary_sensor", name="Regulation hunting"
    ),
    HelioEntitySpec(key="source_stale", platform="binary_sensor", name="Source stale"),
    HelioEntitySpec(
        key="regulation_active", platform="binary_sensor", name="Regulation active"
    ),
    HelioEntitySpec(
        key="mqtt_connected", platform="binary_sensor", name="MQTT connected"
    ),
    HelioEntitySpec(
        key="site_cap_active", platform="binary_sensor", name="Site power cap active"
    ),
    HelioEntitySpec(
        key="heater_load_backoff_active",
        platform="binary_sensor",
        name="Routed load backoff active",
    ),
    HelioEntitySpec(
        key="vacation",
        platform="switch",
        name="Vacation mode",
    ),
    HelioEntitySpec(
        key="max_routed_w",
        platform="number",
        name="Max routed power (W)",
        native_unit=UnitOfPower.WATT,
        min_value=0,
        max_value=20000,
        step=100,
    ),
    HelioEntitySpec(
        key="triac_target",
        platform="number",
        name="Target triac opening",
        native_unit="%",
        min_value=0,
        max_value=100,
        step=1,
    ),
    HelioEntitySpec(
        key="source",
        platform="select",
        name="Meter source",
    ),
)


def entities_for_mode(
    data: dict[str, Any], mode: str, platform: str | None = None
) -> list[HelioEntitySpec]:
    out: list[HelioEntitySpec] = []
    for spec in STATIC_ENTITIES:
        if platform and spec.platform != platform:
            continue
        if not entity_enabled_for_mode(spec.key, mode):
            continue
        if not capability_enabled(data, spec.capability):
            continue
        out.append(spec)
    if entity_enabled_for_mode("action_1", mode) and (platform is None or platform == "switch"):
        for spec in iter_action_specs(data):
            if platform and spec.platform != platform:
                continue
            out.append(spec)
    return out


def read_binary_value(data: dict[str, Any], key: str) -> bool | None:
    if key == "vacation":
        cfg = data.get("config") or {}
        return bool(cfg.get("vacation_enabled"))
    raw = read_snapshot_key(data, key)
    if key in ("adc_clipping", "regulation_hunting", "source_stale", "regulation_active",
               "mqtt_connected", "site_cap_active", "heater_load_backoff_active"):
        if raw is None:
            raw = _diagnostics(data).get(key)
        return _on_off(raw)
    if key.startswith("action_"):
        return _on_off(raw)
    return _on_off(raw)
