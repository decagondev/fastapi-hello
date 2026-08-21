# Development entry points. Run `make help` for the list.
.DEFAULT_GOAL := help
SHELL := /bin/bash

VENV       := .venv
PY         := $(VENV)/bin/python
PIP        := $(VENV)/bin/pip
BIN        := $(VENV)/bin
SRC        := src tests
UVICORN    := $(BIN)/uvicorn
IMAGE      := fastapi-hello
PORT       ?= 8000

.PHONY: help
help: ## Show this help
	@grep -hE '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-14s\033[0m %s\n", $$1, $$2}'

# --- setup -----------------------------------------------------------------

.PHONY: venv
venv: ## Create the virtual environment
	@test -d $(VENV) || (command -v uv >/dev/null && uv venv $(VENV) || python3 -m venv $(VENV))

.PHONY: install
install: venv ## Install dev dependencies and git hooks
	@if command -v uv >/dev/null; then \
		VIRTUAL_ENV=$(VENV) uv pip install -e ".[dev]"; \
	else \
		$(PIP) install --upgrade pip && $(PIP) install -e ".[dev]"; \
	fi
	$(BIN)/pre-commit install --install-hooks
	$(BIN)/pre-commit install --hook-type commit-msg
	@echo "Ready. Try: make run"

.PHONY: lock
lock: ## Freeze the current environment to requirements.lock
	$(PIP) freeze --exclude-editable > requirements.lock

# --- running ---------------------------------------------------------------

.PHONY: run
run: ## Start the dev server with autoreload
	$(UVICORN) app.main:app --reload --app-dir src --host 127.0.0.1 --port $(PORT)

.PHONY: serve
serve: ## Start the server as it runs in production
	$(UVICORN) app.main:app --app-dir src --host 0.0.0.0 --port $(PORT) --workers 4

.PHONY: shell
shell: ## Open a Python REPL with the app importable
	$(PY) -i -c "from app.main import create_app; app = create_app(); print('`app` is ready')"

# --- quality ---------------------------------------------------------------

.PHONY: fmt
fmt: ## Format the code
	$(BIN)/ruff format $(SRC)
	$(BIN)/ruff check --fix $(SRC)

.PHONY: lint
lint: ## Lint and verify formatting
	$(BIN)/ruff check $(SRC)
	$(BIN)/ruff format --check $(SRC)

.PHONY: arch
arch: ## Verify the layering rules hold
	$(PY) scripts/check_architecture.py

.PHONY: typecheck
typecheck: ## Run mypy in strict mode
	$(BIN)/mypy

.PHONY: test
test: ## Run the test suite with coverage
	$(BIN)/pytest

.PHONY: test-unit
test-unit: ## Run only the fast unit tests
	$(BIN)/pytest -m unit --no-cov

.PHONY: test-integration
test-integration: ## Run only the integration tests
	$(BIN)/pytest -m integration --no-cov

.PHONY: cov
cov: ## Write a browsable HTML coverage report
	$(BIN)/pytest --cov-report=html
	@echo "Open htmlcov/index.html"

.PHONY: audit
audit: ## Check dependencies against known CVEs
	$(BIN)/pip-audit --strict .

.PHONY: hooks
hooks: ## Run every pre-commit hook over all files
	$(BIN)/pre-commit run --all-files

.PHONY: check
check: lint arch typecheck test ## Everything CI runs. Do this before pushing.
	@echo "All checks passed."

# --- docker ----------------------------------------------------------------

.PHONY: docker-build
docker-build: ## Build the container image
	docker build -t $(IMAGE):local .

.PHONY: docker-run
docker-run: docker-build ## Run the container locally
	docker run --rm -p $(PORT):8000 -e APP_HOST=0.0.0.0 $(IMAGE):local

.PHONY: up
up: ## Start via docker compose
	docker compose up --build

.PHONY: down
down: ## Stop docker compose
	docker compose down -v

# --- housekeeping ----------------------------------------------------------

.PHONY: clean
clean: ## Remove caches and build artefacts
	rm -rf build dist htmlcov .coverage coverage.xml junit.xml \
		.pytest_cache .mypy_cache .ruff_cache *.egg-info src/*.egg-info
	find . -type d -name __pycache__ -prune -exec rm -rf {} +

.PHONY: distclean
distclean: clean ## Also remove the virtual environment
	rm -rf $(VENV)
