#!/usr/bin/env bash
# Package custom_components/helio_zero for HACS zip_release (helio-zero-hacs.zip).
set -euo pipefail
cd "$(dirname "$0")/.."
OUT="${OUT:-helio-zero-hacs.zip}"
rm -f "$OUT"
(
  cd custom_components/helio_zero
  zip -r "../../$OUT" . -x '*__pycache__/*' -x '*.pyc' -x '*~'
)
echo "Wrote $OUT"

# Smoke-test archive layout (HACS extractall target is custom_components/helio_zero/).
if command -v unzip >/dev/null 2>&1; then
  zip_list="$(unzip -l "$OUT")"
  case "$zip_list" in
    *" manifest.json"*) ;;
    *)
      echo "ERROR: zip missing manifest.json at archive root" >&2
      exit 1
      ;;
  esac
  case "$zip_list" in
    *" __init__.py"*) ;;
    *)
      echo "ERROR: zip missing __init__.py at archive root" >&2
      exit 1
      ;;
  esac
  case "$zip_list" in
    *brand/icon.png*) ;;
    *)
      echo "ERROR: zip missing brand/icon.png" >&2
      exit 1
      ;;
  esac
  case "$zip_list" in
    *helio_zero/manifest.json*)
      echo "ERROR: zip must not nest helio_zero/ (causes helio_zero/helio_zero/ on install)" >&2
      exit 1
      ;;
  esac
  case "$zip_list" in
    *__pycache__*)
      echo "ERROR: zip contains __pycache__" >&2
      exit 1
      ;;
  esac
  echo "OK: zip layout smoke test passed"
fi
