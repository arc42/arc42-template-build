# Architecture Decision Records

This directory contains Architecture Decision Records (ADRs) for arc42-template-build.

## Format

We use the [Nygard format](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions) for ADRs:

- **Status**: Proposed, Accepted, Deprecated, Superseded
- **Context**: The issue motivating this decision
- **Decision**: The change we're proposing or have agreed to
- **Consequences**: The results of the decision (positive and negative)

## Index

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| [001](001-use-adrs-to-document-decisions.md) | Use Architecture Decision Records | Accepted | 2025-11-18 |
| [002](002-use-make-as-primary-interface.md) | Use Make as Primary Build Interface | Accepted | 2025-11-18 |
| [003](003-use-python-for-orchestration.md) | Use Python for Build Orchestration | Accepted | 2025-11-18 |
| [004](004-docker-only-execution.md) | Docker-Only Execution | Accepted | 2025-11-18 |
| [005](005-two-repository-model.md) | Two-Repository Model with Submodule | Accepted | 2025-11-18 |
| [006](006-plugin-architecture-for-converters.md) | Plugin Architecture for Format Converters | Accepted | 2025-11-18 |
| [007](007-yaml-for-configuration.md) | YAML for Configuration | Accepted | 2025-11-18 |
| [008](008-asciidoctor-pandoc-two-phase-conversion.md) | Asciidoctor + Pandoc Two-Phase Conversion | Accepted | 2025-11-18 |
| [009](009-parallel-builds-with-threadpool.md) | Parallel Builds with ThreadPoolExecutor | Accepted | 2025-11-18 |
| [010](010-validation-first-build-approach.md) | Validation-First Build Approach | Accepted | 2025-11-18 |

## Decision Process

1. **Identify** significant architectural decision
2. **Document** using ADR template
3. **Discuss** with team/community (via PR)
4. **Accept** when consensus reached
5. **Implement** the decision
6. **Reference** ADR in code/docs

## Superseding Decisions

When a decision is superseded:
- Original ADR status → "Superseded by ADR-XXX"
- New ADR references the old one
- Original ADR remains in repository (historical record)

## Template

```markdown
# ADR-NNN: Title

**Status:** Proposed | Accepted | Deprecated | Superseded

**Date:** YYYY-MM-DD

## Context

What is the issue we're seeing that is motivating this decision?

## Decision

What is the change we're proposing and/or doing?

## Consequences

What becomes easier or more difficult because of this change?

**Positive:**
- Benefit 1
- Benefit 2

**Negative:**
- Drawback 1
- Drawback 2

**Mitigation:**
- How we address drawbacks
```
