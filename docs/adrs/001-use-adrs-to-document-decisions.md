# ADR-001: Use Architecture Decision Records

**Status:** Accepted

**Date:** 2025-11-18

## Context

The arc42-template-build project involves many architectural decisions affecting maintainability, extensibility, and developer experience. Without documentation, rationale behind decisions gets lost, making it harder for new contributors to understand why certain approaches were chosen.

## Decision

We will document significant architectural decisions using Architecture Decision Records (ADRs) in the Nygard format, stored in `docs/adrs/`.

Each ADR will be:
- Numbered sequentially (001, 002, etc.)
- Named descriptively (`001-use-adrs-to-document-decisions.md`)
- Immutable once accepted (new ADRs supersede old ones)
- Brief and focused on context, decision, and consequences

## Consequences

**Positive:**
- Decision rationale is preserved for future reference
- New contributors can understand "why" not just "what"
- Decisions can be reviewed and challenged constructively
- Creates audit trail of project evolution

**Negative:**
- Adds documentation overhead
- Requires discipline to write ADRs when making decisions
- May be skipped for minor decisions (need clear threshold)

**Mitigation:**
- Keep ADRs brief (200-400 words)
- Only document significant decisions
- Template makes writing ADRs quick
