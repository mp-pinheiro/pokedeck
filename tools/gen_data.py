#!/usr/bin/env python3
"""Generate data/species.json and data/moves.json from pokeemerald-expansion
source headers (pin to a release tag, e.g. expansion/1.16.1).

  python3 tools/gen_data.py <exp_src_dir> [out_dir]

<exp_src_dir> must contain: species.h, moves.h, moves_info.h, gen_1..9_families.h
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


def parse_moves_info(path):
    header_rx = re.compile(r"\[(MOVE_[A-Z0-9_]+)\]\s*=")
    name_rx = re.compile(r'\.name\s*=\s*COMPOUND_STRING\("((?:[^"\\]|\\.)*)"\)')
    type_rx = re.compile(r"\.type\s*=\s*TYPE_([A-Z_]+)")
    cat_rx = re.compile(r"\.category\s*=\s*DAMAGE_CATEGORY_([A-Z]+)")
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    out = {}
    for const, block in _blocks(text, header_rx):
        m = name_rx.search(block)
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


def main():
    src = sys.argv[1]
    out_dir = sys.argv[2] if len(sys.argv) > 2 else "data"

    sp_ids = parse_id_map(os.path.join(src, "species.h"), "SPECIES")
    sp_names = parse_species_names([os.path.join(src, f"gen_{g}_families.h") for g in range(1, 10)])
    species = {}
    for const, sid in sp_ids.items():
        name = sp_names.get(const)
        if name and name not in ("-", "??????????"):
            species[str(sid)] = name

    mv_ids = parse_id_map(os.path.join(src, "moves.h"), "MOVE")
    mv_info = parse_moves_info(os.path.join(src, "moves_info.h"))
    moves = {}
    for const, mid in mv_ids.items():
        info = mv_info.get(const)
        if info and info["name"] not in ("-",):
            moves[str(mid)] = info

    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "species.json"), "w", encoding="utf-8") as fh:
        json.dump(species, fh, separators=(",", ":"), ensure_ascii=False)
    with open(os.path.join(out_dir, "moves.json"), "w", encoding="utf-8") as fh:
        json.dump(moves, fh, separators=(",", ":"), ensure_ascii=False)

    print(f"species: {len(species)} entries (from {len(sp_ids)} ids, {len(sp_names)} names)")
    print(f"moves:   {len(moves)} entries (from {len(mv_ids)} ids, {len(mv_info)} info)")
    print("  species 1 / 25 / 260 / 268:",
          species.get("1"), "/", species.get("25"), "/", species.get("260"), "/", species.get("268"))
    print("  moves 1 / 55:", moves.get("1"), "/", moves.get("55"))


if __name__ == "__main__":
    main()
