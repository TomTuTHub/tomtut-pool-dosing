from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import slugify

from .const import DOMAIN, MEASUREMENTS, RELAYS, CONF_NAME


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[BinarySensorEntity] = []

    # -------------------------
    # Measurement-based binaries
    # -------------------------
    for key, meta in MEASUREMENTS.items():
        if meta.get("binary"):
            entities.append(
                PoolMeasurementBinary(
                    coordinator=coordinator,
                    entry=entry,
                    key=key,
                    meta=meta,
                )
            )

    # -------------------------
    # Relay-based binaries
    # -------------------------
    for relay_id, name in RELAYS.items():
        entities.append(
            PoolRelayBinary(
                coordinator=coordinator,
                entry=entry,
                relay_id=relay_id,
                name=name,
            )
        )

    async_add_entities(entities)


# ==========================================================
# Base class
# ==========================================================
class _BaseBinary(CoordinatorEntity, BinarySensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator, entry: ConfigEntry):
        super().__init__(coordinator)
        self._entry = entry
        self._device_name = entry.data.get(CONF_NAME, entry.title)
        self._device_slug = slugify(self._device_name)

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": self._device_name,
            "manufacturer": "Vendor-neutral (Beniferro / Poolsana compatible)",
            "model": "Pool Dosing (local API)",
        }


# ==========================================================
# Measurement binary sensors
# ==========================================================
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
        return value == 1


# ==========================================================
# Relay binary sensors
# ==========================================================
class PoolRelayBinary(_BaseBinary):
    def __init__(self, coordinator, entry: ConfigEntry, relay_id: str, name: str):
        super().__init__(coordinator, entry)
        self._relay_id = relay_id

        self._attr_name = name
        self._attr_unique_id = f"{entry.entry_id}_relay_{relay_id}"
        self._attr_icon = "mdi:power-plug"

    @property
    def is_on(self):
        relays = (self.coordinator.data or {}).get("relays", {})
        relay = relays.get(self._relay_id, {})
        return bool(relay.get("power"))
