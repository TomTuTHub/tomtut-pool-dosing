from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MEASUREMENTS, RELAYS, RELAY_FIELDS, CONF_NAME


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[BinarySensorEntity] = []

    # Measurement-based binaries (0/1)
    for key, meta in MEASUREMENTS.items():
        if meta.get("binary"):
            entities.append(PoolMeasurementBinary(coordinator, entry, key, meta))

    # Relay endpoint binaries (power/can_run/duty_active/locked)
    for relay_id, relay_name in RELAYS.items():
        for field_key, field_meta in RELAY_FIELDS.items():
            entities.append(PoolRelayFieldBinary(coordinator, entry, relay_id, relay_name, field_key, field_meta))

    async_add_entities(entities)


class _BaseBinary(CoordinatorEntity, BinarySensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator, entry: ConfigEntry):
        super().__init__(coordinator)
        self._entry = entry
        self._device_name = entry.data.get(CONF_NAME, entry.title)

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": self._device_name,
            "manufacturer": "Vendor-neutral (Beniferro/Poolsana compatible)",
            "model": "Pool Dosing (local API)",
        }


class PoolMeasurementBinary(_BaseBinary):
    def __init__(self, coordinator, entry: ConfigEntry, key: str, meta: dict):
        super().__init__(coordinator, entry)
        self._key = key

        self._attr_name = meta.get("name", key)
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_icon = meta.get("icon")

    @property
    def is_on(self):
        data = (self.coordinator.data or {}).get("measurements", {})
        value = (data.get(self._key, {}) or {}).get("value")
        if value is None:
            return None
        return value == 1


class PoolRelayFieldBinary(_BaseBinary):
    def __init__(self, coordinator, entry: ConfigEntry, relay_id: str, relay_name: str, field_key: str, field_meta: dict):
        super().__init__(coordinator, entry)
        self._relay_id = relay_id
        self._field_key = field_key

        field_label = field_meta.get("name", field_key)
        self._attr_name = f"{relay_name} {field_label}"
        self._attr_unique_id = f"{entry.entry_id}_relay_{relay_id}_{field_key}"
        self._attr_icon = field_meta.get("icon")

    @property
    def is_on(self):
        relays = (self.coordinator.data or {}).get("relays", {})
        relay = relays.get(self._relay_id, {})
        value = relay.get(self._field_key)
        if value is None:
            return None
        return bool(value)
