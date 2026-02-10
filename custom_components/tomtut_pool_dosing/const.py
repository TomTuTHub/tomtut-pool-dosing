from __future__ import annotations

from datetime import timedelta

DOMAIN = "tomtut_pool_dosing"

CONF_HOST = "host"

# festes Polling (Coordinator)
DEFAULT_UPDATE_INTERVAL = timedelta(seconds=5)

API_PATH_MEASUREMENTS = "/api/measurements"
API_PATH_RELAYS = "/api/relays"

MEASUREMENTS: dict[str, dict] = {
    # numeric
    "ph": {"name": "pH", "unit": "pH", "icon": "mdi:flask"},
    "rx": {"name": "Redox", "unit": "mV", "icon": "mdi:flash-outline"},
    "conductivity": {"name": "Conductivity", "unit": "µS/cm", "icon": "mdi:water"},
    "pressure": {"name": "Pressure", "unit": "bar", "icon": "mdi:gauge"},
    "temperature_1": {"name": "Temperature 1", "unit": "°C", "icon": "mdi:thermometer"},
    "temperature_2": {"name": "Temperature 2", "unit": "°C", "icon": "mdi:thermometer"},
    "temperature_3": {"name": "Temperature 3", "unit": "°C", "icon": "mdi:thermometer"},

    # binary
    "flowswitch": {"name": "Flow", "binary": True, "icon": "mdi:water-pump"},
    "levelswitch_1": {"name": "pH Level", "binary": True, "icon": "mdi:beaker-outline"},
    "levelswitch_2": {"name": "Rx Level", "binary": True, "icon": "mdi:beaker-alert-outline"},
    "levelswitch_3": {"name": "Level Switch 3", "binary": True, "icon": "mdi:beaker-check"},
}

RELAYS: dict[str, str] = {
    "1": "Relay 1",
    "2": "Relay 2",
    "3": "Relay 3",
    "4": "Relay 4",
}
