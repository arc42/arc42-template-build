# ADR-005: Two-Repository Model with Submodule

**Status:** Accepted

**Date:** 2025-11-18

## Context

arc42 content and build system could be:
- **Single repo**: Build logic and content together
- **Two repos**: Build system references content via submodule
- **Monorepo**: Both plus other arc42 tools

Original arc42-template repository contains only content (AsciiDoc, images). Adding complex build logic there would:
- Complicate contributor workflow
- Mix concerns (content vs. tooling)
- Make content repo harder to fork

## Decision

Use **two-repository model**:
- **arc42-template** (content): AsciiDoc sources, images, version.properties
- **arc42-template-build** (this repo): Build system, Docker, converters

Content included as Git submodule, updated independently.

## Consequences

**Positive:**
- **Clear separation of concerns**: Content vs. build
- **Simplified contributions**: Translators work only on content repo
- **Build system reusable**: Can build req42, other templates
- **Independent versioning**: Content and build evolve separately
- **Smaller content repo**: No build system clutter

**Negative:**
- **Submodule complexity**: Must initialize and update submodule
- **Coordination needed**: Content changes may need build updates
- **Extra repository**: More repos to manage

**Mitigation:**
- `make update-submodule` handles initialization automatically
- Submodule pinned to specific commit (stability)
- Clear documentation for submodule management
