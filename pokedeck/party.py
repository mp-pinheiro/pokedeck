"""Decode Gen-3 party Pokémon (encrypted 100-byte structs) from RAM.

Each slot = BoxPokemon (80B) + a 20B unencrypted battle tail. The 48 secure bytes
@0x20 are XOR-decrypted with (otId ^ personality) and the four 12-byte substructs
are ordered by personality % 24. In pokeemerald-expansion species/moves are 11-bit.
Verified live 2026-06-07 (gPlayerParty Brionne; gEnemyParty Cascoon + Cutiefly).
"""
import struct

SLOT_SIZE = 100
PARTY_SIZE = 6
_ORDERS = [
    "GAEM", "GAME", "GEAM", "GEMA", "GMAE", "GMEA",
    "AGEM", "AGME", "AEGM", "AEMG", "AMGE", "AMEG",
    "EGAM", "EGMA", "EAGM", "EAMG", "EMGA", "EMAG",
    "MGAE", "MGEA", "MAGE", "MAEG", "MEGA", "MEAG",
]


def decode_slot(slot):
    """Decode one 100-byte party slot; returns a dict, or None if empty/invalid."""
    if len(slot) < SLOT_SIZE:
        return None
    pid, otid = struct.unpack_from("<II", slot, 0)
    if pid == 0:
        return None
    enc = bytearray(slot[0x20:0x20 + 48])
    key = otid ^ pid
    for i in range(0, 48, 4):
        struct.pack_into("<I", enc, i, struct.unpack_from("<I", enc, i)[0] ^ key)
    checksum = struct.unpack_from("<H", slot, 0x1C)[0]
    if sum(struct.unpack_from("<H", enc, i)[0] for i in range(0, 48, 2)) & 0xFFFF != checksum:
        return None
    order = _ORDERS[pid % 24]
    w0 = struct.unpack_from("<I", enc, order.index("G") * 12)[0]
    species = w0 & 0x7FF
    if not species:
        return None
    attacks = order.index("A") * 12
    return {
        "species": species,
        "item": (w0 >> 16) & 0x3FF,
        "moves": [struct.unpack_from("<H", enc, attacks + 2 * j)[0] & 0x7FF for j in range(4)],
        "level": slot[0x54],
        "hp": struct.unpack_from("<H", slot, 0x56)[0],
        "max_hp": struct.unpack_from("<H", slot, 0x58)[0],
        "shiny": (((otid >> 16) ^ (otid & 0xFFFF) ^ (pid >> 16) ^ (pid & 0xFFFF)) < 8),
    }


def decode_party(block):
    mons = []
    for i in range(PARTY_SIZE):
        mon = decode_slot(block[i * SLOT_SIZE:(i + 1) * SLOT_SIZE])
        if mon:
            mons.append(mon)
    return mons


def read_party(client, party_addr, count=PARTY_SIZE):
    return decode_party(client.read_memory(party_addr, count * SLOT_SIZE))


if __name__ == "__main__":
    import sys
    data = open(sys.argv[1], "rb").read()
    addr = int(sys.argv[2], 16)
    region = int(sys.argv[3], 16) if len(sys.argv) > 3 else 0x02000000
    for mon in decode_party(data[addr - region: addr - region + PARTY_SIZE * SLOT_SIZE]):
        print(mon)
