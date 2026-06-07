#!/usr/bin/env python3
"""Probe RetroArch UDP through a SOCKS5 UDP-ASSOCIATE proxy (the host bridge).

The Claude Code sandbox can't reach host loopback directly, but the host SOCKS5
proxy (CLAUDE_CODE_HOST_SOCKS_PROXY_PORT, e.g. 46459) egresses on the host side,
so its 127.0.0.1 is the host loopback where RetroArch listens.

  python3 tools/socks_udp_test.py 46459 "READ_CORE_MEMORY 080000a0 16"
"""
import socket
import struct
import sys


def socks5_udp(proxy_host, proxy_port, dst_host, dst_port, payload, timeout=5.0):
    tcp = socket.create_connection((proxy_host, proxy_port), timeout=timeout)
    print(f"  [1] connected to socks proxy {proxy_host}:{proxy_port}")
    tcp.settimeout(timeout)
    tcp.sendall(b"\x05\x01\x00")  # VER5, 1 method, NO-AUTH
    if tcp.recv(2) != b"\x05\x00":
        raise RuntimeError("socks5 no-auth handshake rejected")
    print("  [2] no-auth handshake OK")
    tcp.sendall(b"\x05\x03\x00\x01\x00\x00\x00\x00\x00\x00")  # UDP ASSOCIATE
    rep = tcp.recv(10)
    if len(rep) < 10 or rep[1] != 0x00:
        raise RuntimeError(f"UDP ASSOCIATE rejected (proxy may not support UDP): {rep!r}")
    relay_ip = socket.inet_ntoa(rep[4:8])
    relay_port = struct.unpack("!H", rep[8:10])[0]
    if relay_ip == "0.0.0.0":
        relay_ip = proxy_host
    print(f"  [3] UDP ASSOCIATE OK, relay={relay_ip}:{relay_port}")
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp.settimeout(timeout)
    header = b"\x00\x00\x00\x01" + socket.inet_aton(dst_host) + struct.pack("!H", dst_port)
    udp.sendto(header + payload, (relay_ip, relay_port))
    print(f"  [4] sent {len(payload)}B to {dst_host}:{dst_port}, waiting for RetroArch...")
    data, _ = udp.recvfrom(65535)
    tcp.close()
    return data[10:]  # strip the 10-byte IPv4 SOCKS UDP header


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 46459
    cmd = sys.argv[2] if len(sys.argv) > 2 else "READ_CORE_MEMORY 080000a0 16"
    reply = socks5_udp("127.0.0.1", port, "127.0.0.1", 55355, cmd.encode("ascii"))
    print("  reply:", reply.decode("ascii", errors="replace"))
