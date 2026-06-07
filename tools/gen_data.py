#!/usr/bin/env python3
"""Generate data/{species,moves,abilities,items}.json from pokeemerald-expansion
source headers (pin to a release tag, e.g. expansion/1.16.1).

  python3 tools/gen_data.py <exp_src_dir> [out_dir]

<exp_src_dir> must contain: species.h, moves.h, moves_info.h, gen_1..9_families.h,
abilities.h, abilities_data.h, items.h, items_data.h, pokedex.h
(pokedex.h = include/constants/pokedex.h, the NationalDexOrder enum)
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


def parse_type_defines(paths):
    """`#define RALTS_FAMILY_TYPE2 (P_UPDATED_TYPES >= GEN_6 ? TYPE_FAIRY : TYPE_PSYCHIC)`
    -> {RALTS_FAMILY_TYPE2: TYPE_FAIRY}. Takes the first TYPE_ (the modern/true branch,
    matching the expansion's default P_UPDATED_TYPES = latest gen)."""
    def_rx = re.compile(r"#define\s+([A-Z0-9_]*_FAMILY_TYPE\d+)\s+(.+)")
    type_rx = re.compile(r"TYPE_[A-Z_]+")
    out = {}
    for path in paths:
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                m = def_rx.search(line)
                if m:
                    tm = type_rx.search(m.group(2))
                    if tm:
                        out[m.group(1)] = tm.group(0)
    return out


_BASE_KEYS = {
    "baseHP": "hp", "baseAttack": "atk", "baseDefense": "def",
    "baseSpAttack": "spa", "baseSpDefense": "spd", "baseSpeed": "spe",
}


def parse_species_info(paths):
    """SPECIES_X -> {types:[TYPE_*], abilities:[ABILITY_*], base:{stat:int}} (raw consts).
    Types/base/abilities reflect the expansion baseline (a romhack may retune them;
    active battlers always read authoritative types/stats straight from RAM)."""
    header_rx = re.compile(r"\[(SPECIES_[A-Z0-9_]+)\]\s*=")
    types_rx = re.compile(r"\.types\s*=\s*MON_TYPES\(([^)]*)\)")
    abil_rx = re.compile(r"\.abilities\s*=\s*\{([^}]*)\}")
    base_rx = {src: re.compile(r"\." + src + r"\s*=\s*(\d+)") for src in _BASE_KEYS}
    out = {}
    for path in paths:
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        for const, block in _blocks(text, header_rx):
            if const in out:
                continue
            tm = types_rx.search(block)
            am = abil_rx.search(block)
            base = {}
            for src, dst in _BASE_KEYS.items():
                bm = base_rx[src].search(block)
                if bm:
                    base[dst] = int(bm.group(1))
            out[const] = {
                "types": [t.strip() for t in tm.group(1).split(",")] if tm else [],
                "abilities": [a.strip() for a in am.group(1).split(",")] if am else [],
                "base": base,
            }
    return out


def parse_species_natdex(paths):
    """SPECIES_X -> NATIONAL_DEX_X constant, from each species block's .natDexNum."""
    header_rx = re.compile(r"\[(SPECIES_[A-Z0-9_]+)\]\s*=")
    nd_rx = re.compile(r"\.natDexNum\s*=\s*(NATIONAL_DEX_[A-Z0-9_]+)")
    out = {}
    for path in paths:
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        for const, block in _blocks(text, header_rx):
            m = nd_rx.search(block)
            if m and const not in out:
                out[const] = m.group(1)
    return out


def parse_national_dex(path):
    """NATIONAL_DEX_X -> number, by position in `enum NationalDexOrder` (NONE=0)."""
    member_rx = re.compile(r"^\s*(NATIONAL_DEX_[A-Z0-9_]+)\s*,", re.M)
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    return {m.group(1): i for i, m in enumerate(member_rx.finditer(text))}


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


# .description = COMPOUND_STRING("a\n" "b.") -> the adjacent string literals.
_DESC_RX = re.compile(r'\.description\s*=\s*COMPOUND_STRING\(\s*((?:"(?:[^"\\]|\\.)*"\s*)+)\)')
_STR_RX = re.compile(r'"((?:[^"\\]|\\.)*)"')


def _field_int(block, key):
    """Integer for `.<key> = <expr>,`. Handles config ternaries
    (`COND >= GEN_X ? new : old` -> new) and #if-guarded variants (the first
    value listed is the active/modern one in the expansion's default config)."""
    m = re.search(r"\." + key + r"\s*=\s*([^,\n]+)", block)
    if not m:
        return None
    val = m.group(1)
    if "?" in val:  # take the true branch, before ':' (avoids matching GEN_5's digit)
        val = val.split("?", 1)[1].split(":", 1)[0]
    n = re.search(r"-?\d+", val)
    return int(n.group(0)) if n else None


def _desc_string(block):
    """`.description = COMPOUND_STRING("a\n" "b.")` -> "a b." (moves and items)."""
    m = _DESC_RX.search(block)
    if not m:
        return None
    text = "".join(_STR_RX.findall(m.group(1)))
    text = text.replace("\\n", " ").replace('\\"', '"').replace("\\\\", "\\")
    return " ".join(text.split()) or None


def parse_block_descs(path, prefix):
    """constant -> effect description, from each `[PREFIX_X] = { .description = ... }`."""
    header_rx = re.compile(r"\[(" + prefix + r"_[A-Z0-9_]+)\]\s*=")
    out = {}
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    for const, block in _blocks(text, header_rx):
        d = _desc_string(block)
        if d:
            out[const] = d
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
            "power": _field_int(block, "power"),
            "accuracy": _field_int(block, "accuracy"),
            "pp": _field_int(block, "pp"),
            "priority": _field_int(block, "priority"),
            "desc": _desc_string(block),
        }
    return out


