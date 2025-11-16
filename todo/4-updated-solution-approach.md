# arc42 Build Process - Updated Solution Proposal (v2)

## Executive Summary

This document proposes a **Python-based, Docker-containerized build system** for the arc42 template that fulfills all requirements while maintaining simplicity, maintainability, and extensibility. The solution uses a plugin-based architecture for format converters, YAML-based configuration, and provides both CLI and CI/CD integration.

This updated version incorporates refinements to improve robustness, clarify implementation details, and optimize performance.

**Key Technology Choices:**
- **Orchestration**: Python 3.11+ with Click CLI framework
- **Containerization**: Docker with multi-stage builds containing ALL required fonts
- **Primary Conversion Tools**: Asciidoctor, Pandoc
- **Font Support**: Complete Unicode coverage for DE, EN, CZ, UKR, RU, ZH (and extensible for others)
- **Configuration**: YAML with JSON Schema validation
- **Testing**: Pytest with Docker-based integration tests
- **CI/CD**: GitHub Actions with matrix builds

**Important Design Principle**: The Docker container is completely self-contained. No fonts, tools, or dependencies from the host machine are used. Everything required for the build is installed inside the container.

---

## 1. Architecture Overview

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Docker Container                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Python Orchestrator (CLI)               │   │
│  │                                                      │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────────┐ │   │
│  │  │  Config  │  │Validator │  │  Build Pipeline   │ │   │
│  │  │  Loader  │  │          │  │    Controller     │ │   │
│  │  └──────────┘  └──────────┘  └──────────────────┘ │   │
│  │                                                      │   │
│  │  ┌─────────────────────────────────────────────┐   │   │
│  │  │          Format Converter Plugins           │   │   │
│  │  │ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐      │   │   │
│  │  │ │ HTML │ │ PDF  │ │ DOCX │ │  MD  │ ...  │   │   │
│  │  │ └──────┘ └──────┘ └──────┘ └──────┘      │   │   │
│  │  └─────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                  Conversion Tools                    │   │
│  │         Asciidoctor | Pandoc | etc.               │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘

