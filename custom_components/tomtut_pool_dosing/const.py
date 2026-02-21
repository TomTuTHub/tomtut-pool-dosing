from __future__ import annotations

from datetime import timedelta

DOMAIN = "tomtut_pool_dosing"

CONF_HOST = "host"
CONF_NAME = "name"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_FLOW_SCAN_INTERVAL = "flow_scan_interval"

DEFAULT_NAME = "TomTuT Pool Dosieranlage"
DEFAULT_SCAN_INTERVAL = timedelta(seconds=120)
DEFAULT_FLOW_SCAN_INTERVAL = timedelta(seconds=5)

API_PATH_MEASUREMENTS = "/api/measurements"
API_PATH_RELAYS = "/api/relays"

COORDINATOR_CHEMISTRY = "chemistry"
COORDINATOR_FLOW = "flow"

MEASUREMENTS: dict[str, dict] = {
    "ph": {"name": "pH", "unit": "pH", "icon": "mdi:flask"},
    "rx": {"name": "Redox", "unit": "mV", "icon": "mdi:flash-outline"},
    "flowswitch": {"name": "Flow", "unit": None, "icon": "mdi:pump"},
}

RELAYS: dict[str, str] = {
    "1": "Relay 1",
    "2": "Relay 2",
}
