# CLAUDE.md - AI Assistant Guide for arc42-template-build

## Repository Overview

This is the **arc42-template-build** repository, a proof-of-concept (PoC) for a modernized build system for the arc42 architecture documentation template. The project aims to replace the complex existing build matrix with a Python-based, Docker-containerized solution.

**Status**: Proof of Concept (v0.1.0)
**Primary Language**: Python 3.11+
**Build Tool**: Docker Compose
**Key Technology**: Asciidoctor, Pandoc

## What is arc42?

arc42 is a template for documenting software and system architecture. This repository builds that template in multiple:
- **Languages**: Currently EN, DE (available in submodule: CZ, ES, FR, IT, NL, PT, RU, UKR, ZH)
- **Flavors**: `withHelp` (with guidance), `plain` (without guidance)
- **Formats**: HTML, PDF, DOCX (planned: Markdown, Confluence, LaTeX, AsciiDoc)

## Project Structure

```
arc42-template-build/
├── src/arc42_builder/           # Python build orchestrator
│   ├── __init__.py              # Package metadata (version 0.1.0)
│   ├── __main__.py              # Entry point
│   └── cli.py                   # Click-based CLI with build logic
├── docker/
│   └── Dockerfile               # Ubuntu 22.04 with Asciidoctor, Pandoc, Python
├── arc42-template/              # Git submodule (upstream arc42 content)
├── workspace/                   # Generated at runtime (gitignored)
│   ├── build/                   # Built artifacts
│   ├── dist/                    # ZIP distributions
│   └── logs/                    # Build logs
├── todo/                        # Design documents and requirements
├── docker-compose.yaml          # Orchestration configuration
├── Makefile                     # Convenience wrapper
├── test.sh                      # Output verification script
└── requirements.txt             # Python dependencies (click, pyyaml)
```

## Core Architecture

### Build Flow

1. **Orchestrator** (`src/arc42_builder/cli.py`):
   - Click-based CLI that accepts language and format options
   - Iterates through build matrix (language × format combinations)
   - Loads version properties from `arc42-template/{LANG}/version.properties`

2. **Format Builders**:
   - `build_html()`: Asciidoctor → HTML5
   - `build_pdf()`: Asciidoctor-PDF → PDF
   - `build_docx()`: Asciidoctor → HTML → Pandoc → DOCX

3. **Output Structure**:
   ```
   workspace/build/{LANG}/{FLAVOR}/{FORMAT}/
   └── arc42-template-{LANG}-{FLAVOR}.{ext}
   ```

### Docker Container

The build runs in a self-contained Docker container with:
- **Base**: Ubuntu 22.04
- **Ruby Tools**: Asciidoctor 2.0.20, Asciidoctor-PDF 2.3.10
- **Python**: 3.x with Click, PyYAML
- **Document Tools**: Pandoc
- **Fonts**: Liberation, DejaVu (for EN/DE)
- **Workspace**: `/workspace` (mounted from host)

## Development Workflows

### Initial Setup

```bash
# Clone repository (done)
git clone <repo-url> arc42-template-build
cd arc42-template-build

# Initialize submodule (CRITICAL - contains source content)
git submodule update --init --recursive
# OR
make update-submodule
```

### Running a Build

**Using Make (recommended)**:
```bash
make build           # Full build (EN + DE, all formats)
make help           # Show available targets
```

**Using Docker Compose directly**:
```bash
docker-compose build builder
docker-compose run --rm builder
```

**Testing outputs**:
```bash
./test.sh           # Verifies 6 expected files exist
```

### CLI Options (for development)

The Python CLI supports filtering:
```bash
# Inside container
python3 -m src.arc42_builder -l EN -f html       # EN HTML only
python3 -m src.arc42_builder -l DE -l EN -f pdf  # EN+DE PDF only
```

### Git Workflow

- **Main Branch**: Main development branch
- **Feature Branches**: Use `claude/` prefix (as per session requirement)
- **Submodule**: `arc42-template` points to https://github.com/arc42/arc42-template.git

## Key Files and Their Purpose

### Build System

| File | Purpose | Key Details |
|------|---------|-------------|
| `src/arc42_builder/cli.py` | Main build orchestrator | Contains all format conversion logic |
| `Dockerfile` | Container definition | Pins Asciidoctor 2.0.20, Asciidoctor-PDF 2.3.10 |
| `docker-compose.yaml` | Service orchestration | Mounts volumes for input/output |
| `Makefile` | Build convenience wrapper | Auto-detects docker-compose vs docker compose |

### Configuration

| File | Purpose | Format |
|------|---------|--------|
| `arc42-template/{LANG}/version.properties` | Version metadata | Java properties (key=value) |
| `requirements.txt` | Python dependencies | Minimal: click, pyyaml, pathlib |

### Documentation

| File | Purpose |
|------|---------|
| `README.md` | User-facing documentation |
| `todo/4-updated-solution-approach.md` | Detailed architecture proposal (future roadmap) |
| `todo/1-refined-arc42_build_process_requirements.md` | Requirements specification |

## Important Conventions

### Code Style

1. **Python**:
   - Use pathlib.Path for all file operations
   - Subprocess commands as list format (not strings)
   - Click decorators for CLI options
   - Type hints encouraged but not enforced

2. **Asciidoctor Attributes**:
   - Always pass `revnumber` and `revdate` from version.properties
   - Use absolute paths for `imagesdir` (e.g., `/workspace/arc42-template/images`)
   - Output files with `-o` flag for explicit control

3. **Naming Conventions**:
   - Output files: `arc42-template-{LANG}-{FLAVOR}.{ext}`
   - Example: `arc42-template-EN-withHelp.html`

