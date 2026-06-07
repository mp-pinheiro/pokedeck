"""Type-ID tables and the defensive type chart (Gen 6+, with Fairy).

pokeemerald-expansion inserts TYPE_NONE=0 at the front, so every type ID is
shifted +1 vs vanilla Gen 3 (Normal=1, not 0) and Fairy/Stellar are appended.
The chart itself is keyed by display name so it is table-independent.
"""

EXPANSION_TYPES = {
    0: "None", 1: "Normal", 2: "Fighting", 3: "Flying", 4: "Poison", 5: "Ground",
    6: "Rock", 7: "Bug", 8: "Ghost", 9: "Steel", 10: "???", 11: "Fire",
    12: "Water", 13: "Grass", 14: "Electric", 15: "Psychic", 16: "Ice",
    17: "Dragon", 18: "Dark", 19: "Fairy", 20: "Stellar",
}

VANILLA_TYPES = {
    0: "Normal", 1: "Fighting", 2: "Flying", 3: "Poison", 4: "Ground", 5: "Rock",
    6: "Bug", 7: "Ghost", 8: "Steel", 9: "???", 10: "Fire", 11: "Water",
    12: "Grass", 13: "Electric", 14: "Psychic", 15: "Ice", 16: "Dragon",
    17: "Dark", 255: "None",
}

TYPE_TABLES = {"expansion": EXPANSION_TYPES, "vanilla": VANILLA_TYPES}

OFFENSIVE_TYPES = [
    "Normal", "Fire", "Water", "Electric", "Grass", "Ice", "Fighting", "Poison",
    "Ground", "Flying", "Psychic", "Bug", "Rock", "Ghost", "Dragon", "Dark",
    "Steel", "Fairy",
]

# attacker -> {defender: multiplier}; entries omitted default to 1.0
CHART = {
    "Normal": {"Rock": 0.5, "Steel": 0.5, "Ghost": 0.0},
    "Fire": {"Fire": 0.5, "Water": 0.5, "Grass": 2, "Ice": 2, "Bug": 2, "Rock": 0.5, "Dragon": 0.5, "Steel": 2},
    "Water": {"Fire": 2, "Water": 0.5, "Grass": 0.5, "Ground": 2, "Rock": 2, "Dragon": 0.5},
    "Electric": {"Water": 2, "Electric": 0.5, "Grass": 0.5, "Ground": 0.0, "Flying": 2, "Dragon": 0.5},
    "Grass": {"Fire": 0.5, "Water": 2, "Grass": 0.5, "Poison": 0.5, "Ground": 2, "Flying": 0.5, "Bug": 0.5, "Rock": 2, "Dragon": 0.5, "Steel": 0.5},
    "Ice": {"Fire": 0.5, "Water": 0.5, "Grass": 2, "Ice": 0.5, "Ground": 2, "Flying": 2, "Dragon": 2, "Steel": 0.5},
    "Fighting": {"Normal": 2, "Ice": 2, "Poison": 0.5, "Flying": 0.5, "Psychic": 0.5, "Bug": 0.5, "Rock": 2, "Ghost": 0.0, "Dark": 2, "Steel": 2, "Fairy": 0.5},
    "Poison": {"Grass": 2, "Poison": 0.5, "Ground": 0.5, "Rock": 0.5, "Ghost": 0.5, "Steel": 0.0, "Fairy": 2},
    "Ground": {"Fire": 2, "Electric": 2, "Grass": 0.5, "Poison": 2, "Flying": 0.0, "Bug": 0.5, "Rock": 2, "Steel": 2},
    "Flying": {"Electric": 0.5, "Grass": 2, "Fighting": 2, "Bug": 2, "Rock": 0.5, "Steel": 0.5},
    "Psychic": {"Fighting": 2, "Poison": 2, "Psychic": 0.5, "Dark": 0.0, "Steel": 0.5},
    "Bug": {"Fire": 0.5, "Grass": 2, "Fighting": 0.5, "Poison": 0.5, "Flying": 0.5, "Psychic": 2, "Ghost": 0.5, "Dark": 2, "Steel": 0.5, "Fairy": 0.5},
    "Rock": {"Fire": 2, "Ice": 2, "Fighting": 0.5, "Ground": 0.5, "Flying": 2, "Bug": 2, "Steel": 0.5},
    "Ghost": {"Normal": 0.0, "Psychic": 2, "Ghost": 2, "Dark": 0.5},
    "Dragon": {"Dragon": 2, "Steel": 0.5, "Fairy": 0.0},
    "Dark": {"Fighting": 0.5, "Psychic": 2, "Ghost": 2, "Dark": 0.5, "Fairy": 0.5},
    "Steel": {"Fire": 0.5, "Water": 0.5, "Electric": 0.5, "Ice": 2, "Rock": 2, "Steel": 0.5, "Fairy": 2},
    "Fairy": {"Fire": 0.5, "Fighting": 2, "Poison": 0.5, "Dragon": 2, "Dark": 2, "Steel": 0.5},
}


def defensive_multipliers(types):
    """Incoming multiplier for each offensive type against a defender's types."""
    defenders = [t for t in types if t in OFFENSIVE_TYPES]
    mults = {}
    for atk in OFFENSIVE_TYPES:
        m = 1.0
        for d in defenders:
            m *= CHART.get(atk, {}).get(d, 1.0)
        mults[atk] = m
    return mults


def weaknesses(types):
    result = {"weak": [], "resist": [], "immune": []}
    if not any(t in OFFENSIVE_TYPES for t in types):
        return result
    for atk, m in defensive_multipliers(types).items():
        if m == 0:
            result["immune"].append((atk, m))
        elif m > 1:
            result["weak"].append((atk, m))
        elif m < 1:
            result["resist"].append((atk, m))
    result["weak"].sort(key=lambda x: -x[1])
    result["resist"].sort(key=lambda x: x[1])
    return result
