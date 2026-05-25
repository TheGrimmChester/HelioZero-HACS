"""Republish MQTT discovery button."""

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN
from .device_info import build_device_info, entity_unique_id


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> bool:
    async_add_entities([RepublishDiscoveryButton(hass, entry)])
    return True


class RepublishDiscoveryButton(ButtonEntity):
    def __init__(self, hass, entry):
        self._hass = hass
        self._entry = entry
        self._attr_name = "Republish MQTT discovery"
        self._attr_unique_id = entity_unique_id(entry, "republish_discovery")

    @property
    def device_info(self) -> DeviceInfo:
        coordinator = self._hass.data[DOMAIN][self._entry.entry_id]
        return build_device_info(self._entry, coordinator)

    async def async_press(self) -> None:
        coordinator = self._hass.data[DOMAIN][self._entry.entry_id]
        await coordinator.async_post_mqtt_discover()
