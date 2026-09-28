#!/usr/bin/env python3
"""Regressionstest zu Issue #2: Kaltstart bei ausgeschalteter Dosieranlage.

Laeuft OHNE Home Assistant, ohne aiohttp, ohne pytest und ohne Hardware
(die HA-Module werden minimal gestubbt):

    python3 tests/test_setup_offline.py

Geprueft wird die echte `__init__.py` zusammen mit `sensor.py` und
`binary_sensor.py`:

  * Anlage aus beim Start -> Setup laeuft durch, Entitaeten existieren,
    Werte leer, `available` False   (das war der Bug: vorher brach das Setup
    mit ConfigEntryNotReady ab und es entstand ueberhaupt keine Entitaet)
  * Anlage kommt zurueck -> derselbe Coordinator fuellt die Werte, ohne dass
    der Config-Entry neu geladen werden muss
  * Anlage von Anfang an erreichbar -> unveraendertes Verhalten
  * echte Programmierfehler (ConfigEntryError) werden NICHT verschluckt
  * beide Coordinator bekommen ihren Config-Entry explizit mit
"""
from __future__ import annotations

import asyncio
import enum
import importlib
import importlib.util
import pathlib
import sys
import types

BASE = pathlib.Path(__file__).resolve().parents[1] / "custom_components" / "tomtut_pool_dosing"


def _mod(name, **attrs):
    m = types.ModuleType(name)
    m.__dict__.update(attrs)
    sys.modules[name] = m
    return m


# ---- minimale HA-/aiohttp-Stubs ---------------------------------------------
class ConfigEntryNotReady(Exception):
    """HA: Setup spaeter erneut versuchen."""


class ConfigEntryError(Exception):
    """HA: fataler Setup-Fehler, kein Retry."""


class UpdateFailed(Exception):
    """HA: eine Aktualisierung ist fehlgeschlagen."""


class StaticPathConfig:
    def __init__(self, url_path, path, cache_headers=True):
        self.url_path = url_path
        self.path = path


class EntityCategory(str, enum.Enum):
    DIAGNOSTIC = "diagnostic"


class SensorEntity:
    pass


class BinarySensorEntity:
    pass


_UNGESETZT = object()


class DataUpdateCoordinator:
    """Nachbau der fuer diese Integration relevanten HA-Semantik."""

    fehler_beim_erst_refresh: Exception | None = None  # vom Test gesetzt

    def __init__(self, *, hass, logger, name, update_method, update_interval,
                 config_entry=_UNGESETZT):
        self.hass = hass
        self.logger = logger
        self.name = name
        self.update_method = update_method
        self.update_interval = update_interval
        # HA wuerde hier auf die ContextVar zurueckfallen; der Test will sehen,
        # ob die Integration den Entry ausdruecklich mitgibt.
        self.config_entry = None if config_entry is _UNGESETZT else config_entry
        self.data = None
        self.last_update_success = False
        self.last_exception = None

    async def async_config_entry_first_refresh(self):
        if type(self).fehler_beim_erst_refresh is not None:
            raise type(self).fehler_beim_erst_refresh
        if self.config_entry is None:
            raise ConfigEntryError(
                "`async_config_entry_first_refresh` is only supported for "
                "coordinators with a config entry"
            )
        await self.async_refresh()
        if self.last_update_success:
            return
        fehler = ConfigEntryNotReady()
        fehler.__cause__ = self.last_exception
        raise fehler

    async def async_refresh(self):
        try:
            self.data = await self.update_method()
        except UpdateFailed as err:
            self.last_exception = err
            self.last_update_success = False
            return
        self.last_update_success = True


class CoordinatorEntity:
    def __init__(self, coordinator):
        self.coordinator = coordinator

    @property
    def available(self):
        return self.coordinator.last_update_success


class ClientTimeout:
    def __init__(self, total=None):
        self.total = total


class ClientConnectorError(OSError):
    pass


_mod("aiohttp", ClientTimeout=ClientTimeout, ClientConnectorError=ClientConnectorError)
_mod("homeassistant")
_mod("homeassistant.components")
_mod("homeassistant.components.http", StaticPathConfig=StaticPathConfig)
_mod("homeassistant.components.sensor", SensorEntity=SensorEntity)
_mod("homeassistant.components.binary_sensor", BinarySensorEntity=BinarySensorEntity)
_mod("homeassistant.config_entries", ConfigEntry=object)
_mod("homeassistant.const", EntityCategory=EntityCategory)
_mod("homeassistant.core", HomeAssistant=object)
_mod("homeassistant.exceptions", ConfigEntryNotReady=ConfigEntryNotReady,
     ConfigEntryError=ConfigEntryError)
_mod("homeassistant.helpers")
_mod("homeassistant.helpers.device_registry", async_get=lambda hass: hass.device_registry)
_mod("homeassistant.helpers.entity_registry", async_get=lambda hass: hass.entity_registry,
     async_entries_for_config_entry=lambda registry, entry_id: list(registry.eintraege))
