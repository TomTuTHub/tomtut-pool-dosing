# TomTuT Pool Dosing

Vendor-neutral Home Assistant integration for pool dosing systems using a local HTTP API.  
Read-only, local polling.

Maintained by **TomTuT**.

---

## Features
- Local HTTP polling (no cloud)
- Read-only (safe)
- Sensors for pH, Redox (ORP), Flow, Levels, Conductivity (if available)
- Designed for Home Assistant dashboards & picture-elements

## Compatibility
Tested with **Beniferro Gen2** devices.  
In Germany sold by **Poolsana**.

> This project is **not affiliated** with any manufacturer or vendor.

## Installation (current state)
This repository currently documents the **YAML-based setup** (REST + template sensors).
A native Home Assistant integration (HACS) is planned.

## API
- `GET /api/measurements`
- `GET /api/relays` (optional)

## License
MIT
