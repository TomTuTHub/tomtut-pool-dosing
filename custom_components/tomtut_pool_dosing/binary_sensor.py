from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MEASUREMENTS, RELAYS


DEVICE_INFO = {
    "identifiers": {("tomtut_pool_dosing", "tomtut_pool_dosieranlage")},
    "name": "TomTuT Pool Dosieranlage",
    "manufacturer": "TomTuT / Beniferro",
    "model": "Gen2",
}


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []

    for key, meta in MEASUREMENTS.items():
        if meta.get("binary"):
            entities.append(
                PoolBinary(coordinator, key, meta["name"], meta.get("icon"))
            )

    for relay_id, name in RELAYS.items():
        entities.append(RelayBinary(coordinator, relay_id, name))

    async_add_entities(entities)


class PoolBinary(CoordinatorEntity, BinarySensorEntity):
    def __init__(self, coordinator, key, name, icon):
        super().__init__(coordinator)
        self.key = key

        self._attr_name = f"TomTuT Pool Dosieranlage {name}"
        self._attr_unique_id = f"tomtut_pool_dosieranlage_{key}"
        self._attr_icon = icon
        self._attr_device_info = DEVICE_INFO

    @property
    def is_on(self):
        val = (
            self.coordinator.data
            .get("measurements", {})
            .get(self.key, {})
            .get("value")
        )
        return None if val is None else bool(int(val))


class RelayBinary(CoordinatorEntity, BinarySensorEntity):
    def __init__(self, coordinator, relay_id, name):
        super().__init__(coordinator)
        self.relay_id = relay_id

        self._attr_name = f"TomTuT Pool Dosieranlage {name}"
        self._attr_unique_id = f"tomtut_pool_dosieranlage_relay_{relay_id}"
        self._attr_icon = "mdi:power-plug"
        self._attr_device_info = DEVICE_INFO

    @property
    def is_on(self):
        return bool(
            self.coordinator.data
            .get("relays", {})
            .get(self.relay_id, {})
            .get("power")
        )
