# Contributing

Thanks for taking the time to contribute. This document is the rulebook: if a
reviewer asks you for something, it should be written down here, and if it
isn't, that's a bug in this document — please open a PR against it.

All participants are bound by our [Code of Conduct](./CODE_OF_CONDUCT.md).

---

## Table of contents

- [Ways to contribute](#ways-to-contribute)
- [Development setup](#development-setup)
- [The workflow](#the-workflow)
- [Branch naming](#branch-naming)
- [Commit messages](#commit-messages)
- [Coding standards](#coding-standards)
- [Architecture rules](#architecture-rules)
- [Testing standards](#testing-standards)
- [Definition of done](#definition-of-done)
- [Opening a pull request](#opening-a-pull-request)
- [Review process](#review-process)
- [Releasing](#releasing)
- [Getting help](#getting-help)

---

## Ways to contribute

You don't have to write code to help:

| Contribution | Start here |
| ------------ | ---------- |
| Report a bug | [Bug report form](https://github.com/decagondev/fastapi-hello/issues/new?template=bug_report.yml) |
| Propose a feature | [Feature request form](https://github.com/decagondev/fastapi-hello/issues/new?template=feature_request.yml) |
| Improve docs | [Docs issue](https://github.com/decagondev/fastapi-hello/issues/new?template=documentation.yml), or just open a PR |
| Review a PR | Any open PR — a second opinion is always welcome |
| Report a vulnerability | [SECURITY.md](./SECURITY.md) — **never** a public issue |

Issues labelled `good first issue` are scoped to be completable in an hour or
two without deep familiarity with the codebase.

**Before starting anything large**, open an issue and get agreement on the
approach. It is far less frustrating than having a finished PR redirected.

---

## Development setup

Requires **Python 3.11+** and **git**.

```bash
git clone https://github.com/decagondev/fastapi-hello.git
cd fastapi-hello

make install        # venv + dev dependencies + git hooks
# equivalently:
#   uv venv && source .venv/bin/activate
#   uv pip install -e ".[dev]"
#   pre-commit install --install-hooks
#   pre-commit install --hook-type commit-msg

make check          # confirm a clean baseline before you change anything
```

If `make check` fails on a fresh clone, that is a bug — please report it.

**Install the hooks.** They run Ruff, mypy and a batch of file checks before
each commit, which is much faster than discovering the same problems in CI.

---

## The workflow

1. **Claim it.** Comment on the issue so two people don't do the same work.
2. **Branch** from an up-to-date `main`.
3. **Commit** in small, logical steps using Conventional Commits.
4. **Test** — new behaviour needs new tests, bug fixes need regression tests.
5. **Run `make check`** until it is green.
6. **Update `CHANGELOG.md`** under `## [Unreleased]`.
7. **Open a PR** using the template, and fill it in properly.
8. **Respond to review** by pushing new commits (don't force-push mid-review —
   it destroys the reviewer's ability to see what changed).
9. **Squash-merge** once approved and green.

---

## Branch naming

```
<type>/<issue-number>-<short-kebab-description>
```

| Example                          | For                        |
| -------------------------------- | -------------------------- |
| `feat/42-portuguese-locale`      | New behaviour              |
| `fix/57-blank-name-500`          | Bug fix                    |
| `docs/61-clarify-config-table`   | Documentation              |
| `refactor/70-extract-registry`   | Structural change          |
| `chore/74-bump-ruff`             | Tooling and dependencies   |

---

## Commit messages

We use [Conventional Commits](https://www.conventionalcommits.org/). The PR
title is checked by CI and becomes the squash-merge commit message, so it
matters more than the individual commits.

```
<type>(<optional scope>): <subject in lowercase, no trailing period>

<optional body: why, not what>

<optional footer: Closes #123 / BREAKING CHANGE: ...>
```

**Types:** `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`,
`build`, `ci`, `chore`, `revert`.

Good:

```
feat(greetings): add Portuguese locale
fix(api): return 422 rather than 500 for an unknown locale
refactor(services): extract formatter selection into a registry
feat(api)!: rename the `name` query parameter to `recipient`
```

Bad: `update stuff`, `Fixed bug.`, `WIP`, `changes as per review`.

Mark breaking changes with `!` after the type/scope **and** a
`BREAKING CHANGE:` footer explaining the migration path.

---

## Coding standards

Tooling is not negotiable but it is also not your job to satisfy by hand —
run `make fmt` and it is done.

| Concern     | Tool                | Command           |
| ----------- | ------------------- | ----------------- |
| Formatting  | Ruff formatter      | `make fmt`        |
| Linting     | Ruff (≈30 rulesets) | `make lint`       |
| Typing      | mypy `--strict`     | `make typecheck`  |
| Tests       | pytest + coverage   | `make test`       |
| Everything  | —                   | `make check`      |

Beyond the tools:

- **Type everything.** `Any` needs a comment justifying it.
- **Docstrings** on every public module, class and function. Google style.
  Say *why*, not *what the code already says*.
- **No `print`.** Use the standard `logging` module; output is structured JSON.
- **Absolute imports only** (`from app.domain.ports import Clock`). Relative
  imports are banned by the linter.
- **Keep functions small.** Complexity above 8 fails the build.
- **Never catch bare `Exception`** outside `core/errors.py`.
- **No secrets in code**, including in tests and fixtures.
- **Datetimes are always timezone-aware.** Get them from the `Clock` port,
  never from `datetime.now()` directly.

---

## Architecture rules

These are enforced in review, and breaking them is the most common reason a PR
gets sent back. The full reasoning is in
[docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md).

1. **Dependencies point inwards.**
   `api → services → domain ← infrastructure`
2. **`domain/` imports no framework.** No `fastapi`, no `pydantic`, no
   `starlette`, and nothing from `infrastructure/`. If you need to import one
   to make something work, the design is wrong — ask in the issue.
3. **Depend on ports, not classes.** Anything a class collaborates with arrives
   through its constructor, typed as a `Protocol` from `domain/ports.py`.
4. **Wire concretes in one place.** `core/container.py` is the only module
   allowed to know which implementation is in use.
5. **Endpoints stay thin.** Parse, delegate, serialise. If there is an `if`
   about business rules in an endpoint, it belongs in a service.
6. **Prefer extension over modification.** Adding a locale should mean adding a
   class, not editing a `match` statement.
7. **Keep protocols narrow.** If an implementer would have to write
   `raise NotImplementedError`, split the protocol.
8. **No mocking of your own code in tests.** If a test needs `unittest.mock` to
   test your class, that class probably takes a dependency it should be given.

---

## Testing standards

- `tests/unit/` — no HTTP, no app instance, no I/O. Should run in milliseconds.
- `tests/integration/` — the real app through `httpx.ASGITransport`.
- Mark tests with `@pytest.mark.unit` or `@pytest.mark.integration`.
- **Coverage must stay at or above 90%.** CI fails below it.
- Every bug fix ships with a test that fails without the fix. Verify this by
  stashing your change and watching it fail.
- Test the failure paths, not just the happy path.
- Use the fixtures in `tests/conftest.py`; prefer injecting a `FrozenClock` or
  a small fake over patching.
- Test names read as sentences: `test_unknown_locale_returns_422`, not
  `test_locale_2`.

```bash
pytest -m unit                  # fast loop while developing
pytest -m integration
pytest --cov-report=html        # then open htmlcov/index.html
pytest -k locale -vv            # one area, verbosely
```

---

## Definition of done

A change is done when **all** of these are true:

- [ ] It solves the problem in the issue, and nothing more
- [ ] `make check` is green locally
- [ ] Tests cover the new behaviour, including at least one failure case
- [ ] Coverage has not dropped
- [ ] Public API surface is documented
- [ ] `CHANGELOG.md` has an entry under `## [Unreleased]`
- [ ] The layering rules above still hold
- [ ] No TODOs left behind without a linked issue
- [ ] The PR description explains *why*, not just *what*

---

## Opening a pull request

- **One concern per PR.** If the description needs the word "also", split it.
- **Under ~400 lines of diff** where possible. CI warns above 800.
- **Open it as a draft** if you want early feedback on direction.
- **Fill in the template.** Unticked checkboxes are fine and honest; deleting
  the checklist is not.
- **Pick the right template** by appending a query parameter to the PR URL:
  `?template=bugfix.md`, `?template=docs.md`, `?template=refactor.md`,
  `?template=release.md`.
- **Link the issue** with `Closes #123`.

---

## Review process

**What to expect:** a first response within about three working days. Two
approvals are needed for changes to `domain/` or `core/container.py`; one for
everything else. Maintainers squash-merge.

**As an author:** assume good faith, answer questions rather than just
changing the code, and push fixes as new commits so the reviewer can follow.
Resolve a conversation only once you've actually addressed it. Disagreeing is
fine — say so and explain why.

**As a reviewer:** be specific and kind. Distinguish blocking comments from
suggestions; prefix the latter with `nit:`. Review the design before the
style — the tools already handle style. Explain the reasoning behind a
requested change, and approve once your concerns are addressed rather than
holding out for perfection.

---

## Releasing

Maintainers only.

1. Open a release PR using `?template=release.md`.
2. Bump `version` in `pyproject.toml` and `__version__` in `src/app/__init__.py`.
3. Move `## [Unreleased]` entries into a new dated version section.
4. Merge once green, then tag:

   ```bash
   git tag -a v0.2.0 -m "v0.2.0"
   git push origin v0.2.0
   ```

5. The release workflow re-runs the checks, publishes a multi-arch image to
   GHCR with build provenance, and publishes the drafted release notes.

We follow [Semantic Versioning](https://semver.org/): breaking API changes bump
major, new backwards-compatible behaviour bumps minor, fixes bump patch.

---

## Getting help

- **Questions:** [Discussions](https://github.com/decagondev/fastapi-hello/discussions)
- **Bugs:** [issue tracker](https://github.com/decagondev/fastapi-hello/issues)
- **Vulnerabilities:** [SECURITY.md](./SECURITY.md)
- **Stuck on a PR:** comment on it and tag a maintainer; we would much rather
  help than watch a contribution stall.
