"""Dev CLI for the battle reader. Run from the repo root:

  python3 -m pokedeck.cli --game lazarus info
  python3 -m pokedeck.cli --game lazarus status
  python3 -m pokedeck.cli --game lazarus live
  python3 -m pokedeck.cli --game lazarus dump 02024084 160
  python3 -m pokedeck.cli --game lazarus decode <hex bytes of one battler>
"""
import argparse
import sys
import time

from .battle import (
    automap_scan,
    build_field_map,
    find_battle_mon,
    in_battle,
    parse_battler,
    read_battlers,
)
from .descriptor import resolve_descriptor
from .retroarch import RetroArchClient, RetroArchError


def _fmt_mult(m):
    return f"x{m:g}"


def print_mon(mon):
    print(f"[{mon.side}] battler {mon.battler}")
    print(f"  species #{mon.species}  Lv{mon.level}  HP {mon.hp}/{mon.max_hp}")
    s = mon.stats
    print(f"  stats  ATK{s['attack']} DEF{s['defense']} SPA{s['spAttack']} SPD{s['spDefense']} SPE{s['speed']}")
    print(f"  types  {', '.join(mon.types) or '—'}")
    w = mon.weaknesses()
    if w["weak"]:
        print(f"  weak   {', '.join(f'{t} {_fmt_mult(m)}' for t, m in w['weak'])}")
    if w["resist"]:
        print(f"  resist {', '.join(f'{t} {_fmt_mult(m)}' for t, m in w['resist'])}")
    if w["immune"]:
        print(f"  immune {', '.join(t for t, _ in w['immune'])}")
    print(f"  moves  {' '.join('#' + str(x) for x in mon.moves) or '—'}")
    if mon.status1:
        print(f"  status 0x{mon.status1:08x}")


def cmd_info(client, desc, args):
    print(f"{desc.name} ({desc.id}) — base {desc.base}, {desc.endianness}-endian")
    print(f"  type table: {desc.battle.type_table}")
    print("  symbols:")
    for name, addr in desc.symbols.items():
        print(f"    {name:18s} 0x{addr:08x}")
    b = desc.battle
    print(f"  battler stride: {b.stride} bytes  (player={b.player_battler}, opponent={b.opponent_battler}, count={b.battler_count})")
    print("  fields:")
    for name, spec in b.fields.items():
        suffix = f" x{spec.count}" if spec.count > 1 else ""
        print(f"    {name:10s} off=0x{spec.offset:02x} size={spec.size}{suffix}")


def cmd_status(client, desc, args):
    print(f"version: {client.version()}")
    st = client.status()
    print(f"status : {st['raw']}")
    if st["system"]:
        print(f"  system={st['system']} content={st['content']} crc={st['crc']}")


def cmd_dump(client, desc, args):
    addr = int(args.address, 16)
    data = client.read_memory(addr, args.length)
    for i in range(0, len(data), 16):
        row = data[i:i + 16]
        hexs = " ".join(f"{b:02x}" for b in row)
        print(f"0x{addr + i:08x}  {hexs}")


def cmd_decode(client, desc, args):
    raw = "".join(args.hex).replace("0x", "").replace(" ", "").replace("\n", "")
    buf = bytes.fromhex(raw)
    need = max(spec.offset + spec.size * spec.count for spec in desc.battle.fields.values())
    if len(buf) < need:
        print(f"ERROR: buffer is {len(buf)} bytes, need at least {need} for {desc.id}", file=sys.stderr)
        sys.exit(1)
    print_mon(parse_battler(buf, desc, 0, "decoded"))


def cmd_live(client, desc, args):
    print(f"polling {desc.name} on {client.host}:{client.port} (Ctrl-C to stop)")
    last_sig = None
    last_in_battle = None
    while True:
        try:
            active, flags = in_battle(client, desc)
            if not active:
                if last_in_battle is not False:
                    print("… not in battle")
                last_in_battle = False
                last_sig = None
                time.sleep(0.25)
                continue
            last_in_battle = True
            mons = read_battlers(client, desc)
            sig = tuple((m.species, m.hp, m.level) for m in mons.values())
            if sig != last_sig:
                print(f"\n=== battle (flags=0x{flags:08x}) ===")
                for mon in mons.values():
                    print_mon(mon)
                last_sig = sig
        except (RetroArchError, OSError) as exc:
            print(f"… read error: {exc}")
            time.sleep(0.5)
        time.sleep(args.interval)


def cmd_battle(client, desc, args):
    flag_addr = desc.symbol("gBattleTypeFlags")
    flag = int.from_bytes(client.read_memory(flag_addr, 4), "little")
    state = "in battle" if flag else "not in battle"
    print(f"gBattleTypeFlags @ 0x{flag_addr:08x} = 0x{flag:08x} ({state})")
    for mon in read_battlers(client, desc).values():
        print_mon(mon)


def cmd_findmon(client, desc, args):
    start, end = int(args.start, 16), int(args.end, 16)
    print(f"scanning 0x{start:08x}-0x{end:08x} for HP={args.hp} Lv={args.level} maxHP={args.maxhp} ...")
    data = client.read_memory(start, end - start)
    hits = find_battle_mon(data, start, args.hp, args.level, args.maxhp)
    if not hits:
        print("no match — re-check the on-screen values, damage your lead for a non-round HP, or widen --start/--end")
        return
    need = max(spec.offset + spec.size * spec.count for spec in desc.battle.fields.values())
    for n, hp_addr in enumerate(hits, 1):
        base_nat, base_pak = hp_addr - 0x2A, hp_addr - 0x29
        print(f"\nmatch #{n}: hp-field @ 0x{hp_addr:08x}")
        print(f"  gBattleMons[0] base -> 0x{base_nat:08x} (natural)  |  0x{base_pak:08x} (packed)")
        off = base_nat - start
        if off >= 0:
            try:
                print_mon(parse_battler(data[off:off + need], desc, 0, "candidate"))
            except Exception as exc:
                print(f"  natural decode failed: {exc}")
            print("  raw[base..+0x60]: " + " ".join(f"{b:02x}" for b in data[off:off + 0x60]))


