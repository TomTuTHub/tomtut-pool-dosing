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
        PoolFlowSwitchSensor(coordinator, entry),
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
    _attr_has_entity_name = True

    def __init__(self, coordinator, entry: ConfigEntry):
        super().__init__(coordinator, entry)
        meta = MEASUREMENTS["ph"]
        self._key = "ph"

        # HA erzeugt daraus: "<Gerät> pH" (weil _attr_has_entity_name=True)
        self._attr_name = meta.get("name", "pH")
        self._attr_unique_id = f"{entry.entry_id}_ph"
        self._attr_icon = meta.get("icon")
        self._attr_native_unit_of_measurement = meta.get("unit")

    @property
    def native_value(self):
        data = (self.coordinator.data or {}).get("measurements", {})
        return (data.get(self._key, {}) or {}).get("value")


class PoolRedoxSensor(_Base):
    _attr_has_entity_name = True

    def __init__(self, coordinator, entry: ConfigEntry):
        super().__init__(coordinator, entry)
        meta = MEASUREMENTS["rx"]
        self._key = "rx"

        self._attr_name = meta.get("name", "Redox")
        self._attr_unique_id = f"{entry.entry_id}_rx"
        self._attr_icon = meta.get("icon")
        self._attr_native_unit_of_measurement = meta.get("unit")

    @property
    def native_value(self):
        data = (self.coordinator.data or {}).get("measurements", {})
        value = (data.get(self._key, {}) or {}).get("value")

        if isinstance(value, str):
            normalized = value.strip().replace(",", ".")
            try:
                numeric = float(normalized)
            except ValueError:
                return value

            if numeric.is_integer():
                return int(numeric)
            return numeric

        return value


class PoolFlowSwitchSensor(_Base):
    _attr_has_entity_name = True

    def __init__(self, coordinator, entry: ConfigEntry):
        super().__init__(coordinator, entry)
        meta = MEASUREMENTS["flowswitch"]
        self._key = "flowswitch"

        self._attr_name = meta.get("name", "Flow")
        self._attr_unique_id = f"{entry.entry_id}_flowswitch"
        self._attr_icon = meta.get("icon")
        # flowswitch ist 0/1 -> keine Einheit
        self._attr_native_unit_of_measurement = None

    @property
    def native_value(self):
        data = (self.coordinator.data or {}).get("measurements", {})
        return (data.get(self._key, {}) or {}).get("value")


class PoolFirmwareVersionSensor(_Base):
    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:information-outline"

    def __init__(self, coordinator, entry: ConfigEntry):
        super().__init__(coordinator, entry)
        self._attr_name = "Firmware Version"
        self._attr_unique_id = f"{entry.entry_id}_firmware_version"

    @property
    def native_value(self):
        return (self.coordinator.data or {}).get("version")


class PoolMacSensor(_Base):
    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:lan"

    def __init__(self, coordinator, entry: ConfigEntry):
        super().__init__(coordinator, entry)
        self._attr_name = "Device MAC"
        self._attr_unique_id = f"{entry.entry_id}_device_mac"

    @property
    def native_value(self):
        return (self.coordinator.data or {}).get("mac")
