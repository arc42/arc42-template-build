# ADR-003: Use Python for Build Orchestration

**Status:** Accepted

**Date:** 2025-11-18

## Context

Build orchestration requires:
- Iterating over language × flavor × format matrix
- Calling external tools (Asciidoctor, Pandoc)
- Parsing YAML configuration
- Complex error handling
- Parallel execution

Options considered:
- **Bash scripts**: Simple but hard to maintain for complex logic
- **Groovy/Gradle**: Powerful but JVM overhead, less familiar
- **Node.js**: Good ecosystem but adds runtime dependency
- **Python**: Mature, readable, excellent libraries

## Decision

Use **Python 3.11+** as the orchestration language with:
- Click for CLI interface
- pathlib for file operations
- subprocess for calling external tools
- ThreadPoolExecutor for parallelism
- PyYAML for configuration

## Consequences

**Positive:**
- Readable, maintainable code (better than shell)
- Excellent libraries: Click, PyYAML, pathlib
- Strong subprocess handling
- Type hints for better IDE support
- Widely known language

**Negative:**
- Adds Python runtime dependency (mitigated by Docker)
- Slightly slower startup than compiled languages (negligible)

**Mitigation:**
- Keep Python dependencies minimal
- Pin versions in requirements.txt
- All execution inside Docker (no host Python needed)
