<p align="center">
  <a href="https://github.com/TheGrimmChester/HelioZero-ESP32">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="assets/brand/helio-zero-logo-dark.svg" />
      <img src="assets/brand/helio-zero-logo-light.svg" alt="HelioZero" width="420" />
    </picture>
  </a>
</p>

# HelioZero — Home Assistant (HACS)

<p align="center">
  <img src="https://img.shields.io/badge/license-EUPL--1.2-blue" alt="EUPL-1.2" />
</p>

Optional [Home Assistant](https://www.home-assistant.io/) custom integration for [HelioZero](https://github.com/TheGrimmChester/HelioZero-ESP32) PV excess routers. Polls the router REST API (`/api/v1/measurements`) when you prefer UI setup over hand-edited MQTT YAML.

**MQTT discovery on the router remains the supported default.** Automations, blueprints, and cookbooks stay in the [HelioZero docs](https://heliozero.clouded.fr/en/integrations/home-assistant/).

Source repository: **[HelioZero-HACS](https://github.com/TheGrimmChester/HelioZero-HACS)**.

## Brand icons

Integration icons/logos live in [`custom_components/helio_zero/`](custom_components/helio_zero/) (`icon.png`, `logo.png`, `@2x` and `dark_*` variants) per [Home Assistant brands](https://github.com/home-assistant/brands) spec. Sources: [`assets/brand/`](assets/brand/) (synced from [HelioZero-ESP32](https://github.com/TheGrimmChester/HelioZero-ESP32)); regenerate with `npm run prepare:brand`.

For the global brands CDN, submit [`brands/custom_integrations/helio_zero/`](brands/custom_integrations/helio_zero/) to [home-assistant/brands](https://github.com/home-assistant/brands) (see [`brands/README.md`](brands/README.md)).

## Install

1. In HACS: **Settings → Custom repositories** → add `https://github.com/TheGrimmChester/HelioZero-HACS` (category **Integration**). No repository subpath.
2. Install **HelioZero** from HACS and restart Home Assistant.
3. **Settings → Devices & services → Add integration → HelioZero**.
4. Enter `http://<router-ip>` and optional API token (router **More → API** permanent access tokens when HTTP API protection is enabled).

**Manual install:** copy [`custom_components/helio_zero/`](https://github.com/TheGrimmChester/HelioZero-HACS/tree/main/custom_components/helio_zero) into your HA `config/custom_components/` directory, restart, then add the integration as above.

**Multiple routers:** add the integration again for each router base URL; each device is labeled with that router’s `router_name` from the API.

**MQTT pack:** blueprints, cookbooks, and discovery YAML remain on the [HelioZero website](https://heliozero.clouded.fr/en/integrations/home-assistant/) — see the [Home Assistant integration pack](https://heliozero.clouded.fr/en/integrations/home-assistant/).

**Initial release 0.1.0:** per-router `unique_id` (`{config_entry_id}_{key}`), HA brand icons, `issue_tracker` in manifest, and device **Open router UI** link (`configuration_url`).

## Entities

HACS registers `unique_id` = `{config_entry_id}_{key}` per router. **Entity IDs are not `helio_zero_*`** — always pick entities from **Developer tools → States** or the device page.

| Platform | Key | Friendly name |
|----------|-----|---------------|
| `sensor` | `house_net_power_w` | House net power |
| `sensor` | `triac_open_percent` | Triac open |
| `switch` | `vacation` | Vacation mode |
| `number` | `max_routed_w` | Max routed power (W) |
| `button` | `republish_discovery` | Republish MQTT discovery |

Diagnostics (host, router name, firmware): **Settings → Devices → Diagnostics**.

**Not exposed by HACS** (use MQTT discovery): `source_stale`, `regulation_hunting`, `source_health`, Linky tariff sensors, meter source select, triac target, action switches, import/export power sensors.

## When to use HACS vs MQTT

| Use MQTT | Use HACS |
|----------|----------|
| Default install | REST-only LAN, no broker |
| Automations on broker | UI setup without editing discovery YAML |
| Lowest latency commands | Vacation / cap / republish from HA UI |
| Full entity set (status, Linky, actions) | House net power + triac % + vacation + cap only |

**Hybrid (HACS + MQTT on one router):** use the [MQTT Lovelace dashboard](https://heliozero.clouded.fr/assets/integrations/home-assistant/lovelace/dashboard.yaml) for monitoring and status; avoid changing the same setting from both integrations.

## Development

REST poll and entity writes share one Home Assistant `aiohttp` clientsession on the data coordinator (`coordinator.py`). Add new REST platforms via `async_patch_config` / `async_post_mqtt_discover` rather than new `ClientSession()` instances.

**CI (every PR):** `python3 -m compileall custom_components/helio_zero` and [hassfest](https://github.com/home-assistant/hassfest).

**Hardware REST contract (when touching coordinator or REST entities):**

```bash
export HELIO_ZERO_FIELD_URL=http://192.168.2.159
export HELIO_ZERO_API_BEARER_TOKEN=<router PAT>
./scripts/run_hardware_checks.sh
```

PATCH tests restore `vacation_enabled` and `max_routed_w` on the device after each run.

## Related

- Firmware & MQTT: [HelioZero](https://github.com/TheGrimmChester/HelioZero-ESP32)
- [HACS documentation](https://heliozero.clouded.fr/en/integrations/home-assistant/hacs/)
- [Home Assistant integration pack](https://heliozero.clouded.fr/en/integrations/home-assistant/) (blueprints, Energy dashboard)
- [Lovelace starter (HACS)](https://heliozero.clouded.fr/assets/integrations/home-assistant/lovelace/dashboard-hacs.yaml)

## License

This repository is **EUPL-1.2** — see [`LICENSE`](LICENSE), same as [HelioZero](https://github.com/TheGrimmChester/HelioZero-ESP32).
