#!/usr/bin/env bash
# Frontend dev loop: run the Python backend (hot-reload) AND the Vite dev server
# (HMR) together. Edit pokedeck/*.py, packages/ui/*, or apps/web/* and see changes
# live. Open the Vite URL it prints (http://localhost:5173) — NOT :8420. Vite
# proxies /api and /events to the backend, so live battle data flows through.
#
#   tools/dev.sh [game]        # default game: lazarus
set -euo pipefail
cd "$(dirname "$0")/.."
GAME="${1:-lazarus}"

echo "starting backend (:8420, --reload) + Vite dev (HMR)…  open the Vite URL below."
python3 -m pokedeck.server --game "$GAME" --reload &
BACKEND=$!
trap 'kill "$BACKEND" 2>/dev/null || true' EXIT INT TERM

pnpm --filter @poke-deck/web dev