def _id_name_table(ids, names, skip=()):
    return {str(i): names[c] for c, i in ids.items() if c in names and names[c] not in skip}


def main():
    src = sys.argv[1]
    out_dir = sys.argv[2] if len(sys.argv) > 2 else "data"

    fam_paths = [os.path.join(src, f"gen_{g}_families.h") for g in range(1, 10)]
    sp_ids = parse_id_map(os.path.join(src, "species.h"), "SPECIES")
    sp_names = parse_species_names(fam_paths)
    species = _id_name_table(sp_ids, sp_names, skip=("-", "??????????"))

    # internal species id -> National Dex number (forms inherit their base's natDexNum).
    nd_num = parse_national_dex(os.path.join(src, "pokedex.h"))
    sp_nd_const = parse_species_natdex(fam_paths)
    nat_dex = {
        str(sp_ids[c]): nd_num[nd]
        for c, nd in sp_nd_const.items()
        if c in sp_ids and nd in nd_num and nd_num[nd] > 0
    }

    mv_ids = parse_id_map(os.path.join(src, "moves.h"), "MOVE")
    mv_info = parse_moves_info(os.path.join(src, "moves_info.h"))
    moves = {str(mid): mv_info[c] for c, mid in mv_ids.items() if c in mv_info and mv_info[c]["name"] != "-"}

    ab_ids = parse_id_map(os.path.join(src, "abilities.h"), "ABILITY")
    ab_names = parse_block_names(os.path.join(src, "abilities_data.h"), "ABILITY")
    abilities = _id_name_table(ab_ids, ab_names, skip=("-------", ""))

    # internal species id -> {types[], base{}, abilities[]} with consts resolved to names.
    type_defines = parse_type_defines(fam_paths)

    def _resolve_type(tc):
        tc = type_defines.get(tc, tc)  # *_FAMILY_TYPE* indirection -> TYPE_*
        if not tc.startswith("TYPE_"):
            return None
        key = tc.replace("TYPE_", "")
        return TYPE_NAME.get(key, key.title())

    def _abil_disp(ac):
        aid = ab_ids.get(ac)
        return abilities.get(str(aid)) if aid is not None else None

    species_info = {}
    for const, info in parse_species_info(fam_paths).items():
        if const not in sp_ids:
            continue
        types = []
        for tc in info["types"]:
            d = _resolve_type(tc)
            if d and d not in ("None", "???") and d not in types:
                types.append(d)
        abil = []
        for ac in info["abilities"]:
            if ac == "ABILITY_NONE":
                continue
            nm = _abil_disp(ac)
            if nm and nm not in abil:
                abil.append(nm)
        species_info[str(sp_ids[const])] = {"types": types, "base": info["base"], "abilities": abil}

    it_ids = parse_id_map(os.path.join(src, "items.h"), "ITEM")
    it_names = parse_block_names(os.path.join(src, "items_data.h"), "ITEM")
    items = _id_name_table(it_ids, it_names, skip=("????????", "??????????", ""))
    it_descs = parse_block_descs(os.path.join(src, "items_data.h"), "ITEM")
    items_desc = {str(it_ids[c]): d for c, d in it_descs.items() if c in it_ids and str(it_ids[c]) in items}

    os.makedirs(out_dir, exist_ok=True)
    tables = (
        ("species", species), ("moves", moves), ("abilities", abilities),
        ("items", items), ("items_desc", items_desc),
        ("nat_dex", nat_dex), ("species_info", species_info),
    )
    for name, table in tables:
        with open(os.path.join(out_dir, name + ".json"), "w", encoding="utf-8") as fh:
            json.dump(table, fh, separators=(",", ":"), ensure_ascii=False)

    print(f"species:{len(species)} moves:{len(moves)} abilities:{len(abilities)} "
          f"items:{len(items)} nat_dex:{len(nat_dex)} species_info:{len(species_info)}")
    print("  species 729/268:", species.get("729"), "/", species.get("268"))
    print("  species_info 729(Brionne):", species_info.get("729"))
    print("  nat_dex 1336(Toedscool)->948? :", nat_dex.get("1336"),
          " 729(Brionne)->729? :", nat_dex.get("729"))
    print("  moves 227/61:", moves.get("227", {}).get("name"), "/", moves.get("61", {}).get("name"))
    print("  abilities 67/61/19:", abilities.get("67"), "/", abilities.get("61"), "/", abilities.get("19"))
    print("  items 28:", items.get("28"), "desc:", items_desc.get("28"))


if __name__ == "__main__":
    main()
