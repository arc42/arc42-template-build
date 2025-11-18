# ADR-008: Asciidoctor + Pandoc Two-Phase Conversion

**Status:** Accepted

**Date:** 2025-11-18

## Context

Need to convert AsciiDoc sources to 10+ formats. Two approaches:
1. **Direct conversion**: AsciiDoc → Format using native backends
2. **Intermediate format**: AsciiDoc → HTML → Format using Pandoc

Direct conversion limits:
- Asciidoctor backends limited (HTML, PDF, DocBook)
- DocBook → other formats adds complexity
- Each format needs custom Asciidoctor backend

Pandoc supports 50+ formats but doesn't read AsciiDoc well.

## Decision

Use **two-phase conversion**:
1. **Phase 1**: AsciiDoc → HTML5 (Asciidoctor)
2. **Phase 2**: HTML → Target format (Pandoc)

Exceptions:
- **PDF**: Direct via Asciidoctor-PDF (better quality)
- **Confluence**: Direct via asciidoctor-confluence
- **HTML**: Direct (no conversion needed)

## Consequences

**Positive:**
- **Leverage strengths**: Best AsciiDoc support (Asciidoctor) + best format support (Pandoc)
- **Easy to add formats**: Pandoc already supports them
- **Proven tools**: Both mature, well-maintained
- **Flexible**: Can optimize per format (direct vs. two-phase)

**Negative:**
- **Double conversion**: Some quality loss in complex formatting
- **Temporary files**: Need intermediate HTML storage
- **Dependencies**: Two tool chains instead of one

**Accepted Trade-offs:**
- Quality loss minimal for text-heavy content like arc42
- Temporary file cleanup automated
- Benefits outweigh complexity for multi-format support
