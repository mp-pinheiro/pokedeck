#!/usr/bin/env python3
"""Assemble a deployable Decky plugin payload from the built artifacts.

Run the two pnpm builds and tools/bundle.sh first (the Makefile does this), then:

  python3 tools/stage.py [--out build/deploy] [--debug]

Produces a directory with the exact on-Deck plugin layout:
  main.py package.json plugin.json README.md dist/ py_modules/ data/ web/

--debug injects the plugin.json "debug" flag so Decky auto-reloads the plugin on
deploy (remove for store submission — that's why the repo plugin.json stays clean).
"""
import argparse
import json
import os
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# (source relative to repo root, destination name in the payload)
LAYOUT = [
    ("main.py", "main.py"),
    ("package.json", "package.json"),
    ("README.md", "README.md"),
    ("dist", "dist"),              # Decky frontend bundle (index.js)
    ("py_modules", "py_modules"),  # the pokedeck python package
    ("defaults/data", "data"),     # species/move tables + game descriptors
    ("defaults/web", "web"),       # built browser SPA (served by the embedded server)
]


def _copy(src, dst):
    if os.path.isdir(src):
        shutil.copytree(src, dst, dirs_exist_ok=True)
    else:
        shutil.copy2(src, dst)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="build/deploy")
    ap.add_argument("--debug", action="store_true", help="set plugin.json debug flag (auto-reload)")
    args = ap.parse_args()

    out = os.path.join(ROOT, args.out)
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(out)

    missing = []
    for src, dst in LAYOUT:
        if dst == "plugin.json":
            continue
        srcp = os.path.join(ROOT, src)
        if not os.path.exists(srcp):
            missing.append(src)
            continue
        _copy(srcp, os.path.join(out, dst))
    if missing:
        raise SystemExit(f"missing build artifacts: {missing} — run `make build` first")

    with open(os.path.join(ROOT, "plugin.json"), encoding="utf-8") as fh:
        meta = json.load(fh)
    if args.debug and "debug" not in meta.get("flags", []):
        meta["flags"] = list(meta.get("flags", [])) + ["debug"]
    with open(os.path.join(out, "plugin.json"), "w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=2)

    print(f"staged plugin payload -> {args.out}  (debug flag: {'on' if args.debug else 'off'})")
    for name in sorted(os.listdir(out)):
        print("  ", name)


if __name__ == "__main__":
    main()
