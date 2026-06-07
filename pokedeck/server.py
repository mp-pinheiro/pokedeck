"""Standalone HTTP + SSE server that reuses the pokedeck reader to push live
battle payloads to a browser. Stdlib only (no third-party deps) so the same
Hub/poll logic can later be embedded in the Decky backend without bundling
anything. SSE is server->push only (exactly our case) and EventSource
auto-reconnects; serving the SPA + SSE from one http://localhost origin avoids
mixed-content/CORS entirely.

  python3 -m pokedeck.server --game lazarus --port 8420
"""
import argparse
import json
import os
import queue
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .battle import read_battle
from .descriptor import resolve_descriptor
from .payload import battle_payload
from .pokedata import PokeData
from .retroarch import RetroArchClient, RetroArchError

WEB_DIR = os.environ.get(
    "POKEDECK_WEB_DIR",
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "apps", "web", "dist"),
)
DISCONNECTED = {"connected": False, "in_battle": False}

_CTYPES = {".html": "text/html", ".js": "text/javascript", ".css": "text/css",
           ".json": "application/json", ".svg": "image/svg+xml", ".ico": "image/x-icon"}


class Hub:
    """Holds the latest payload and fans it out to SSE subscriber queues."""

    def __init__(self):
        self._subs = set()
        self._lock = threading.Lock()
        self.latest = dict(DISCONNECTED)

    def publish(self, payload):
        self.latest = payload
        with self._lock:
            subs = list(self._subs)
        for q in subs:
            try:
                q.put_nowait(payload)
            except queue.Full:
                pass

    def subscribe(self):
        q = queue.Queue(maxsize=16)
        with self._lock:
            self._subs.add(q)
        return q

    def unsubscribe(self, q):
        with self._lock:
            self._subs.discard(q)


def poll_loop(hub, client, descriptor, pd, interval):
    last = None
    while True:
        try:
            in_battle, mons = read_battle(client, descriptor)
            payload = {"connected": True, "in_battle": in_battle}
            if in_battle:
                payload.update(battle_payload(mons, pd))
        except (RetroArchError, OSError):
            payload = dict(DISCONNECTED)
        if payload != last:
            last = payload
            hub.publish(payload)
        time.sleep(interval)


def make_handler(hub):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def _send(self, body, ctype, status=200):
            self.send_response(status)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            path = self.path.split("?", 1)[0]
            if path == "/events":
                return self._sse()
            if path == "/api/state":
                return self._send(json.dumps(hub.latest).encode(), "application/json")
            # static SPA + fallback to index.html for client routes
            rel = path.lstrip("/") or "index.html"
            full = os.path.normpath(os.path.join(WEB_DIR, rel))
            if not full.startswith(WEB_DIR) or not os.path.isfile(full):
                full = os.path.join(WEB_DIR, "index.html")
            try:
                with open(full, "rb") as fh:
                    body = fh.read()
            except OSError:
                return self._send(b"poke-deck: web app not built (run pnpm --filter @poke-deck/web build)",
                                  "text/plain", 503)
            self._send(body, _CTYPES.get(os.path.splitext(full)[1], "application/octet-stream"))

        def _sse(self):
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.end_headers()
            q = hub.subscribe()
            try:
                self._event(hub.latest)
                while True:
                    try:
                        self._event(q.get(timeout=15))
                    except queue.Empty:
                        self.wfile.write(b": ping\n\n")
                        self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError):
                pass
            finally:
                hub.unsubscribe(q)

        def _event(self, payload):
            self.wfile.write(b"data: " + json.dumps(payload).encode() + b"\n\n")
            self.wfile.flush()

    return Handler


def build_client(args):
    return RetroArchClient(
        args.ra_host, args.ra_port,
        timeout=5.0 if args.transport != "udp" else 1.0,
        transport=args.transport, socks_port=args.socks_port, relay_port=args.relay_port,
    )


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--game", default="lazarus")
    p.add_argument("--ra-host", default="127.0.0.1")
    p.add_argument("--ra-port", type=int, default=55355)
    p.add_argument("--transport", choices=["udp", "tcp", "socks"], default="udp")
    p.add_argument("--socks-port", type=int, default=None)
    p.add_argument("--relay-port", type=int, default=55356)
    p.add_argument("--interval", type=float, default=0.25)
    p.add_argument("--port", type=int, default=8420, help="web server port (avoid Decky's 1337/8080)")
    args = p.parse_args()

    desc = resolve_descriptor(args.game)
    hub = Hub()
    threading.Thread(target=poll_loop, args=(hub, build_client(args), desc, PokeData(), args.interval),
                     daemon=True).start()
    httpd = ThreadingHTTPServer(("127.0.0.1", args.port), make_handler(hub))
    print(f"poke-deck web on http://127.0.0.1:{args.port}  (game={desc.name}, ra-transport={args.transport})")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
