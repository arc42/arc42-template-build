# arc42-template-build

**Docker-only build system for the arc42 architecture documentation template**

Generate arc42 templates in multiple languages, formats, and flavors using a modern, reproducible, containerized build pipeline.

---

## 🚀 Quick Start

### Prerequisites

**Only requirement: Docker** (or Docker Compose)

- No Python, Ruby, Node.js, or other tools needed on your host!
- Works on Linux, macOS, Windows (Docker Desktop)
- Works in GitHub Codespaces
- Works in any CI/CD with Docker support

Install Docker: https://docs.docker.com/get-docker/

### Build Everything

```bash
# Check prerequisites
make check

# Initialize template submodule (first time only)
make update-submodule

# Build all templates
make build
```

That's it! Outputs will be in `workspace/build/`

---

## 📋 Available Commands

### Essential Commands

| Command | Description |
|---------|-------------|
| `make build` | Build all templates (default target) |
| `make check` | Verify Docker is available and setup is correct |
| `make clean` | Remove all generated artifacts |
| `make help` | Show all available commands |

### Development Commands

| Command | Description |
|---------|-------------|
| `make validate` | Run pre-build validation (inside Docker) |
| `make test` | Run test suite (inside Docker) |
| `make shell` | Open a shell in the container for debugging |
| `make build-image` | Build Docker image without running build |

### Submodule Management

| Command | Description |
|---------|-------------|
| `make update-submodule` | Update to commit referenced in parent repo (safe, recommended) |
| `make update-submodule-latest` | Update to latest commit from master branch |
| `make update-submodule-latest SUBMODULE_BRANCH=<branch>` | Update to latest from specific branch |

### Advanced Usage

```bash
# Build specific language and format
docker compose run --rm builder build --lang EN --format pdf

# Build with specific flavor
docker compose run --rm builder build --lang DE --format html --flavor plain

# Show available formats
docker compose run --rm builder list-formats

# Run validation only
make validate
```

---

## 🏗️ How It Works

### Architecture

```
┌─────────────────────────────────────────┐
│         Docker Container                 │
│  ┌────────────────────────────────────┐ │
│  │  Python Build Orchestrator         │ │
│  │  - Configuration System            │ │
│  │  - Format Converter Plugins        │ │
│  │  - Parallel Build Pipeline         │ │
│  └────────────────────────────────────┘ │
│  ┌────────────────────────────────────┐ │
│  │  Conversion Tools                  │ │
│  │  - Asciidoctor + PDF               │ │
│  │  - Pandoc                          │ │
│  │  - Full Unicode Fonts              │ │
│  └────────────────────────────────────┘ │
└─────────────────────────────────────────┘
          ↓                    ↑
    Reads from            Writes to
          ↓                    ↑
┌──────────────────┐  ┌──────────────────┐
│ arc42-template/  │  │ workspace/build/ │
│ (AsciiDoc)       │  │ (HTML/PDF/DOCX)  │
└──────────────────┘  └──────────────────┘
```

### Build Process

1. **Configuration** - Loads `config/build.yaml` to determine what to build
2. **Validation** - Checks template sources, fonts, includes, images
3. **Generation** - Converts AsciiDoc to target formats in parallel
4. **Output** - Creates organized directory structure with all artifacts

### Supported Outputs

**Languages:** EN, DE, FR, CZ, ES, IT, NL, PT, RU, UKR, ZH

**Formats:**
- HTML (single-page)
- PDF (with full font support for all languages)
- DOCX (Microsoft Word)
- Markdown (GitHub-flavored)
- AsciiDoc (pass-through)

**Flavors:**
- `plain` - Only section headings and minimal text
- `withHelp` - Full explanatory text and guidance

---

## ⚙️ Configuration

Edit `config/build.yaml` to customize your build:

```yaml
# Select languages
languages:
  - EN
  - DE
  # - FR
  # ...

# Enable/disable formats
formats:
  html:
    enabled: true
    priority: 1
  pdf:
    enabled: true
    priority: 1
    options:
      page_size: "A4"
  # ...

# Choose flavors
flavors:
  - plain
  - withHelp

# Build settings
build:
  parallel: true
  max_workers: 4
  validate: true
```

### Environment Variables

Override settings via environment variables:

```bash
# Override max workers
export ARC42_BUILD_MAX_WORKERS=8

# Change log level
export ARC42_LOG_LEVEL=DEBUG

# Build with overrides
make build
```

---