Inputs:                          Outputs:
- arc42-template repo     →      - build/ (artifacts)
- build.yaml config       →      - dist/ (ZIP files)
- version.properties      →      - logs/
```

### 1.2 Component Responsibilities

| Component | Responsibility |
|-----------|---------------|
| **CLI Orchestrator** | Main entry point, coordinates build process. |
| **Config Loader** | Parses and validates YAML configuration. |
| **Validator** | **(Refined)** Runs pre-build checks: validates `version.properties`, verifies `include::` and `image::` references using the AsciiDoc toolchain, and confirms required fonts are installed in the container. |
| **Build Controller**| Manages the build pipeline execution. |
| **Format Plugins** | Format-specific conversion logic. |
| **Packager** | Creates ZIP archives for distribution. |

---

## 2. Technology Stack

### 2.1 Core Technologies

| Layer | Technology | Justification |
|-------|------------|--------------|
| **Orchestration** | Python 3.11+ | Excellent ecosystem, readable, maintainable |
| **CLI Framework** | Click 8.1+ | Robust CLI with subcommands, options, help |
| **Configuration** | PyYAML + jsonschema | YAML parsing with validation |
| **Logging** | Python logging + Rich | Structured logs with pretty console output |
| **Testing** | Pytest + Docker | Unit and integration testing |
| **Containerization** | Docker 24+ | Reproducible builds, tool isolation |

### 2.2 Conversion Tools

| Format | Primary Tool | Conversion Path |
|--------|-------------|-----------------|
| **HTML** | Asciidoctor | AsciiDoc → HTML |
| **PDF** | Asciidoctor PDF | AsciiDoc → PDF |
| **DOCX** | Pandoc | AsciiDoc → HTML → DOCX |
| **Markdown** | Asciidoctor + Pandoc | AsciiDoc → HTML → Markdown |
| **AsciiDoc** | Asciidoctor | AsciiDoc → Preprocessed AsciiDoc (single file) |
| **Confluence** | Asciidoctor | AsciiDoc → XHTML (Confluence dialect) |
| **LaTeX** | Pandoc | AsciiDoc → LaTeX |

### 2.3 Supporting Libraries

```python
# requirements.txt
click>=8.1.0
pyyaml>=6.0
jsonschema>=4.17.0
jinja2>=3.1.0          # Template processing
rich>=13.0.0           # Pretty console output
python-dotenv>=1.0.0   # Environment configuration
gitpython>=3.1.0       # Git operations
pathlib>=1.0.0        # Path handling
dataclasses>=0.6      # Configuration models
```

---

## 3. Directory Structure

### 3.1 Build Repository Structure

```
arc42-build/
├── docker/
│   ├── Dockerfile                 # Multi-stage build
│   ├── requirements.txt          # Python dependencies
│   └── tools-versions.txt        # Tool version pins
├── src/
│   ├── arc42_builder/
│   │   ├── __main__.py          # CLI entry point
│   │   ├── cli.py               # Click CLI definition
│   │   ├── config/
│   │   │   ├── loader.py        # Configuration loading
│   │   │   ├── schema.json      # Config JSON schema
│   │   │   └── models.py        # Config dataclasses
│   │   ├── core/
│   │   │   ├── builder.py       # Main build controller
│   │   │   ├── validator.py     # Pre-build validation
│   │   │   └── packager.py      # ZIP packaging
│   │   ├── converters/
│   │   │   ├── base.py          # Abstract converter
│   │   │   ├── html.py          # HTML converter
│   │   │   ├── pdf.py           # PDF converter
│   │   │   ├── docx.py          # DOCX converter
│   │   │   ├── markdown.py      # Markdown converter
│   │   │   ├── asciidoc.py      # AsciiDoc pass-through converter
│   │   │   └── __init__.py      # Plugin registry
│   │   └── utils/
│   │       ├── logging.py       # Logging setup
│   │       ├── paths.py         # Path utilities
│   │       └── git.py           # Git operations
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── config/
│   ├── build.yaml               # Default configuration
│   └── examples/
├── .github/
│   └── workflows/
│       ├── build.yml           # CI build workflow
│       └── release.yml         # Release workflow
├── docker-compose.yml
├── Makefile
├── README.md
└── LICENSE
```

### 3.2 Runtime Directory Structure

(No changes from original proposal)

---

## 4. Core Implementation Details

### 4.1 Configuration Model (Refined)

The configuration is updated to clarify multi-page outputs and include the `asciidoc` pass-through format.

```yaml
# config/build.yaml
version: "1.0"
template:
  repository: "https://github.com/arc42/arc42-template.git"
  ref: "main"
  path: "./arc42-template"

languages: [EN, DE, FR, CZ, ES, IT, NL, PT, RU, UKR, ZH]

formats:
  html:
    enabled: true
    priority: 1
    options:
      # Future: add multi-page support
      single_page: true
  pdf:
    enabled: true
    priority: 1
    options:
      page_size: "A4"
      use_language_themes: true
  docx:
    enabled: true
    priority: 1
    options: {}
  markdown:
    enabled: true
    priority: 1
    options:
      variant: "gfm"
      # If false, generates one .md file per chapter
      multi_page: false
  asciidoc:
    enabled: true
    priority: 1
    options:
      # Creates a single, self-contained .adoc file with all includes processed
      bundle_includes: true

flavors: [plain, withHelp]

build:
  parallel: true
  max_workers: 4
  validate: true
  clean_before: true
  create_zips: true
  verify_fonts: true

logging:
  level: "INFO"
  file: true
  console: true
