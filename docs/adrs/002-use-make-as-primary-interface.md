# ADR-002: Use Make as Primary Build Interface

**Status:** Accepted

**Date:** 2025-11-18

## Context

Users need a simple, consistent way to invoke builds across different platforms (Linux, macOS, Windows). Options considered:
- Shell scripts (`.sh`)
- NPM scripts (`package.json`)
- Just/Task runners
- Direct Docker Compose commands
- Make

## Decision

Use **Makefile** as the primary user-facing interface for all build operations.

Key targets:
- `make build` - Full build
- `make validate` - Pre-build validation
- `make test-build-artifacts` - Post-build validation
- `make dist` - Create distributions
- `make clean` - Remove outputs

## Consequences

**Positive:**
- Ubiquitous: Make pre-installed on Linux/macOS, easily available on Windows
- Self-documenting: `make help` shows all targets
- Platform-agnostic: Abstracts Docker Compose version differences
- Familiar: Most developers know Make basics
- Composable: Targets can depend on each other

**Negative:**
- Make syntax can be arcane (tabs vs spaces)
- Less powerful than modern task runners
- Windows users may need to install Make separately

**Mitigation:**
- Keep Makefile simple (no complex logic)
- Document all targets with comments
- Provide fallback: users can call Docker Compose directly
