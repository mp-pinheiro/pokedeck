"""poke-deck Decky backend: polls RetroArch and pushes battle info to the QAM,
and ALSO hosts the same stdlib HTTP+SSE server (pokedeck.server) so a browser on
the LAN/Deck can show the battle simultaneously — one poll, two sinks.

Runs on the Steam Deck alongside RetroArch (reads memory over direct UDP). The
`pokedeck` package goes in py_modules/, data tables + descriptors under data/,
and the built web SPA under web/ (see tools/bundle.sh).
"""
import asyncio
import os
import threading

import decky

# descriptor.py / pokeapi.py read their dirs at import — point them at the bundled
# descriptors and a writable cache before importing anything from pokedeck.
os.environ.setdefault("POKEDECK_GAMES_DIR", os.path.join(decky.DECKY_PLUGIN_DIR, "data", "games"))
_RUNTIME = getattr(decky, "DECKY_PLUGIN_RUNTIME_DIR", None) or os.path.join(decky.DECKY_PLUGIN_DIR, "data")
os.environ.setdefault("POKEDECK_CACHE_DIR", os.path.join(_RUNTIME, "pokeapi"))

from pokedeck.descriptor import resolve_game
from pokedeck.pokeapi import species_extra
from pokedeck.pokedata import PokeData
from pokedeck.retroarch import RetroArchClient
from pokedeck.server import Hub, Session, make_server, read_payload

DATA_DIR = os.path.join(decky.DECKY_PLUGIN_DIR, "data")
WEB_DIR = os.path.join(decky.DECKY_PLUGIN_DIR, "web")
SERVER_PORT = 8420  # avoid Decky's 1337 and Steam CEF's 8080
NOT_CONNECTED = {"connected": False, "in_battle": False}


class Plugin:
    # Class-body defaults: Decky does not truly instantiate Plugin (self is the
    # class object, decky-loader #509), and the frontend may call methods before
    # _main finishes — so these must exist up front.
    _latest = dict(NOT_CONNECTED)
    _session = None
    _server = None
    _task = None

    async def get_snapshot(self) -> dict:
        return self._latest

    async def get_species(self, dex: int) -> dict:
        """Frontend-callable PokeAPI lookup (flavor/evolution/sprites), disk-cached.
        Runs the blocking fetch off the event loop. Returns {} when unreachable."""
        try:
            data = await asyncio.to_thread(species_extra, dex)
            if not data:
                decky.logger.warning("get_species(%s): no data (PokeAPI unreachable from the Deck?)", dex)
            return data or {}
        except Exception:
            decky.logger.exception("get_species failed")
            return {}

    async def set_game(self, game: str) -> dict:
        """Frontend-callable: switch the active game descriptor (QAM + browser)."""
        if self._session is None:
            return {"game": None}
        self._session.set_game(game)
        return {"game": self._session.game}

    async def _poll_loop(self):
        decky.logger.info("poke-deck capture loop started")
        while True:
            try:
                payload = read_payload(self._session)
                if payload != self._latest:
                    self._latest = payload
                    self._hub.publish(payload)          # browsers (SSE)
                    await decky.emit("battle_update", payload)  # QAM panel
            except Exception:
                decky.logger.exception("poll error")
            await asyncio.sleep(self._interval)

    async def _main(self):
        self.loop = asyncio.get_event_loop()
        self._interval = 0.5
        self._latest = dict(NOT_CONNECTED)
        pd = PokeData(DATA_DIR)
        desc, stem = resolve_game("pokemon_lazarus")
        self._session = Session(RetroArchClient(transport="udp"), desc, pd, stem)
        self._hub = Hub()
        self._server = None
        try:
            self._server = make_server(self._hub, self._session, port=SERVER_PORT, web_dir=WEB_DIR)
            threading.Thread(target=self._server.serve_forever, daemon=True).start()
            decky.logger.info("poke-deck web/SSE server on 127.0.0.1:%d", SERVER_PORT)
        except OSError as exc:
            decky.logger.warning("poke-deck web server not started (%s); QAM panel still works", exc)
        decky.logger.info("poke-deck loaded: game=%s species=%d", desc.id, len(pd.species))
        self._task = self.loop.create_task(self._poll_loop())

    async def _unload(self):
        server = getattr(self, "_server", None)
        if server is not None:
            server.shutdown()
        task = getattr(self, "_task", None)
        if task is not None:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        decky.logger.info("poke-deck unloaded")
