# ADR-007: YAML for Configuration

**Status:** Accepted

**Date:** 2025-11-18

## Context

Build configuration needs to specify:
- Languages to build
- Formats enabled/disabled
- Format-specific options
- Build settings (parallel workers, etc.)

Format options:
- **JSON**: Machine-readable, no comments
- **YAML**: Human-readable, supports comments
- **TOML**: Clear, but less familiar
- **Python/Groovy**: Executable config (security risk)

## Decision

Use **YAML** (`config/build.yaml`) for configuration with:
- PyYAML library for parsing
- Strongly-typed config models (dataclasses)
- Schema validation (future)
- CLI overrides allowed

## Consequences

**Positive:**
- **Readable**: Clear hierarchy, easy to edit
- **Comments**: Document options inline
- **Widely supported**: YAML parsers in all languages
- **Flexible**: Supports complex structures
- **Familiar**: Used by Docker Compose, Kubernetes, CI/CD

**Negative:**
- **YAML pitfalls**: Indentation-sensitive, quirky parsing
- **No native validation**: Need external schema (JSON Schema)
- **Version issues**: YAML 1.1 vs 1.2 differences

**Mitigation:**
- Keep YAML simple (no anchors, complex features)
- Validate config at load time
- Provide example configs with comments
- Use safe_load (no arbitrary code execution)
