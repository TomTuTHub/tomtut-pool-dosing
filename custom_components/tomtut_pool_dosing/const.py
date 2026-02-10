from __future__ import annotations

from datetime import timedelta

DOMAIN = "tomtut_pool_dosing"

CONF_HOST = "host"
CONF_NAME = "name"
CONF_SCAN_INTERVAL = "scan_interval"

DEFAULT_NAME = "TomTuT Pool Dosieranlage"
DEFAULT_SCAN_INTERVAL = timedelta(seconds=5)

API_PATH_MEASUREMENTS = "/api/measurements"
API_PATH_RELAYS = "/api/relays"

# Minimal-Final: genau das, was du zuletzt wolltest (inkl. flowswitch als Sensorwert 0/1)
MEASUREMENTS: dict[str, dict] = {
    "ph": {"name": "pH", "unit": "pH", "icon": "mdi:flask"},
    "rx": {"name": "Redox", "unit": "mV", "icon": "mdi:flash-outline"},
    "flowswitch": {"name": "Flow", "unit": None, "icon": "mdi:pump"},
}

# Minimal-Final: nur Relay 1+2, und in HA verwenden wir nur "power"
RELAYS: dict[str, str] = {
    "1": "Relay 1",
    "2": "Relay 2",
}
