# TomTuT Pool Dosing

Community-driven Home Assistant integration for **Beniferro pool dosing systems**
using the officially documented **local REST API**.

Read-only, local polling.

Maintained by **TomTuT**.

---

## Important
⚠️ This integration is an **independent community project**.

- It is **not developed, commissioned, or supported** by Beniferro or Poolsana.
- It exists solely because Beniferro provides a **publicly documented local REST API**.

### Cloud / App / Setup note (important!)
- The **official app and initial device setup** may rely on Beniferro’s **cloud services**.
- **Probe calibration and configuration changes** currently must be done via the **official app** (and therefore typically via the cloud).
- This Home Assistant integration is **read-only** and currently supports **local Wifi/LAN reading** of measurements via the REST API **without a cloud requirement for reading**.

More background (German):  
👉 https://tomtut.de/dosieranlage

Official Beniferro API documentation:  
👉 https://docs.myswimmingpool.eu/beniferro/local-api

---

## Features
- Local HTTP polling of measurements (LAN)
- Read-only (safe, no control actions (yet, i hope))
- Sensors for pH, Redox (ORP), Flow and injektion-pumps
- Use the gear icon to Setup Time-Interval for REST poll intervall and set IP

---

## Compatibility
- **Manufacturer:** Beniferro  
- **Hardware generation:** Gen2 devices
- Tested with installations sold in Germany (e.g. via Poolsana)

> Mentioning Poolsana is for context only.  
> This project has **no affiliation** with Poolsana or Beniferro.

---

## Installation
Installation via **HACS (Custom Repository)**.

The device must be reachable in the local network for polling the REST API.

---

## API
Based on the official Beniferro local API:
- `GET /api/measurements`
- `GET /api/relays` (optional, read-only)

API reference:  
👉 https://docs.myswimmingpool.eu/beniferro/local-api

## Support this project
If you like this integration, you can support my work here:
👉 https://www.tomtut.de/product/dankeschoen-fuer-thomas-buy-me-a-coffee/

---


## Disclaimer
This software is provided **as-is**, without warranty of any kind.

Use at your own risk.

---

## License
MIT

---

Das war TomTuT,
bleib hart am Gas!

## Dashboard images (static)
Bilder aus dem integrations-eigenen Ordner `custom_components/tomtut_pool_dosing/static` können direkt in Lovelace verwendet werden – ohne Ablage unter `/config/www` und ohne `/local`-Pfad.

Copy & paste Beispiele:
```yaml
image: /api/tomtut_pool_dosing/static/dosier_v1.png
image: /api/tomtut_pool_dosing/static/dosier_v2.png
image: /api/tomtut_pool_dosing/static/dosier_v3.png
image: /api/tomtut_pool_dosing/static/dosier_v4.png
```
