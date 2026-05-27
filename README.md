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
  <a href="https://my.home-assistant.io/redirect/hacs_repository/?owner=TheGrimmChester&repository=HelioZero-HACS&category=integration">
    <img src="https://my.home-assistant.io/badges/hacs_integration.svg" alt="Open in HACS" />
  </a>
</p>

**Requires Home Assistant 2026.3.0 or newer** (inline integration brand images in `brand/`). Lovelace starter dashboards on the docs site target **2026.4+** (sections view).

Optional [Home Assistant](https://www.home-assistant.io/) custom integration for [HelioZero](https://github.com/TheGrimmChester/HelioZero-ESP32) PV excess routers. Polls the router REST API (`/api/v1/measurements`) when you prefer UI setup over hand-edited MQTT YAML.

**MQTT discovery on the router remains the supported default.** Automations, blueprints, and cookbooks stay in the [HelioZero docs](https://heliozero.clouded.fr/en/integrations/home-assistant/).

Source repository: **[HelioZero-HACS](https://github.com/TheGrimmChester/HelioZero-HACS)**.

## Brand icons

Integration icons/logos ship in [`custom_components/helio_zero/brand/`](custom_components/helio_zero/brand/) (`icon.png`, `logo.png`, `@2x` and `dark_*` variants) for [Home Assistant 2026.3+ inline brand images](https://developers.home-assistant.io/blog/2026/02/24/brands-proxy-api/). Sources: [`assets/brand/`](assets/brand/) (synced from [HelioZero-ESP32](https://github.com/TheGrimmChester/HelioZero-ESP32)); regenerate with `npm run prepare:brand` (set `HELIO_ZERO_ESP32_ROOT` when the ESP32 repo is not a sibling directory).

## Install

1. In HACS: **Settings → Custom repositories** → add `https://github.com/TheGrimmChester/HelioZero-HACS` (category **Integration**). No repository subpath.
2. Install **HelioZero** from HACS (**Releases** tab → `v0.1.x` when offered) and restart Home Assistant.
3. **Settings → Devices & services → Add integration → HelioZero**.
4. Enter `http://<router-ip>` and optional API token (router **More → API** permanent access tokens when HTTP API protection is enabled).

**Manual install:** copy [`custom_components/helio_zero/`](https://github.com/TheGrimmChester/HelioZero-HACS/tree/main/custom_components/helio_zero) into your HA `config/custom_components/` directory, restart, then add the integration as above.

**Multiple routers:** add the integration again for each router base URL; each device is labeled with that router’s `router_name` from the API.

**After setup:**

| Home Assistant action | What it changes |
|---------------------|-----------------|
| **Configure** (integration card) | Integration mode (`companion` / `rest_only`, reloads entities when changed) and **REST refresh interval** (15–120 seconds, applied immediately) |
| **Reconfigure** (⋮ menu on the integration) | Router base URL (IP/hostname) and API token — leave token empty to keep the current token |

**MQTT pack:** blueprints, cookbooks, and discovery YAML remain on the [HelioZero website](https://heliozero.clouded.fr/en/integrations/home-assistant/) — see the [Home Assistant integration pack](https://heliozero.clouded.fr/en/integrations/home-assistant/).

### HelioZero missing from “Add integration”?

1. **Settings → System → Logs** — search for `helio_zero`. An `ImportError` or version message means the custom component did not load (fix the error, or upgrade Home Assistant to **2026.3+**).
2. Confirm the folder exists: `config/custom_components/helio_zero/manifest.json`.
3. In HACS, open **HelioZero →** use **Redownload** and pick the latest **Release** (not a hidden/empty default branch). Restart Home Assistant.
4. If you previously installed from `main` before `v0.1.0`, remove `config/custom_components/helio_zero`, redownload the release zip, restart, then add the integration again.

**Initial release 0.1.0:** per-router `unique_id` (`{config_entry_id}_{key}`), HA brand icons, `issue_tracker` in manifest, and device **Open router UI** link (`configuration_url`).

## Entities

`unique_id` = `{config_entry_id}_{key}` per router. Pick entities from **Developer tools → States** or the device page.

| Mode | Entities |
|------|----------|
| **`companion`** (default when MQTT discovery exists) | `button.republish_discovery` only |
| **`rest_only`** | Full MQTT discovery parity via REST (sensors, binary sensors, vacation, triac, actions, …) |

Configure mode and REST refresh interval (15–120 s) under **Settings → Devices & services → HelioZero → Configure** (changes apply without restart).

Diagnostics: **Settings → Devices → Diagnostics** (redacted token, effective mode, snapshot keys).

## When to use HACS vs MQTT

| Use MQTT | Use HACS |
|----------|----------|
| Default install | REST-only LAN (`rest_only`) |
| Broker automations & device triggers | UI setup without editing discovery YAML |
| Lowest latency MQTT commands | Full entity surface when no MQTT entities |

**Hybrid:** leave default **companion** mode (or set explicitly) so HACS does not duplicate MQTT entities; use the [MQTT Lovelace dashboard](https://heliozero.clouded.fr/assets/integrations/home-assistant/lovelace/dashboard.yaml) for monitoring.

## Development

REST poll and entity writes share one Home Assistant `aiohttp` clientsession on the data coordinator (`coordinator.py`). Add new REST platforms via `async_patch_config` / `async_post_mqtt_discover` rather than new `ClientSession()` instances.

**CI (every PR):** `./scripts/test-unit.sh` (compileall, `pytest -m "not hardware"`), `home-assistant/actions/hassfest@master`, and `hacs/action@main`.

**Hardware REST contract (when touching coordinator or REST entities):**

```bash
export HELIO_ZERO_FIELD_URL=http://192.168.2.159
export HELIO_ZERO_API_BEARER_TOKEN=<router PAT>
./scripts/run_hardware_checks.sh
```

PATCH tests restore `vacation_enabled` and `max_routed_w` on the device after each run.

## Releasing

1. Bump `custom_components/helio_zero/manifest.json` `version` and add a `## X.Y.Z` section to `CHANGELOG.md`.
2. Open a PR; wait for **CI** and **hacs** workflows green (`hassfest@master`, `hacs/action@main`, `./scripts/test-unit.sh`).
3. Merge to `main`, then tag and push (tag must match manifest, e.g. `0.1.0` → `v0.1.0`):

   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```

4. GitHub Actions **Release** validates, builds `helio-zero-hacs.zip`, and publishes a GitHub Release. Mark the stable tag **Latest** on GitHub.
5. In HACS, install from **Releases** when `zip_release` is enabled (`hacs.json`).

Dry-run without tagging: **Actions → Release → Run workflow** (artifact only, no GitHub Release).

See [Developer guide — HACS integration release](https://heliozero.clouded.fr/en/developer/#hacs-integration-release) and [HACS publishing docs](https://www.hacs.xyz/docs/publish/integration/).

## Related

- Firmware & MQTT: [HelioZero](https://github.com/TheGrimmChester/HelioZero-ESP32)
- [HACS documentation](https://heliozero.clouded.fr/en/integrations/home-assistant/hacs/)
- [Home Assistant integration pack](https://heliozero.clouded.fr/en/integrations/home-assistant/) (blueprints, Energy dashboard)
- [Lovelace starter (HACS)](https://heliozero.clouded.fr/assets/integrations/home-assistant/lovelace/dashboard-hacs.yaml)

## License

This repository is **EUPL-1.2** — see [`LICENSE`](LICENSE), same as [HelioZero](https://github.com/TheGrimmChester/HelioZero-ESP32).