## 📂 Project Structure

```
arc42-template-build/
├── arc42-template/         # Git submodule with arc42 content
├── config/
│   ├── build.yaml         # Main configuration file
│   └── schema.json        # Configuration validation schema
├── docker/
│   ├── Dockerfile         # Multi-stage Docker build
│   ├── custom-fonts/      # Optional custom fonts
│   └── pdf-themes/        # Optional PDF themes
├── src/arc42_builder/     # Python build system
│   ├── config/           # Configuration loading
│   ├── converters/       # Format converter plugins
│   ├── core/             # Build pipeline and validator
│   └── cli.py            # Command-line interface
├── workspace/
│   ├── build/            # Generated artifacts
│   ├── dist/             # ZIP archives (if enabled)
│   └── logs/             # Build logs
├── docker-compose.yaml    # Container orchestration
├── Makefile              # Build commands
└── README.md             # This file
```

---

## 🔧 Development

### Opening a Shell

Debug or explore inside the container:

```bash
make shell
```

Inside the container:
```bash
# Run CLI directly
python3 -m src.arc42_builder --help

# Check installed tools
asciidoctor --version
pandoc --version

# List installed fonts
fc-list | grep -i noto
```

### Adding a New Format

1. Create a converter plugin in `src/arc42_builder/converters/`
2. Inherit from `ConverterPlugin` base class
3. Implement `convert()` and `check_dependencies()` methods
4. Register in `converters/__init__.py`
5. Add format config to `config/build.yaml`

See existing converters for examples.

### Running Tests

```bash
# Run all tests
make test

# Or run pytest directly in container
docker compose run --rm builder pytest /app/tests -v
```

---

## 🌐 GitHub Codespaces

This project is fully configured for GitHub Codespaces:

1. Click **Code** → **Codespaces** → **Create codespace on [branch]**
2. Wait for container to initialize (auto-runs `make check`)
3. Run `make build` in the terminal

The `.devcontainer/` configuration provides:
- Docker-in-Docker support
- Pre-installed extensions (Docker, Python, YAML)
- Automatic submodule initialization

---

## 🐳 CI/CD Integration

### GitHub Actions Example

```yaml
name: Build Templates
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          submodules: true
      - name: Build
        run: make build
      - uses: actions/upload-artifact@v3
        with:
          name: arc42-templates
          path: workspace/build/
```

### Other CI Systems

Any CI system with Docker support works:

```bash
# Generic CI script
docker compose build builder
docker compose run --rm builder build --all
```

---

## 📝 Requirements & Design

Detailed documentation:

- **Requirements**: `todo/1-refined-arc42_build_process_requirements.md`
- **Solution Approach**: `todo/4-updated-solution-approach.md`
- **Implementation Notes**: `todo/5-configuration-system-implementation.md`

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make changes (all inside Docker, no local deps needed!)
4. Run `make test` and `make validate`
5. Submit a pull request

---

## 📜 License

This build system is open source. See LICENSE file.

The arc42 template itself is licensed separately - see https://arc42.org/license

---

## 🆘 Troubleshooting

### "Docker not found"

Install Docker: https://docs.docker.com/get-docker/

### "Template submodule not initialized" or submodule errors

**First time setup:**
```bash
make update-submodule
```

**If the referenced commit doesn't exist or submodule is corrupted:**
```bash
# Safe: updates to latest from master and shows you what changed
make update-submodule-latest

# Or update to a specific branch
make update-submodule-latest SUBMODULE_BRANCH=9.0-draft
```

The `update-submodule` target is error-resistant and will automatically:
- Try standard git submodule update first
- Fall back to re-cloning if the update fails
- Provide helpful error messages if the referenced commit doesn't exist

### "Font missing" errors

The Docker image includes comprehensive font support. If you see font errors:
1. Rebuild the image: `make build-image`
2. Check installed fonts: `make shell` then `fc-list`

### Build fails

```bash
# Check validation
make validate

# Clean and rebuild
make clean
make build

# Debug in shell
make shell
python3 -m src.arc42_builder validate
```

### Performance

Adjust parallel workers in `config/build.yaml`:

```yaml
build:
  max_workers: 8  # Increase for more CPU cores
```

---

## 📧 Support

- Issues: https://github.com/arc42/arc42-template-build/issues
- arc42 Docs: https://docs.arc42.org
- arc42 Community: https://arc42.org

---

**Built with ❤️ using Python, Docker, Asciidoctor, and Pandoc**
