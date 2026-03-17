from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_HOST, CONF_NAME, DOMAIN


class PoolDosingEntity(CoordinatorEntity):
    """Gemeinsame Basisklasse für alle TomTuT Pool Dosing Entitäten."""

    _attr_has_entity_name = True

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._device_name = entry.data.get(CONF_NAME, entry.title)
        self._host = (entry.options.get(CONF_HOST) or entry.data.get(CONF_HOST) or "").strip()

    @property
    def device_info(self) -> dict:
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": self._device_name,
            "manufacturer": "Vendor-neutral (Beniferro/Poolsana compatible)",
            "model": "Pool Dosing (local API)",
        }
