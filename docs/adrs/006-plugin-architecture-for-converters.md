# ADR-006: Plugin Architecture for Format Converters

**Status:** Accepted

**Date:** 2025-11-18

## Context

Need to support 10+ output formats (HTML, PDF, Markdown, DOCX, RST, etc.). Adding formats should be easy without modifying core orchestration.

Approaches considered:
- **Monolithic functions**: One big script with if/else for each format
- **Switch statement**: Central dispatcher calling format-specific code
- **Plugin system**: Abstract base class, converters auto-registered

## Decision

Implement **plugin architecture** with:
- `ConverterPlugin` abstract base class
- Each format = separate file in `src/arc42_builder/converters/`
- Converters registered in `__init__.py` registry
- Common interface: `convert(context)`, `check_dependencies()`

## Consequences

**Positive:**
- **Easy to add formats**: Create single file, implement interface
- **Testable**: Each converter tested independently
- **Encapsulated**: Converter knows its own dependencies
- **Discoverable**: `list-formats` command shows all converters
- **Maintainable**: Changes to one format don't affect others
- **Extensible**: Future: load external plugins

**Negative:**
- **Indirection**: Extra abstraction layer
- **Boilerplate**: Each converter needs class definition
- **Runtime registry**: Small overhead at startup

**Accepted Trade-offs:**
- Slight complexity increase worth it for extensibility
- Boilerplate minimal (base class provides defaults)
- Registry overhead negligible (milliseconds)
