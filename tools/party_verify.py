#!/usr/bin/env python3
"""Verify Gen-3 party decryption against a captured EWRAM dump.

  python3 tools/party_verify.py <ewram.bin> <party_addr_hex> [region_base_hex]

Gen-3 party Pokemon = 100 bytes: BoxPokemon (80B) + a 20B unencrypted battle tail.
The 48 secure bytes @0x20 are XOR-decrypted with (otId ^ personality) and the four
12-byte substructs are ordered by personality % 24. Species is the first field of
the Growth substruct (11-bit in expansion; fits in the low u16).
"""
import struct
import sys

# substruct order (G=Growth A=Attacks E=EVs M=Misc) by personality % 24
ORDERS = [
    "GAEM", "GAME", "GEAM", "GEMA", "GMAE", "GMEA",
    "AGEM", "AGME", "AEGM", "AEMG", "AMGE", "AMEG",
    "EGAM", "EGMA", "EAGM", "EAMG", "EMGA", "EMAG",
    "MGAE", "MGEA", "MAGE", "MAEG", "MEGA", "MEAG",
]


def read_slot(data, base):
    pid, otid = struct.unpack_from("<II", data, base)
    checksum = struct.unpack_from("<H", data, base + 0x1C)[0]
    enc = bytearray(data[base + 0x20: base + 0x20 + 48])
    key = otid ^ pid
    for i in range(0, 48, 4):
        struct.pack_into("<I", enc, i, struct.unpack_from("<I", enc, i)[0] ^ key)
    csum = sum(struct.unpack_from("<H", enc, i)[0] for i in range(0, 48, 2)) & 0xFFFF
    growth = ORDERS[pid % 24].index("G") * 12
    attacks = ORDERS[pid % 24].index("A") * 12
    species = struct.unpack_from("<H", enc, growth)[0] & 0x7FF
    moves = [struct.unpack_from("<H", enc, attacks + 2 * j)[0] & 0x7FF for j in range(4)]
    return {
        "pid": f"0x{pid:08x}", "checksum_ok": csum == checksum,
        "species": species, "moves": moves,
        "level": data[base + 0x54],
        "hp": struct.unpack_from("<H", data, base + 0x56)[0],
        "maxhp": struct.unpack_from("<H", data, base + 0x58)[0],
    }


def main():
    data = open(sys.argv[1], "rb").read()
    party_addr = int(sys.argv[2], 16)
    region = int(sys.argv[3], 16) if len(sys.argv) > 3 else 0x02000000
    off = party_addr - region
    for slot in range(6):
        b = off + slot * 100
        if b + 100 > len(data):
            break
        print(f"slot {slot}: {read_slot(data, b)}")


if __name__ == "__main__":
    main()
