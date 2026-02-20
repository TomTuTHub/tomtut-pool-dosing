from __future__ import annotations

import logging
from datetime import timedelta
from pathlib import Path

import aiohttp
from aiohttp import web

from homeassistant.components.http import HomeAssistantView, StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    CONF_HOST,
    CONF_NAME,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    API_PATH_MEASUREMENTS,
    API_PATH_RELAYS,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[str] = ["sensor", "binary_sensor"]
STATIC_URL_PATH = "/api/tomtut_pool_dosing/static"
STATIC_URL_PATH_LOCAL = "/local/tomtut_pool_dosing"
IMAGE_API_URL = "/api/tomtut_pool_dosing/image/{filename}"
STATIC_REGISTRATION_KEY = "static_path_registered"
IMAGE_VIEW_REGISTRATION_KEY = "image_view_registered"


class PoolDosingImageView(HomeAssistantView):
    """Serve packaged integration images via a stable API endpoint."""

    url = IMAGE_API_URL
    name = "api:tomtut_pool_dosing:image"

    def __init__(self, static_dir: Path) -> None:
        self._static_dir = static_dir

    async def get(self, request, filename: str):
        if Path(filename).name != filename:
            return web.Response(status=400, text="Invalid filename")

        image_path = self._static_dir / filename
        if not image_path.is_file():
            return web.Response(status=404, text="Image not found")

        return web.FileResponse(path=image_path, headers={"Cache-Control": "no-store"})


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    domain_data = hass.data.setdefault(DOMAIN, {})

    static_dir = Path(__file__).parent / "static"

    if not domain_data.get(STATIC_REGISTRATION_KEY):
        await hass.http.async_register_static_paths(
            [
                StaticPathConfig(
                    STATIC_URL_PATH,
                    str(static_dir),
                    cache_headers=False,
                ),
                StaticPathConfig(
                    STATIC_URL_PATH_LOCAL,
                    str(static_dir),
                    cache_headers=False,
                ),
            ]
        )
        domain_data[STATIC_REGISTRATION_KEY] = True

    if not domain_data.get(IMAGE_VIEW_REGISTRATION_KEY):
        hass.http.register_view(PoolDosingImageView(static_dir))
        domain_data[IMAGE_VIEW_REGISTRATION_KEY] = True

    host: str = (entry.options.get(CONF_HOST) or entry.data[CONF_HOST]).strip()

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
        name=entry.data.get(CONF_NAME, entry.title),
        update_method=_async_update,
        update_interval=update_interval,
    )

    try:
        await coordinator.async_config_entry_first_refresh()
    except UpdateFailed as err:
        # Wichtig: nicht “hart failen”, sondern HA soll retryen
        raise ConfigEntryNotReady(str(err)) from err

    domain_data[entry.entry_id] = coordinator

    await _async_remove_stale_last_successful_update_entity(hass, entry)

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update by reloading the config entry."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok


async def _async_remove_stale_last_successful_update_entity(
    hass: HomeAssistant, entry: ConfigEntry
) -> None:
    """Remove stale diagnostics entity from older versions.

    Some previous integration versions created a "Last Successful Update" sensor,
    which is no longer provided. This prevents a persistent "entity no longer
    provided" warning for users after updating.
    """
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
