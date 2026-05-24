"""Poll HelioZero REST API."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

import aiohttp
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class HelioZeroCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Fetch measurements and device info."""

    def __init__(self, hass, host: str, token: str | None) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=30),
        )
        self._host = host.rstrip("/")
        self._token = token

    @property
    def host(self) -> str:
        """Router base URL (config entry)."""
        return self._host

    async def _async_update_data(self) -> dict[str, Any]:
        headers = {}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        cfg_body: dict = {}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self._host}/api/v1/measurements", headers=headers, timeout=10
                ) as resp:
                    resp.raise_for_status()
                    measurements = await resp.json()
                async with session.get(
                    f"{self._host}/api/v1/device", headers=headers, timeout=10
                ) as resp:
                    resp.raise_for_status()
                    device = await resp.json()
                async with session.get(
                    f"{self._host}/api/v1/state", headers=headers, timeout=10
                ) as resp:
                    state = await resp.json() if resp.status == 200 else {}
                async with session.get(
                    f"{self._host}/api/v1/health", headers=headers, timeout=10
                ) as resp:
                    health = await resp.json() if resp.status == 200 else {}
                async with session.get(
                    f"{self._host}/api/v1/config", headers=headers, timeout=10
                ) as resp:
                    cfg_body = await resp.json() if resp.status == 200 else {}
        except Exception as err:
            raise UpdateFailed(str(err)) from err
        config = cfg_body.get("config", cfg_body) if isinstance(cfg_body, dict) else {}
        return {
            "measurements": measurements,
            "device": device,
            "state": state,
            "health": health,
            "config": config,
        }
