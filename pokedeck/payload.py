"""Build JSON-serializable battle payloads for the frontend (decky.emit)."""


def mon_to_dict(mon, pd):
    weak = mon.weaknesses()
    moves = []
    for mid in mon.moves:
        if not mid:
            continue
        mv = pd.move(mid)
        moves.append({
            "id": mid,
            "name": mv["name"] if mv else f"#{mid}",
            "type": mv["type"] if mv else None,
            "category": mv["category"] if mv else None,
        })
    return {
        "species_id": mon.species,
        "species": pd.species_name(mon.species) or f"#{mon.species}",
        "level": mon.level,
        "hp": mon.hp,
        "max_hp": mon.max_hp,
        "status": mon.status1,
        "stats": mon.stats,
        "types": mon.types,
        "weak": [[t, m] for t, m in weak["weak"]],
        "resist": [[t, m] for t, m in weak["resist"]],
        "immune": [t for t, _ in weak["immune"]],
        "moves": moves,
    }


def battle_payload(mons, pd):
    return {side: mon_to_dict(mon, pd) for side, mon in mons.items()}
