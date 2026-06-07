#!/usr/bin/env bash
# Stage the plugin for `decky plugin build .`. The Decky CLI only bundles root
# *.py, dist/, bin/, defaults/, py_modules/ — so copy the pokedeck package into
# py_modules/ and the data tables + descriptors into defaults/data/ (the build
# strips the defaults/ prefix, landing them at <plugin>/data/). The ROM is never
# copied. Run after `pnpm run build`.
set -euo pipefail
cd "$(dirname "$0")/.."

rm -rf py_modules/pokedeck defaults/data
mkdir -p py_modules/pokedeck defaults/data/games

cp pokedeck/*.py py_modules/pokedeck/
cp data/species.json data/moves.json defaults/data/
cp data/games/*.json defaults/data/games/

echo "staged py_modules/pokedeck and defaults/data for 'decky plugin build .'"
