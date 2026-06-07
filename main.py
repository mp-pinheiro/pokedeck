"""poke-deck Decky backend: polls RetroArch and pushes battle info to the QAM.

Runs on the Steam Deck alongside RetroArch, so it reads memory over direct UDP
(transport="udp"). The `pokedeck` package must be bundled into py_modules/ and
the data/ tables + game descriptors under the plugin dir (see tools/bundle.sh).
"""
import asyncio
import os

import decky

from pokedeck.battle import read_battle
from pokedeck.descriptor import GameDescriptor
from pokedeck.payload import battle_payload
from pokedeck.pokedata import PokeData
from pokedeck.retroarch import RetroArchClient, RetroArchError

DATA_DIR = os.path.join(decky.DECKY_PLUGIN_DIR, "data")
NOT_CONNECTED = {"connected": False, "in_battle": False}


class Plugin:
    async def get_snapshot(self) -> dict:
        """Frontend pulls the latest state on QAM open (no waiting for a poll)."""
        return self._latest

    async def set_interval(self, seconds: float) -> bool:
        self._interval = max(0.2, float(seconds))
        return True

    def _read_once(self) -> dict:
        try:
            in_battle, mons = read_battle(self._client, self._desc)
        except (RetroArchError, OSError):
            return NOT_CONNECTED
        if not in_battle:
            return {"connected": True, "in_battle": False}
        return {"connected": True, "in_battle": True, **battle_payload(mons, self._pd)}

    async def _poll_loop(self):
        decky.logger.info("poke-deck capture loop started")
        while True:
            try:
                payload = self._read_once()
                if payload != self._latest:
                    self._latest = payload
                    await decky.emit("battle_update", payload)
            except Exception:
                decky.logger.exception("poll error")
            await asyncio.sleep(self._interval)

    async def _main(self):
        self.loop = asyncio.get_event_loop()
        self._interval = 0.5
        self._latest = NOT_CONNECTED
        self._pd = PokeData(DATA_DIR)
        self._desc = GameDescriptor.load(os.path.join(DATA_DIR, "games", "pokemon_lazarus.json"))
        self._client = RetroArchClient(transport="udp")
        decky.logger.info("poke-deck loaded: game=%s species=%d moves=%d",
                          self._desc.id, len(self._pd.species), len(self._pd.moves))
        self._task = self.loop.create_task(self._poll_loop())

    async def _unload(self):
        task = getattr(self, "_task", None)
        if task is not None:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        decky.logger.info("poke-deck unloaded")
