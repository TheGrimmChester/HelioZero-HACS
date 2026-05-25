#!/usr/bin/env bash
# HACS REST contract tests against a lab router (Path A — production firmware).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

BASE="${HELIO_ZERO_FIELD_URL:-${HELIO_ZERO_HIL_URL:-}}"
if [[ -z "${BASE}" ]]; then
  echo "Set HELIO_ZERO_FIELD_URL or HELIO_ZERO_HIL_URL (e.g. http://192.168.2.159)" >&2
  exit 1
fi

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
  .venv/bin/pip install -q -r requirements-dev.txt
elif ! .venv/bin/python -c "import pytest" 2>/dev/null; then
  .venv/bin/pip install -q -r requirements-dev.txt
fi

export HELIO_ZERO_FIELD_URL="${HELIO_ZERO_FIELD_URL:-$BASE}"
export HELIO_ZERO_HIL_URL="${HELIO_ZERO_HIL_URL:-$BASE}"

# If PAT returns 401, tests fall back to HELIO_ZERO_HIL_PASSWORD when set.
if [[ -z "${HELIO_ZERO_API_BEARER_TOKEN:-}" && -z "${HELIO_ZERO_HIL_PASSWORD:-}" ]]; then
  echo "Hint: set HELIO_ZERO_API_BEARER_TOKEN and/or HELIO_ZERO_HIL_PASSWORD" >&2
fi

echo "== HACS hardware REST (${HELIO_ZERO_FIELD_URL}) =="
.venv/bin/pytest tests/test_hacs_rest_hardware.py -v -m hardware
echo "HACS hardware REST checks passed"
