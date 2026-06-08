"""PokeAPI augmentation: flavor text, evolution chain, dex metadata and extra
sprites for a National-Dex number. Stdlib-only urllib, results cached to disk so
it works offline after the first lookup and stays well under PokeAPI's rate
limits. The HTTP fetch is injectable (`fetch=`) so parsing is testable without
network. Battle-relevant data (stats/types/abilities/moves) comes from the ROM;
this is purely the reference/flavour layer.
"""
import json
import logging
import os
import ssl
import urllib.request
from urllib.error import HTTPError, URLError

_log = logging.getLogger(__name__)

# Decky's bundled Python on SteamOS can't locate the CA bundle (default context
# raises CERTIFICATE_VERIFY_FAILED), so point it at the system bundle explicitly.
_CA_CANDIDATES = (
    "/etc/ssl/certs/ca-certificates.crt",  # SteamOS / Arch / Debian
    "/etc/pki/tls/certs/ca-bundle.crt",    # Fedora / RHEL
    "/etc/ssl/cert.pem",                   # macOS / BSD
)


def _ssl_context():
    for path in _CA_CANDIDATES:
        if os.path.isfile(path):
            try:
                return ssl.create_default_context(cafile=path)
            except OSError:
                continue
    return ssl.create_default_context()


_SSL = _ssl_context()

_PKG = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(_PKG)
CACHE_DIR = os.environ.get("POKEDECK_CACHE_DIR", os.path.join(_REPO, "data", "cache", "pokeapi"))
BASE = "https://pokeapi.co/api/v2"
_TIMEOUT = 8.0


def _http_get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "poke-deck/1.0"})
    with urllib.request.urlopen(req, timeout=_TIMEOUT, context=_SSL) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _english(entries, key):
    for e in entries:
        if e.get("language", {}).get("name") == "en":
            return e.get(key)
    return None


def _evolution_names(chain):
    """Flatten the (possibly branching) evolution chain into ordered species names."""
    names = []

    def walk(node):
        name = (node.get("species") or {}).get("name")
        if name and name not in names:
            names.append(name)
        for nxt in node.get("evolves_to", []):
            walk(nxt)

    if chain:
        walk(chain)
    return names


def _cache_path(dex):
    return os.path.join(CACHE_DIR, f"{dex}.json")


def species_extra(dex, fetch=_http_get):
    """Slim reference payload for a National-Dex number, or None if unreachable.
    Cached to CACHE_DIR/<dex>.json after the first successful fetch."""
    try:
        dex = int(dex)
    except (TypeError, ValueError):
        return None
    if not 1 <= dex <= 1025:
        return None

    path = _cache_path(dex)
    if os.path.isfile(path):
        try:
            with open(path, encoding="utf-8") as fh:
                return json.load(fh)
        except (OSError, ValueError):
            pass

    try:
        poke = fetch(f"{BASE}/pokemon/{dex}/")
        spec = fetch(f"{BASE}/pokemon-species/{dex}/")
    except (URLError, HTTPError, ValueError, OSError, TimeoutError) as exc:
        _log.warning("pokeapi fetch failed for dex %s: %r", dex, exc)
        return None

    evolution = []
    chain_url = (spec.get("evolution_chain") or {}).get("url")
    if chain_url:
        try:
            evolution = _evolution_names((fetch(chain_url) or {}).get("chain"))
        except (URLError, HTTPError, ValueError, OSError, TimeoutError):
            evolution = []

    flavor = _english(spec.get("flavor_text_entries", []), "flavor_text")
    if flavor:
        flavor = " ".join(flavor.replace("­", "").split())

    sprites = poke.get("sprites", {}) or {}
    other = sprites.get("other", {}) or {}
    slim = {
        "dex": dex,
        "genus": _english(spec.get("genera", []), "genus"),
        "flavor": flavor,
        "height_m": round((poke.get("height") or 0) / 10.0, 1),
        "weight_kg": round((poke.get("weight") or 0) / 10.0, 1),
        "base_exp": poke.get("base_experience"),
        "capture_rate": spec.get("capture_rate"),
        "gender_rate": spec.get("gender_rate"),  # -1 = genderless, else female eighths
        "egg_groups": [g.get("name") for g in spec.get("egg_groups", [])],
        "evolution": evolution,
        "sprites": {
            "front": sprites.get("front_default"),
            "shiny": sprites.get("front_shiny"),
            "artwork": (other.get("official-artwork") or {}).get("front_default"),
            "home": (other.get("home") or {}).get("front_default"),
        },
    }

    try:
        os.makedirs(CACHE_DIR, exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(slim, fh)
    except OSError:
        pass
    return slim
