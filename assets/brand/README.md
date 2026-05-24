# Brand assets (canonical for HACS)

SVG sources are synced from [HelioZero-ESP32/assets/brand](https://github.com/TheGrimmChester/HelioZero-ESP32/tree/main/assets/brand) — edit there only.

Regenerate PNGs for Home Assistant:

```bash
npm run prepare:brand
```

This updates `custom_components/helio_zero/*.png` and `brands/custom_integrations/helio_zero/` per [home-assistant/brands](https://github.com/home-assistant/brands) image spec (256/512 icon, logo shortest side 128–512).
