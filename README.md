# FastAPI Hello

[![CI](https://github.com/your-org/fastapi-hello/actions/workflows/ci.yml/badge.svg)](https://github.com/your-org/fastapi-hello/actions/workflows/ci.yml)
[![codecov](https://img.shields.io/badge/coverage-90%25%20min-brightgreen)](./pyproject.toml)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

A hello-world FastAPI service that is deliberately built like a production
system: layered architecture, dependency inversion throughout, strict typing,
full CI, and the contribution scaffolding a real repository needs.

It exists to be **cloned and gutted** — replace the greeting domain with your
own and the surrounding structure still holds.

---

## Table of contents

- [Quick start](#quick-start)
- [API](#api)
- [Architecture](#architecture)
- [How SOLID shows up here](#how-solid-shows-up-here)
- [Project layout](#project-layout)
- [Development workflow](#development-workflow)
- [Configuration](#configuration)
- [Testing](#testing)
- [Docker](#docker)
- [CI/CD](#cicd)
- [Contributing](#contributing)

---

## Quick start

Requires Python 3.11+. [`uv`](https://github.com/astral-sh/uv) is recommended
but plain `pip` works everywhere.

```bash
# 1. Clone and enter
git clone https://github.com/your-org/fastapi-hello.git
cd fastapi-hello

# 2. Install (uv)
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"

#    ...or with pip
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# 3. Install the git hooks
pre-commit install --install-hooks
pre-commit install --hook-type commit-msg

# 4. Run it
make run          # or: uvicorn app.main:app --reload --app-dir src
```

Then visit <http://127.0.0.1:8000/docs>.

```bash
curl "http://127.0.0.1:8000/api/v1/greetings/hello?name=Ada&locale=fr"
# {"recipient":"Ada","message":"Bonjour, Ada !","locale":"fr","created_at":"..."}
```

---

## API

| Method | Path                        | Description                              |
| ------ | --------------------------- | ---------------------------------------- |
| `GET`  | `/`                         | Service metadata                         |
| `GET`  | `/api/v1/health/live`       | Liveness probe                           |
| `GET`  | `/api/v1/health/ready`      | Readiness probe (checks dependencies)    |
| `GET`  | `/api/v1/greetings/hello`   | Greet `?name=`, optionally `?locale=`    |
| `POST` | `/api/v1/greetings`         | Greet from a JSON body                   |
| `GET`  | `/api/v1/greetings/locales` | List supported locales                   |
| `GET`  | `/docs` · `/redoc`          | Interactive documentation                |

Errors use a consistent [RFC 9457](https://www.rfc-editor.org/rfc/rfc9457)
style problem document:

```json
{
  "type": "https://httpstatuses.io/422",
  "title": "Unprocessable Entity",
  "status": 422,
  "code": "unsupported_locale",
  "detail": "Locale 'zz' is not supported. Supported locales: de, en, es, fr, ja.",
  "request_id": "9f2c...",
  "supported_locales": ["de", "en", "es", "fr", "ja"]
}
```

Every response carries `X-Request-ID` and `X-Process-Time-Ms`.

---

## Architecture

Dependencies point **inwards**. The domain is the centre and imports nothing
from the layers around it.

```
        HTTP
         │
    ┌────▼─────────────────────────────────────────┐
    │  api/          routing, DTO ↔ domain, deps   │
    ├────▼─────────────────────────────────────────┤
    │  services/     use cases, orchestration      │
    ├────▼─────────────────────────────────────────┤
    │  domain/       entities, ports, rules        │  ← no framework imports
    └────▲─────────────────────────────────────────┘
         │ implements ports
    ┌────┴─────────────────────────────────────────┐
    │  infrastructure/  repositories, clock,       │
    │                   formatters                 │
    └──────────────────────────────────────────────┘
                     ▲
          core/container.py wires it all together
```

The rule enforced by review (and by the import graph) is simple:
**`domain/` may not import `fastapi`, `pydantic`, or anything from
`infrastructure/`.** See [ARCHITECTURE.md](./docs/ARCHITECTURE.md) for the
long version and for how to add a feature.

---

## How SOLID shows up here

This is not a checklist bolted on afterwards — each principle is load-bearing:

| Principle | Where to look |
| --------- | ------------- |
| **S**ingle responsibility | `GreetingService` only orchestrates; rendering lives in formatters, storage in repositories, HTTP in endpoints, error→status mapping in `core/errors.py`. |
| **O**pen/closed | Add a locale by writing a new formatter and registering it in `FormatterRegistry`. `tests/unit/test_open_closed_extension.py` adds one from *outside* the package without editing a single existing line. |
| **L**iskov substitution | Every formatter honours the same contract with no extra preconditions, so `DefaultFormatter` and `JapaneseFormatter` are freely interchangeable — the registry's fallback relies on it. |
| **I**nterface segregation | `Clock`, `GreetingTemplateRepository`, `GreetingFormatter` and `GreetingUseCase` are separate one-or-two-method `Protocol`s. Nothing implements a method it doesn't need. |
| **D**ependency inversion | `GreetingService` receives ports through its constructor. The only module that knows about concrete classes is `core/container.py`. Tests inject a `FrozenClock` with zero mocking or monkeypatching. |

---

## Project layout

```
.
├── .github/
│   ├── ISSUE_TEMPLATE/          issue forms (bug, feature, docs, question)
│   ├── PULL_REQUEST_TEMPLATE/   alternative PR templates (bugfix, docs, release)
│   ├── workflows/               ci, codeql, dependency-review, release, labeler, stale
│   ├── CODEOWNERS
│   ├── PULL_REQUEST_TEMPLATE.md default PR template
│   ├── dependabot.yml
│   ├── labeler.yml
│   └── release-drafter.yml
├── docs/
│   ├── ARCHITECTURE.md          layer rules, extension recipes, ADR index
│   └── adr/0001-record-architecture-decisions.md
├── src/app/
│   ├── api/                     routers, dependency providers
│   ├── core/                    config, logging, container, error mapping
│   ├── domain/                  entities, ports, exceptions  (framework-free)
│   ├── infrastructure/          clock, repositories, formatters
│   ├── middleware/              request id, timing
│   ├── schemas/                 pydantic DTOs
│   ├── services/                use cases
│   ├── main.py                  application factory
│   └── __main__.py              `python -m app`
├── tests/
│   ├── unit/                    no I/O, no app instance
│   └── integration/             full ASGI app via httpx
├── CHANGELOG.md   CODE_OF_CONDUCT.md   CONTRIBUTING.md   SECURITY.md
├── Dockerfile     docker-compose.yml   Makefile
└── pyproject.toml  .pre-commit-config.yaml  .editorconfig  .env.example
```

---

## Development workflow

`make help` lists everything. The ones you'll use daily:

| Command          | What it does                                            |
| ---------------- | ------------------------------------------------------- |
| `make install`   | Create the venv, install dev extras, install hooks       |
| `make run`       | Start uvicorn with autoreload                           |
| `make fmt`       | Format with Ruff                                        |
| `make lint`      | Ruff lint + format check                                |
| `make typecheck` | mypy in strict mode                                     |
| `make test`      | pytest with coverage (fails under 90%)                  |
| `make check`     | lint + typecheck + test — **run this before pushing**   |
| `make audit`     | `pip-audit` against known CVEs                          |
| `make clean`     | Remove caches and build artefacts                       |

Ruff replaces Black, isort, flake8, pyupgrade and Bandit in one binary, so
there is exactly one tool to configure and one to blame.

---

## Configuration

All settings are validated by `pydantic-settings` and read from the
environment (or a local `.env`) with the `APP_` prefix. Copy the example:

```bash
cp .env.example .env
```

| Variable             | Default          | Notes                                     |
| -------------------- | ---------------- | ----------------------------------------- |
| `APP_ENVIRONMENT`    | `local`          | `local` · `test` · `staging` · `production` |
| `APP_DEBUG`          | `false`          | Never enable in production                |
| `APP_HOST` / `APP_PORT` | `127.0.0.1` / `8000` |                                      |
| `APP_LOG_LEVEL`      | `INFO`           |                                           |
| `APP_LOG_JSON`       | `true`           | Set `false` for readable local logs       |
| `APP_DOCS_ENABLED`   | `true`           | Disable to hide `/docs` in production     |
| `APP_DEFAULT_LOCALE` | `en`             |                                           |
| `APP_CORS_ORIGINS`   | *(empty)*        | JSON list, e.g. `["https://example.com"]` |

---

## Testing

```bash
make test                       # everything, with coverage
pytest -m unit                  # fast feedback loop
pytest -m integration           # full app through ASGI
pytest --cov-report=html        # browsable report in htmlcov/
```

Unit tests never touch HTTP; integration tests drive the real application via
`httpx.ASGITransport` with a frozen clock, so results are deterministic.
Coverage below **90%** fails the build.

---

## Docker

```bash
docker compose up --build       # http://localhost:8000
```

The image is a multi-stage build on `python:3.12-slim`, runs as a non-root
user, and ships a `HEALTHCHECK` pointed at the liveness probe.

---

## CI/CD

Every pull request runs:

1. **Lint** — Ruff check + format verification
2. **Types** — mypy strict
3. **Tests** — pytest on Python 3.11 / 3.12 / 3.13, coverage uploaded
4. **Security** — pip-audit, CodeQL, dependency review on the diff
5. **Build** — package build + Docker image build
6. **Hygiene** — conventional commit PR titles, pre-commit on all files

Tagging `v*` builds and publishes a container image to GHCR and drafts release
notes from merged PR labels.

---

## Contributing

Please read [CONTRIBUTING.md](./CONTRIBUTING.md) — it covers branch naming,
conventional commits, the definition of done, and the review checklist. All
participants are bound by the [Code of Conduct](./CODE_OF_CONDUCT.md).
Security issues go through [SECURITY.md](./SECURITY.md), never a public issue.

## License

[MIT](./LICENSE)
