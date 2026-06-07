"""SOCKS5 client for reaching host-loopback services through the Claude Code
host-bridge proxy (CLAUDE_CODE_HOST_SOCKS_PROXY_PORT).

The sandbox network namespace can't reach host loopback directly, but the host
SOCKS5 proxy egresses on the host side, so its 127.0.0.1 is the host's loopback.
It supports TCP CONNECT (verified) but NOT UDP ASSOCIATE — so reaching
RetroArch's UDP command interface needs a host-side socat TCP<->UDP relay that we
CONNECT to through this proxy.
"""
import os
import socket
import struct


def host_socks_port():
    return int(os.environ.get("CLAUDE_CODE_HOST_SOCKS_PROXY_PORT", "46459"))


def socks5_connect(dst_host, dst_port, proxy_host="127.0.0.1", proxy_port=None,
                   timeout=5.0, retries=3):
    """Open a TCP tunnel to dst_host:dst_port (on the host) via the SOCKS5 proxy.

    Retries the proxy connect — the host proxy is occasionally absent in a given
    sandbox command's namespace.
    """
    if proxy_port is None:
        proxy_port = host_socks_port()
    last = None
    for _ in range(retries):
        try:
            sock = socket.create_connection((proxy_host, proxy_port), timeout=timeout)
        except OSError as exc:
            last = exc
            continue
        try:
            sock.settimeout(timeout)
            sock.sendall(b"\x05\x01\x00")
            if sock.recv(2) != b"\x05\x00":
                raise OSError("SOCKS5 no-auth handshake rejected")
            sock.sendall(b"\x05\x01\x00\x01" + socket.inet_aton(dst_host) + struct.pack("!H", dst_port))
            rep = sock.recv(10)
            if len(rep) < 2 or rep[1] != 0x00:
                raise OSError(f"SOCKS5 CONNECT to {dst_host}:{dst_port} failed (rep={rep!r})")
            return sock
        except OSError as exc:
            sock.close()
            last = exc
    raise OSError(f"socks5_connect failed after {retries} tries: {last}")


if __name__ == "__main__":
    import sys
    host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 5173
    sock = socks5_connect(host, port)
    sock.sendall(f"GET / HTTP/1.0\r\nHost: {host}\r\n\r\n".encode())
    print("first line:", sock.recv(256).decode("latin1").splitlines()[0])
    sock.close()
