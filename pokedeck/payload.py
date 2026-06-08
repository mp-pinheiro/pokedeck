"""Build JSON-serializable battle payloads for the frontend (decky.emit)."""
from . import typechart


def _typing(types):
    """weak/resist/immune lists (payload form) for a list of type display names."""
    w = typechart.weaknesses(types)
    return {
        "weak": [[t, m] for t, m in w["weak"]],
        "resist": [[t, m] for t, m in w["resist"]],
        "immune": [t for t, _ in w["immune"]],
    }


def move_dict(pd, mid, cur_pp=None):
    """One move's display payload. cur_pp is the live remaining PP (None off-RAM)."""
    mv = pd.move(mid)
    return {
        "id": mid,
        "name": mv["name"] if mv else f"#{mid}",
        "type": mv["type"] if mv else None,
        "category": mv["category"] if mv else None,
        "power": mv.get("power") if mv else None,
        "accuracy": mv.get("accuracy") if mv else None,
        "priority": mv.get("priority") if mv else None,
        "pp_max": mv.get("pp") if mv else None,
        "pp": cur_pp,
        "desc": mv.get("desc") if mv else None,
    }


def mon_to_dict(mon, pd):
    # Active battlers carry authoritative types straight from RAM (reflect any romhack
    # retyping); base stats + the species ability list come from the static table.
    info = pd.info(mon.species)
    moves = [
        move_dict(pd, mid, mon.pp[i] if i < len(mon.pp) else None)
        for i, mid in enumerate(mon.moves) if mid
    ]
    return {
        "species_id": mon.species,
        "dex": pd.national_dex(mon.species),
        "species": pd.species_name(mon.species) or f"#{mon.species}",
        "level": mon.level,
        "hp": mon.hp,
        "max_hp": mon.max_hp,
        "status": mon.status1,
        "shiny": mon.is_shiny,
        "ability": pd.ability_name(mon.ability) or (f"#{mon.ability}" if mon.ability else None),
        "ability_desc": pd.ability_desc(mon.ability) if mon.ability else None,
        "abilities": info.get("abilities", []),
        "item": pd.item_name(mon.item) or (f"#{mon.item}" if mon.item else None),
        "item_desc": pd.item_desc(mon.item) if mon.item else None,
        "friendship": mon.friendship,
        "ivs": mon.iv_spread if mon.ivs else None,
        "stats": mon.stats,
        "base": info.get("base") or None,
        "types": mon.types,
        **_typing(mon.types),
        "moves": moves,
    }


def battle_payload(mons, pd):
    return {side: mon_to_dict(mon, pd) for side, mon in mons.items()}


def party_mon_to_dict(mon, pd):
    # Box/party structs don't store types; derive them (and weaknesses) from the
    # species baseline. Active battlers get authoritative types from RAM instead.
    info = pd.info(mon["species"])
    types = info.get("types", [])
    moves = [move_dict(pd, mid) for mid in mon["moves"] if mid]
    return {
        "species_id": mon["species"],
        "dex": pd.national_dex(mon["species"]),
        "species": pd.species_name(mon["species"]) or f"#{mon['species']}",
        "level": mon["level"],
        "hp": mon["hp"],
        "max_hp": mon["max_hp"],
        "shiny": mon["shiny"],
        "item": pd.item_name(mon["item"]) or (f"#{mon['item']}" if mon["item"] else None),
        "item_desc": pd.item_desc(mon["item"]) if mon["item"] else None,
        "abilities": info.get("abilities", []),
        "base": info.get("base") or None,
        "types": types,
        **_typing(types),
        "moves": moves,
    }


def party_payload(party, pd):
    return [party_mon_to_dict(m, pd) for m in party]
