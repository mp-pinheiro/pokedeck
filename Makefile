# poke-deck — build and one-command deploy to a Steam Deck over SSH.
# Copy .env.example to .env and set DECK_HOST / DECK_PASSWORD, then `make deploy`.

ifneq (,$(wildcard .env))
include .env
export
endif

PLUGIN_NAME      = poke-deck
DECK_HOST       ?= steamdeck
DECK_USER       ?= deck
DECK_PORT       ?= 22
DECK_PLUGIN_DIR ?= /home/deck/homebrew/plugins/$(PLUGIN_NAME)
CEF_DEBUG_PORT  ?= 8081
DEBUG           ?= 1        # 1 = inject plugin.json "debug" flag (Decky auto-reload on deploy)
STAGE            = build/deploy
GAME            ?= lazarus

SSH   = ssh -p $(DECK_PORT) $(DECK_USER)@$(DECK_HOST)
SCP   = scp -P $(DECK_PORT)
# homebrew/plugins is root-owned: run privileged steps as `sudo -S` fed by sshpass.
SUDO  = sshpass -p '$(DECK_PASSWORD)' ssh -p $(DECK_PORT) $(DECK_USER)@$(DECK_HOST) "echo '$(DECK_PASSWORD)' | sudo -S"
DBG   = $(if $(filter 1 true yes,$(DEBUG)),--debug,)

.PHONY: all install web build stage deploy verify logs cef restart undeploy dev clean help
all: build

install:
	pnpm i

# Frontend dev: Python backend (hot-reload) + Vite dev server (HMR). Open the
# Vite URL it prints (http://localhost:5173), not :8420.
web:
	bash tools/dev.sh $(GAME)

build:
	pnpm run build                      # Decky frontend -> dist/index.js
	pnpm --filter @poke-deck/web build  # browser SPA   -> apps/web/dist
	bash tools/bundle.sh                # stage py_modules/ + defaults/{data,web}

stage: build
	python3 tools/stage.py --out $(STAGE) $(DBG)

# Build, ship the payload to /tmp, then sudo-install it into the plugin dir.
deploy: stage
	@echo "Deploying to $(DECK_USER)@$(DECK_HOST):$(DECK_PLUGIN_DIR) ..."
	$(SSH) "rm -rf /tmp/$(PLUGIN_NAME)-deploy && mkdir -p /tmp/$(PLUGIN_NAME)-deploy"
	$(SCP) -r $(STAGE)/. $(DECK_USER)@$(DECK_HOST):/tmp/$(PLUGIN_NAME)-deploy/
	$(SUDO) rm -rf '$(DECK_PLUGIN_DIR)'
	$(SUDO) mkdir -p '$(DECK_PLUGIN_DIR)'
	$(SUDO) cp -r /tmp/$(PLUGIN_NAME)-deploy/. '$(DECK_PLUGIN_DIR)/'
	$(SUDO) chown -R $(DECK_USER):$(DECK_USER) '$(DECK_PLUGIN_DIR)'
	$(SSH) "rm -rf /tmp/$(PLUGIN_NAME)-deploy"
	@echo "Deployed.$(if $(filter 1 true yes,$(DEBUG)), debug flag set -> Decky auto-reloads., run 'make restart' to reload.)"
	@echo "CEF DevTools: http://$(DECK_HOST):$(CEF_DEBUG_PORT)  (enable 'Allow Remote CEF Debugging' in Decky)"

verify:
	@$(SSH) "for f in main.py plugin.json package.json dist/index.js py_modules/pokedeck/server.py data/species_info.json web/index.html; do \
	  if [ -e '$(DECK_PLUGIN_DIR)/'\$$f ]; then echo \"ok   \$$f\"; else echo \"MISS \$$f\"; fi; done"

logs:
	$(SUDO) journalctl -u plugin_loader -f -n 80

cef:
	@echo "Enable 'Allow Remote CEF Debugging' in Decky -> Developer, then open:"
	@echo "  http://$(DECK_HOST):$(CEF_DEBUG_PORT)"
	@echo "Tabs: QuickAccess = the panel UI, SharedJSContext = the JS console/logs."

restart:
	$(SUDO) systemctl restart plugin_loader

undeploy:
	$(SUDO) rm -rf '$(DECK_PLUGIN_DIR)'
	@echo "Removed $(DECK_PLUGIN_DIR)"

dev: install deploy

clean:
	rm -rf $(STAGE) dist py_modules defaults

help:
	@echo "poke-deck workflow:"
	@echo "  make web       frontend dev: backend (hot-reload) + Vite HMR (open :5173)"
	@echo "  make deploy    build + push to the Deck (DEBUG=1 -> auto-reload)"
	@echo "  make verify    check the deployed files exist"
	@echo "  make logs      tail Decky loader logs"
	@echo "  make cef       print the CEF DevTools URL"
	@echo "  make restart   restart Decky (force reload)"
	@echo "  make undeploy  remove the plugin from the Deck"
	@echo "  make dev       install + deploy"
	@echo "  make clean     remove local build artifacts"
