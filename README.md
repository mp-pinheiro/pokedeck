# Poke Deck

Live Pokémon battle info on the Steam Deck. A [Decky](https://decky.xyz) plugin that
reads RetroArch's emulated memory and shows the active battlers' species, level, HP,
stats, types, weaknesses, and moves in the Quick Access Menu. Modular and data-driven
so any GB/GBC (Gen 1/2) or GBA (Gen 3) Pokémon game can be added with a descriptor +
data tables. First target: the GBA romhack **Pokémon Lazarus** (pokeemerald-expansion).

## Layout

- `pokedeck/` — reusable Python core (shared by the dev CLI and the Decky backend)
  - `retroarch.py` — RetroArch network-command client (direct UDP, or via a relay)
  - `descriptor.py` — per-game memory map loaded from `data/games/*.json`
  - `battle.py` — decode `gBattleMons`; locate it live (`automap`/`findmon`); in-battle gate
  - `typechart.py` — expansion type IDs + Gen-6 type chart + weakness calc
  - `pokedata.py` / `payload.py` — species/move name resolution + frontend payload
  - `socks.py` — SOCKS5 client for the sandbox→host bridge (dev only)
  - `cli.py` — dev CLI (`python3 -m pokedeck.cli ...`)
- `data/games/*.json` — per-game descriptors; `data/{species,moves}.json` — name tables
- `main.py` + `src/index.tsx` — Decky backend (asyncio poll → `decky.emit`) + QAM panel
- `tools/` — dev utilities (data generator, fixtures, probes)

## Dev CLI

RetroArch must have Network Commands enabled (UDP 55355), running the **mGBA** core.

    python3 -m pokedeck.cli --game lazarus info
    python3 -m pokedeck.cli automap --hp <HP> --level <LV> --maxhp <MAXHP> [--opp-level <N>]
    python3 -m pokedeck.cli live           # poll a live battle
    python3 -m pokedeck.cli decode <hex>   # offline: decode one battler block

### Reaching RetroArch

- On the Deck the backend reads memory directly over UDP (`--transport udp`, default).
- From a sandboxed dev shell that can't reach host loopback, use the host SOCKS bridge
  plus a host-side socat relay (SOCKS can't carry UDP, so socat bridges TCP↔UDP):

      # on the host (where RetroArch runs), once:
      socat -T3 TCP4-LISTEN:55356,bind=127.0.0.1,reuseaddr,fork UDP4:127.0.0.1:55355
      # then, from the sandbox:
      python3 -m pokedeck.cli --transport socks <cmd>

## Mapping a new game

Expansion builds relocate every EWRAM symbol, so `gBattleMons` must be found live:

1. Enter a battle; note your lead's current HP / level / max HP (and the opponent's level).
2. `automap --hp .. --level .. --maxhp .. --opp-level ..` → prints the gBattleMons base,
   alignment (natural/packed), and battler stride, plus a ready descriptor patch.
3. Paste the patch into `data/games/<game>.json` and set `verified: true`.

## Build

    pnpm install && pnpm run build         # frontend -> dist/index.js
    # bundle pokedeck/ -> py_modules/ and data/ -> defaults/data/, then build the
    # installable zip with the Decky CLI (needs Docker):
    # sudo ./cli/decky plugin build .

ROMs are never committed (`*.gba` is gitignored). Name tables are generated from
pokeemerald-expansion (pinned to 1.16.1) via `tools/gen_data.py`.

## Deploying to the Steam Deck

The Deck is the primary target; the fastest loop is over SSH — no manual side-load.
Enable SSH in SteamOS, copy `.env.example` to `.env`, set `DECK_HOST` / `DECK_PASSWORD`,
then:

    make deploy     # build (frontend + SPA + bundle), SCP, sudo-install on the Deck
    make logs       # tail Decky loader logs
    make verify     # confirm the deployed files exist
    make cef        # print the CEF DevTools URL
    make undeploy   # remove the plugin

`make deploy` stages the plugin payload (`tools/stage.py`) into the exact on-Deck
layout (`main.py`, `dist/`, `py_modules/pokedeck/`, `data/`, `web/`) and installs it
to `~/homebrew/plugins/poke-deck`. With `DEBUG=1` (default) it injects the plugin.json
`debug` flag so **Decky auto-reloads** on each deploy — the repo `plugin.json` stays
clean (the flag is added only to the deployed copy; use `DEBUG=0` for a store-like build).

**Frontend debugging:** turn on *Allow Remote CEF Debugging* in Decky → Developer, then
open `http://steamdeck:8081` in a Chromium browser (or Playwright MCP). The `QuickAccess`
tab is the panel UI; `SharedJSContext` is the JS console. Needs `sshpass` locally for the
sudo-over-SSH steps; `make help` lists every target.

## Browser app

A standalone React web app (`apps/web`) shows the same live battle info in any
browser, sharing presentational components with the Decky panel via a pnpm workspace:

- `packages/ui` — shared host-agnostic React (`MonCard`, `BattleView`, `GamePicker`,
  `useBattleState`) + payload types. `react` is a **peerDependency only** and it imports
  no `@decky/*`, so the *same source* builds in both hosts (Vite bundles its own React;
  `@decky/rollup` externalizes React to Steam's `SP_REACT`).
- `apps/web` — Vite browser shell (SSE transport).
- `pokedeck/server.py` — stdlib-only HTTP+SSE server reusing the reader (zero deps).
- `src/index.tsx` — Decky shell, consuming the same `packages/ui` via an `@decky/api` transport.

Run it on the machine where RetroArch is (Network Commands on, mGBA core):

    pnpm install
    pnpm --filter @poke-deck/web build
    python3 -m pokedeck.server --game lazarus     # then open http://localhost:8420

For **live UI work** use HMR instead — `make web` (or `bash tools/dev.sh`) runs the
backend with `--reload` *and* the Vite dev server together. Open the **Vite** URL it
prints (`http://localhost:5173`), not `:8420`; Vite proxies `/api` and `/events` to the
backend, and editing `packages/ui` or `apps/web` hot-reloads (the backend hot-reloads on
`pokedeck/*.py` too). `:8420` only serves the pre-built `dist/`.

The Decky backend (`main.py`) also hosts the same SSE server (port 8420), so the QAM
panel and a LAN browser show the battle at once. Switch games live via the in-app picker
(`POST /api/game`) or, in Decky, the `set_game` backend method.
