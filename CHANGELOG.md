# Changelog

## 0.1.2

- REST refresh interval configurable from **1 second to 5 minutes** (was 15 s – 2 min).
- **Default integration mode is now `rest_only`** (full REST entity set). Hybrid MQTT setups: open **Configure** and pick **companion** to avoid duplicate entities.
- Options flow: descriptive EN/FR labels for **Integration mode** (`SelectSelector` list); step text explains companion vs REST only.

## 0.1.0

First public release (custom repository + GitHub Release zip).

- Home Assistant **2026.3.0** minimum (`hacs.json`; brand icons on 2026.3.x).
- Re-enable default branch in HACS (`hide_default_branch: false`) so a broken release install can recover from `main`.
- Lazy-import coordinator from `device_info` so config flow registration does not pull the full platform stack at load time.
- Safer `DataUpdateCoordinator` / `runtime_data` usage on older Home Assistant builds.
- **`rest_only`** mode: MQTT discovery parity via REST (`/api/v1/telemetry/snapshot`, extended diagnostics).
- **`companion`** mode: auto-detect MQTT entities; register **republish discovery** button only.
- Options flow: integration mode and **REST refresh interval** (15–120 seconds, applied live).
- **Reconfigure** flow: change router URL or API token after setup (⋮ menu).
- Multiple routers: add the integration again per base URL.
- Entity registry: sensors, binary sensors, switches, numbers, selects, button.
- Coordinator: `asyncio.gather`, `entry.runtime_data`, `/sources/diagnostics` poll.
- CI / release: `hacs/action@main`, `hassfest@master`, gated `release.yaml`, `helio-zero-hacs.zip` (flat zip root for HACS `zip_release` — files extract into `custom_components/helio_zero/`, not `helio_zero/helio_zero/`).
