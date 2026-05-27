# Contributing to HelioZero-HACS

Thank you for helping improve the HelioZero Home Assistant integration.

## Development setup

1. Clone this repository and use a feature branch (or `main` after merge).
2. Install dev dependencies: `pip install -r requirements-dev.txt`
3. Run unit tests: `./scripts/test-unit.sh`
4. Run hardware contract tests only when you have a lab router (never commit tokens):

```bash
export HELIO_ZERO_FIELD_URL=http://192.168.2.159
export HELIO_ZERO_API_BEARER_TOKEN=<your PAT>
pytest -m hardware -q
```

## Pull requests

- One logical change per PR when possible (store hygiene vs entity parity).
- CI must pass: brand gate, HACS validation, hassfest, `compileall`, `pytest -m "not hardware"`.
- Do not include router passwords, API tokens, or LAN IPs in issues or PR descriptions.

## Release checklist (maintainers)

**Nightly (automatic):** merges to `main` that touch integration paths publish `vX.Y.Z-nightly.<sha>` pre-releases when CI is green. No maintainer action required.

**Stable (manual):**

0. On GitHub (**TheGrimmChester** account → repo **Settings → General**):
   - **Description:** `Home Assistant custom integration for HelioZero ESP32 PV excess routers (REST companion to MQTT discovery).`
   - **Topics:** `homeassistant`, `hacs`, `integration`
   Then remove `ignore: description topics` from [`.github/workflows/hacs.yaml`](.github/workflows/hacs.yaml) and [`release.yaml`](.github/workflows/release.yaml) (required before HACS default store submission).
1. Update `custom_components/helio_zero/manifest.json` `version` and `CHANGELOG.md` (`## X.Y.Z`).
2. `./scripts/test-unit.sh`, `./scripts/build-release.sh`, and `RELEASE_TAG_NAME=vX.Y.Z python3 scripts/verify_release_version.py` locally.
3. Merge with green **CI** + **hacs** workflows.
4. `git tag vX.Y.Z && git push origin vX.Y.Z` — [`.github/workflows/release.yaml`](.github/workflows/release.yaml) gates on hassfest, HACS validation, unit tests, then publishes `helio-zero-hacs.zip`.
5. On GitHub, mark the stable release **Latest**. Confirm HACS custom repo shows the new release version.

First public release was **`v0.1.0`** (task010 surface). Do not tag until `main` contains the release workflow and manifest version.

## Commits

Follow the repository’s existing message style. Integration code is **EUPL-1.2** (see `LICENSE`).
