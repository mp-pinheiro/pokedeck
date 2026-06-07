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