```

### 4.2 Plugin Architecture for Converters (Refined)

The core architecture remains, but the `HtmlConverter` is simplified, and a new `AsciidocConverter` is added.

```python
# src/arc42_builder/converters/base.py
# (No changes from original proposal)

# src/arc42_builder/converters/html.py (Refined for robust flavor handling)
import subprocess
from pathlib import Path
from .base import ConverterPlugin, BuildContext

class HtmlConverter(ConverterPlugin):
    def __init__(self):
        super().__init__("html", priority=1)
    
    def check_dependencies(self) -> bool:
        # ... (same as before)
    
    def convert(self, context: BuildContext) -> Path:
        output_file = context.output_dir / f"arc42-template-{context.language}-{context.flavor}.html"
        
        # Build asciidoctor command
        cmd = [
            "asciidoctor",
            "-b", "html5",
            "-a", f"revnumber={context.version_props['revnumber']}",
            "-a", f"revdate={context.version_props['revdate']}",
            # REFINED: Pass flavor as an attribute for AsciiDoc's conditional processing
            "-a", f"flavor={context.flavor}",
            "-D", str(context.output_dir),
            "-o", str(output_file),
            str(context.source_dir / "arc42-template.adoc")
        ]
        
        # REFINED: If flavor is 'withHelp', define the 'show-help' attribute.
        # The AsciiDoc source should use ifdef::show-help[] or ifeval::["{flavor}" == "withHelp"]
        if context.flavor == "withHelp":
            cmd.append("-a show-help")
        
        subprocess.run(cmd, check=True)
        return output_file
    
    def get_output_extension(self) -> str:
        return ".html"

# src/arc42_builder/converters/asciidoc.py (New Plugin)
import subprocess
from pathlib import Path
from .base import ConverterPlugin, BuildContext

class AsciidocConverter(ConverterPlugin):
    """
    A 'pass-through' converter that produces a single, self-contained AsciiDoc file
    with all includes processed.
    """
    def __init__(self):
        super().__init__("asciidoc", priority=1)

    def check_dependencies(self) -> bool:
        # ... (checks for asciidoctor)

    def convert(self, context: BuildContext) -> Path:
        output_file = context.output_dir / f"arc42-template-{context.language}-{context.flavor}.adoc"
        
        cmd = [
            "asciidoctor",
            "-b", "docbook", # Backend doesn't matter, we just want the preprocessed source
            "--no-header-footer",
            "-a", f"flavor={context.flavor}",
            # ... other attributes ...
            str(context.source_dir / "arc42-template.adoc"),
            "-o", "-" # Output to stdout
        ]
        if context.flavor == "withHelp":
            cmd.append("-a show-help")

        # Run asciidoctor to get the fully resolved content
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Write the captured stdout to the output file
        output_file.write_text(result.stdout, encoding='utf-8')
        
        return output_file

    def get_output_extension(self) -> str:
        return ".adoc"
```

### 4.3 Flavor Processing (Removed)

**(Refinement)** This section is removed. The original proposal for a Python-based `FlavorProcessor` that uses regex is brittle. The refined approach delegates flavor handling entirely to AsciiDoctor's native conditional processing directives (e.g., `ifdef::show-help[]`), which is more robust and simplifies the build script. The build orchestrator is only responsible for passing the correct attributes to the `asciidoctor` command.

### 4.4 Build Pipeline Controller (Refined)

The controller is simplified by removing the flavor preprocessing step.

```python
# src/arc42_builder/core/builder.py
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
# ... other imports

from ..converters import get_converter
from ..config.models import BuildConfig
from .validator import Validator
from .packager import Packager

