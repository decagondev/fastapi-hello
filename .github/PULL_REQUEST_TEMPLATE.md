<!--
  Thanks for contributing!

  PR titles must follow Conventional Commits, e.g.
      feat(greetings): add Portuguese locale
      fix(api): return 422 instead of 500 for unknown locales
  A CI job checks this, so a non-conforming title will fail the build.

  Other templates are available by adding a query parameter to the PR URL:
      ?template=bugfix.md   ?template=docs.md   ?template=refactor.md   ?template=release.md
-->

## Summary

<!-- What does this change and, more importantly, why? Two or three sentences. -->

## Related issues

<!-- "Closes #123" auto-closes on merge. Use "Refs #123" for partial work. -->

Closes #

## Type of change

- [ ] `feat` — new user-facing behaviour
- [ ] `fix` — bug fix
- [ ] `refactor` — behaviour unchanged, structure improved
- [ ] `perf` — performance improvement
- [ ] `docs` — documentation only
- [ ] `test` — tests only
- [ ] `build` / `ci` / `chore` — tooling and pipelines

## How this was tested

<!-- Commands you ran and what you observed. "CI is green" on its own is not enough. -->

```bash
make check
```

## Architecture checklist

The layering rules in [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) are what
keep this codebase workable. Confirm each one:

- [ ] `domain/` still imports no framework code (no `fastapi`, no `pydantic`, nothing from `infrastructure/`)
- [ ] New collaborators are injected as **ports**, not constructed inside the class that uses them
- [ ] Concrete implementations are wired only in `core/container.py`
- [ ] New behaviour was added by **extension** (a new class) rather than by editing an existing branch, where reasonable
- [ ] Business rules live in `services/` or `domain/`, not in endpoints
- [ ] New protocols are narrow — no method an implementer would be forced to stub out

## Quality checklist

- [ ] `make check` passes locally (lint, format, mypy strict, tests)
- [ ] Coverage has not dropped below the 90% gate
- [ ] New and changed code has tests, including at least one failure-path test
- [ ] Public functions and classes have docstrings
- [ ] `CHANGELOG.md` updated under `## [Unreleased]`
- [ ] Docs updated (README / ARCHITECTURE / docstrings) if behaviour changed
- [ ] No secrets, tokens, or personal data in code, tests, or fixtures

## Breaking changes

- [ ] This PR contains no breaking changes

<!-- If it does: describe the break, the migration path, and mark the PR title
     with a `!` (e.g. `feat(api)!: rename locale query parameter`). -->

## Screenshots / sample output

<!-- API responses, logs, or terminal output where useful. Delete if not. -->

## Notes for reviewers

<!-- Where should a reviewer start? Anything you are unsure about or want
     pushback on? Flag it here — it makes review far faster. -->
