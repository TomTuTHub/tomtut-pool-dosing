from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, ENTITY_PREFIX, RELAYS


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[BinarySensorEntity] = [
        PoolRelayPowerBinary(coordinator, entry, relay_id="1"),
        PoolRelayPowerBinary(coordinator, entry, relay_id="2"),
    ]

    async_add_entities(entities)


class _BaseBinary(CoordinatorEntity, BinarySensorEntity):
    _attr_has_entity_name = False

    def __init__(self, coordinator, entry: ConfigEntry):
        super().__init__(coordinator)
        self._entry = entry

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": "TomTuT Pool Dosieranlage",
            "manufacturer": "Beniferro / Poolsana compatible",
            "model": "Pool Dosing (local API)",
        }


class PoolRelayPowerBinary(_BaseBinary):
    def __init__(self, coordinator, entry: ConfigEntry, relay_id: str):
        super().__init__(coordinator, entry)
        self._relay_id = relay_id

        # Entity-IDs:
        # bsp: binary_sensor.tomtut_pool_dosieranlage_relay_1_power
        self.entity_id = f"binary_sensor.{ENTITY_PREFIX}_relay_{relay_id}_power"

        self._attr_name = f"Relay {relay_id} Power"
        self._attr_unique_id = f"{entry.entry_id}_relay_{relay_id}_power"
        self._attr_icon = "mdi:power-plug"

    @property
    def is_on(self):
        relays = (self.coordinator.data or {}).get("relays", {})
        relay = relays.get(self._relay_id, {}) or {}
        value = relay.get("power")
        if value is None:
            return None
        return bool(value)
