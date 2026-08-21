---
name: Refactor
about: Improve structure without changing behaviour
---

## Motivation

<!-- What was hard to change, test, or understand before this? -->

## What moved

<!-- A short map of the change: old location -> new location. -->

| Before | After |
| ------ | ----- |
|        |       |

## Behaviour is unchanged

- [ ] No public API changed (no new/renamed/removed endpoints, fields, or status codes)
- [ ] No test assertions were weakened or deleted to make the change pass
- [ ] The existing test suite passes untouched, or changes are limited to imports and fixture wiring

## Architectural impact

- [ ] Dependencies still point inwards (`api → services → domain ← infrastructure`)
- [ ] `docs/ARCHITECTURE.md` updated if the layer rules or extension recipes changed
- [ ] An ADR was added under `docs/adr/` if this changes a significant decision

## Checklist

- [ ] `make check` passes
- [ ] Coverage did not drop
