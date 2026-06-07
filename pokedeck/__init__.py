"""poke-deck: live Pokémon battle-info reader for RetroArch.

Reusable core shared by the dev CLI (tools) and the Decky plugin backend.
Data-driven: per-game memory maps live in data/games/*.json so adding a game
is a descriptor + static tables, no code changes.
"""

__version__ = "0.1.0"
