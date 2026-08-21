---
name: Bug fix
about: Repair broken behaviour
---

## The bug

<!-- What was happening, and who it affected. -->

## Root cause

<!-- Why it happened. Fixes without a stated root cause tend to come back. -->

## The fix

<!-- What you changed, and why this approach over the alternatives. -->

## Regression test

Every bug fix needs a test that fails before the change and passes after it.

- [ ] Added a test reproducing the bug
- [ ] Confirmed it fails on `main` (`git stash` the fix and run it)

```bash
# Test name and command
pytest tests/unit/test_greeting_service.py::test_...
```

## Blast radius

- [ ] No behaviour changed beyond the bug itself
- [ ] Considered whether the same mistake exists elsewhere in the codebase

## Checklist

- [ ] `make check` passes
- [ ] `CHANGELOG.md` updated under `### Fixed`
- [ ] Closes the originating issue (`Closes #`)
