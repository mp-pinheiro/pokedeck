#!/usr/bin/env python3
"""Probe RetroArch's UDP network command interface (READ_CORE_MEMORY, etc.).

Dev/test harness for the poke-deck battle-info tool: validates the live
memory-read pipeline against a running RetroArch before any Decky code exists.

Enable in RetroArch: Settings > Network > Network Commands (network_cmd_enable),
default UDP port 55355. Use the mGBA core for accurate GBA memory maps.

Examples:
  python3 ra_probe.py version
  python3 ra_probe.py status
  python3 ra_probe.py read 02000000 16     # GBA EWRAM, 16 bytes
"""
import argparse
import socket
import sys

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 55355


def send_command(host, port, command, timeout=1.0, bufsize=8192):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)
    try:
        sock.sendto(command.encode("ascii"), (host, port))
        data, _ = sock.recvfrom(bufsize)
        return data.decode("ascii", errors="replace").strip()
    finally:
        sock.close()


def read_core_memory(host, port, address, num_bytes, **kw):
    reply = send_command(host, port, f"READ_CORE_MEMORY {address:x} {num_bytes}", **kw)
    parts = reply.split()
    if len(parts) < 3 or parts[0] != "READ_CORE_MEMORY":
        raise RuntimeError(f"unexpected reply: {reply!r}")
    if parts[2] == "-1":
        raise RuntimeError(f"core read failed @ {parts[1]}: {' '.join(parts[2:])}")
    return bytes(int(b, 16) for b in parts[2:])


def parse_addr(s):
    return int(s, 16)  # accepts "02000000" or "0x02000000"


def cmd_version(args):
    print(send_command(args.host, args.port, "VERSION"))


def cmd_status(args):
    print(send_command(args.host, args.port, "GET_STATUS"))


def cmd_read(args):
    addr = parse_addr(args.address)
    data = read_core_memory(args.host, args.port, addr, args.length)
    print(f"addr=0x{addr:08x} len={len(data)}")
    print(" ".join(f"{b:02x}" for b in data))
    if len(data) >= 2:
        print(f"u16[0]={int.from_bytes(data[0:2], 'little')}")
    if len(data) >= 4:
        print(f"u32[0]={int.from_bytes(data[0:4], 'little')}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--host", default=DEFAULT_HOST)
    p.add_argument("--port", type=int, default=DEFAULT_PORT)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("version").set_defaults(func=cmd_version)
    sub.add_parser("status").set_defaults(func=cmd_status)
    r = sub.add_parser("read")
    r.add_argument("address", help="emulated address, hex (e.g. 02000000 = GBA EWRAM)")
    r.add_argument("length", type=int, help="number of bytes")
    r.set_defaults(func=cmd_read)
    args = p.parse_args()
    try:
        args.func(args)
    except socket.timeout:
        print("ERROR: no reply (is RetroArch running with Network Commands enabled?)", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
