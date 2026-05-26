# Changelog

## 0.1.0

First public release (custom repository + GitHub Release zip).

- Home Assistant **2026.4.0** minimum (`hacs.json`).
- **`rest_only`** mode: MQTT discovery parity via REST (`/api/v1/telemetry/snapshot`, extended diagnostics).
- **`companion`** mode: auto-detect MQTT entities; register **republish discovery** button only.
- Options flow: integration mode and **REST refresh interval** (15–120 seconds, applied live).
- **Reconfigure** flow: change router URL or API token after setup (⋮ menu).
- Multiple routers: add the integration again per base URL.
- Entity registry: sensors, binary sensors, switches, numbers, selects, button.
- Coordinator: `asyncio.gather`, `entry.runtime_data`, `/sources/diagnostics` poll.
- CI / release: `hacs/action@main`, `hassfest@master`, gated `release.yaml`, `helio-zero-hacs.zip`.
