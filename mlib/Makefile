SHELL := /bin/bash

PYTHON := .venv/bin/python
INTERACTIVE_DIR := SHAD/interactive
COMPOSE := docker compose
PYTHON_LINT_PATHS := generate_lecture.py generate_images.py SHAD/interactive/scripts

.PHONY: help
help:
	@printf "Available targets:\n"
	@printf "  setup-python      Install Python dev tools into .venv\n"
	@printf "  lint-python       Run ruff checks for maintained Python tooling\n"
	@printf "  lint-python-all   Run ruff checks for the whole repository\n"
	@printf "  format-python     Run ruff formatter\n"
	@printf "  lint-js           Run ESLint for SHAD/interactive\n"
	@printf "  format-js         Run ESLint autofix for SHAD/interactive\n"
	@printf "  test-js           Run Vitest model tests for SHAD/interactive\n"
	@printf "  lint              Run Python and JS linters\n"
	@printf "  interactive-dev   Run Vite dev server locally\n"
	@printf "  interactive-test  Run SHAD/interactive Vitest model tests\n"
	@printf "  interactive-build Build SHAD/interactive\n"
	@printf "  interactive-smoke Run Playwright smoke against local dev server\n"
	@printf "  interactive-quality Run lint, tests, build, and smoke\n"
	@printf "  mission-audit    Audit SHAD/interactive mission authoring quality\n"
	@printf "  bundle-budget    Check SHAD/interactive bundle size budgets\n"
	@printf "  compose-dev       Run Docker dev server with hot reload\n"
	@printf "  compose-prod      Build and run production container\n"
	@printf "  compose-down      Stop interactive compose services\n"

.PHONY: setup-python
setup-python:
	$(PYTHON) -m pip install -r requirements-dev.txt

.PHONY: lint-python
lint-python:
	$(PYTHON) -m ruff check $(PYTHON_LINT_PATHS)

.PHONY: lint-python-all
lint-python-all:
	$(PYTHON) -m ruff check .

.PHONY: format-python
format-python:
	$(PYTHON) -m ruff format .

.PHONY: lint-js
lint-js:
	cd $(INTERACTIVE_DIR) && npm run lint

.PHONY: format-js
format-js:
	cd $(INTERACTIVE_DIR) && npm run lint:fix

.PHONY: test-js
test-js:
	cd $(INTERACTIVE_DIR) && npm run test

.PHONY: lint
lint: lint-python lint-js

.PHONY: interactive-dev
interactive-dev:
	cd $(INTERACTIVE_DIR) && npm run dev -- --host 127.0.0.1

.PHONY: interactive-test
interactive-test: test-js

.PHONY: interactive-build
interactive-build:
	cd $(INTERACTIVE_DIR) && npm run build

.PHONY: interactive-smoke
interactive-smoke:
	setsid bash -c 'cd $(INTERACTIVE_DIR) && exec npm run dev -- --host 127.0.0.1' & \
	server_pid=$$!; \
	trap 'kill -TERM -$$server_pid 2>/dev/null || true' EXIT; \
	$(PYTHON) $(INTERACTIVE_DIR)/scripts/wait_for_port.py --port 5173 --timeout 45; \
	$(PYTHON) $(INTERACTIVE_DIR)/scripts/smoke_playwright.py

.PHONY: interactive-quality
interactive-quality: lint-python lint-js test-js interactive-build interactive-smoke

.PHONY: mission-audit
mission-audit:
	$(PYTHON) $(INTERACTIVE_DIR)/scripts/audit_mission_quality.py

.PHONY: bundle-budget
bundle-budget:
	$(PYTHON) $(INTERACTIVE_DIR)/scripts/check_bundle_budget.py --no-build

.PHONY: compose-dev
compose-dev:
	$(COMPOSE) -f $(INTERACTIVE_DIR)/docker-compose.dev.yml up --build

.PHONY: compose-prod
compose-prod:
	$(COMPOSE) -f $(INTERACTIVE_DIR)/docker-compose.yml up --build -d

.PHONY: compose-down
compose-down:
	$(COMPOSE) -f $(INTERACTIVE_DIR)/docker-compose.yml down --remove-orphans
	$(COMPOSE) -f $(INTERACTIVE_DIR)/docker-compose.dev.yml down --remove-orphans
