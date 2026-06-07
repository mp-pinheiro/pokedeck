"""Decode in-battle Pokémon (gBattleMons) using a game descriptor.

For Gen 3 the in-battle struct holds already-derived values (species, level,
HP, the 5 stats, types, status, moves), so battle reads need no decryption —
unlike the encrypted party/box structs.
"""
from dataclasses import dataclass, field

from . import typechart
from .descriptor import FieldSpec


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


def parse_battler(buf, descriptor, battler_index=0, side="?", fields=None):
    if fields is None:
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


# Fields before the hp slot are identical for natural and packed alignment
# (the only divergence is a padding byte before hp). hp/level/maxHP/status1 are
# derived from the located hp offset (0x2A natural, 0x29 packed).
_PRE_HP_FIELDS = ("species", "attack", "defense", "speed", "spAttack", "spDefense",
                  "moves", "type1", "type2", "type3")


def build_field_map(descriptor, hp_off):
    fields = {k: v for k, v in descriptor.battle.fields.items() if k in _PRE_HP_FIELDS}
    fields["hp"] = FieldSpec(hp_off, 2)
    fields["level"] = FieldSpec(hp_off + 2, 1)
    fields["maxHP"] = FieldSpec(hp_off + 4, 2)
    fields["status1"] = FieldSpec(hp_off + 0x26, 4)
    return fields


def _u16(data, off):
    return int.from_bytes(data[off:off + 2], "little")


def plausible_battler(data, base, hp_off):
    """Heuristic: does `base` look like a live BattlePokemon for this alignment?
    Anchored on the version-stable front half (species/moves/types) plus the
    hp/level/maxHP trio, so it rejects almost all misaligned offsets."""
    if base < 0 or base + hp_off + 6 > len(data):
        return False
    if not 1 <= _u16(data, base) <= 1700:  # species (NUM_SPECIES ~1697)
        return False
    if not 1 <= data[base + hp_off + 2] <= 100:  # level
        return False
    hp, maxhp = _u16(data, base + hp_off), _u16(data, base + hp_off + 4)
    if not 0 < hp <= maxhp <= 9999:
        return False
    if any(_u16(data, base + 2 + i * 2) > 9999 for i in range(5)):  # 5 stats
        return False
    if any(data[base + 0x22 + t] >= 21 for t in range(3)):  # types < NUMBER_OF_MON_TYPES
        return False
    return 0 < _u16(data, base + 0x0C) <= 1100  # move[0] present (MOVES_COUNT)


def _find_stride(data, base, hp_off, opp_level, stride_range):
    # Known expansion sizeof(BattlePokemon): 104 (1.13/1.14), 136 (1.15), 140 (1.16).
    # Strides are even; test the common sizes first, then sweep the window.
    candidates = [104, 136, 140] + list(range(stride_range[0], stride_range[1] + 1, 2))
    seen = set()
    for stride in candidates:
        if stride in seen:
            continue
        seen.add(stride)
        b2 = base + stride
        if plausible_battler(data, b2, hp_off):
            if opp_level is None or data[b2 + hp_off + 2] == opp_level:
                return stride
    return None


def automap_scan(data, hp, level, maxhp, opp_level=None, stride_range=(96, 160)):
    """Locate gBattleMons[0] by the hp/level/maxHP signature, determine alignment,
    and find the battler stride. Returns a list of {base_index, hp_off, stride}."""
    out = []
    hp_bytes = hp.to_bytes(2, "little")
    i = data.find(hp_bytes)
    while i != -1:
        if i + 6 <= len(data) and data[i + 2] == level and _u16(data, i + 4) == maxhp:
            for hp_off in (0x2A, 0x29):
                base = i - hp_off
                if plausible_battler(data, base, hp_off):
                    out.append({
                        "base_index": base,
                        "hp_off": hp_off,
                        "stride": _find_stride(data, base, hp_off, opp_level, stride_range),
                    })
                    break
        i = data.find(hp_bytes, i + 1)
    return out


def _hp_offset(descriptor):
    return descriptor.battle.fields["hp"].offset


def read_battle(client, descriptor):
    """Read active battlers with a robust in-battle gate: validate battler 0
    (independent of the relocated/stale gBattleTypeFlags). Returns
    (in_battle, {side: BattleMon})."""
    base = descriptor.symbol("gBattleMons")
    stride = descriptor.battle.stride
    block = client.read_memory(base, stride * descriptor.battle.battler_count)
    hp_off = _hp_offset(descriptor)
    if not plausible_battler(block, descriptor.battle.player_battler * stride, hp_off):
        return False, {}
    mons = {}
    for side, idx in (("player", descriptor.battle.player_battler),
                      ("opponent", descriptor.battle.opponent_battler)):
        mons[side] = parse_battler(block[idx * stride:(idx + 1) * stride], descriptor, idx, side)
    return True, mons
