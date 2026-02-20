# TomTuT Pool Dosing

Community Home Assistant integration for Beniferro Gen2 pool dosing systems via local REST API.

## Wichtig
Diese Integration ist ein unabhängiges Community-Projekt und nicht von Beniferro/Poolsana beauftragt oder supportet.

## Dashboard-Bilder aus der Integration
Die PNG-Dateien im Ordner `custom_components/tomtut_pool_dosing/static` können direkt in Lovelace genutzt werden.

Verwende dafür den API-Pfad:

```yaml
image: /api/tomtut_pool_dosing/static/dosier_v1.png
```

Weitere Dateien:

- `/api/tomtut_pool_dosing/static/dosier_v2.png`
- `/api/tomtut_pool_dosing/static/dosier_v3.png`
- `/api/tomtut_pool_dosing/static/dosier_v4.png`

## Features
- Lokales Polling über HTTP (LAN)
- Read-only Zugriff (keine Steuerbefehle)
- Sensoren für pH, Redox, Flow und Relais/Pumpen

## Installation
- Über HACS als Custom Repository: `https://github.com/TomTuTHub/tomtut-pool-dosing`
- Oder manuell den Ordner `tomtut_pool_dosing` nach `<config>/custom_components/` kopieren.

## API
Offizielle Dokumentation:
- https://docs.myswimmingpool.eu/beniferro/local-api

## License
MIT
