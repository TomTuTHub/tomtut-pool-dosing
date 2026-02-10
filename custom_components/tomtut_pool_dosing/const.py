from __future__ import annotations

from datetime import timedelta

DOMAIN = "tomtut_pool_dosing"

CONF_HOST = "host"
CONF_NAME = "name"
CONF_SCAN_INTERVAL = "scan_interval"

DEFAULT_NAME = "TomTuT Pool Dosing"
DEFAULT_SCAN_INTERVAL = timedelta(seconds=10)  # 5s geht, 10s ist gesünder

API_PATH_MEASUREMENTS = "/api/measurements"
API_PATH_RELAYS = "/api/relays"

MEASUREMENTS: dict[str, dict] = {
    # =====================
    # Numeric measurements
    # =====================
    "ph": {
        "name": "pH",
        "unit": "pH",
        "icon": "mdi:flask",
    },
    "rx": {
        "name": "Redox",
        "unit": "mV",
        "icon": "mdi:flash-outline",
    },
    "conductivity": {
        "name": "Conductivity",
        "unit": "µS/cm",
        "icon": "mdi:water",
    },
    "pressure": {
        "name": "Pressure",
        "unit": "bar",
        "icon": "mdi:gauge",
    },
    "temperature_1": {
        "name": "Temperature 1",
        "unit": "°C",
        "icon": "mdi:thermometer",
    },
    "temperature_2": {
        "name": "Temperature 2",
        "unit": "°C",
        "icon": "mdi:thermometer",
    },
    "temperature_3": {
        "name": "Temperature 3",
        "unit": "°C",
        "icon": "mdi:thermometer",
    },

    # =====================
    # Binary / relay-like
    # =====================
    "flowswitch": {
        "name": "Flow",
        "binary": True,
        "icon": "mdi:pump",
    },
    "levelswitch_1": {
        "name": "pH Dosing Active",
        "binary": True,
        "icon": "mdi:beaker-outline",
    },
    "levelswitch_2": {
        "name": "Redox Dosing Active",
        "binary": True,
        "icon": "mdi:beaker-alert-outline",
    },
    "levelswitch_3": {
        "name": "Level Switch 3",
        "binary": True,
        "icon": "mdi:beaker-check",
    },
}

RELAYS: dict[str, str] = {
    "1": "Relay 1",
    "2": "Relay 2",
    "3": "Relay 3",
    "4": "Relay 4",
}