_mod("homeassistant.helpers.aiohttp_client",
     async_get_clientsession=lambda hass: hass.session)
_mod("homeassistant.helpers.update_coordinator",
     DataUpdateCoordinator=DataUpdateCoordinator, UpdateFailed=UpdateFailed,
     CoordinatorEntity=CoordinatorEntity)

# ---- echte Integration laden -------------------------------------------------
spec = importlib.util.spec_from_file_location(
    "tomtut_pool_dosing", BASE / "__init__.py", submodule_search_locations=[str(BASE)]
)
integration = importlib.util.module_from_spec(spec)
sys.modules["tomtut_pool_dosing"] = integration
spec.loader.exec_module(integration)
sensor_platform = importlib.import_module("tomtut_pool_dosing.sensor")
binary_platform = importlib.import_module("tomtut_pool_dosing.binary_sensor")


# ---- Testdoubles -------------------------------------------------------------
MESSWERTE = {
    "measurements": {
        "ph": {"value": 7.2},
        "rx": {"value": "715"},
        "flowswitch": {"value": "on"},
    },
    "version": "2.14",
    "mac": "AA:BB:CC:DD:EE:FF",
}
RELAIS = {"relays": {"1": {"power": 1}, "2": {"power": 0}}, "version": "2.14"}


class FakeAntwort:
    def __init__(self, payload):
        self._payload = payload

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False

    def raise_for_status(self):
        return None

    async def json(self):
        return self._payload


class FakeSession:
    """Dosieranlage: `erreichbar` schaltet sie an und aus."""

    def __init__(self, erreichbar=False):
        self.erreichbar = erreichbar
        self.aufrufe = []

    def get(self, url, timeout=None):
        self.aufrufe.append(url)
        if not self.erreichbar:
            raise ClientConnectorError("Connection refused")
        payload = RELAIS if url.endswith("/api/relays") else MESSWERTE
        return FakeAntwort(payload)


class FakeRegistry:
    def __init__(self):
        self.eintraege = []
        self.entfernt = []

    def async_remove(self, entity_id):
        self.entfernt.append(entity_id)

    def async_get_device(self, identifiers=None):
        return None

    def async_update_device(self, *args, **kwargs):
        return None


class FakeHttp:
    def __init__(self):
        self.registriert = []

    async def async_register_static_paths(self, configs):
        for cfg in configs:
            if cfg.url_path in self.registriert:
                raise RuntimeError(f"Pfad {cfg.url_path} ist bereits registriert")
            self.registriert.append(cfg.url_path)


class FakeConfigEntries:
    def __init__(self):
        self.weitergereicht = []

    async def async_forward_entry_setups(self, entry, platforms):
        self.weitergereicht.append((entry, list(platforms)))


class FakeHass:
    def __init__(self, session):
        self.data = {}
        self.session = session
        self.http = FakeHttp()
        self.config_entries = FakeConfigEntries()
        self.device_registry = FakeRegistry()
        self.entity_registry = FakeRegistry()


class FakeEntry:
    def __init__(self):
        self.entry_id = "entry1"
        self.title = "Pool Dosieranlage"
        self.data = {"host": "192.168.1.50", "name": "Pool Dosieranlage"}
        self.options = {}
        self.aufraeumer = []

    def add_update_listener(self, listener):
        return lambda: None

    def async_on_unload(self, func):
        self.aufraeumer.append(func)


def entitaeten_bauen(hass, entry):
    """Die echten Plattform-Setups laufen lassen und alle Entitaeten einsammeln."""
    gesammelt = []
    asyncio.run(sensor_platform.async_setup_entry(hass, entry, gesammelt.extend))
    asyncio.run(binary_platform.async_setup_entry(hass, entry, gesammelt.extend))
    return gesammelt


def hole(entitaeten, klasse, nr=0):
    """Entitaet nach Klassenname holen (die beiden Relais teilen sich eine Klasse)."""
    return [e for e in entitaeten if type(e).__name__ == klasse][nr]


# ---- Checks ------------------------------------------------------------------
bestanden = 0
gescheitert = []


def check(bedingung, text):
    global bestanden
    if bedingung:
        bestanden += 1
        print(f"  ok   {text}")
    else:
        gescheitert.append(text)
        print(f"  FEHL {text}")


print("1) Kaltstart mit ausgeschalteter Anlage (Issue #2)")
session = FakeSession(erreichbar=False)
hass = FakeHass(session)
entry = FakeEntry()
try:
    erfolg = asyncio.run(integration.async_setup_entry(hass, entry))
    abbruch = None
except BaseException as err:  # noqa: BLE001
    erfolg, abbruch = False, err
check(abbruch is None,
      f"Setup bricht NICHT mehr ab (vorher ConfigEntryNotReady){'' if abbruch is None else f' - {abbruch!r}'}")
check(erfolg is True, "async_setup_entry meldet True (Entry bleibt geladen)")
check(len(hass.config_entries.weitergereicht) == 1
      and hass.config_entries.weitergereicht[0][1] == ["sensor", "binary_sensor"],
      "beide Plattformen werden aufgebaut -> Entitaeten entstehen")
