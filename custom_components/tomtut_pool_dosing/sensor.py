from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MEASUREMENTS


DEVICE_INFO = {
    "identifiers": {("tomtut_pool_dosing", "tomtut_pool_dosieranlage")},
    "name": "TomTuT Pool Dosieranlage",
    "manufacturer": "TomTuT / Beniferro",
    "model": "Gen2",
}


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        PoolSensor(coordinator, key, meta)
        for key, meta in MEASUREMENTS.items()
        if not meta.get("binary")
    ]

    async_add_entities(entities)


class PoolSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, key, meta):
        super().__init__(coordinator)

        self.key = key

        self._attr_name = f"TomTuT Pool Dosieranlage {meta['name']}"
        self._attr_unique_id = f"tomtut_pool_dosieranlage_{key}"
        self._attr_icon = meta.get("icon")
        self._attr_native_unit_of_measurement = meta.get("unit")

        # 🔴 WICHTIG: exakt gleich wie bei binary_sensor.py
        self._attr_device_info = DEVICE_INFO

    @property
    def native_value(self):
        return (
            self.coordinator.data
            .get("measurements", {})
            .get(self.key, {})
            .get("value")
        )
