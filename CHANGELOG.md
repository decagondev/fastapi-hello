# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

<!-- New features. Add your entry here as part of your PR. -->

### Changed

- Render the architecture, layering and request-lifecycle diagrams as
  Mermaid instead of ASCII art in `README.md` and `docs/ARCHITECTURE.md`

### Deprecated

### Removed

### Fixed

### Security

---

## [0.1.0] - 2026-01-01

### Added

- Layered FastAPI service with `domain`, `services`, `infrastructure`, `api`
  and `core` packages, and a hand-written composition root
- Greeting endpoints: `GET /api/v1/greetings/hello`, `POST /api/v1/greetings`,
  `GET /api/v1/greetings/locales`
- Liveness and readiness probes under `/api/v1/health`
- Five built-in locales (`en`, `es`, `fr`, `de`, `ja`) with a pluggable
  formatter registry
- RFC 9457-style problem documents for all error responses, carrying the
  request id
- Structured JSON logging, request-id propagation, and request timing headers
- Typed settings via `pydantic-settings` with an `APP_` environment prefix
- Test suite covering unit and integration layers, gated at 90% coverage
- Ruff (lint + format), mypy strict, pre-commit hooks, and a `Makefile`
- GitHub Actions: CI matrix, CodeQL, dependency review, PR hygiene, release,
  and stale management
- Contribution scaffolding: PR templates, issue forms, CODEOWNERS, Dependabot,
  labeler, and release drafter
- Multi-stage Dockerfile running as a non-root user, plus Compose setup

[Unreleased]: https://github.com/decagondev/fastapi-hello/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/decagondev/fastapi-hello/releases/tag/v0.1.0
