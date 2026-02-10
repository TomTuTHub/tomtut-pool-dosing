from __future__ import annotations

import asyncio
import aiohttp
import voluptuous as vol

from homeassistant import config_entries
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

        if not name:
            errors["base"] = "cannot_connect"
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(
                    {
                        vol.Required(CONF_NAME, default=DEFAULT_NAME): str,
                        vol.Required(CONF_HOST): str,
                    }
                ),
                errors=errors,
            )

        # Verbindung testen (damit Setup nicht direkt crasht)
        if not await self._async_test_connection(host):
            errors["base"] = "cannot_connect"
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(
                    {
                        vol.Required(CONF_NAME, default=name): str,
                        vol.Required(CONF_HOST, default=host): str,
                    }
                ),
                errors=errors,
            )

        # 1 Anlage pro Host (Unique ID = Host)
        await self.async_set_unique_id(host)
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title=name,
            data={
                CONF_NAME: name,
                CONF_HOST: host,
            },
        )

    async def _async_test_connection(self, host: str) -> bool:
        session = async_get_clientsession(self.hass)
        url = f"http://{host}{API_PATH_MEASUREMENTS}"

        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status != 200:
                    return False
                data = await resp.json()

            # Minimaler Plausibilitätscheck: muss measurements enthalten
            return isinstance(data, dict) and "measurements" in data

        except (aiohttp.ClientError, asyncio.TimeoutError, ValueError):
            return False

    @staticmethod
    def async_get_options_flow(config_entry):
        return TomTuTPoolDosingOptionsFlowHandler(config_entry)


class TomTuTPoolDosingOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None) -> FlowResult:
        if user_input is None:
            current = self.config_entry.options.get(
                CONF_SCAN_INTERVAL, int(DEFAULT_SCAN_INTERVAL.total_seconds())
            )
            return self.async_show_form(
                step_id="init",
                data_schema=vol.Schema(
                    {
                        vol.Required(CONF_SCAN_INTERVAL, default=int(current)): vol.All(
                            vol.Coerce(int), vol.Range(min=5, max=300)
                        )
                    }
                ),
            )

        return self.async_create_entry(title="", data=user_input)
