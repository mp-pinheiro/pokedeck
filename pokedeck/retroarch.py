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
    def __init__(self, host="127.0.0.1", port=55355, timeout=1.0,
                 transport="udp", socks_port=None, relay_host="127.0.0.1", relay_port=55356):
        self.host = host
        self.port = port
        self.timeout = timeout
        # transport: "udp" = direct (on-device); "tcp"/"socks" = via a host-side
        # socat TCP<->UDP relay, reached directly ("tcp") or through the Claude
        # Code host SOCKS bridge ("socks") so a sandboxed process can reach it.
        self.transport = transport
        self.socks_port = socks_port
        self.relay_host = relay_host
        self.relay_port = relay_port

    def _command(self, command, expect_reply=True, bufsize=8192):
        if self.transport == "udp":
            return self._command_udp(command, expect_reply, bufsize)
        return self._command_relay(command, expect_reply)

    def _command_udp(self, command, expect_reply=True, bufsize=8192):
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

    def _open_relay(self):
        if self.transport == "socks":
            from .socks import socks5_connect
            return socks5_connect(self.relay_host, self.relay_port,
                                  proxy_port=self.socks_port, timeout=self.timeout)
        return socket.create_connection((self.relay_host, self.relay_port), timeout=self.timeout)

    def _command_relay(self, command, expect_reply=True):
        import select
        sock = self._open_relay()
        sock.settimeout(self.timeout)
        try:
            sock.sendall(command.encode("ascii"))
            if not expect_reply:
                return None
            data = sock.recv(65536)
            while True:  # one relayed UDP datagram may arrive as >1 TCP chunk
                ready, _, _ = select.select([sock], [], [], 0.05)
                if not ready:
                    break
                more = sock.recv(65536)
                if not more:
                    break
                data += more
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

    def read_memory(self, address, num_bytes, chunk=256, retries=3):
        """Read num_bytes from an emulated address in small chunks.

        Large reads can exceed RetroArch's reply buffer and get no response, so
        keep chunk small (<=256 verified working). Each chunk retries on timeout.
        """
        out = bytearray()
        offset = 0
        while offset < num_bytes:
            n = min(chunk, num_bytes - offset)
            out += self._read_chunk(address + offset, n, retries)
            offset += n
        return bytes(out)

    def _read_chunk(self, address, num_bytes, retries=3):
        for _ in range(retries):
            try:
                reply = self._command(f"READ_CORE_MEMORY {address:x} {num_bytes}")
            except socket.timeout:
                continue
            parts = reply.split()
            if len(parts) < 3 or parts[0] != "READ_CORE_MEMORY":
                raise RetroArchError(f"unexpected reply: {reply!r}")
            if parts[2] == "-1":
                raise RetroArchError(f"core read failed @ 0x{address:x}: {' '.join(parts[2:])}")
            try:
                data = bytes(int(b, 16) for b in parts[2:])
            except ValueError:
                raise RetroArchError(f"non-hex reply @ 0x{address:x}: {reply!r}")
            if len(data) != num_bytes:
                raise RetroArchError(f"short read @ 0x{address:x}: got {len(data)} of {num_bytes} bytes")
            return data
        raise TimeoutError(f"no reply after {retries} tries @ 0x{address:x}")
