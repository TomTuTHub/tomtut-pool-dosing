# TomTuT Pool Dosing (Beniferro) - Home Assistant Integration

This custom integration reads measurements and relay states from Beniferro Gen2 local HTTP API.

## Install (local)
Copy the `tomtut_pool_dosing` folder to `<config>/custom_components/` and restart Home Assistant.

## Install via HACS
1. Create a GitHub repo with this content.
2. Add `hacs.json` and push a release / tag.
3. In HACS → Integrations → … → Add custom repository by URL (category: integration).
4. Install and restart.

## Notes
- API endpoints: `/api/measurements` and `/api/relays`.
- The integration is read-only (device API is read-only).
- Options: polling interval in seconds (via Integration options). Changing options reloads the entry.

Documentation: https://docs.myswimmingpool.eu/beniferro/local-api
