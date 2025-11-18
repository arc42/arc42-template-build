# ADR-010: Validation-First Build Approach

**Status:** Accepted

**Date:** 2025-11-18

## Context

Builds can fail due to:
- Missing template files or includes
- Broken image references
- Missing fonts for non-Latin languages
- Invalid AsciiDoc syntax
- Incorrect configuration

Failing late (during conversion) wastes time building partial artifacts. Need to decide: validate before or during build?

Options:
- **No validation**: Fail during conversion
- **Partial validation**: Check only critical items
- **Validation-first**: Comprehensive checks before any conversion
- **Continuous validation**: Check as we build

## Decision

Implement **validation-first approach**:
1. Pre-build validation phase runs before any conversion
2. Validates:
   - Template directory structure
   - Version.properties files
   - AsciiDoc include references
   - Image references (warning, not error)
   - Required fonts installation
3. Build only proceeds if validation passes
4. Post-build validation for generated artifacts (Markdown syntax)

Exposed as:
- Automatic: Runs before build (if `build.validate: true`)
- Manual: `make validate` command
- Post-build: `make test-build-artifacts`

## Consequences

**Positive:**
- **Fast failure**: Catch errors in seconds, not minutes
- **Clear errors**: Validation reports exact file/line of problem
- **No partial builds**: All-or-nothing approach
- **Developer feedback**: Find issues before lengthy build
- **CI-friendly**: Pre-commit hooks can run validation

**Negative:**
- **Upfront cost**: Validation takes 5-10 seconds
- **Duplicate checks**: Asciidoctor will check anyway
- **Maintenance**: Validator must stay in sync with converters

**Mitigation:**
- Validation much faster than build (worth the cost)
- Can disable with `build.validate: false`
- Modular validator easy to maintain