def cmd_automap(client, desc, args):
    if args.dump:
        with open(args.dump, "rb") as fh:
            data = fh.read()
        base_addr = int(args.base, 16)
        print(f"loaded {len(data)} bytes from {args.dump} (base 0x{base_addr:08x})")
    else:
        base_addr, end = int(args.start, 16), int(args.end, 16)
        print(f"scanning 0x{base_addr:08x}-0x{end:08x} ...")
        data = client.read_memory(base_addr, end - base_addr)
    results = automap_scan(data, args.hp, args.level, args.maxhp, args.opp_level)
    if not results:
        print("no plausible gBattleMons found — re-check HP/level/maxHP or widen --start/--end")
        return
    for r in results:
        base_abs = base_addr + r["base_index"]
        hp_off = r["hp_off"]
        align = "natural" if hp_off == 0x2A else "packed"
        fields = build_field_map(desc, hp_off)
        need = max(s.offset + s.size * s.count for s in fields.values())
        print(f"\n=== gBattleMons[0] @ 0x{base_abs:08x}  ({align}, hp_off=0x{hp_off:02x}) ===")
        print_mon(parse_battler(data[r["base_index"]:r["base_index"] + need], desc, 0, "player", fields))
        stride = r["stride"]
        if stride:
            opp_idx = r["base_index"] + stride
            print(f"\n  battler stride = {stride} (0x{stride:02x})  opponent @ 0x{base_abs + stride:08x}")
            print_mon(parse_battler(data[opp_idx:opp_idx + need], desc, 1, "opponent", fields))
        else:
            print("\n  stride not found — pass --opp-level <n> or check you are in a battle")
        print("\n  --- descriptor patch (data/games/pokemon_lazarus.json) ---")
        print(f'    symbols.gBattleMons   = "0x{base_abs:08x}"')
        print(f'    battle.battler_stride = {stride if stride else "<unknown>"}')
        print(f'    battle.alignment      = "{align}"')
        if hp_off != 0x2A:
            print(f'    packed offsets: hp=0x{hp_off:02x} level=0x{hp_off + 2:02x} maxHP=0x{hp_off + 4:02x} status1=0x{hp_off + 0x26:02x}')


COMMANDS = {
    "info": cmd_info,
    "status": cmd_status,
    "dump": cmd_dump,
    "decode": cmd_decode,
    "battle": cmd_battle,
    "live": cmd_live,
    "findmon": cmd_findmon,
    "automap": cmd_automap,
}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--game", default="lazarus", help="descriptor name (lazarus, emerald) or path to a JSON")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=55355)
    p.add_argument("--interval", type=float, default=0.1, help="live poll interval seconds")
    p.add_argument("--transport", choices=["udp", "tcp", "socks"], default="udp",
                   help="udp=direct (on-device); socks=via host SOCKS bridge + socat relay")
    p.add_argument("--socks-port", type=int, default=None, dest="socks_port",
                   help="host SOCKS proxy port (default $CLAUDE_CODE_HOST_SOCKS_PROXY_PORT)")
    p.add_argument("--relay-port", type=int, default=55356, dest="relay_port",
                   help="host socat TCP port forwarding to RetroArch UDP 55355")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("info")
    sub.add_parser("status")
    sub.add_parser("live")
    sub.add_parser("battle")
    fm = sub.add_parser("findmon")
    fm.add_argument("--hp", type=int, required=True)
    fm.add_argument("--level", type=int, required=True)
    fm.add_argument("--maxhp", type=int, required=True)
    fm.add_argument("--start", default="02000000")
    fm.add_argument("--end", default="02040000")
    am = sub.add_parser("automap")
    am.add_argument("--hp", type=int, required=True)
    am.add_argument("--level", type=int, required=True)
    am.add_argument("--maxhp", type=int, required=True)
    am.add_argument("--opp-level", type=int, default=None, dest="opp_level")
    am.add_argument("--start", default="02000000")
    am.add_argument("--end", default="02040000")
    am.add_argument("--dump", default=None, help="read a raw dump file instead of live RetroArch")
    am.add_argument("--base", default="02000000", help="base address of the --dump file")
    d = sub.add_parser("dump")
    d.add_argument("address", help="hex address, e.g. 02024084")
    d.add_argument("length", type=int)
    dec = sub.add_parser("decode")
    dec.add_argument("hex", nargs="+")
    args = p.parse_args(argv)

    desc = resolve_descriptor(args.game)
    client = RetroArchClient(args.host, args.port,
                             timeout=5.0 if args.transport != "udp" else 1.0,
                             transport=args.transport, socks_port=args.socks_port,
                             relay_port=args.relay_port)
    try:
        COMMANDS[args.cmd](client, desc, args)
    except KeyboardInterrupt:
        print("\nstopped")
    except (RetroArchError, OSError) as exc:
        print(f"ERROR: {exc} (is RetroArch running with Network Commands enabled?)", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
