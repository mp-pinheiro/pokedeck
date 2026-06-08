# poke-deck — agent guide

A Decky Loader (Steam Deck) plugin + companion browser app that reads live Pokémon
battle info from RetroArch and shows species/types/weaknesses/abilities/moves. v1
target game is the GBA romhack **Pokémon Lazarus** (built on pokeemerald-expansion).
**The Steam Deck is the primary target; the browser is just local testing.**

## Reaching RetroArch from the Claude sandbox (READ THIS)

The Claude Bash sandbox runs in an isolated network namespace, so it can't hit the
host's `127.0.0.1:55355` (RetroArch's UDP command port) directly, and the host SOCKS
bridge rejects UDP. The working path is a **host-side TCP↔UDP relay** that the user
runs **once**, which the sandbox reaches over the SOCKS bridge:

```bash
# on the host (where RetroArch runs):
socat -T3 TCP4-LISTEN:55356,bind=127.0.0.1,reuseaddr,fork UDP4:127.0.0.1:55355
```
Then from the sandbox use the `socks` transport (it socks5-CONNECTs to the relay via
`$CLAUDE_CODE_HOST_SOCKS_PROXY_PORT`):
```bash
python3 -m pokedeck.cli battle --transport socks        # one-shot read
python3 -m pokedeck.server --game lazarus --transport socks   # live server
```
RetroArch must have `network_cmd_enable=true` and the **mGBA** core (GBA). Direct
`--transport udp` is for on-device (the Deck) only. Details: memory `sandbox-no-host-loopback`.

## Layout

- `pokedeck/` — **stdlib-only** Python backend (no third-party deps): `server.py`
  (HTTP+SSE), `main.py`-side reuse, `retroarch.py` (udp/tcp/socks transports),
  `socks.py`, `battle.py`/`party.py` (Gen-3 RAM decode), `pokedata.py` (lookup tables),
  `payload.py` (**the JSON contract**), `pokeapi.py` (PokeAPI proxy + disk cache),
  `descriptor.py` (per-game memory maps), `typechart.py`, `cli.py`.
- `main.py` — Decky backend: embeds `pokedeck.server` (port 8420) **and** `decky.emit`s
  to the QAM panel. Exposes `get_snapshot`/`set_game`/`get_species`.
- `packages/ui/` — shared React. **Host-agnostic: inline styles only, `react` as a
  peerDependency, and NO `@decky/*` imports** — the same source builds under Vite and
  `@decky/rollup`. `packages/ui/src/types.ts` MUST match `pokedeck/payload.py`.
- `apps/web/` — Vite browser shell (SSE transport, custom fonts/background live here).
- `src/index.tsx` — Decky shell (consumes `packages/ui` via an `@decky/api` transport).
- `data/games/*.json` — per-game descriptors (symbol addresses + battle-struct offsets).
  `data/*.json` — generated lookup tables. `tools/` — generators, bundler, deploy stager.

## Gamepad navigation (Deck)

Steam's gamepad nav only traverses `@decky/ui` `<Focusable>` — plain divs are
unreachable and the panel won't scroll. `packages/ui` stays `@decky`-free, so
interactivity is injected via `InteractiveProvider` (`Pressable`/`FocusItem`/
`CancelZone`); the Decky shell supplies Focusable-backed renderers (A activates,
focus stops scroll, B = Back, visible focus ring). Memory: `deck-first-gamepad-nav`.

## Dev workflow

- `make web` — frontend dev loop: backend (`--reload`) + Vite HMR. **Open the Vite URL
  (`:5173`), NOT `:8420`** (8420 serves the pre-built `dist/`). HMR covers `packages/ui`
  (it resolves to source). Backend `--reload` watches `pokedeck/*.py` + the `data/`
  tables (cache excluded).
- `make deploy` — build + SCP + sudo-install to the Deck over SSH (needs `.env` from
  `.env.example`: `DECK_HOST` as an **IP** (WSL can't resolve `steamdeck`), `DECK_PASSWORD`).
  `DEBUG=1` injects the plugin.json `debug` flag (auto-reload) into the *deployed* copy
  only. `make logs` / `make verify` / `make cef`. Memory: `decky-deploy-reference`.

## Data generation

`tools/gen_data.py <expansion_src_dir>` parses pokeemerald-expansion (pin
**1.16.1**) headers → `species/moves/abilities/items(.json)`, their `_desc` tables,
`nat_dex.json` (internal id → National-Dex #; the enum diverges from dex order past
905), and `species_info.json` (types/base stats/abilities). The parser resolves
**symbolic enum ids** (e.g. `ABILITY_STAMINA = ABILITIES_COUNT_GEN6`) — don't regress
that to integer-only matching. Needs `pokedex.h` (NationalDexOrder) in the src dir
(fetch via `gh api` if missing). `tools/bundle.sh` must list every `data/*.json` it ships.

## On-Deck gotchas

- HTTPS from the plugin fails with `CERTIFICATE_VERIFY_FAILED` (bundled Python has no
  CA path) — `pokeapi.py` points the SSL context at `/etc/ssl/certs/ca-certificates.crt`.
- The `debug` flag makes Decky watch the plugin dir; `sys.dont_write_bytecode = True`
  in `main.py` keeps `.pyc` writes from tripping reloads. Per-file `cp` on deploy still
  causes a ~5s reload-settle burst (cosmetic).
- I can't reach the Deck from the sandbox; the user runs `make deploy`/`make logs`.

## Working rules

- **Verify before claiming done:** esbuild/Vite/`@decky/rollup` strip types without
  checking, so run `pnpm exec tsc --noEmit` on `packages/ui`, `apps/web`, and root,
  plus build both targets. Test backend changes by exercising the real payload, not
  just imports.
- Commits: **Conventional Commits** (`feat:`/`fix:`/`docs:`/`build:`/`chore:`),
  ≤50-char subject, no body — match the existing history.
- ROMs are never committed (`*.gba` gitignored). `.env` and `data/cache/` are gitignored.
