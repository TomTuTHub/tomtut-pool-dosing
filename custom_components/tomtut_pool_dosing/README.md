# TomTuT Pool Dosing (Beniferro) - Home Assistant Integration

This custom integration reads measurements and relay states from Beniferro Gen2 local HTTP API.

## Install via HACS
1. In HACS → Integrations → … → Add custom repository by URL (category: integration).
   1.1 https://github.com/TomTuTHub/tomtut-pool-dosing
2. Install and restart.

PS: I am working on that it will be available out-of-the-box in HACS :) 

Alternative: 
Downlaod from https://github.com/TomTuTHub/tomtut-pool-dosing and 
copy the `tomtut_pool_dosing` folder to `<config>/custom_components/` and restart Home Assistant.

## Configuring
Install TomTuT under:
Einstellungen - Geräte & Dienste - Integration hinzufügen - "TomTuT Pool Dosing"

## Official REST API
Documentation: https://docs.myswimmingpool.eu/beniferro/local-api

## Dashboard images (static)
Bilder aus dem integrations-eigenen Ordner `custom_components/tomtut_pool_dosing/static` können direkt in Lovelace verwendet werden – ohne Ablage unter `/config/www`.
Unterstützte Pfade sind `/api/tomtut_pool_dosing/static/...` und `/local/tomtut_pool_dosing/...`.
