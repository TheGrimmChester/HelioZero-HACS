"""HelioZero HACS integration.

Licensed under the EUPL — see LICENSE in the repository root.
"""

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from .const import DOMAIN
from .coordinator import HelioZeroCoordinator

PLATFORMS = ["sensor", "switch", "number", "button"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    coordinator = HelioZeroCoordinator(
        hass, entry.data[CONF_HOST], entry.data.get(CONF_API_TOKEN) or None
    )
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
