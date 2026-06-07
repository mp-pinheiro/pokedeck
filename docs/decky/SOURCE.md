# Decky plugin-dev docs (mirror)

Local mirrors of the Steam Deck Homebrew **deckbrew** plugin-dev wiki, kept here
for offline reference during development. Canonical (and cleaner-rendering) source:
<https://wiki.deckbrew.xyz/en/plugin-dev>

Content © Steam Deck Homebrew, licensed CC BY-NC-SA (see each file's footer).
Pulled from the `deck-charge-scheduler` repo.

- **getting-started.md** — plugin structure, `plugin.json` / `package.json` fields, `definePlugin`, `SettingsManager`. Note the `"debug"` flag → auto-reload (used by `make deploy`).
- **plugin-dev.md** — section index.
- **env-vars.md** — `DECKY_PLUGIN_*` environment variables (runtime/settings/log dirs).
- **backend-frontend-communication.md** — `call()` / `addEventListener` between `main.py` and the frontend (the pattern `src/index.tsx` uses).
- **cef-debugging.md** — remote Chromium DevTools on `:8081` (`QuickAccess` tab = panel UI, `SharedJSContext` = JS console). See `make cef`.
- **route-patching.md** — patching Steam UI routes (not used here, but reference).
- **new-api-migration.md** — migrating to `@decky/api`.
- **review-and-testing.md** — store review + testing process (for submission).
- **submitting-plugins.md** — submitting to the plugin database.
