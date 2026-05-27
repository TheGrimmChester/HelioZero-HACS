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
chmod +x scripts/verify-release-zip.sh
./scripts/verify-release-zip.sh "$OUT"
