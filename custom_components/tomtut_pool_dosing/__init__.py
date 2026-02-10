from __future__ import annotations

import logging
from datetime import timedelta

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    CONF_HOST,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    API_PATH_MEASUREMENTS,
    API_PATH_RELAYS,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[str] = ["sensor", "binary_sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})

    host: str = entry.data[CONF_HOST].strip()

    scan_interval = entry.options.get(
        CONF_SCAN_INTERVAL, int(DEFAULT_SCAN_INTERVAL.total_seconds())
    )
    update_interval = timedelta(seconds=int(scan_interval))

    session = async_get_clientsession(hass)

    async def _fetch_json(path: str) -> dict:
        url = f"http://{host}{path}"
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def _async_update() -> dict:
        try:
            measurements_payload = await _fetch_json(API_PATH_MEASUREMENTS)
            relays_payload = await _fetch_json(API_PATH_RELAYS)
        except Exception as err:
            raise UpdateFailed(err) from err

        merged: dict = dict(measurements_payload or {})
        merged["relays"] = (relays_payload or {}).get("relays", {})
        merged["relays_version"] = (relays_payload or {}).get("version")
        return merged

    coordinator = DataUpdateCoordinator(
        hass=hass,
        logger=_LOGGER,
        name=DOMAIN,
        update_method=_async_update,
        update_interval=update_interval,
    )

    await coordinator.async_config_entry_first_refresh()
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
