from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MEASUREMENTS


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        PoolBinarySensor(coordinator, entry, key, meta)
        for key, meta in MEASUREMENTS.items()
        if meta.get("binary")
    ]

    async_add_entities(entities)


class PoolBinarySensor(CoordinatorEntity, BinarySensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator, entry: ConfigEntry, key: str, meta: dict):
        super().__init__(coordinator)
        self._entry = entry
        self._key = key
        self._meta = meta

        self._attr_name = meta.get("name", key)
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_icon = meta.get("icon")

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": self._entry.title,
            "manufacturer": "Vendor-neutral (Beniferro/Poolsana compatible)",
            "model": "Pool Dosing (local API)",
        }

    @property
    def is_on(self):
        data = (self.coordinator.data or {}).get("measurements", {})
        value = (data.get(self._key, {}) or {}).get("value")
        return bool(value) if value is not None else None
