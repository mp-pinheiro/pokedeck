#!/usr/bin/env python3
"""Minimal TCP stand-in for `socat + RetroArch`, to verify the relay transport
offline (no host bridge needed). Answers READ_CORE_MEMORY/VERSION over TCP the
way socat would deliver RetroArch's UDP replies.
"""
import socket
import sys


def handle(conn):
    data = conn.recv(4096).decode("ascii", errors="replace").strip()
    parts = data.split()
    if parts and parts[0] == "READ_CORE_MEMORY":
        addr, n = parts[1], int(parts[2])
        canned = b"POKEMON EMERBPEE"[:n].ljust(n, b"\x00")
        reply = f"READ_CORE_MEMORY {addr} " + " ".join(f"{b:02x}" for b in canned)
        conn.sendall(reply.encode())
    elif parts and parts[0] == "VERSION":
        conn.sendall(b"1.21.0")
    conn.close()


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 55356
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("127.0.0.1", port))
    srv.listen(8)
    print(f"fake retroarch relay on 127.0.0.1:{port}", flush=True)
    while True:
        conn, _ = srv.accept()
        handle(conn)


if __name__ == "__main__":
    main()
