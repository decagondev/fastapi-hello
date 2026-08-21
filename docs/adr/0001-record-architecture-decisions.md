# 1. Record architecture decisions

- **Status:** Accepted
- **Date:** 2026-01-01
- **Deciders:** Maintainers

## Context

Architectural choices in this repository — ports-and-adapters layering, a
hand-written composition root, protocols instead of abstract base classes — are
not self-evident from the code alone. Without a record, each one gets
re-litigated in review by whoever encounters it next, and the reasoning is lost
when the people who made the decision move on.

## Decision

We will keep lightweight Architecture Decision Records in `docs/adr/`, in the
format described by Michael Nygard.

- One Markdown file per decision, numbered sequentially:
  `NNNN-short-title-in-kebab-case.md`.
- Each record states **Context**, **Decision** and **Consequences**, and carries
  a status of Proposed, Accepted, Deprecated or Superseded.
- Records are immutable once accepted. A change of mind means a new ADR that
  supersedes the old one, with both linked.
- An ADR is required when a decision is expensive to reverse, constrains future
  work, or is likely to surprise a new contributor. Everyday choices do not
  need one.

## Consequences

**Positive:** reviewers can point at a document instead of re-arguing;
newcomers can read the history of the design; superseded decisions leave a
visible trail.

**Negative:** a small amount of writing overhead per significant decision, and
records will drift out of date if not superseded diligently. We accept this —
a stale ADR with a clear date is still more useful than an undocumented
decision.

## Template

```markdown
# N. Title

- **Status:** Proposed | Accepted | Deprecated | Superseded by [ADR-000X](...)
- **Date:** YYYY-MM-DD
- **Deciders:** ...

## Context
What forces are at play? What makes this decision necessary?

## Decision
What we are doing, stated in the active voice.

## Consequences
What becomes easier, and what becomes harder.
```
