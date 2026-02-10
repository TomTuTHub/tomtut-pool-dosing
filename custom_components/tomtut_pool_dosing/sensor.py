from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MEASUREMENTS, CONF_NAME


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[SensorEntity] = [
        PoolPhSensor(coordinator, entry),
        PoolRedoxSensor(coordinator, entry),
        PoolFirmwareVersionSensor(coordinator, entry),
        PoolMacSensor(coordinator, entry),
    ]

    async_add_entities(entities)


class _Base(CoordinatorEntity, SensorEntity):
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


class PoolPhSensor(_Base):
    _attr_has_entity_name = False  # wir setzen entity_id fest

    def __init__(self, coordinator, entry: ConfigEntry):
        super().__init__(coordinator, entry)
        meta = MEASUREMENTS["ph"]
        self._key = "ph"

        self._attr_name = "TomTuT Pool Dosieranlage pH"
        self._attr_unique_id = f"{entry.entry_id}_ph"
        self._attr_icon = meta.get("icon")
        self._attr_native_unit_of_measurement = meta.get("unit")

        # ✅ exakt deine gewünschte Entity-ID
        self.entity_id = "sensor.tomtut_pool_dosieranlage_ph"

    @property
    def native_value(self):
        data = (self.coordinator.data or {}).get("measurements", {})
        return (data.get(self._key, {}) or {}).get("value")


class PoolRedoxSensor(_Base):
    _attr_has_entity_name = False

    def __init__(self, coordinator, entry: ConfigEntry):
        super().__init__(coordinator, entry)
        meta = MEASUREMENTS["rx"]
        self._key = "rx"

        self._attr_name = "TomTuT Pool Dosieranlage Redox"
        self._attr_unique_id = f"{entry.entry_id}_redox"
        self._attr_icon = meta.get("icon")
        self._attr_native_unit_of_measurement = meta.get("unit")

        # ✅ exakt deine gewünschte Entity-ID
        self.entity_id = "sensor.tomtut_pool_dosieranlage_redox"

    @property
    def native_value(self):
        data = (self.coordinator.data or {}).get("measurements", {})
        return (data.get(self._key, {}) or {}).get("value")


class PoolFirmwareVersionSensor(_Base):
    _attr_has_entity_name = False
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:information-outline"

    def __init__(self, coordinator, entry: ConfigEntry):
        super().__init__(coordinator, entry)
        self._attr_name = "Firmware Version"
        self._attr_unique_id = f"{entry.entry_id}_firmware_version"

        # ✅ exakt deine gewünschte Entity-ID
        self.entity_id = "sensor.firmware_version"

    @property
    def native_value(self):
        return (self.coordinator.data or {}).get("version")


class PoolMacSensor(_Base):
    _attr_has_entity_name = False
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:lan"

    def __init__(self, coordinator, entry: ConfigEntry):
        super().__init__(coordinator, entry)
        self._attr_name = "Device MAC"
        self._attr_unique_id = f"{entry.entry_id}_device_mac"

        # ✅ exakt deine gewünschte Entity-ID
        self.entity_id = "sensor.device_mac"

    @property
    def native_value(self):
        return (self.coordinator.data or {}).get("mac")
