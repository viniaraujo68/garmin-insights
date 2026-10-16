#!/usr/bin/env bash
set -uo pipefail

HOST=127.0.0.1
PORT=5173
SYNC=true

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
URL="http://localhost:${PORT}"

if [[ "${SYNC}" == true ]]; then
  echo "==> syncing Garmin data"
  if ! (cd "${ROOT}/pipeline" && uv run --frozen python -m passada.run); then
    echo "==> sync incomplete: the site keeps the last good data (if the token expired, log in again in a separate terminal)" >&2
  fi
fi

if curl -sf -o /dev/null "http://${HOST}:${PORT}/"; then
  echo "==> site already running at ${URL}: reload the page"
  exit 0
fi

echo "==> building the site"
BUILD_LOG="$(mktemp)"
if ! (cd "${ROOT}/web" && npm run build >"${BUILD_LOG}" 2>&1); then
  cat "${BUILD_LOG}" >&2
  exit 1
fi
rm -f "${BUILD_LOG}"

echo "==> site at ${URL} (Ctrl+C to stop)"
cd "${ROOT}/web" && HOST="${HOST}" PORT="${PORT}" PASSADA_SITE_DIR="${ROOT}/data/site" exec node build
