from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CONF_HOST, MEASUREMENTS


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities,
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[SensorEntity] = []

    # Firmware/Version (top-level: {"version":"251203"})
    entities.append(PoolVersionSensor(coordinator, entry))

    # numeric measurement sensors
    for key, meta in MEASUREMENTS.items():
        if meta.get("binary"):
            continue
        entities.append(PoolMeasurementSensor(coordinator, entry, key, meta))

    async_add_entities(entities)


class PoolBaseSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self.entry = entry

    @property
    def device_info(self):
        host = self.entry.data.get(CONF_HOST, "unknown")
        # Alles unter EIN Gerät im UI bündeln
        return {
            "identifiers": {(DOMAIN, self.entry.unique_id or self.entry.entry_id)},
            "name": f"Pool Dosieranlage ({host})",
            "manufacturer": "Beniferro / Poolsana",
            "model": "Gen2",
        }


class PoolMeasurementSensor(PoolBaseSensor):
    def __init__(self, coordinator, entry: ConfigEntry, key: str, meta: dict) -> None:
        super().__init__(coordinator, entry)
        self.key = key
        self.meta = meta

        self._attr_name = meta.get("name", key)
        self._attr_icon = meta.get("icon")
        self._attr_native_unit_of_measurement = meta.get("unit")

        base = entry.unique_id or entry.entry_id
        self._attr_unique_id = f"{base}_measurement_{key}"

    @property
    def native_value(self):
        return (
            (self.coordinator.data or {})
            .get("measurements", {})
            .get(self.key, {})
            .get("value")
        )


class PoolVersionSensor(PoolBaseSensor):
    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_name = "Firmware Version"
        self._attr_icon = "mdi:numeric"

        base = entry.unique_id or entry.entry_id
        self._attr_unique_id = f"{base}_version"

    @property
    def native_value(self):
        return (self.coordinator.data or {}).get("version")
