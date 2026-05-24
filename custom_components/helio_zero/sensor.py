"""Sensors from REST measurements."""

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import HelioZeroCoordinator
from .device_info import build_device_info, entity_unique_id


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> bool:
    coordinator: HelioZeroCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            HelioZeroSensor(coordinator, entry, "house_net_power_w", "House net power", "W"),
            HelioZeroSensor(coordinator, entry, "triac_open_percent", "Triac open", "%"),
        ]
    )
    return True


class HelioZeroSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, entry, key, name, unit):
        super().__init__(coordinator)
        self._entry = entry
        self._key = key
        self._attr_name = name
        self._attr_unique_id = entity_unique_id(entry, key)
        self._attr_native_unit_of_measurement = unit

    @property
    def device_info(self) -> DeviceInfo:
        return build_device_info(self._entry, self.coordinator)

    @property
    def native_value(self):
        m = self.coordinator.data.get("measurements", {})
        if self._key == "house_net_power_w":
            raw = m.get("raw_meter") or {}
            if raw.get("house_net_power_w") is not None:
                return raw.get("house_net_power_w")
            house = m.get("house") or {}
            return house.get("grid_net_w")
        if self._key == "triac_open_percent":
            state = self.coordinator.data.get("state") or {}
            return state.get("triac_open_percent")
        channel = m.get("house", m)
        return channel.get(self._key)
