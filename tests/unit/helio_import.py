"""Load helio_zero modules without importing package __init__ (no homeassistant required)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from unittest.mock import MagicMock

_PKG = Path(__file__).resolve().parents[2] / "custom_components" / "helio_zero"
_PKG_NAME = "custom_components.helio_zero"


def _stub_ha() -> None:
    for name in (
        "homeassistant",
        "homeassistant.config_entries",
        "homeassistant.core",
        "homeassistant.helpers",
        "homeassistant.helpers.entity_registry",
    ):
        if name not in sys.modules:
            sys.modules[name] = MagicMock()

    const = sys.modules.setdefault("homeassistant.const", MagicMock())
    for cls_name, attrs in (
        ("UnitOfPower", {"WATT": "W"}),
        ("UnitOfElectricPotential", {"VOLT": "V"}),
        ("UnitOfElectricCurrent", {"AMPERE": "A"}),
        ("UnitOfEnergy", {"WATT_HOUR": "Wh"}),
        ("UnitOfFrequency", {"HERTZ": "Hz"}),
        ("UnitOfTemperature", {"CELSIUS": "°C"}),
    ):
        setattr(const, cls_name, type(cls_name, (), attrs))


def load_module(rel_path: str) -> ModuleType:
    _stub_ha()
    full_name = f"{_PKG_NAME}.{rel_path.replace('/', '.').replace('.py', '')}"
    if full_name in sys.modules:
        return sys.modules[full_name]
    path = _PKG / rel_path
    spec = importlib.util.spec_from_file_location(full_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[full_name] = mod
    spec.loader.exec_module(mod)
    return mod


def load_const():
    return load_module("const.py")


def load_integration_mode():
    load_const()
    return load_module("integration_mode.py")


def load_entity_registry():
    load_integration_mode()
    return load_module("entity_registry.py")


def load_connection():
    load_const()
    if "aiohttp" not in sys.modules:
        sys.modules["aiohttp"] = MagicMock()
    return load_module("connection.py")


def load_device_info():
    load_const()
    if "aiohttp" not in sys.modules:
        sys.modules["aiohttp"] = MagicMock()
    coord_name = f"{_PKG_NAME}.coordinator"
    if coord_name not in sys.modules:
        coord_mod = ModuleType(coord_name)
        coord_mod.HelioZeroCoordinator = MagicMock()  # type: ignore[attr-defined]
        sys.modules[coord_name] = coord_mod
    return load_module("device_info.py")
