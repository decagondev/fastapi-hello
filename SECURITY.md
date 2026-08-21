# Security Policy

## Supported versions

| Version | Supported |
| ------- | --------- |
| 0.1.x   | ✅ Yes    |
| < 0.1   | ❌ No     |

Only the latest minor release receives security fixes.

## Reporting a vulnerability

**Please do not open a public issue for a security problem.**

Report it privately through
[GitHub Security Advisories](https://github.com/decagondev/fastapi-hello/security/advisories/new),
or by email to **security@example.com**.

Please include:

- A description of the issue and its impact
- Steps to reproduce, or a proof of concept
- The affected version or commit SHA
- Any suggested mitigation

### What to expect

| Stage | Target |
| ----- | ------ |
| Acknowledgement of your report | 48 hours |
| Initial assessment and severity rating | 5 working days |
| Fix released for critical issues | 14 days |
| Fix released for other issues | 30 days |
| Public advisory | After the fix ships, or 90 days, whichever comes first |

We will keep you updated as we work, and — unless you prefer otherwise — credit
you in the advisory. We do not currently run a paid bounty programme.

## Safe harbour

We will not pursue legal action against researchers who act in good faith:
avoid privacy violations and service degradation, do not access or modify data
belonging to others, and give us reasonable time to fix the issue before
disclosing it.

## Security measures in this repository

- **Dependency scanning** — Dependabot opens weekly PRs; `pip-audit` runs in CI
  and fails the build on known CVEs
- **Dependency review** — every PR is checked for newly introduced advisories
  and disallowed licences
- **Static analysis** — CodeQL with the `security-extended` query suite, plus
  Ruff's Bandit-derived rules (`S`) on every commit
- **Supply chain** — build provenance attestation is published with each
  release image
- **Runtime** — the container runs as a non-root user; internal error detail is
  never returned to clients; `/docs` can be disabled via `APP_DOCS_ENABLED`

## Hardening checklist for deployment

This template is not production-configured out of the box. Before deploying:

- [ ] Set `APP_ENVIRONMENT=production` and `APP_DEBUG=false`
- [ ] Set `APP_DOCS_ENABLED=false` unless the docs are meant to be public
- [ ] Configure `APP_CORS_ORIGINS` explicitly — never use `*` with credentials
- [ ] Terminate TLS in front of the application and enforce HTTPS
- [ ] Add authentication and rate limiting for any non-public endpoint
- [ ] Ship logs somewhere durable and alert on 5xx rates
- [ ] Run the container with a read-only root filesystem and no added capabilities
- [ ] Pin and regularly rebuild the base image
