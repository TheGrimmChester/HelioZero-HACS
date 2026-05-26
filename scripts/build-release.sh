#!/usr/bin/env bash
# Package custom_components/helio_zero for HACS zip_release (helio-zero-hacs.zip).
set -euo pipefail
cd "$(dirname "$0")/.."
OUT="${OUT:-helio-zero-hacs.zip}"
rm -f "$OUT"
(
  cd custom_components
  zip -r "../$OUT" helio_zero -x '*__pycache__/*' -x '*.pyc' -x '*~'
)
echo "Wrote $OUT"

# Smoke-test archive layout (HACS expects helio_zero/ at zip root).
if command -v unzip >/dev/null 2>&1; then
  zip_list="$(unzip -l "$OUT")"
  case "$zip_list" in
    *helio_zero/manifest.json*) ;;
    *)
      echo "ERROR: zip missing helio_zero/manifest.json" >&2
      exit 1
      ;;
  esac
  case "$zip_list" in
    *helio_zero/__init__.py*) ;;
    *)
      echo "ERROR: zip missing helio_zero/__init__.py" >&2
      exit 1
      ;;
  esac
  case "$zip_list" in
    *helio_zero/brand/icon.png*) ;;
    *)
      echo "ERROR: zip missing helio_zero/brand/icon.png" >&2
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
