# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

This is a Python-based build system for the arc42 template that generates documentation in multiple languages (EN, DE, FR, ES, IT, NL, PT, RU, UKR, CZ, ZH) and formats (HTML, PDF, DOCX, Markdown, AsciiDoc). The system runs inside a Docker container with all required tools and fonts for international language support.

## Common Commands

### Build Commands
- `make build` - Build Docker image and generate all configured templates
- `make update-submodule` - Initialize or update the arc42-template submodule (required after cloning)
- `make check` - Verify project setup and submodule status
- `make clean` - Remove generated artifacts (build/, dist/, logs/)
- `make help` - Display all available make targets

### Docker Commands
- `docker compose build builder` - Build the Docker image only
- `docker compose run --rm builder` - Run the default build (build --all)
- `docker compose run --rm builder build --lang EN --format pdf` - Build specific language/format
- `docker compose run --rm builder validate` - Run validation checks only
- `docker compose run --rm builder list-formats` - List available output formats

### Python CLI Commands (inside container)
- `python3 -m src.arc42_builder build --all` - Build everything
- `python3 -m src.arc42_builder build --lang EN DE --format html pdf` - Build specific combinations
- `python3 -m src.arc42_builder validate` - Validate template sources and environment
- `python3 -m src.arc42_builder --verbose` - Enable debug logging

### Testing
- `./test.sh` - Quick verification that expected output files were created
- Check `workspace/build/` for generated artifacts organized by language/flavor/format

## Architecture

### High-Level Structure
The system is a **plugin-based Python orchestrator** running in Docker:
- **CLI Layer** (`cli.py`): Click-based command interface
- **Build Pipeline** (`core/builder.py`): Orchestrates parallel builds across language/flavor/format matrix
- **Config System** (`config/`): YAML-based configuration with dataclass models
- **Converter Plugins** (`converters/`): Format-specific implementations (HTML, PDF, DOCX, Markdown, AsciiDoc)
- **Validation** (`core/validator.py`): Pre-build checks for templates and environment

### Build Process Flow
1. Configuration loaded from `config/build.yaml` (or CLI overrides)
2. Optional validation and workspace cleanup
3. Build matrix generated: languages × flavors × formats
4. Parallel/sequential execution via ThreadPoolExecutor
5. Each converter plugin processes AsciiDoc source → target format
6. Output written to `workspace/build/{language}/{flavor}/{format}/`

### Key Design Patterns
- **Plugin architecture**: Each output format is a `ConverterPlugin` implementing `check_dependencies()` and `convert()`
- **Build context**: `BuildContext` dataclass passes language, flavor, paths, and config to converters
- **Factory pattern**: `get_converter(format_name)` retrieves plugin instances from `CONVERTERS` registry

### Template Structure
- Template source lives in `arc42-template/` git submodule
- Each language has: `{LANG}/asciidoc/` (source) and `{LANG}/version.properties` (metadata)
- Two flavors: `plain` (minimal) and `withHelp` (with explanations)

### Docker Container
- Based on Ubuntu 22.04 with comprehensive font support for all languages
- Tools: asciidoctor, asciidoctor-pdf, pandoc, Python 3.11, Ruby
- CJK fonts: fonts-noto-cjk, fonts-wqy-microhei
- Cyrillic fonts: fonts-noto
- Custom fonts/themes can be added via `docker/custom-fonts/` and `docker/pdf-themes/`

## Configuration

### Primary Config File: `config/build.yaml`
Controls which languages, formats, and flavors to build:

```yaml
languages: [EN, DE]  # Which languages to build
flavors: [plain, withHelp]  # Content variants
formats:
  html: {enabled: true, priority: 1}
  pdf: {enabled: true, priority: 1, options: {page_size: "A4"}}
  # ... etc
build:
  parallel: true
  max_workers: 4
  validate: true
  clean_before: true
```

### Key Config Options
- **languages**: Must match top-level directories in arc42-template submodule
- **flavors**: `plain` or `withHelp` (controls content via AsciiDoc attributes)
- **formats.{format}.enabled**: Toggle format on/off
- **build.parallel**: Enable concurrent builds (much faster)
- **build.max_workers**: Number of parallel threads

## Development Guidelines

### Adding a New Output Format
1. Create `src/arc42_builder/converters/{format_name}.py`
2. Implement `ConverterPlugin` abstract class:
   - `check_dependencies()`: Verify required CLI tools available
   - `convert(context: BuildContext)`: Execute conversion and return output Path
3. Register in `src/arc42_builder/converters/__init__.py` CONVERTERS dict
4. Add format config to `config/build.yaml`

### Code Organization
- `src/arc42_builder/`: Main application package
  - `cli.py`: Entry point with Click commands
  - `core/`: Build pipeline and validation logic
  - `config/`: Configuration loading and models
  - `converters/`: Format-specific plugins
- `docker/`: Dockerfile and container configuration
- `scripts/`: Helper scripts (e.g., `get_config_value.py`)
- `tests/`: Unit and integration tests (fixtures, unit/, integration/)

### Working with the Template Submodule
- The `arc42-template` directory is a git submodule pointing to the source repository
- Always run `make update-submodule` after cloning or to get latest changes
- Template path is configurable via `config/build.yaml` → `template.path`
- Don't edit template files directly; make changes in the upstream arc42-template repo

### Dependencies
- Python: click, pyyaml, pathlib (see `requirements.txt`)
- System: Docker, Docker Compose, Make, Git
- Container tools: asciidoctor (2.0.20), asciidoctor-pdf (2.3.10), pandoc

### Output Structure
Generated files appear in `workspace/build/{language}/{flavor}/{format}/` with naming convention:
`arc42-template-{LANG}-{flavor}.{ext}`

Example: `workspace/build/EN/withHelp/pdf/arc42-template-EN-withHelp.pdf`

### Environment Variables
- `LOG_LEVEL`: Set via docker-compose.yaml or CLI `--verbose` flag (DEBUG/INFO/WARNING/ERROR)
- Container uses `/workspace` as working directory, with volumes mounted from host
- Python path set to `/app` for module imports
