from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CONF_HOST, MEASUREMENTS


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[SensorEntity] = []

    # Measurements (nur numeric)
    for key, meta in MEASUREMENTS.items():
        if meta.get("binary"):
            continue
        entities.append(PoolMeasurementSensor(coordinator, entry, key, meta))

    # Diagnostics: Version + MAC
    entities.append(PoolVersionSensor(coordinator, entry))
    entities.append(PoolMacSensor(coordinator, entry))

    async_add_entities(entities)


class _Base(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, entry: ConfigEntry):
        super().__init__(coordinator)
        self._entry = entry

    @property
    def device_info(self):
        # ein Gerät pro Config-Entry (ohne IP im Entity-Namen)
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": self._entry.title,
            "manufacturer": "Vendor-neutral (Beniferro/Poolsana compatible)",
            "model": "Pool Dosing (local API)",
        }


class PoolMeasurementSensor(_Base):
    _attr_has_entity_name = True

    def __init__(self, coordinator, entry: ConfigEntry, key: str, meta: dict):
        super().__init__(coordinator, entry)
        self._key = key
        self._meta = meta

        self._attr_name = meta.get("name", key)
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_icon = meta.get("icon")
        self._attr_native_unit_of_measurement = meta.get("unit")

    @property
    def native_value(self):
        data = (self.coordinator.data or {}).get("measurements", {})
        return (data.get(self._key, {}) or {}).get("value")


class PoolVersionSensor(_Base):
    _attr_name = "Firmware Version"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:information-outline"

    def __init__(self, coordinator, entry: ConfigEntry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_version"

    @property
    def native_value(self):
        return (self.coordinator.data or {}).get("version")


class PoolMacSensor(_Base):
    _attr_name = "Device MAC"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:lan"

    def __init__(self, coordinator, entry: ConfigEntry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_mac"

    @property
    def native_value(self):
        return (self.coordinator.data or {}).get("mac")
