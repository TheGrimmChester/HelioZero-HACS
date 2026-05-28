"""Poll HelioZero REST API."""

from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from typing import Any

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .connection import scan_interval_seconds
from .const import (
    CONF_API_TOKEN,
    CONF_FAILURE_COUNT_UNTIL_UNAVAILABLE,
    CONF_HOST,
    CONF_SKIP_UNAVAILABLE_ON_FAILURE,
    DEFAULT_FAILURE_COUNT_UNTIL_UNAVAILABLE,
    DEFAULT_SKIP_UNAVAILABLE_ON_FAILURE,
    DOMAIN,
    MAX_FAILURE_COUNT_UNTIL_UNAVAILABLE,
    MIN_FAILURE_COUNT_UNTIL_UNAVAILABLE,
)
from .integration_mode import configured_mode

_LOGGER = logging.getLogger(__name__)

_REQUEST_TIMEOUT = aiohttp.ClientTimeout(total=10)


class HelioZeroCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Fetch measurements, telemetry snapshot, and device info."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        interval = scan_interval_seconds(entry.options)
        coordinator_kwargs: dict[str, Any] = {
            "update_interval": timedelta(seconds=interval),
        }
        try:
            super().__init__(
                hass,
                _LOGGER,
                name=DOMAIN,
                config_entry=entry,
                **coordinator_kwargs,
            )
        except TypeError:
            super().__init__(
                hass,
                _LOGGER,
                name=DOMAIN,
                **coordinator_kwargs,
            )
        self._entry = entry
        self._session = async_get_clientsession(hass)
        self._configured_mode = configured_mode(entry)
        self._consecutive_failures = 0
        self._apply_entry_data(entry)
        self._apply_failure_policy(entry)

    def _apply_entry_data(self, entry: ConfigEntry) -> None:
        self._host = entry.data[CONF_HOST].rstrip("/")
        token = entry.data.get(CONF_API_TOKEN) or ""
        self._token = token if token else None

    def _apply_failure_policy(self, entry: ConfigEntry) -> None:
        raw_skip = entry.options.get(
            CONF_SKIP_UNAVAILABLE_ON_FAILURE,
            DEFAULT_SKIP_UNAVAILABLE_ON_FAILURE,
        )
        self._skip_unavailable_on_failure = bool(raw_skip)

        raw_threshold = entry.options.get(
            CONF_FAILURE_COUNT_UNTIL_UNAVAILABLE,
            DEFAULT_FAILURE_COUNT_UNTIL_UNAVAILABLE,
        )
        try:
            threshold = int(raw_threshold)
        except (TypeError, ValueError):
            threshold = DEFAULT_FAILURE_COUNT_UNTIL_UNAVAILABLE
        self._failure_count_until_unavailable = max(
            MIN_FAILURE_COUNT_UNTIL_UNAVAILABLE,
            min(MAX_FAILURE_COUNT_UNTIL_UNAVAILABLE, threshold),
        )

    def update_from_entry(self, entry: ConfigEntry) -> bool:
        """Apply connection and poll-interval changes. Return True if platforms need reload."""
        new_mode = configured_mode(entry)
        needs_reload = new_mode != self._configured_mode
        self._entry = entry
        self._apply_entry_data(entry)
        self._apply_failure_policy(entry)
        self.update_interval = timedelta(seconds=scan_interval_seconds(entry.options))
        self._configured_mode = new_mode
        return needs_reload

    @property
    def host(self) -> str:
        return self._host

    @property
    def entry(self) -> ConfigEntry:
        return self._entry

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
        async with await self._request("PATCH", "/api/v1/config", json=body) as resp:
            resp.raise_for_status()

    async def async_post_mqtt_discover(self) -> None:
        async with await self._request("POST", "/api/v1/mqtt/discover") as resp:
            resp.raise_for_status()

    async def async_post_triac_override(self, command: str) -> None:
        async with await self._request(
            "POST", "/api/v1/triac/override", json={"command": command}
        ) as resp:
            resp.raise_for_status()

    async def async_post_action_override(
        self, idx: int, state: str, *, triac_open_percent: int = 0
    ) -> None:
        body: dict[str, Any] = {"state": state}
        if triac_open_percent:
            body["triac_open_percent"] = triac_open_percent
        async with await self._request(
            "POST", f"/api/v1/actions/{idx}/override", json=body
        ) as resp:
            resp.raise_for_status()

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            (
                measurements,
                device,
                state,
                health,
                cfg_body,
                snapshot,
                sources_diag,
                actions_cfg,
            ) = await asyncio.gather(
                self._async_get_json("/api/v1/measurements", required=True),
                self._async_get_json("/api/v1/device", required=True),
                self._async_get_json("/api/v1/state", required=False),
                self._async_get_json("/api/v1/health", required=False),
                self._async_get_json("/api/v1/config", required=False),
                self._async_get_json("/api/v1/telemetry/snapshot", required=False),
                self._async_get_json("/api/v1/sources/diagnostics", required=False),
                self._async_get_json("/api/v1/actions/config", required=False),
            )
        except Exception as err:
            self._consecutive_failures += 1
            if not self._skip_unavailable_on_failure:
                raise UpdateFailed(str(err)) from err

            threshold = self._failure_count_until_unavailable
            if threshold > 0 and self._consecutive_failures >= threshold:
                raise UpdateFailed(str(err)) from err

            # In skip mode we keep entities available by serving last good payload.
            if self.data:
                _LOGGER.debug(
                    "Skipping unavailable after polling failure (%s/%s): %s",
                    self._consecutive_failures,
                    threshold if threshold > 0 else "never",
                    err,
                )
                return self.data
            raise UpdateFailed(str(err)) from err
        self._consecutive_failures = 0
        config = cfg_body.get("config", cfg_body) if isinstance(cfg_body, dict) else {}
        actions_config = actions_cfg if isinstance(actions_cfg, dict) else {}
        return {
            "measurements": measurements,
            "device": device,
            "state": state,
            "health": health,
            "config": config,
            "snapshot": snapshot,
            "sources_diagnostics": sources_diag,
            "actions_config": actions_config,
        }
