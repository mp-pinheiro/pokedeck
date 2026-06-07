"""RetroArch UDP network command client (READ_CORE_MEMORY, VERSION, GET_STATUS).

Reads the emulated system memory map the core exposes via libretro
SET_MEMORY_MAPS. Addresses are emulated-system addresses (GBA EWRAM 0x02000000,
IWRAM 0x03000000), not host buffer offsets. Enable in RetroArch via
network_cmd_enable=true (default UDP port 55355); use the mGBA core for GBA.
"""
import socket


class RetroArchError(Exception):
    pass


class RetroArchClient:
    def __init__(self, host="127.0.0.1", port=55355, timeout=1.0):
        self.host = host
        self.port = port
        self.timeout = timeout

    def _command(self, command, expect_reply=True, bufsize=8192):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(self.timeout)
        try:
            sock.sendto(command.encode("ascii"), (self.host, self.port))
            if not expect_reply:
                return None
            data, _ = sock.recvfrom(bufsize)
            return data.decode("ascii", errors="replace").strip()
        finally:
            sock.close()

    def version(self):
        return self._command("VERSION")

    def status(self):
        reply = self._command("GET_STATUS")
        info = {"raw": reply, "state": None, "system": None, "content": None, "crc": None}
        parts = reply.split(None, 2)
        if len(parts) >= 2:
            info["state"] = parts[1]
        if len(parts) == 3:
            segs = parts[2].split(",")
            if len(segs) >= 3:
                info["system"] = segs[0]
                info["content"] = ",".join(segs[1:-1])
                info["crc"] = segs[-1].replace("crc32=", "")
        return info

    def read_memory(self, address, num_bytes, chunk=256):
        """Read num_bytes from an emulated address, chunked to fit UDP datagrams."""
        out = bytearray()
        offset = 0
        while offset < num_bytes:
            n = min(chunk, num_bytes - offset)
            out += self._read_chunk(address + offset, n)
            offset += n
        return bytes(out)

    def _read_chunk(self, address, num_bytes):
        reply = self._command(f"READ_CORE_MEMORY {address:x} {num_bytes}")
        parts = reply.split()
        if len(parts) < 3 or parts[0] != "READ_CORE_MEMORY":
            raise RetroArchError(f"unexpected reply: {reply!r}")
        if parts[2] == "-1":
            raise RetroArchError(f"core read failed @ 0x{address:x}: {' '.join(parts[2:])}")
        return bytes(int(b, 16) for b in parts[2:])
