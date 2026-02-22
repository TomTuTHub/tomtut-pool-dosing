# TomTuT Pool Dosing

Community Home Assistant integration for **Beniferro Gen2** pool dosing systems via **local REST API** (LAN).

➡️ **More info & guides (German):** https://www.tomtut.de/dosieranlage

---

## Disclaimer

This integration is an independent community project and is **not** commissioned, endorsed, affiliated with, or supported by **Beniferro / Poolsana**.  
Use at your own risk.

---

## Features

- Local polling via HTTP (LAN)
- Read-only access (no control commands, yet :) )
- Sensors for **pH**, **Redox**, **Flow**, and **relay/pump status**

---

## Screenshots / Dashboard images

The PNG files in `custom_components/tomtut_pool_dosing/static` can be used directly in Lovelace (e.g. `picture-elements`).

Example:

```yaml
type: picture-elements
image: /api/tomtut_pool_dosing/static/dosier_v1.png
elements: []
```

Available images:

- `/api/tomtut_pool_dosing/static/dosier_v1.png`
- `/api/tomtut_pool_dosing/static/dosier_v2.png`
- `/api/tomtut_pool_dosing/static/dosier_v3.png`
- `/api/tomtut_pool_dosing/static/dosier_v4.png`

---

## Installation

### HACS (Custom repository)

1. HACS → **Integrations**
2. Menu (⋮) → **Custom repositories**
3. Add repository URL: `https://github.com/TomTuTHub/tomtut-pool-dosing`
4. Category: **Integration**
5. Install → **Restart Home Assistant**

### Manual

1. Copy `custom_components/tomtut_pool_dosing` to:
   - `<config>/custom_components/tomtut_pool_dosing`
2. Restart Home Assistant

---

## Configuration

1. Settings → **Devices & Services**
2. **Add Integration**
3. Search for **TomTuT Pool Dosing**
4. Enter the device IP / host and confirm

---

## API Documentation

Official Beniferro Gen2 Local API documentation:  
https://docs.myswimmingpool.eu/beniferro/local-api

---

## Support / Issues

Please open a **GitHub Issue** in this repository and include:

- Home Assistant version
- Integration version
- Device model (Beniferro Gen2)
- Relevant logs (**Settings → System → Logs**)
- Steps to reproduce (what you did, what you expected, what happened)
- Did you watch my Blogarticle and YouTube-Video under https://tomtut.de/dosieranlage ?

---

## Contributing

Contributions are welcome!

1. Fork the repo
2. Create a feature branch
3. Commit with a clear message
4. Open a Pull Request

---

## License

MIT

---

Das war TomTuT, bleib hart am Gas.
