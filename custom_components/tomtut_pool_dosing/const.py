from __future__ import annotations

from datetime import timedelta

DOMAIN = "tomtut_pool_dosing"

CONF_HOST = "host"
CONF_SCAN_INTERVAL = "scan_interval"

DEFAULT_SCAN_INTERVAL = timedelta(seconds=5)

API_PATH_MEASUREMENTS = "/api/measurements"
API_PATH_RELAYS = "/api/relays"

# Harte, finale Entity-ID Prefixes (so wie du es willst)
ENTITY_PREFIX = "tomtut_pool_dosieranlage"
FIRMWARE_ENTITY_ID = "sensor.firmware_version"
MAC_ENTITY_ID = "sensor.device_mac"

# Measurements (nur was du willst)
# keys exakt aus Example Response
MEASUREMENTS = {
    "ph": {"name": "pH", "unit": "pH", "icon": "mdi:flask"},
    "rx": {"name": "Redox", "unit": "mV", "icon": "mdi:flash-outline"},
    "flowswitch": {"name": "Flow", "unit": None, "icon": "mdi:pump"},
}

# Relays (nur was du willst)
RELAYS = {
    "1": "pH Injection (Relay 1)",
    "2": "Redox Injection (Relay 2)",
}
