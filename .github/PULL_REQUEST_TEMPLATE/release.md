---
name: Release
about: Cut a new version
---

## Version

`vX.Y.Z` — <!-- major / minor / patch, and why -->

## Release checklist

- [ ] `version` bumped in `pyproject.toml`
- [ ] `__version__` bumped in `src/app/__init__.py`
- [ ] `CHANGELOG.md`: `## [Unreleased]` section renamed to this version with today's date
- [ ] A fresh `## [Unreleased]` section added at the top
- [ ] `main` is green
- [ ] No open PRs intended for this release

## Changes in this release

<!-- Paste the CHANGELOG section for this version. -->

## Post-merge

- [ ] Tag `vX.Y.Z` pushed (triggers the release workflow)
- [ ] Container image published to GHCR
- [ ] GitHub release notes reviewed
