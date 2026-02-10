from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    MEASUREMENTS,
    ENTITY_PREFIX,
    FIRMWARE_ENTITY_ID,
    MAC_ENTITY_ID,
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[SensorEntity] = [
        PoolPhSensor(coordinator, entry),
        PoolRedoxSensor(coordinator, entry),
        PoolFlowSensor(coordinator, entry),
        PoolFirmwareSensor(coordinator, entry),
        PoolMacSensor(coordinator, entry),
    ]

    async_add_entities(entities)


class _Base(CoordinatorEntity, SensorEntity):
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


class PoolPhSensor(_Base):
    _attr_has_entity_name = False  # wir setzen Entity-ID & Name hart

    def __init__(self, coordinator, entry: ConfigEntry):
        super().__init__(coordinator, entry)

        meta = MEASUREMENTS["ph"]
        self.entity_id = f"sensor.{ENTITY_PREFIX}_ph"
        self._attr_name = "pH"
        self._attr_unique_id = f"{entry.entry_id}_ph"
        self._attr_icon = meta.get("icon")
        self._attr_native_unit_of_measurement = meta.get("unit")

    @property
    def native_value(self):
        data = (self.coordinator.data or {}).get("measurements", {})
        return (data.get("ph", {}) or {}).get("value")


class PoolRedoxSensor(_Base):
    _attr_has_entity_name = False

    def __init__(self, coordinator, entry: ConfigEntry):
        super().__init__(coordinator, entry)

        meta = MEASUREMENTS["rx"]
        self.entity_id = f"sensor.{ENTITY_PREFIX}_redox"
        self._attr_name = "Redox"
        self._attr_unique_id = f"{entry.entry_id}_rx"
        self._attr_icon = meta.get("icon")
        self._attr_native_unit_of_measurement = meta.get("unit")

    @property
    def native_value(self):
        data = (self.coordinator.data or {}).get("measurements", {})
        return (data.get("rx", {}) or {}).get("value")


class PoolFlowSensor(_Base):
    _attr_has_entity_name = False

    def __init__(self, coordinator, entry: ConfigEntry):
        super().__init__(coordinator, entry)

        meta = MEASUREMENTS["flowswitch"]
        self.entity_id = f"sensor.{ENTITY_PREFIX}_flow"
        self._attr_name = "Flow"
        self._attr_unique_id = f"{entry.entry_id}_flowswitch"
        self._attr_icon = meta.get("icon")
        # flowswitch ist 0/1 => keine Einheit
        self._attr_native_unit_of_measurement = None

    @property
    def native_value(self):
        data = (self.coordinator.data or {}).get("measurements", {})
        return (data.get("flowswitch", {}) or {}).get("value")


class PoolFirmwareSensor(_Base):
    _attr_has_entity_name = False
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:information-outline"

    def __init__(self, coordinator, entry: ConfigEntry):
        super().__init__(coordinator, entry)

        self.entity_id = FIRMWARE_ENTITY_ID
        self._attr_name = "Firmware Version"
        self._attr_unique_id = f"{entry.entry_id}_firmware"

    @property
    def native_value(self):
        return (self.coordinator.data or {}).get("version")


class PoolMacSensor(_Base):
    _attr_has_entity_name = False
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:lan"

    def __init__(self, coordinator, entry: ConfigEntry):
        super().__init__(coordinator, entry)

        self.entity_id = MAC_ENTITY_ID
        self._attr_name = "Device MAC"
        self._attr_unique_id = f"{entry.entry_id}_mac"

    @property
    def native_value(self):
        return (self.coordinator.data or {}).get("mac")
