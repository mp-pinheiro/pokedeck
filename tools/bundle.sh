#!/usr/bin/env bash
# Stage the plugin for `decky plugin build .`. The Decky CLI only bundles root
# *.py, dist/, bin/, defaults/, py_modules/ — so copy the pokedeck package into
# py_modules/, the data tables + descriptors into defaults/data/, and the built
# web SPA into defaults/web/ (the build strips the defaults/ prefix, so these
# land at <plugin>/data and <plugin>/web). The ROM is never copied. Run after
# `pnpm run build` and `pnpm --filter @poke-deck/web build`.
set -euo pipefail
cd "$(dirname "$0")/.."

rm -rf py_modules/pokedeck defaults/data defaults/web
mkdir -p py_modules/pokedeck defaults/data/games defaults/web

cp pokedeck/*.py py_modules/pokedeck/
cp data/species.json data/moves.json data/abilities.json data/items.json data/nat_dex.json data/species_info.json defaults/data/
cp data/games/*.json defaults/data/games/

if [ -d apps/web/dist ]; then
  cp -r apps/web/dist/. defaults/web/
else
  echo "WARN: apps/web/dist missing — run 'pnpm --filter @poke-deck/web build' first"
fi

echo "staged py_modules/pokedeck, defaults/data, defaults/web for 'decky plugin build .'"
