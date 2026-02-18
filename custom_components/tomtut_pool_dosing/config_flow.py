from __future__ import annotations

import asyncio
from datetime import timedelta

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    DOMAIN,
    CONF_HOST,
    CONF_NAME,
    CONF_SCAN_INTERVAL,
    DEFAULT_NAME,
    DEFAULT_SCAN_INTERVAL,
    API_PATH_MEASUREMENTS,
)


class TomTuTPoolDosingConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 2

    async def async_step_user(self, user_input=None) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(
                    {
                        vol.Required(CONF_NAME, default=DEFAULT_NAME): str,
                        vol.Required(CONF_HOST): str,
                    }
                ),
            )

        name = (user_input.get(CONF_NAME) or "").strip()
        host = (user_input.get(CONF_HOST) or "").strip()

        if not await self._async_test_connection(host):
            errors["base"] = "cannot_connect"
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(
                    {
                        vol.Required(CONF_NAME, default=name or DEFAULT_NAME): str,
                        vol.Required(CONF_HOST, default=host): str,
                    }
                ),
                errors=errors,
            )

        await self.async_set_unique_id(host)
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title=name,
            data={CONF_NAME: name, CONF_HOST: host},
        )

    async def _async_test_connection(self, host: str) -> bool:
        session = async_get_clientsession(self.hass)
        url = f"http://{host}{API_PATH_MEASUREMENTS}"
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return False
                data = await resp.json()
            return isinstance(data, dict) and "measurements" in data
        except (aiohttp.ClientError, asyncio.TimeoutError, ValueError):
            return False

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return TomTuTPoolDosingOptionsFlowHandler()


MIN_SCAN_INTERVAL = 5
MAX_SCAN_INTERVAL = 300


class TomTuTPoolDosingOptionsFlowHandler(config_entries.OptionsFlow):
    async def async_step_init(self, user_input=None) -> FlowResult:
        if user_input is None:
            current = self._normalize_scan_interval(
                self.config_entry.options.get(CONF_SCAN_INTERVAL)
            )
            return self.async_show_form(
                step_id="init",
                data_schema=vol.Schema(
                    {
                        vol.Required(CONF_SCAN_INTERVAL, default=int(current)): vol.All(
                            vol.Coerce(int),
                            vol.Range(min=MIN_SCAN_INTERVAL, max=MAX_SCAN_INTERVAL),
                        )
                    }
                ),
            )

        return self.async_create_entry(
            title="",
            data={
                CONF_SCAN_INTERVAL: self._normalize_scan_interval(
                    user_input.get(CONF_SCAN_INTERVAL)
                )
            },
        )

    @staticmethod
    def _normalize_scan_interval(value) -> int:
        default_value = int(DEFAULT_SCAN_INTERVAL.total_seconds())

        if value is None:
            return default_value
        if isinstance(value, timedelta):
            return int(value.total_seconds())

        try:
            interval = int(value)
        except (TypeError, ValueError):
            return default_value

        return max(MIN_SCAN_INTERVAL, min(MAX_SCAN_INTERVAL, interval))
