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
- No cloud access is required.

Official Beniferro API documentation:  
👉 https://docs.myswimmingpool.eu/beniferro/local-api

---

## Features
- Local HTTP polling (no cloud dependency)
- Read-only (safe, no control actions)
- Sensors for pH, Redox (ORP), Flow, Levels, Conductivity (if available)
- Native Home Assistant Config Flow
- Designed for dashboards & picture-elements

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

This integration uses the **local REST API** provided by the device.
The device must be reachable in the local network.

---

## API
Based on the official Beniferro local API:
- `GET /api/measurements`
- `GET /api/relays` (optional, read-only)

API reference:  
👉 https://docs.myswimmingpool.eu/beniferro/local-api

---

## Disclaimer
This software is provided **as-is**, without warranty of any kind.

Use at your own risk.

---

## License
MIT
