# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

`make help` lists everything. Daily targets:

| Command                 | What it runs                                              |
| ----------------------- | --------------------------------------------------------- |
| `make install`          | venv + `pip install -e ".[dev]"` + pre-commit hooks        |
| `make run`              | `uvicorn app.main:app --reload --app-dir src`              |
| `make fmt`              | `ruff format` then `ruff check --fix`                      |
| `make lint`             | `ruff check` + `ruff format --check`                       |
| `make arch`             | `python scripts/check_architecture.py`                     |
| `make typecheck`        | `mypy` (strict, config in `pyproject.toml`)                |
| `make test`             | `pytest` with coverage, **fails under 90%**                |
| `make check`            | lint + arch + typecheck + test — run before pushing        |

Targeted test runs:

```bash
pytest -m unit --no-cov                       # fast loop, no HTTP
pytest -m integration --no-cov                # full ASGI app
pytest tests/unit/test_greeting_service.py::test_greets_in_each_locale
pytest -k locale -vv
pytest --cov-report=html                      # htmlcov/index.html
```

The `Makefile` is POSIX-only (`SHELL := /bin/bash`, `.venv/bin/...`). On Windows
run the underlying tools directly (`.venv\Scripts\pytest`, `ruff`, `mypy`,
`python scripts/check_architecture.py`) — the commands are identical, only the
venv path differs.

## Architecture

Clean architecture with dependencies pointing inwards:
`api → services → domain ← infrastructure`, wired in `core/container.py`.

**This is mechanically enforced.** `scripts/check_architecture.py` parses the AST
of every module under `src/app` and fails on forbidden imports; it runs in
`make check`, in a pre-commit hook, in CI, and again from
`tests/unit/test_architecture.py`. The rules:

- `domain/` may import nothing from `api`, `services`, `infrastructure`, `core`,
  `schemas`, `middleware`, and no `fastapi`/`starlette`/`pydantic`/`uvicorn`.
- `services/` may import only `domain` (no `infrastructure`, no framework).
- `infrastructure/` may import only `domain`.

If a change requires breaking a rule, the design is wrong — rework it rather
than editing the forbidden lists.

### Ports and dependency injection

Every abstraction is a `typing.Protocol` in `domain/ports.py` (`Clock`,
`GreetingTemplateRepository`, `GreetingFormatter`, `FormatterResolver`,
`GreetingUseCase`). Adapters in `infrastructure/` never import the protocol —
structural typing means mypy checks conformance at the injection site, and
`@runtime_checkable` lets `tests/unit/test_infrastructure.py` assert it.

Collaborators arrive through keyword-only constructor arguments typed as ports.
`core/container.py::build_container` is the **only** module allowed to name a
concrete class. There is no DI framework and no `app.dependency_overrides`
machinery — `api/deps.py` pulls objects off `app.state.container` and exposes
them as `Annotated` dependency aliases (`GreetingServiceDep`, `SettingsDep`).

### Application wiring

`main.create_app(settings=None, container=None)` is a factory; the module-level
`app = create_app()` exists only for uvicorn. The container is attached to
`app.state` **eagerly, not inside the lifespan handler**, so transports that
never fire startup events still see a wired app.

Tests exploit this: `tests/conftest.py` builds a real `Container` with a
`FrozenClock` and passes it to `create_app()`. Prefer that over patching —
`unittest.mock` on first-party code is against the contribution rules.

### Cross-cutting behaviour

- Middleware is written as **raw ASGI classes**, not `BaseHTTPMiddleware`, because
  the latter runs in a separate task and breaks `ContextVar` propagation to
  endpoints. `RequestContextMiddleware` sets `request_id_ctx` (read by the
  logging filter and by error responses); `TimingMiddleware` adds
  `X-Process-Time-Ms`. Registration order in `create_app` is deliberate —
  middleware runs bottom-up, so request-id is outermost.
- All errors funnel through `core/errors.py`, which maps `DomainError` subclasses
  to status codes and renders RFC 9457 problem documents carrying the request id.
  **Endpoints must not contain try/except for domain errors** — raise from the
  service and add a mapping to `_STATUS_BY_ERROR` if a new status is needed.
- Everything is `async def`, even where nothing awaits, so adding real I/O later
  is not a signature-churning refactor.

## Conventions that will fail the build

- **No relative imports** (`ban-relative-imports = "all"`). Always `from app.x import y`.
- **No `print`** outside `scripts/` — use `logging`; output is structured JSON.
- **Timezone-aware datetimes only**, obtained from the `Clock` port, never
  `datetime.now()` (ruff `DTZ`).
- **mypy strict** over `src/app`, `tests`, and `scripts`. `Any` needs a comment.
- **Google-style docstrings** on public modules, classes, functions.
- Max cyclomatic complexity 8; max function args 6; line length 100.
- `TC001`/`TC002`/`TC003` are ignored on purpose — FastAPI and Pydantic resolve
  annotations at runtime, so signature imports must stay outside
  `if TYPE_CHECKING:` blocks. Do not "fix" them.
- Coverage must stay ≥ 90%; `filterwarnings = ["error"]` turns warnings into
  test failures.
- Commit messages and PR titles must be Conventional Commits (enforced by a
  `commit-msg` hook and by the `pr-hygiene` workflow).
- Every change gets a `CHANGELOG.md` entry under `## [Unreleased]`.

## Adding a locale (the open/closed path)

1. Add the pattern to `DEFAULT_TEMPLATES` in
   `infrastructure/repositories/in_memory.py`.
2. Only if it needs special rules, add a formatter class in
   `infrastructure/formatters/` and pass it to `FormatterRegistry` in
   `build_container`.
3. Add a case to `test_greets_in_each_locale`.

Never add a `match`/`if` on locale in a service or endpoint —
`tests/unit/test_open_closed_extension.py` registers a formatter from outside
the package specifically to keep this extensible-without-editing property honest.

## Reference docs

`docs/ARCHITECTURE.md` (layer table, request lifecycle, extension recipes,
deliberate trade-offs), `CONTRIBUTING.md` (workflow, definition of done, review
rules), `docs/adr/` (add an ADR for hard-to-reverse decisions).
