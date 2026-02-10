from __future__ import annotations

import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    API_PATH_MEASUREMENTS,
    API_PATH_RELAYS,
    UPDATE_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor", "binary_sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    host = entry.data["host"]
    session = async_get_clientsession(hass)

    async def _update():
        try:
            async with session.get(f"http://{host}{API_PATH_MEASUREMENTS}", timeout=10) as r1:
                r1.raise_for_status()
                measurements = await r1.json()

            async with session.get(f"http://{host}{API_PATH_RELAYS}", timeout=10) as r2:
                r2.raise_for_status()
                relays = await r2.json()

            return {
                "measurements": measurements.get("measurements", {}),
                "relays": relays.get("relays", {}),
            }
        except Exception as err:
            raise UpdateFailed(err) from err

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="TomTuT Pool Dosieranlage",
        update_method=_update,
        update_interval=UPDATE_INTERVAL,
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    hass.data[DOMAIN].pop(entry.entry_id)
    return True
