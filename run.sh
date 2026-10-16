#!/usr/bin/env bash
set -uo pipefail

HOST=127.0.0.1
PORT=5173
SYNC=true
TOKEN_FILE="${HOME}/.garminconnect/garmin_tokens.json"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
URL="http://localhost:${PORT}"
LOGIN="cd ${ROOT}/pipeline && uv run --frozen python -m garmin_insights.login"

if [[ ! -d "${ROOT}/web/node_modules" ]]; then
  echo "==> installing site dependencies"
  (cd "${ROOT}/web" && npm ci --no-audit --no-fund) || exit 1
fi

if [[ "${SYNC}" == true ]]; then
  if [[ ! -f "${TOKEN_FILE}" ]]; then
    echo "==> no Garmin login found: logging in once"
    (cd "${ROOT}/pipeline" && uv run --frozen python -m garmin_insights.login) || exit 1
  fi
  echo "==> syncing Garmin data"
  if ! (cd "${ROOT}/pipeline" && uv run --frozen python -m garmin_insights.run); then
    echo "==> sync incomplete: the site keeps the last good data. If the login expired, run: ${LOGIN}" >&2
  fi
fi

if [[ ! -f "${ROOT}/data/site/meta.json" ]]; then
  echo "==> no data published yet: run with SYNC=true first" >&2
  exit 1
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
cd "${ROOT}/web" && HOST="${HOST}" PORT="${PORT}" SITE_DIR="${ROOT}/data/site" exec node build
