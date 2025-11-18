# ADR-004: Docker-Only Execution

**Status:** Accepted

**Date:** 2025-11-18

## Context

Build requires multiple tools: Ruby (Asciidoctor), Python, Pandoc, and 50+ fonts. Installing these locally is:
- Complex (different package managers per OS)
- Error-prone (version conflicts)
- Time-consuming (hours of setup)
- Non-reproducible (different environments)

Options:
- **Local installation**: Provide scripts for each OS
- **Hybrid**: Optional Docker or local
- **Docker-only**: Require Docker, nothing else

## Decision

**All builds must run inside Docker containers.** No local installation of Ruby, Python, Pandoc, or fonts required.

Users only need:
- Docker (or Docker Desktop)
- Git (for cloning)

## Consequences

**Positive:**
- **Reproducibility**: Exact same environment everywhere
- **Version control**: Dockerfile pins all tool versions
- **Zero host dependencies**: Works on any platform with Docker
- **No "works on my machine"**: Container is the machine
- **CI/CD ready**: Same Docker image in CI and locally

**Negative:**
- Docker required (barrier for some users)
- Slower first build (image download/build)
- Container overhead (minimal with volume mounts)
- Debugging harder (need to shell into container)

**Mitigation:**
- Excellent Docker documentation in README
- `make shell` for easy debugging
- Docker is industry standard, most developers have it
- One-time setup cost, huge long-term benefits
