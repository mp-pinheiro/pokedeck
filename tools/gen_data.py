#!/usr/bin/env python3
"""Generate data/{species,moves,abilities,items}.json from pokeemerald-expansion
source headers (pin to a release tag, e.g. expansion/1.16.1).

  python3 tools/gen_data.py <exp_src_dir> [out_dir]

<exp_src_dir> must contain: species.h, moves.h, moves_info.h, gen_1..9_families.h,
abilities.h, abilities_data.h, items.h, items_data.h
"""
import json
import os
import re
import sys

# Expansion TYPE_* -> display name (kept in sync with pokedeck/typechart.py)
TYPE_NAME = {
    "NORMAL": "Normal", "FIGHTING": "Fighting", "FLYING": "Flying", "POISON": "Poison",
    "GROUND": "Ground", "ROCK": "Rock", "BUG": "Bug", "GHOST": "Ghost", "STEEL": "Steel",
    "MYSTERY": "???", "FIRE": "Fire", "WATER": "Water", "GRASS": "Grass",
    "ELECTRIC": "Electric", "PSYCHIC": "Psychic", "ICE": "Ice", "DRAGON": "Dragon",
    "DARK": "Dark", "FAIRY": "Fairy", "STELLAR": "Stellar",
}

# .name = _("X") | COMPOUND_STRING("X") | ITEM_NAME("X") -> "X"; non-string macros skip
NAME_RX = re.compile(r'\.name\s*=\s*[A-Za-z_]*\("((?:[^"\\]|\\.)*)"\)')


def parse_id_map(path, prefix):
    """constant -> id, from explicit `PREFIX_X = N,` enum lines."""
    rx = re.compile(r"^\s*(" + prefix + r"_[A-Z0-9_]+)\s*=\s*(\d+)\s*,", re.M)
    with open(path, encoding="utf-8") as fh:
        return {m.group(1): int(m.group(2)) for m in rx.finditer(fh.read())}


def _blocks(text, header_rx):
    """Yield (constant, block_text) for each `[CONST] =` section."""
    marks = [(m.group(1), m.start()) for m in header_rx.finditer(text)]
    for i, (const, start) in enumerate(marks):
        end = marks[i + 1][1] if i + 1 < len(marks) else len(text)
        yield const, text[start:end]


def parse_species_names(paths):
    header_rx = re.compile(r"\[(SPECIES_[A-Z0-9_]+)\]\s*=")
    name_rx = re.compile(r'\.speciesName\s*=\s*_\("((?:[^"\\]|\\.)*)"\)')
    names = {}
    for path in paths:
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        for const, block in _blocks(text, header_rx):
            m = name_rx.search(block)
            if m and const not in names:
                names[const] = m.group(1)
    return names


def parse_block_names(path, prefix):
    """constant -> display name, from `[PREFIX_X] = { .name = MACRO("Name") }`."""
    header_rx = re.compile(r"\[(" + prefix + r"_[A-Z0-9_]+)\]\s*=")
    out = {}
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    for const, block in _blocks(text, header_rx):
        m = NAME_RX.search(block)
        if m:
            out[const] = m.group(1)
    return out


def parse_moves_info(path):
    header_rx = re.compile(r"\[(MOVE_[A-Z0-9_]+)\]\s*=")
    type_rx = re.compile(r"\.type\s*=\s*TYPE_([A-Z_]+)")
    cat_rx = re.compile(r"\.category\s*=\s*DAMAGE_CATEGORY_([A-Z]+)")
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    out = {}
    for const, block in _blocks(text, header_rx):
        m = NAME_RX.search(block)
        if not m:
            continue
        ty = type_rx.search(block)
        ct = cat_rx.search(block)
        out[const] = {
            "name": m.group(1),
            "type": TYPE_NAME.get(ty.group(1), ty.group(1).title()) if ty else None,
            "category": ct.group(1).lower() if ct else None,
        }
    return out


def _id_name_table(ids, names, skip=()):
    return {str(i): names[c] for c, i in ids.items() if c in names and names[c] not in skip}


def main():
    src = sys.argv[1]
    out_dir = sys.argv[2] if len(sys.argv) > 2 else "data"

    sp_ids = parse_id_map(os.path.join(src, "species.h"), "SPECIES")
    sp_names = parse_species_names([os.path.join(src, f"gen_{g}_families.h") for g in range(1, 10)])
    species = _id_name_table(sp_ids, sp_names, skip=("-", "??????????"))

    mv_ids = parse_id_map(os.path.join(src, "moves.h"), "MOVE")
    mv_info = parse_moves_info(os.path.join(src, "moves_info.h"))
    moves = {str(mid): mv_info[c] for c, mid in mv_ids.items() if c in mv_info and mv_info[c]["name"] != "-"}

    ab_ids = parse_id_map(os.path.join(src, "abilities.h"), "ABILITY")
    ab_names = parse_block_names(os.path.join(src, "abilities_data.h"), "ABILITY")
    abilities = _id_name_table(ab_ids, ab_names, skip=("-------", ""))

    it_ids = parse_id_map(os.path.join(src, "items.h"), "ITEM")
    it_names = parse_block_names(os.path.join(src, "items_data.h"), "ITEM")
    items = _id_name_table(it_ids, it_names, skip=("????????", "??????????", ""))

    os.makedirs(out_dir, exist_ok=True)
    for name, table in (("species", species), ("moves", moves), ("abilities", abilities), ("items", items)):
        with open(os.path.join(out_dir, name + ".json"), "w", encoding="utf-8") as fh:
            json.dump(table, fh, separators=(",", ":"), ensure_ascii=False)

    print(f"species:{len(species)} moves:{len(moves)} abilities:{len(abilities)} items:{len(items)}")
    print("  species 729/268:", species.get("729"), "/", species.get("268"))
    print("  moves 227/61:", moves.get("227", {}).get("name"), "/", moves.get("61", {}).get("name"))
    print("  abilities 67/61/19:", abilities.get("67"), "/", abilities.get("61"), "/", abilities.get("19"))
    print("  items 28:", items.get("28"))


if __name__ == "__main__":
    main()
