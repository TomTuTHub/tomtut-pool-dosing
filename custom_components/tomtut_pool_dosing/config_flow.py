from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .const import (
    DOMAIN,
    CONF_HOST,
    CONF_SCAN_INTERVAL,
    DEFAULT_NAME,
    DEFAULT_SCAN_INTERVAL,
)


class TomTuTPoolDosingConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(
                    {
                        vol.Required(CONF_HOST): str,
                        vol.Optional(CONF_NAME, default="Pool Dosieranlage"): str,
                    }
                ),
            )

        host = user_input[CONF_HOST].strip()
        name = user_input.get(CONF_NAME, "Pool Dosieranlage").strip()

        # verhindert doppelte Einträge pro Host
        await self.async_set_unique_id(host)
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title=f"{name} ({host})",
            data={CONF_HOST: host},
        )

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