### Docker Best Practices

1. **Volume Mounts**:
   - Source content (arc42-template): Read-only (`:ro`)
   - Output directories (build, dist, logs): Read-write
   - Python source (src): Read-only (`:ro`)

2. **Working Directory**: Always `/workspace` inside container

3. **Container Philosophy**: Self-contained - no host dependencies

## Common Tasks for AI Assistants

### Adding a New Format

1. **Create converter function** in `cli.py`:
   ```python
   def build_FORMAT(source_dir, output_dir, lang, version_props):
       """Build FORMAT output"""
       # Implementation
   ```

2. **Add to CLI choices**:
   ```python
   @click.option('--format', '-f', 'formats',
                 type=click.Choice(['html', 'pdf', 'docx', 'FORMAT']))
   ```

3. **Add to build loop**:
   ```python
   elif fmt == 'FORMAT':
       build_FORMAT(source_dir, output_dir, lang, version_props)
   ```

4. **Update test.sh** with expected output file

### Adding a New Language

1. **Verify submodule** has `arc42-template/{LANG}/` directory
2. **Update CLI choices**:
   ```python
   @click.option('--language', '-l', type=click.Choice(['EN', 'DE', 'LANG']))
   ```
3. **Install required fonts** in Dockerfile (if non-Latin script)
4. **Update test.sh** and README.md

### Debugging Build Issues

1. **Check submodule initialized**:
   ```bash
   ls -la arc42-template/
   # Should contain EN/, DE/, etc., not be empty
   ```

2. **Inspect container**:
   ```bash
   docker-compose run --rm builder bash
   # Explore /workspace
   ```

3. **View detailed errors**:
   - Python tracebacks appear in console
   - Asciidoctor errors show line numbers
   - Check `workspace/logs/` when implemented

### Modifying the Build Process

**Current State (PoC)**:
- All logic in single `cli.py` file
- No configuration file support
- Sequential builds (no parallelization)

**Future Architecture** (see `todo/4-updated-solution-approach.md`):
- Plugin-based converters (`src/arc42_builder/converters/`)
- YAML configuration (`config/build.yaml`)
- Parallel builds with ThreadPoolExecutor
- Proper validation phase
- ZIP packaging

**When making changes**:
- Keep PoC simple and focused
- Reference future architecture for design decisions
- Update both code AND documentation

## Testing Strategy

### Current Testing

```bash
./test.sh              # Checks 6 files exist
```

### Future Testing (Planned)

- **Unit Tests**: Pytest for individual converters
- **Integration Tests**: Full Docker-based builds
- **Validation**: AsciiDoc include/image reference checking

## CI/CD Considerations

**Current**: Manual builds only

**Planned** (per architecture docs):
- GitHub Actions with matrix builds
- Parallel builds per language
- Artifact upload to releases
- Docker image caching

## Troubleshooting Guide

### Common Issues

1. **Empty arc42-template/ directory**:
   ```bash
   git submodule update --init --recursive
   ```

2. **Permission errors in workspace/**:
   - Check Docker volume mounts
   - May need to adjust file ownership

3. **Asciidoctor command not found**:
   - Rebuild Docker image: `docker-compose build builder`
   - Check Dockerfile gem installation

4. **DOCX build fails**:
   - Requires Pandoc (included in Dockerfile)
   - Temp HTML file created then converted

5. **Version properties not found**:
   - Check `arc42-template/{LANG}/version.properties` exists
   - Fallback: empty string used

### Debugging Checklist

- [ ] Submodule initialized?
- [ ] Docker image built recently?
- [ ] workspace/ directories exist?
- [ ] Source AsciiDoc files present in arc42-template/?
- [ ] Correct working directory (/workspace in container)?

## Future Roadmap

See `todo/4-updated-solution-approach.md` for complete details. Key items:

- [ ] Plugin architecture for converters
- [ ] YAML configuration file
- [ ] Parallel builds
- [ ] More languages (FR, ZH, UKR, RU, CZ)
- [ ] More formats (Markdown, Confluence)
- [ ] Plain flavor support
- [ ] ZIP packaging
- [ ] Proper validation (includes, images, fonts)
- [ ] CI/CD integration
- [ ] Multi-page HTML output

## Important Notes for AI Assistants

1. **Submodule is Critical**: The `arc42-template/` directory is a Git submodule. Always ensure it's initialized. Empty directory = build will fail.

2. **Paths are Container-Relative**: Inside Docker, paths start with `/workspace`. Outside, they're relative to repo root.

3. **Version is a PoC**: Code prioritizes simplicity over robustness. Don't over-engineer.

4. **Follow Future Architecture**: When enhancing beyond PoC scope, consult `todo/4-updated-solution-approach.md` for approved design patterns.

5. **Test Before Committing**: Run `make build && ./test.sh` to verify changes.

6. **Document Changes**: Update README.md and this file when changing workflows or structure.

## Quick Reference

| Task | Command |
|------|---------|
| Full build | `make build` |
| Update submodule | `make update-submodule` |
| Test outputs | `./test.sh` |
| Clean outputs | `rm -rf workspace/build/*` |
| Enter container | `docker-compose run --rm builder bash` |
| Rebuild Docker image | `docker-compose build builder` |

## Version History

- **0.1.0** (Current): Initial PoC
  - Languages: EN, DE
  - Formats: HTML, PDF, DOCX
  - Flavor: withHelp only
  - Architecture: Monolithic CLI

---

**Last Updated**: 2025-11-17
**arc42 Template Version**: 9.0 (submodule updated to commit f507ad6)
**Maintainer**: arc42 team
**License**: (See LICENSE file)