class BuildPipeline:
    def __init__(self, config: BuildConfig):
        self.config = config
        self.validator = Validator(config) # Validator may need config
        self.packager = Packager()
        self.logger = logging.getLogger(__name__)
    
    def run(self) -> Dict[str, List[Path]]:
        """Execute complete build pipeline"""
        
        # Phase 1: Validation (Refined)
        self.logger.info("Phase 1: Validating sources and environment...")
        # The validator now performs more detailed checks
        self.validator.run_all_validations()
        self.logger.info("✓ Validation successful.")
        
        # Phase 2: Build matrix generation
        build_matrix = self._generate_build_matrix()
        
        # Phase 3: Parallel execution
        # ... (no changes to execution logic)
        
        # Phase 4: Packaging
        # ... (no changes)
        
        return results
    
    def _generate_build_matrix(self) -> List[Dict]:
        # ... (no changes)

    def _build_single(self, task: Dict) -> Path:
        """Build single artifact"""
        # ... (logging)
        
        converter = get_converter(task['format'])
        
        context = BuildContext(
            language=task['language'],
            flavor=task['flavor'],
            source_dir=self.config.template_path / task['language'] / 'asciidoc',
            output_dir=Path('build') / task['language'] / task['flavor'] / task['format'],
            version_props=self._load_version_props(task['language']),
            config=task['config']
        )
        
        context.output_dir.mkdir(parents=True, exist_ok=True)
        
        # REFINED: The flavor preprocessing step is removed.
        # The responsibility is now fully on the converter plugins
        # to use the correct AsciiDoc attributes.
        
        output_path = converter.convert(context)
        self.logger.info(f"Created: {output_path}")
        
        return output_path
```

---

## 5. Docker Configuration

### 5.1 Dockerfile
(No changes from original proposal)

### 5.2 Docker Compose
(No changes from original proposal)

### 5.3 Docker Image Optimization Strategy (New)

**(Refinement)** The proposed `Dockerfile` is comprehensive but will produce a very large Docker image (potentially 1-2 GB+) due to the inclusion of font packages for all languages (especially CJK). While simple, this can be inefficient for CI environments.

**Alternative Strategy:**

For CI/CD pipelines, we can define multiple, smaller Docker images tailored to specific language sets. This can be achieved with separate Dockerfiles or multi-stage builds with different targets.

- **`arc42-builder:latin`**: Base image with fonts for Latin-based languages (EN, DE, ES, etc.).
- **`arc42-builder:cyrillic`**: Extends the `latin` image with Cyrillic fonts (for RU, UKR).
- **`arc42-builder:cjk`**: Extends the `latin` image with CJK fonts (for ZH).
- **`arc42-builder:full`**: The default image that includes all fonts.

The GitHub Actions matrix could then be configured to pull the appropriate, smaller image for the language it is building, saving significant time on image downloads and reducing disk space usage. For local development, the `full` image remains a convenient default. This is a trade-off between complexity and performance that can be implemented as a future optimization.

---

## 6. CLI Interface
(No changes from original proposal)

---

## 7. Testing Strategy
(No changes from original proposal)

---

## 8. CI/CD Integration
(No changes from original proposal, but would be adapted if using the Docker image optimization strategy from section 5.3)

---

## 9. Extension Points
(No changes from original proposal)

---

## 10. Implementation Roadmap
(No changes from original proposal)

---

## 11. Key Design Decisions

### 11.1 - 11.3
(No changes from original proposal)

### 11.4 Flavor Processing Strategy (Refined)
- **Decision**: Delegate flavor processing entirely to the AsciiDoc toolchain. The build orchestrator passes attributes (`-a flavor=withHelp`, `-a show-help`) to the `asciidoctor` command. The AsciiDoc source files are responsible for using conditional directives (`ifdef`, `ifeval`) to include or exclude help text based on these attributes.
- **Alternative Considered**: Manually preprocessing AsciiDoc files with Python regex.
- **Rationale**: The refined approach is far more robust, simpler to maintain, and correctly separates the concerns of the build tool from the content. It leverages the power of the AsciiDoc toolchain instead of reinventing it.

---

## 12. Open Questions Resolution
(No changes from original proposal)

---

## Appendices
(No changes from original proposal)
