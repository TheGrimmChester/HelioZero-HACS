"""Poll HelioZero REST API."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

import aiohttp
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

_REQUEST_TIMEOUT = aiohttp.ClientTimeout(total=10)


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
        self._token = token or None
        self._session = async_get_clientsession(hass)

    @property
    def host(self) -> str:
        """Router base URL (config entry)."""
        return self._host

    def _auth_headers(self) -> dict[str, str]:
        if not self._token:
            return {}
        return {"Authorization": f"Bearer {self._token}"}

    async def _request(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, Any] | None = None,
    ) -> aiohttp.ClientResponse:
        return await self._session.request(
            method,
            f"{self._host}{path}",
            headers=self._auth_headers(),
            json=json,
            timeout=_REQUEST_TIMEOUT,
        )

    async def _async_get_json(self, path: str, *, required: bool) -> dict[str, Any]:
        async with await self._request("GET", path) as resp:
            if required:
                resp.raise_for_status()
                payload = await resp.json()
                return payload if isinstance(payload, dict) else {}
            if resp.status != 200:
                return {}
            payload = await resp.json()
            return payload if isinstance(payload, dict) else {}

    async def async_patch_config(self, body: dict[str, Any]) -> None:
        """PATCH /api/v1/config (vacation, max_routed_w, etc.)."""
        async with await self._request("PATCH", "/api/v1/config", json=body) as resp:
            resp.raise_for_status()

    async def async_post_mqtt_discover(self) -> None:
        """POST /api/v1/mqtt/discover."""
        async with await self._request("POST", "/api/v1/mqtt/discover") as resp:
            resp.raise_for_status()

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            measurements = await self._async_get_json(
                "/api/v1/measurements", required=True
            )
            device = await self._async_get_json("/api/v1/device", required=True)
            state = await self._async_get_json("/api/v1/state", required=False)
            health = await self._async_get_json("/api/v1/health", required=False)
            cfg_body = await self._async_get_json("/api/v1/config", required=False)
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
