#!/usr/bin/env python3
"""Generate a synthetic EWRAM dump with two in-battle Pokémon, to test automap
offline (no emulator). Mirrors the pokeemerald-expansion BattlePokemon prefix,
natural alignment: species@0x00, stats@0x02..0x0A, moves@0x0C, types@0x22..0x24,
hp@0x2A, level@0x2C, maxHP@0x2E. Player (Lv22, 21/61) and opponent (Cascoon
#268, Lv9) one stride (0x68) apart — matching the live Lazarus battle.
"""
import struct
import sys

STRIDE = 0x68
PLAYER_OFF = 0x1000


def write_mon(buf, off, species, stats, moves, types, hp, level, maxhp):
    struct.pack_into("<H", buf, off + 0x00, species)
    for i, s in enumerate(stats):
        struct.pack_into("<H", buf, off + 0x02 + i * 2, s)
    for i, m in enumerate(moves):
        struct.pack_into("<H", buf, off + 0x0C + i * 2, m)
    buf[off + 0x22], buf[off + 0x23], buf[off + 0x24] = types
    struct.pack_into("<H", buf, off + 0x2A, hp)
    buf[off + 0x2C] = level
    struct.pack_into("<H", buf, off + 0x2E, maxhp)


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "ewram_fixture.bin"
    buf = bytearray(0x2000)
    write_mon(buf, PLAYER_OFF, species=260, stats=(120, 90, 110, 95, 100),
              moves=(55, 57, 58, 70), types=(12, 0, 0), hp=21, level=22, maxhp=61)
    write_mon(buf, PLAYER_OFF + STRIDE, species=268, stats=(45, 35, 15, 30, 30),
              moves=(33, 0, 0, 0), types=(7, 0, 0), hp=20, level=9, maxhp=20)
    with open(path, "wb") as fh:
        fh.write(buf)
    print(f"wrote {len(buf)} bytes to {path} (player @ 0x{PLAYER_OFF:x}, opponent @ 0x{PLAYER_OFF + STRIDE:x})")


if __name__ == "__main__":
    main()
