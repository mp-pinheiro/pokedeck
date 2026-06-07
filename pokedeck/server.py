"""Stdlib-only HTTP + SSE server that reuses the pokedeck reader to push live
battle payloads to a browser. No third-party deps, so the same Hub/Session/
make_server can be embedded in the Decky backend without bundling anything
(see main.py). SSE is server->push only (our exact case) and EventSource
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
from .descriptor import list_games, resolve_game
from .party import read_party
from .payload import battle_payload, party_payload
from .pokeapi import species_extra
from .pokedata import PokeData
from .retroarch import RetroArchClient, RetroArchError

DEFAULT_WEB_DIR = os.environ.get(
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


class Session:
    """The current game/reader, swappable at runtime via POST /api/game. PokeData
    is shared across games (all use the same National-Dex name numbering)."""

    def __init__(self, client, descriptor, pd, game):
        self.client = client
        self.pd = pd
        self._descriptor = descriptor
        self._game = game  # canonical key (filename stem); matches list_games ids
        self._lock = threading.Lock()

    @property
    def descriptor(self):
        with self._lock:
            return self._descriptor

    @property
    def game(self):
        with self._lock:
            return self._game

    def set_game(self, game):
        descriptor, stem = resolve_game(game)
        with self._lock:
            self._descriptor = descriptor
            self._game = stem
        return descriptor


def read_payload(session):
    descriptor = session.descriptor
    try:
        in_battle, mons = read_battle(session.client, descriptor)
    except (RetroArchError, OSError):
        return dict(DISCONNECTED)
    payload = {"connected": True, "in_battle": in_battle}
    if in_battle:
        payload.update(battle_payload(mons, session.pd))
    if "gPlayerParty" in descriptor.symbols:
        payload["party"] = _read_party(session.client, descriptor, "gPlayerParty", session.pd)
    if in_battle and "gEnemyParty" in descriptor.symbols:
        payload["opponent_party"] = _read_party(session.client, descriptor, "gEnemyParty", session.pd)
    return payload


def _read_party(client, descriptor, symbol, pd):
    try:
        return party_payload(read_party(client, descriptor.symbol(symbol)), pd)
    except (RetroArchError, OSError):
        return []


def poll_loop(hub, session, interval):
    import sys
    last = None
    while True:
        try:
            payload = read_payload(session)
        except Exception as exc:  # never let the poll thread die
            print(f"poke-deck poll error: {exc!r}", file=sys.stderr)
            payload = dict(DISCONNECTED)
        if payload != last:
            last = payload
            hub.publish(payload)
        time.sleep(interval)


def make_handler(hub, session, web_dir):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def _send(self, body, ctype, status=200):
            self.send_response(status)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _json(self, obj, status=200):
            self._send(json.dumps(obj).encode(), "application/json", status)

        def _info(self):
            return {
                "game": session.game,
                "name": session.descriptor.name,
                "games": list_games(),
                "connected": hub.latest.get("connected", False),
                "in_battle": hub.latest.get("in_battle", False),
            }

        def do_GET(self):
            path = self.path.split("?", 1)[0]
            if path == "/events":
                return self._sse()
            if path == "/api/state":
                return self._json(hub.latest)
            if path == "/api/info":
                return self._json(self._info())
            if path.startswith("/api/species/"):
                try:
                    dex = int(path.rsplit("/", 1)[1])
                except (ValueError, IndexError):
                    return self._json({"error": "bad dex"}, 400)
                return self._json(species_extra(dex))  # null when unreachable; cached on success
            rel = path.lstrip("/") or "index.html"
            root = os.path.realpath(web_dir)
            full = os.path.realpath(os.path.join(root, rel))
            if not (full == root or full.startswith(root + os.sep)) or not os.path.isfile(full):
                full = os.path.join(root, "index.html")  # SPA fallback
            try:
                with open(full, "rb") as fh:
                    body = fh.read()
            except OSError:
                return self._send(b"poke-deck: web app not built (pnpm --filter @poke-deck/web build)",
                                  "text/plain", 503)
            self._send(body, _CTYPES.get(os.path.splitext(full)[1], "application/octet-stream"))

        def do_POST(self):
            if self.path.split("?", 1)[0] != "/api/game":
                return self.send_error(404)
            try:
                length = int(self.headers.get("Content-Length", 0))
                game = json.loads(self.rfile.read(length) or b"{}").get("game")
                if not isinstance(game, str):
                    raise ValueError("game must be a string")
                session.set_game(game)
            except (ValueError, TypeError, KeyError, OSError) as exc:
                return self._json({"error": str(exc)}, 400)
            self._json(self._info())

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


def make_server(hub, session, port=8420, host="127.0.0.1", web_dir=DEFAULT_WEB_DIR):
    return ThreadingHTTPServer((host, port), make_handler(hub, session, web_dir))


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

    descriptor, stem = resolve_game(args.game)
    session = Session(build_client(args), descriptor, PokeData(), stem)
    hub = Hub()
    threading.Thread(target=poll_loop, args=(hub, session, args.interval), daemon=True).start()
    httpd = make_server(hub, session, args.port)
    print(f"poke-deck web on http://127.0.0.1:{args.port}  (game={session.descriptor.name}, ra-transport={args.transport})")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
