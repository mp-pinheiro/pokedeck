"""Decode in-battle Pokémon (gBattleMons) using a game descriptor.

For Gen 3 the in-battle struct holds already-derived values (species, level,
HP, the 5 stats, types, status, moves), so battle reads need no decryption —
unlike the encrypted party/box structs.
"""
from dataclasses import dataclass, field

from . import typechart


@dataclass
class BattleMon:
    battler: int
    side: str
    species: int
    level: int
    hp: int
    max_hp: int
    stats: dict
    type_ids: list
    types: list
    moves: list
    status1: int = 0

    def weaknesses(self):
        return typechart.weaknesses(self.types)


def _read_field(buf, spec, byteorder):
    if spec.count > 1:
        return [
            int.from_bytes(buf[spec.offset + i * spec.size: spec.offset + (i + 1) * spec.size], byteorder)
            for i in range(spec.count)
        ]
    return int.from_bytes(buf[spec.offset: spec.offset + spec.size], byteorder)


def parse_battler(buf, descriptor, battler_index=0, side="?"):
    fields = descriptor.battle.fields
    byteorder = "little" if descriptor.endianness == "little" else "big"
    table = typechart.TYPE_TABLES[descriptor.battle.type_table]

    def get(name):
        return _read_field(buf, fields[name], byteorder) if name in fields else None

    type_ids = [get("type1"), get("type2"), get("type3")]
    type_ids = [t for t in type_ids if t is not None]

    types = []
    for name in (get("type1"), get("type2")):
        label = table.get(name) if name is not None else None
        if label and label not in ("None", "???") and label not in types:
            types.append(label)

    stats = {k: get(k) for k in ("attack", "defense", "speed", "spAttack", "spDefense")}

    return BattleMon(
        battler=battler_index,
        side=side,
        species=get("species"),
        level=get("level"),
        hp=get("hp"),
        max_hp=get("maxHP"),
        stats=stats,
        type_ids=type_ids,
        types=types,
        moves=get("moves") or [],
        status1=get("status1") or 0,
    )


def in_battle(client, descriptor):
    """Return (is_in_battle, raw_flags). gBattleTypeFlags is 0 outside battle."""
    flags = int.from_bytes(client.read_memory(descriptor.symbol("gBattleTypeFlags"), 4), "little")
    return flags != 0, flags


def read_battlers(client, descriptor, sides=("player", "opponent")):
    """Read the active battlers in one block and decode each side."""
    base = descriptor.symbol("gBattleMons")
    stride = descriptor.battle.stride
    block = client.read_memory(base, stride * descriptor.battle.battler_count)

    index_for = {
        "player": descriptor.battle.player_battler,
        "opponent": descriptor.battle.opponent_battler,
    }
    out = {}
    for side in sides:
        idx = index_for[side]
        buf = block[idx * stride: (idx + 1) * stride]
        out[side] = parse_battler(buf, descriptor, idx, side)
    return out


def find_battle_mon(data, start_addr, hp, level, maxhp):
    """Locate the active BattlePokemon by the (hp, +2 level, +4 maxHP) signature.

    Returns absolute addresses of matching hp fields. Alignment-agnostic: the
    relative spacing of hp/level/maxHP is identical for natural and packed
    layouts, so the gBattleMons base is hp_addr minus the hp offset (0x2A or 0x29).
    """
    hp_bytes = hp.to_bytes(2, "little")
    hits = []
    i = data.find(hp_bytes)
    while i != -1:
        if i + 6 <= len(data) and data[i + 2] == level and int.from_bytes(data[i + 4:i + 6], "little") == maxhp:
            hits.append(start_addr + i)
        i = data.find(hp_bytes, i + 1)
    return hits
