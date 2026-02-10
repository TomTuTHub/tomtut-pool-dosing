from __future__ import annotations

from datetime import timedelta

DOMAIN = "tomtut_pool_dosing"

CONF_HOST = "host"
CONF_NAME = "name"
CONF_SCAN_INTERVAL = "scan_interval"

DEFAULT_NAME = "TomTuT Pool Dosing"
DEFAULT_SCAN_INTERVAL = timedelta(seconds=5)

API_PATH_MEASUREMENTS = "/api/measurements"
API_PATH_RELAYS = "/api/relays"

# Alles aus dem Example Response (measurements) + Binär-Markierung für die 0/1 Felder
MEASUREMENTS: dict[str, dict] = {
    # numeric
    "temperature_1": {"name": "Temperature 1", "unit": "°C", "icon": "mdi:thermometer"},
    "temperature_2": {"name": "Temperature 2", "unit": "°C", "icon": "mdi:thermometer"},
    "temperature_3": {"name": "Temperature 3", "unit": "°C", "icon": "mdi:thermometer"},
    "ph": {"name": "pH", "unit": "pH", "icon": "mdi:flask"},
    "rx": {"name": "Redox", "unit": "mV", "icon": "mdi:flash-outline"},
    "conductivity": {"name": "Conductivity", "unit": "µS/cm", "icon": "mdi:water"},
    "pressure": {"name": "Pressure", "unit": "bar", "icon": "mdi:gauge"},

    # binary (0/1)
    "flowswitch": {"name": "Flow", "binary": True, "icon": "mdi:pump"},
    "levelswitch_1": {"name": "pH Tank Level OK", "binary": True, "icon": "mdi:beaker-outline"},
    "levelswitch_2": {"name": "Redox Tank Level OK", "binary": True, "icon": "mdi:beaker-alert-outline"},
    "levelswitch_3": {"name": "Level Switch 3", "binary": True, "icon": "mdi:beaker-check"},
}

# Relay Outputs 1..4 (aus /api/relays)
RELAYS: dict[str, str] = {
    "1": "Relay 1",
    "2": "Relay 2",
    "3": "Relay 3",
    "4": "Relay 4",
}

# Relay-Felder aus der Doku / Example Response
RELAY_FIELDS: dict[str, dict] = {
    "power": {"name": "Power", "icon": "mdi:power-plug"},
    "can_run": {"name": "Can Run", "icon": "mdi:shield-check"},
    "duty_active": {"name": "Duty Active", "icon": "mdi:timer-sync"},
    "locked": {"name": "Locked", "icon": "mdi:lock"},
}
