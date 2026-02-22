# TomTuT Pool Dosing

Community Home Assistant integration for Beniferro Gen2 pool dosing systems via local REST API.

## Important
This integration is an independent community project and is not commissioned, endorsed, or supported by Beniferro/Poolsana.

## Which README is required?
For Home Assistant / HACS, this repository uses **one** README file: `README.md` in the repository root.
There is no second README required in this project.

## Dashboard images from the integration
The PNG files in `custom_components/tomtut_pool_dosing/static` can be used directly in Lovelace.

Use this API path:

```yaml
image: /api/tomtut_pool_dosing/static/dosier_v1.png
```

Additional files:

- `/api/tomtut_pool_dosing/static/dosier_v2.png`
- `/api/tomtut_pool_dosing/static/dosier_v3.png`
- `/api/tomtut_pool_dosing/static/dosier_v4.png`

## Features
- Local polling via HTTP (LAN)
- Read-only access (no control commands)
- Sensors for pH, redox, flow, and relay/pump status

## Installation
- Via HACS as a custom repository: `https://github.com/TomTuTHub/tomtut-pool-dosing`
- Or manually copy the `tomtut_pool_dosing` folder to `<config>/custom_components/`

## API
Official documentation:
- https://docs.myswimmingpool.eu/beniferro/local-api

## License
MIT

## Das war TomTuT, bleib hart am Gas :) 
