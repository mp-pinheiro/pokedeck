"""Build JSON-serializable battle payloads for the frontend (decky.emit)."""


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
    }


def mon_to_dict(mon, pd):
    weak = mon.weaknesses()
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
        "item": pd.item_name(mon.item) or (f"#{mon.item}" if mon.item else None),
        "friendship": mon.friendship,
        "ivs": mon.iv_spread if mon.ivs else None,
        "stats": mon.stats,
        "types": mon.types,
        "weak": [[t, m] for t, m in weak["weak"]],
        "resist": [[t, m] for t, m in weak["resist"]],
        "immune": [t for t, _ in weak["immune"]],
        "moves": moves,
    }


def battle_payload(mons, pd):
    return {side: mon_to_dict(mon, pd) for side, mon in mons.items()}


def party_mon_to_dict(mon, pd):
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
        "moves": moves,
    }


def party_payload(party, pd):
    return [party_mon_to_dict(m, pd) for m in party]
