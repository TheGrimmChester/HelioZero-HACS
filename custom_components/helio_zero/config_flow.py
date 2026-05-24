"""Config flow for HelioZero."""

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST
import aiohttp

from .const import CONF_API_TOKEN, DOMAIN
from .device_info import title_from_public


class HelioZeroConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            host = user_input[CONF_HOST].rstrip("/")
            token = user_input.get(CONF_API_TOKEN) or None
            headers = {"Authorization": f"Bearer {token}"} if token else {}
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{host}/api/v1/public", headers=headers, timeout=8) as resp:
                        if resp.status != 200:
                            errors["base"] = "cannot_connect"
                        else:
                            body = await resp.json()
                            await self.async_set_unique_id(host)
                            self._abort_if_unique_id_configured()
                            return self.async_create_entry(
                                title=title_from_public(body, host),
                                data={CONF_HOST: host, CONF_API_TOKEN: token or ""},
                            )
            except aiohttp.ClientError:
                errors["base"] = "cannot_connect"
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST, default="http://192.168.1.42"): str,
                    vol.Optional(CONF_API_TOKEN): str,
                }
            ),
            errors=errors,
        )
