"""Per-game memory-map descriptors loaded from data/games/*.json.

A descriptor encodes the emulated symbol addresses (gBattleMons, etc.), the
in-battle struct field offsets, and which type-ID table the game uses, so the
parser is fully data-driven.
"""
import json
import os
from dataclasses import dataclass

_PKG_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(_PKG_DIR)
GAMES_DIR = os.environ.get("POKEDECK_GAMES_DIR", os.path.join(REPO_ROOT, "data", "games"))

_ALIASES = {"lazarus": "pokemon_lazarus", "emerald": "pokemon_emerald"}


def _to_int(value):
    if isinstance(value, bool):
        raise TypeError("bool is not an address/offset")
    if isinstance(value, int):
        return value
    return int(value, 0)  # "0x02024084" or decimal string


@dataclass
class FieldSpec:
    offset: int
    size: int
    count: int = 1


@dataclass
class BattleLayout:
    stride: int
    battler_count: int
    player_battler: int
    opponent_battler: int
    type_table: str
    fields: dict  # name -> FieldSpec


@dataclass
class GameDescriptor:
    id: str
    name: str
    base: str
    endianness: str
    symbols: dict  # name -> int
    battle: BattleLayout
    raw: dict

    @classmethod
    def load(cls, path):
        with open(path, encoding="utf-8") as fh:
            raw = json.load(fh)

        symbols = {}
        for key, value in raw.get("symbols", {}).items():
            if key.startswith("_") or isinstance(value, bool):
                continue
            symbols[key] = _to_int(value)

        battle = raw["battle"]
        fields = {}
        for name, spec in battle["fields"].items():
            if name.startswith("_"):
                continue
            fields[name] = FieldSpec(_to_int(spec["off"]), int(spec["size"]), int(spec.get("count", 1)))

        layout = BattleLayout(
            stride=_to_int(battle["battler_stride"]),
            battler_count=int(battle["battler_count"]),
            player_battler=int(battle["player_battler"]),
            opponent_battler=int(battle["opponent_battler"]),
            type_table=battle.get("type_table", "expansion"),
            fields=fields,
        )
        return cls(
            id=raw["id"],
            name=raw["name"],
            base=raw.get("base", ""),
            endianness=raw.get("endianness", "little"),
            symbols=symbols,
            battle=layout,
            raw=raw,
        )

    def symbol(self, name):
        return self.symbols[name]


def resolve_descriptor(name_or_path):
    if os.path.isfile(name_or_path):
        return GameDescriptor.load(name_or_path)
    key = _ALIASES.get(name_or_path, name_or_path)
    path = os.path.join(GAMES_DIR, key + ".json")
    if not os.path.isfile(path):
        raise FileNotFoundError(f"no descriptor for {name_or_path!r} (looked at {path})")
    return GameDescriptor.load(path)


def list_games():
    """[{id, name}] for every descriptor in GAMES_DIR (for the game picker)."""
    out = []
    for fn in sorted(os.listdir(GAMES_DIR)):
        if fn.endswith(".json"):
            try:
                d = GameDescriptor.load(os.path.join(GAMES_DIR, fn))
                out.append({"id": d.id, "name": d.name})
            except (OSError, ValueError, KeyError):
                pass
    return out
