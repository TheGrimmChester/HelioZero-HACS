# Brand assets (canonical for HACS)

SVG sources are synced from [HelioZero-ESP32/assets/brand](https://github.com/TheGrimmChester/HelioZero-ESP32/tree/main/assets/brand) — edit there only (`helio-zero-icon-light.svg`, `helio-zero-icon-dark.svg`, logos).

Regenerate PNGs for Home Assistant 2026.3+:

```bash
export HELIO_ZERO_ESP32_ROOT=/path/to/HelioZero-ESP32   # optional if sibling repo
npm run prepare:brand
```

This updates `custom_components/helio_zero/brand/*.png` per [inline brand images](https://developers.home-assistant.io/blog/2026/02/24/brands-proxy-api/) (256/512 icon, logo shortest side 128–512).
