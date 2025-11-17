# arc42 Template Directory Structure

This directory contains example files showing the expected structure for the arc42-template repository.

## Directory Layout

The build system expects this structure for each language in the arc42-template submodule:

```
{LANG}/
├── arc42-template.adoc          # Main template file (includes all sections)
├── adoc/                         # All content files
│   ├── config.adoc              # Configuration (see example in this dir)
│   ├── about-arc42.adoc
│   ├── 01_introduction_and_goals.adoc
│   ├── 02_architecture_constraints.adoc
│   ├── 03_context_and_scope.adoc
│   ├── 04_solution_strategy.adoc
│   ├── 05_building_block_view.adoc
│   ├── 06_runtime_view.adoc
│   ├── 07_deployment_view.adoc
│   ├── 08_concepts.adoc
│   ├── 09_architecture_decisions.adoc
│   ├── 10_quality_requirements.adoc
│   ├── 11_technical_risks.adoc
│   └── 12_glossary.adoc
├── images/                       # Language-specific images
│   ├── arc42-logo.png
│   ├── 01_2_iso-25010-topics-{LANG}.drawio.png
│   ├── 05_building_blocks-{LANG}.png
│   ├── 08-concepts-{LANG}.drawio.png
│   └── 10_stimulus.png
└── version.properties            # Version metadata (revnumber, revdate, etc.)
```

## Key Changes from Previous Structure

### Old Structure (deprecated):
```
{LANG}/
├── asciidoc/
│   ├── arc42-template.adoc
│   └── src/
│       ├── config.adoc           # imagesdir: ./images
│       └── *.adoc
├── images/
└── version.properties
```

### New Structure (current):
```
{LANG}/
├── arc42-template.adoc            # Moved up one level
├── adoc/                          # Flattened (no src/ subdirectory)
│   ├── config.adoc               # imagesdir: ../images
│   └── *.adoc
├── images/
└── version.properties
```

## Configuration Notes

### config.adoc

The `config.adoc` file must be updated to reflect the new path:

**Old (deprecated):**
```asciidoc
:imagesdir: ./images
```

**New (current):**
```asciidoc
:imagesdir: ../images
```

This is because `config.adoc` is now at `{LANG}/adoc/config.adoc` and images are at `{LANG}/images/`.

### arc42-template.adoc

The main template file should include content files from the `adoc/` directory:

```asciidoc
= arc42 Template

include::adoc/config.adoc[]
include::adoc/about-arc42.adoc[]
include::adoc/01_introduction_and_goals.adoc[]
// ... etc
```

## Build System Impact

The build system (`src/arc42_builder/`) has been updated to:
- Set `source_dir` to the language root (e.g., `arc42-template/EN/`)
- Expect `arc42-template.adoc` at `source_dir/arc42-template.adoc`
- Expect content files at `source_dir/adoc/*.adoc`
- Expect images at `source_dir/images/*.png`
- Expect PDF themes (if present) at `source_dir/pdf-theme/`

## Migration Steps

If you have an existing arc42-template with the old structure:

1. Create `adoc/` directory at language root
2. Move all `.adoc` files from `asciidoc/src/` to `adoc/`
3. Move `arc42-template.adoc` from `asciidoc/` to language root
4. Update `config.adoc` to set `:imagesdir: ../images`
5. Update include paths in `arc42-template.adoc` to use `adoc/` prefix
6. Remove old `asciidoc/` directory

## Example

See `config.adoc` in this directory for a reference configuration file.
