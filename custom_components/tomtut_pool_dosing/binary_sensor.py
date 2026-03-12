from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import COORDINATOR_FLOW, DOMAIN
from .entity import PoolDosingEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR_FLOW]

    entities: list[BinarySensorEntity] = [
        PoolRelayPowerBinary(coordinator, entry, relay_id="1"),
        PoolRelayPowerBinary(coordinator, entry, relay_id="2"),
    ]

    async_add_entities(entities)


class _BaseBinary(PoolDosingEntity, BinarySensorEntity):
    pass


class PoolRelayPowerBinary(_BaseBinary):
    def __init__(self, coordinator, entry: ConfigEntry, relay_id: str):
        super().__init__(coordinator, entry)
        self._relay_id = relay_id

        self._attr_translation_key = f"relay_{relay_id}"
        self._attr_unique_id = f"{entry.entry_id}_relay_{relay_id}_power"
        self._attr_icon = "mdi:pump"

    @property
    def is_on(self):
        relays = (self.coordinator.data or {}).get("relays", {})
        relay = relays.get(self._relay_id, {}) or {}
        value = relay.get("power")
        if value is None:
            return None
        return bool(value)
