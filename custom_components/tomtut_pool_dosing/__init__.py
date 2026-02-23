from __future__ import annotations

import logging
from datetime import timedelta
from pathlib import Path

import aiohttp

from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    API_PATH_MEASUREMENTS,
    API_PATH_RELAYS,
    CONF_FLOW_SCAN_INTERVAL,
    CONF_HOST,
    CONF_NAME,
    CONF_SCAN_INTERVAL,
    COORDINATOR_CHEMISTRY,
    COORDINATOR_FLOW,
    DEFAULT_FLOW_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[str] = ["sensor", "binary_sensor"]
STATIC_URL_PATH = "/api/tomtut_pool_dosing/static"
STATIC_REGISTRATION_KEY = "static_path_registered"


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    domain_data = hass.data.setdefault(DOMAIN, {})

    if not domain_data.get(STATIC_REGISTRATION_KEY):
        static_dir = Path(__file__).parent / "static"
        await hass.http.async_register_static_paths(
            [
                StaticPathConfig(
                    STATIC_URL_PATH,
                    str(static_dir),
                    cache_headers=False,
                ),
            ]
        )
        domain_data[STATIC_REGISTRATION_KEY] = True

    host: str = (entry.options.get(CONF_HOST) or entry.data[CONF_HOST]).strip()

    chemistry_interval = timedelta(
        seconds=int(
            entry.options.get(
                CONF_SCAN_INTERVAL,
                int(DEFAULT_SCAN_INTERVAL.total_seconds()),
            )
        )
    )
    flow_interval = timedelta(
        seconds=int(
            entry.options.get(
                CONF_FLOW_SCAN_INTERVAL,
                int(DEFAULT_FLOW_SCAN_INTERVAL.total_seconds()),
            )
        )
    )

    session = async_get_clientsession(hass)

    async def _fetch_json(path: str) -> dict:
        url = f"http://{host}{path}"
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def _async_update_chemistry() -> dict:
        try:
            return dict(await _fetch_json(API_PATH_MEASUREMENTS) or {})
        except Exception as err:
            raise UpdateFailed(err) from err

    async def _async_update_flow() -> dict:
        try:
            measurements_payload = await _fetch_json(API_PATH_MEASUREMENTS)
            relays_payload = await _fetch_json(API_PATH_RELAYS)
        except Exception as err:
            raise UpdateFailed(err) from err

        merged: dict = dict(measurements_payload or {})
        merged["relays"] = (relays_payload or {}).get("relays", {})
        merged["relays_version"] = (relays_payload or {}).get("version")
        return merged

    chemistry_coordinator = DataUpdateCoordinator(
        hass=hass,
        logger=_LOGGER,
        name=f"{entry.data.get(CONF_NAME, entry.title)} Chemistry",
        update_method=_async_update_chemistry,
        update_interval=chemistry_interval,
    )
    flow_coordinator = DataUpdateCoordinator(
        hass=hass,
        logger=_LOGGER,
        name=f"{entry.data.get(CONF_NAME, entry.title)} Flow",
        update_method=_async_update_flow,
        update_interval=flow_interval,
    )

    try:
        await chemistry_coordinator.async_config_entry_first_refresh()
        await flow_coordinator.async_config_entry_first_refresh()
    except UpdateFailed as err:
        raise ConfigEntryNotReady(str(err)) from err

    domain_data[entry.entry_id] = {
        COORDINATOR_CHEMISTRY: chemistry_coordinator,
        COORDINATOR_FLOW: flow_coordinator,
    }

    await _async_remove_stale_last_successful_update_entity(hass, entry)
    await _async_clear_stale_device_configuration_url(hass, entry)

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def _async_clear_stale_device_configuration_url(
    hass: HomeAssistant, entry: ConfigEntry
) -> None:
    device_registry = dr.async_get(hass)
    device = device_registry.async_get_device(identifiers={(DOMAIN, entry.entry_id)})
    if device is None or device.configuration_url is None:
        return

    device_registry.async_update_device(
        device.id,
        configuration_url=None,
    )


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok


async def _async_remove_stale_last_successful_update_entity(
    hass: HomeAssistant, entry: ConfigEntry
) -> None:
    registry = er.async_get(hass)
    stale_suffixes = {
        "_last_successful_update",
        "_last_successful",
        "_last_update_successful",
    }

    for entity_entry in er.async_entries_for_config_entry(registry, entry.entry_id):
        unique_id = entity_entry.unique_id or ""
        original_name = (entity_entry.original_name or "").strip().lower()
        if unique_id.endswith(tuple(stale_suffixes)) or original_name == "last successful update":
            registry.async_remove(entity_entry.entity_id)