check(entry.entry_id in hass.data.get(integration.DOMAIN, {}),
      "Coordinator liegen in hass.data")

if entry.entry_id not in hass.data.get(integration.DOMAIN, {}):
    print("\nDas Setup ist abgebrochen - alles Weitere ist nicht mehr pruefbar.")
    print(f"{len(gescheitert)} Checks GESCHEITERT:")
    for t in gescheitert:
        print("  -", t)
    sys.exit(1)

koordinatoren = hass.data[integration.DOMAIN][entry.entry_id]
chemie = koordinatoren[integration.COORDINATOR_CHEMISTRY]
fluss = koordinatoren[integration.COORDINATOR_FLOW]
check(chemie.config_entry is entry and fluss.config_entry is entry,
      "beide Coordinator bekommen config_entry ausdruecklich mit")
check(chemie.last_update_success is False and chemie.data is None,
      "Chemie-Coordinator weiss, dass er keine Daten hat")

entitaeten = entitaeten_bauen(hass, entry)
check(len(entitaeten) == 11, f"11 Entitaeten gebaut (gefunden: {len(entitaeten)})")
check(hole(entitaeten, "PoolPhSensor").native_value is None
      and hole(entitaeten, "PoolRedoxSensor").native_value is None,
      "pH und Redox liefern None statt zu crashen")
check(hole(entitaeten, "PoolRelayPowerBinary", 0).is_on is None
      and hole(entitaeten, "PoolRelayPowerBinary", 1).is_on is None,
      "beide Relais liefern None statt zu crashen")
check(hole(entitaeten, "PoolPhSensor").available is False,
      "Entitaeten sind 'nicht verfuegbar' (genau das gewuenschte Verhalten)")
check(hole(entitaeten, "PoolDeviceNameSensor").native_value == "Pool Dosieranlage",
      "statische Diagnose-Sensoren liefern trotzdem ihren Wert")

print("2) Anlage wird eingeschaltet - ohne Neuladen des Entry")
session.erreichbar = True
asyncio.run(chemie.async_refresh())
asyncio.run(fluss.async_refresh())
check(hole(entitaeten, "PoolPhSensor").native_value == 7.2, "pH fuellt sich (7.2)")
check(hole(entitaeten, "PoolRedoxSensor").native_value == 715, "Redox fuellt sich (715)")
check(hole(entitaeten, "PoolFirmwareVersionSensor").native_value == "2.14", "Firmware fuellt sich")
check(hole(entitaeten, "PoolRelayPowerBinary", 0).is_on is True
      and hole(entitaeten, "PoolRelayPowerBinary", 1).is_on is False,
      "Relais 1 meldet an, Relais 2 aus")
check(hole(entitaeten, "PoolPhSensor").available is True, "Entitaeten sind wieder verfuegbar")

print("3) Anlage von Anfang an erreichbar (unveraenderter Normalfall)")
hass2 = FakeHass(FakeSession(erreichbar=True))
entry2 = FakeEntry()
check(asyncio.run(integration.async_setup_entry(hass2, entry2)) is True, "Setup erfolgreich")
entitaeten2 = entitaeten_bauen(hass2, entry2)
check(hole(entitaeten2, "PoolPhSensor").native_value == 7.2
      and hole(entitaeten2, "PoolPhSensor").available is True,
      "Werte stehen sofort bereit")
check(hass2.http.registriert == [integration.STATIC_URL_PATH],
      "statischer Bildpfad wird registriert")

print("4) Grenzen: fatale Fehler werden nicht verschluckt")
DataUpdateCoordinator.fehler_beim_erst_refresh = ConfigEntryError("kaputt verdrahtet")
try:
    asyncio.run(integration.async_setup_entry(FakeHass(FakeSession()), FakeEntry()))
    durchgereicht = False
except ConfigEntryError:
    durchgereicht = True
finally:
    DataUpdateCoordinator.fehler_beim_erst_refresh = None
check(durchgereicht, "ConfigEntryError bricht das Setup weiterhin ab")

print("5) Doppel-Setup registriert den Bildpfad nicht erneut")
hass3 = FakeHass(FakeSession(erreichbar=True))
asyncio.run(integration.async_setup_entry(hass3, FakeEntry()))
zweiter = FakeEntry()
zweiter.entry_id = "entry2"
try:
    asyncio.run(integration.async_setup_entry(hass3, zweiter))
    doppelt_ok = True
except RuntimeError:
    doppelt_ok = False
check(doppelt_ok and hass3.http.registriert == [integration.STATIC_URL_PATH],
      "zweiter Entry laeuft, Pfad nur einmal registriert")

print()
if gescheitert:
    print(f"{len(gescheitert)} von {bestanden + len(gescheitert)} Checks GESCHEITERT:")
    for t in gescheitert:
        print("  -", t)
    sys.exit(1)
print(f"{bestanden}/{bestanden} Checks bestanden")
