# arc42-template-build – Architecture Documentation

**About arc42:** This architecture documentation uses the arc42 template. It's the project's own "eating our own dog food" example.

**Version:** 0.2.0
**Status:** Proof of Concept → Production-Ready
**Last Updated:** 2025-11-18

---

## 1. Introduction and Goals

### What is arc42-template-build?

arc42-template-build is a Docker-based build system that generates the arc42 architecture documentation template in multiple languages, formats, and content flavors.

### Quality Goals

| Priority | Quality Goal | Motivation |
|----------|-------------|------------|
| 1 | **Reproducibility** | Builds must be deterministic and version-controlled |
| 1 | **Developer Experience** | Single command (`make build`) to generate all outputs |
| 2 | **Extensibility** | Easy to add new formats, languages, or templates |
| 2 | **Maintainability** | Clean separation of concerns, plugin architecture |
| 3 | **Performance** | Parallel builds for multiple format/language combinations |

### Key Stakeholders

| Role | Concerns |
|------|----------|
| arc42 Core Team | Reliable release artifacts, easy maintenance |
| Translators | Validation of translations, font support for all scripts |
| Users/Developers | High-quality output in preferred format (PDF, Markdown, etc.) |
| Contributors | Easy to understand, test, and extend the build system |

---

## 2. Constraints

### Technical Constraints

| Constraint | Rationale |
|------------|-----------|
| **Docker-only execution** | Ensures reproducibility across all platforms |
| **Open-source tools only** | No proprietary software or SaaS dependencies |
| **Python 3.11+ orchestrator** | Modern, readable orchestration with strong typing |
| **Ubuntu 22.04 base image** | Stable, well-supported foundation with comprehensive packages |

### Organizational Constraints

| Constraint | Impact |
|------------|--------|
| Two-repository model | Build logic separated from content (arc42-template submodule) |
| GitHub as primary platform | CI/CD via GitHub Actions, releases via GitHub Releases |

---

## 3. Context and Scope

### Business Context

```
┌─────────────────────────────────────────────────────────┐
│                   arc42 Ecosystem                        │
│                                                          │
│  ┌──────────────┐                    ┌───────────────┐ │
│  │ arc42-       │  reads/validates   │ arc42-        │ │
│  │ template-    │◄───────────────────┤ template      │ │
│  │ build        │                    │ (submodule)   │ │
│  │              │                    │               │ │
│  │ (this repo)  │                    │ (content)     │ │
│  └──────┬───────┘                    └───────────────┘ │
│         │                                               │
│         │ produces                                      │
│         ▼                                               │
│  ┌──────────────┐                                      │
│  │ Build        │                                      │
│  │ Artifacts    │                                      │
│  │              │                                      │
│  │ • HTML       │                                      │
│  │ • PDF        │                                      │
│  │ • Markdown   │                                      │
│  │ • DOCX       │                                      │
│  │ • etc.       │                                      │
│  └──────┬───────┘                                      │
│         │                                               │
│         │ downloaded/used by                            │
│         ▼                                               │
│  ┌──────────────┐                                      │
│  │ Developers   │                                      │
│  │ and Teams    │                                      │
│  └──────────────┘                                      │
└─────────────────────────────────────────────────────────┘
```

### Technical Context

**Input:**
- AsciiDoc source files from `arc42-template/` submodule
- `version.properties` files per language
- Images (PNG/JPG diagrams)
- Build configuration (`config/build.yaml`)

**Output:**
- Structured directory tree: `workspace/build/{LANG}/{FLAVOR}/{FORMAT}/`
- ZIP distributions: `workspace/dist/{LANG}/{FLAVOR}/{FORMAT}/*.zip`
- Validation reports and logs

**Tools:**
- **Asciidoctor 2.0.20**: AsciiDoc → HTML/PDF conversion
- **Asciidoctor-PDF 2.3.10**: Direct PDF generation
- **Pandoc**: Format conversion (HTML → Markdown, DOCX, RST, etc.)
- **Python 3.11**: Build orchestration with Click CLI
- **Docker Compose**: Container orchestration

---

## 4. Solution Strategy

### Architecture Approach

**Plugin-Based Converter System:**
- Each output format is a plugin implementing the `ConverterPlugin` interface
- Central `BuildPipeline` orchestrates parallel builds
- Configuration-driven: all build options in `config/build.yaml`

**Key Design Decisions:**

| Decision | Rationale |
|----------|-----------|
| **Python orchestrator** | Better than shell for complex logic, good library ecosystem |
| **Plugin architecture** | New formats added by creating single converter class |
| **Two-phase approach** | Asciidoctor → intermediate HTML → Pandoc (flexible conversions) |
| **Parallel execution** | ThreadPoolExecutor for concurrent builds (4 workers default) |
| **Validation-first** | Pre-flight checks prevent wasted build time |

### Technology Choices

```
AsciiDoc Sources
      │
      ▼
┌─────────────────────┐
│   Asciidoctor       │ ──► HTML, PDF (direct)
│   (Ruby)            │
└─────────────────────┘
      │
      ▼ (intermediate HTML)
┌─────────────────────┐
│   Pandoc            │ ──► Markdown, DOCX, RST, Textile
│   (Haskell)         │
└─────────────────────┘
      │
      ▼ (specific backends)
┌─────────────────────┐
│ Asciidoctor-        │ ──► Confluence XHTML
│ Confluence          │
└─────────────────────┘
```

---

## 5. Building Block View

### Level 1: System Overview

```
┌───────────────────────────────────────────────────────────┐
│              arc42-template-build (Docker Container)       │
│                                                            │
│  ┌────────────────────────────────────────────────────┐  │
│  │  CLI Interface (src/arc42_builder/cli.py)          │  │
│  │  • build    • validate    • test-artifacts         │  │
│  │  • dist     • test        • list-formats           │  │
│  └────────────────────┬───────────────────────────────┘  │
│                       │                                   │
│                       ▼                                   │
│  ┌────────────────────────────────────────────────────┐  │
│  │  Core (src/arc42_builder/core/)                    │  │
│  │  ┌──────────────┐  ┌────────────┐                 │  │
│  │  │ BuildPipeline│  │ Validator  │                 │  │
│  │  │              │  │            │                 │  │
│  │  │ • orchestrate│  │ • validate │                 │  │
│  │  │ • parallel   │  │ • check    │                 │  │
│  │  └──────┬───────┘  └────────────┘                 │  │
│  └─────────┼──────────────────────────────────────────┘  │
│            │                                              │
│            ▼                                              │
│  ┌────────────────────────────────────────────────────┐  │
│  │  Converters (src/arc42_builder/converters/)        │  │
│  │  ┌──────┐ ┌──────┐ ┌─────────┐ ┌──────────┐       │  │
│  │  │ HTML │ │ PDF  │ │Markdown │ │Confluence│  ...  │  │
│  │  └──────┘ └──────┘ └─────────┘ └──────────┘       │  │
│  └────────────────────────────────────────────────────┘  │
│                                                            │
│  ┌────────────────────────────────────────────────────┐  │
│  │  Configuration (src/arc42_builder/config/)         │  │
│  │  • ConfigLoader    • Models                        │  │
│  └────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────┘
```

### Level 2: Converter Plugin Architecture

Each converter follows this interface:

```python
class ConverterPlugin(ABC):
    def __init__(self, name: str, priority: int):
        self.name = name
        self.priority = priority

    def check_dependencies(self) -> bool:
        """Verify required tools available"""

    def convert(self, context: BuildContext) -> Path:
        """Execute conversion, return output path"""

    def get_output_extension(self) -> str:
        """Return file extension (.html, .pdf, etc.)"""
```

**Implemented Converters:**

| Converter | Priority | Dependencies | Output |
|-----------|----------|-------------|--------|
| HtmlConverter | 1 | asciidoctor | Single-page HTML |
| PdfConverter | 1 | asciidoctor-pdf | PDF with fonts |
| DocxConverter | 1 | asciidoctor, pandoc | Microsoft Word |
| MarkdownConverter | 1 | asciidoctor, pandoc | Single-file GFM |
| MarkdownMpConverter | 1 | asciidoctor, pandoc | Multi-page Markdown |
| GithubMarkdownConverter | 2 | asciidoctor, pandoc | GitHub-optimized MD |
| GithubMarkdownMpConverter | 2 | asciidoctor, pandoc | Multi-page GitHub MD |
| ConfluenceConverter | 2 | asciidoctor-confluence | Confluence XHTML |
| RstConverter | 3 | asciidoctor, pandoc | reStructuredText |
| TextileConverter | 3 | asciidoctor, pandoc | Textile markup |
| AsciidocConverter | 1 | asciidoctor | Bundled AsciiDoc |

### Level 3: Key Components

**ConfigLoader** (`src/arc42_builder/config/loader.py`):
- Parses YAML configuration
- Validates against schema
- Provides strongly-typed config objects

**BuildPipeline** (`src/arc42_builder/core/builder.py`):
- Iterates over language × flavor × format matrix
- Executes converters in parallel (ThreadPoolExecutor)
- Handles errors and logging

**Validator** (`src/arc42_builder/core/validator.py`):
- Pre-build: checks template structure, version files, fonts
- Source validation: verifies includes, images exist
- Post-build: validates Markdown syntax using Pandoc

---

## 6. Runtime View

### Build Process Flow

```
┌─────────────┐
│ make build  │
└──────┬──────┘
       │
       ▼
┌──────────────────────────────────────┐
│ 1. Build Docker Image                │
│    docker compose build builder      │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│ 2. Run Container                     │
│    docker compose run builder        │
└──────┬───────────────────────────────┘
       │
       ▼ (inside container)
┌──────────────────────────────────────┐
│ 3. Load Configuration                │
│    • Parse build.yaml                │
│    • Determine build matrix          │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│ 4. Validation Phase                  │
│    • Check template directory        │
│    • Verify version.properties       │
│    • Check AsciiDoc includes         │
│    • Scan for missing images         │
│    • Verify fonts installed          │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│ 5. Build Phase (Parallel)            │
│                                      │
│  ┌───────────┐  ┌───────────┐       │
│  │ EN/plain/ │  │EN/withHelp│  ...  │
│  │  html     │  │  html     │       │
│  │  pdf      │  │  pdf      │       │
│  │  markdown │  │  markdown │       │
│  └───────────┘  └───────────┘       │
│                                      │
│  ThreadPoolExecutor (4 workers)      │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│ 6. Output                            │
│    workspace/build/{LANG}/{FLAVOR}/  │
│                    {FORMAT}/         │
└──────────────────────────────────────┘
```

### Converter Execution Pattern

For each format (e.g., Markdown):

```
1. MarkdownConverter.check_dependencies()
   ├─► Check asciidoctor available
   └─► Check pandoc available

2. MarkdownConverter.convert(context)
   ├─► Generate intermediate HTML
   │   └─► asciidoctor -b html5 template.adoc -o temp.html
   │
   ├─► Convert HTML to Markdown
   │   └─► pandoc temp.html -f html -t gfm -o output.md
   │
   └─► Clean up temporary files
       └─► temp.html.unlink()

3. Return output path
```

---

## 7. Deployment View

### Docker Container Structure

```
┌─────────────────────────────────────────┐
│  Docker Image: arc42-builder            │
│  Base: Ubuntu 22.04                      │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │ Layer 1: System Dependencies       │ │
│  │ • Ruby + gems (asciidoctor)        │ │
│  │ • Python 3.11 + pip                │ │
│  │ • Pandoc                           │ │
│  │ • Fonts (Noto, Liberation, CJK)    │ │
│  └────────────────────────────────────┘ │
│  ┌────────────────────────────────────┐ │
│  │ Layer 2: Python Environment        │ │
│  │ • click, pyyaml, pathlib           │ │
│  └────────────────────────────────────┘ │
│  ┌────────────────────────────────────┐ │
│  │ Layer 3: Application Code          │ │
│  │ • src/arc42_builder/               │ │
│  │ • config/build.yaml                │ │
│  └────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

### Volume Mounts

```
Host                          Container
────────────────────────────  ─────────────────
./arc42-template/    ──────►  /workspace/arc42-template/ (ro)
./src/               ──────►  /app/src/ (ro)
./config/            ──────►  /app/config/ (ro)
./workspace/build/   ◄──────  /workspace/build/ (rw)
./workspace/dist/    ◄──────  /workspace/dist/ (rw)
./workspace/logs/    ◄──────  /workspace/logs/ (rw)
```

### Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `PYTHONPATH` | `/app` | Python module resolution |
| `LANG` | `C.UTF-8` | UTF-8 locale support |
| `RUBYOPT` | `-Eutf-8` | Ruby UTF-8 encoding |

---

## 8. Cross-Cutting Concepts

### Configuration Management

**Hierarchical Configuration:**
```yaml
# config/build.yaml
languages: [EN, DE]
formats:
  html:
    enabled: true
    priority: 1
    options:
      single_page: true
flavors: [plain, withHelp]
build:
  parallel: true
  max_workers: 4
```

**Override via CLI:**
```bash
python -m src.arc42_builder build --lang EN --format pdf
```

### Error Handling

**Validation Errors:**
- Fail fast during validation phase
- Clear error messages with file paths and line numbers
- Example: "Missing image: images/diagram-01.png referenced in EN/src/05_building_block_view.adoc:42"

**Conversion Errors:**
- Continue on error by default (`continue_on_error: true`)
- Collect all errors and report at end
- Option for fail-fast mode

### Logging Strategy

```python
logging.basicConfig(
    level="INFO",
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)
```

**Log Levels:**
- `DEBUG`: Detailed command execution, file operations
- `INFO`: Build progress, validation results
- `WARNING`: Missing optional resources, non-critical issues
- `ERROR`: Conversion failures, validation errors

### Font Management

**Comprehensive Font Coverage:**
- Latin scripts: Liberation, DejaVu, Noto Sans
- CJK (Chinese, Japanese, Korean): Noto CJK, WenQuanYi
- Cyrillic (Russian, Ukrainian): Noto fonts with Cyrillic
- Czech: FreeFonts with Latin Extended-A

**Validation:**
```python
required_fonts = ["Noto Sans", "Noto Sans CJK SC", "Liberation Sans"]
fc-list : family  # Check installed fonts
```

---

## 9. Architecture Decisions

### ADR-001: Two-Repository Model

**Status:** Accepted

**Context:** Build logic could be in arc42-template repo or separate.

**Decision:** Separate `arc42-template-build` repository.

**Consequences:**
- ✅ Clear separation of content vs. build concerns
- ✅ Content translators don't need to understand build system
- ✅ Build system can support multiple templates (arc42, req42)
- ❌ Requires Git submodule management

---

### ADR-002: Plugin Architecture for Converters

**Status:** Accepted

**Context:** Need extensible system for 10+ output formats.

**Decision:** Abstract base class `ConverterPlugin` with registry pattern.

**Consequences:**
- ✅ New formats added by single file (e.g., `rst.py`)
- ✅ Each converter encapsulates its dependencies
- ✅ Easy to test converters independently
- ⚠️ Slight indirection vs. monolithic script

---

### ADR-003: Asciidoctor + Pandoc Two-Phase Conversion

**Status:** Accepted

**Context:** Need to generate many formats from AsciiDoc.

**Decision:** AsciiDoc → HTML (via Asciidoctor) → Other formats (via Pandoc)

**Consequences:**
- ✅ Leverages Asciidoctor's excellent AsciiDoc support
- ✅ Pandoc's wide format support (50+ formats)
- ✅ Reliable, well-maintained tools
- ❌ Some formats go through two conversions (quality loss possible)
- ⚠️ Confluence uses dedicated asciidoctor-confluence

---

### ADR-004: Docker-Only Execution

**Status:** Accepted

**Context:** Build requires Ruby, Python, Pandoc, fonts, etc.

**Decision:** All builds run inside Docker container.

**Consequences:**
- ✅ Reproducible across Linux, macOS, Windows
- ✅ Version-pinned dependencies (Dockerfile)
- ✅ No "works on my machine" issues
- ❌ Requires Docker installation (acceptable for target users)

---

### ADR-005: YAML Configuration

**Status:** Accepted

**Context:** Need human-readable config for languages/formats.

**Decision:** Use `config/build.yaml` as single source of truth.

**Consequences:**
- ✅ Easy to read and edit
- ✅ Good YAML parsing libraries in Python
- ✅ Supports comments for documentation
- ✅ Can validate against JSON schema

---

## 10. Quality Requirements

### Quality Scenario: Reproducible Builds

**Scenario:** Developer builds arc42 template twice with same commit.

**Expected Behavior:**
- Byte-identical output for deterministic formats (HTML, Markdown, AsciiDoc)
- PDF may vary slightly (metadata timestamps) but content identical

**Implementation:**
- Pinned tool versions in Dockerfile
- No network calls during build
- Deterministic directory iteration

---

### Quality Scenario: Adding New Format

**Scenario:** Developer wants to add MediaWiki format.

**Steps:**
1. Create `src/arc42_builder/converters/mediawiki.py`
2. Implement `MediaWikiConverter(ConverterPlugin)`
3. Register in `converters/__init__.py`
4. Add config section to `build.yaml`
5. Run `make build`

**Time to implement:** 1-2 hours for straightforward format.

---

### Quality Scenario: Multi-Language Support

**Scenario:** All 11 languages build successfully with proper fonts.

**Requirements:**
- Font coverage verified during validation
- Character rendering tested for EN, DE, RU, ZH, etc.
- Warning (not error) for missing optional fonts

**Implementation:**
- `Validator.verify_fonts_installed()` checks `fc-list`
- Dockerfile installs comprehensive Noto font family

---

## 11. Risks and Technical Debt

### Current Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Pandoc output quality varies** | Medium | Medium | Use Asciidoctor-native backends where possible (HTML, PDF) |
| **Font licensing for CJK** | Low | High | All fonts are open-source (Noto, Liberation) |
| **Submodule sync issues** | Medium | Low | Makefile target `update-submodule` with error recovery |
| **Large Docker image size** | Low | Low | Multi-stage build reduces final size; acceptable for this use case |

### Technical Debt

| Item | Priority | Effort |
|------|----------|--------|
| **No integration tests** | High | Medium - Add pytest with Docker fixtures |
| **No CI/CD pipeline** | High | Low - Add GitHub Actions workflow |
| **Multi-page HTML not implemented** | Medium | Medium - New converter needed |
| **LaTeX format not implemented** | Low | Medium - Requires additional dependencies |
| **No artifact upload to releases** | Medium | Low - Extend CI workflow |

---

## 12. Glossary

| Term | Definition |
|------|------------|
| **AsciiDoc** | Lightweight markup language, more powerful than Markdown |
| **arc42** | Template for software architecture documentation (this project) |
| **Converter Plugin** | Python class implementing format-specific conversion logic |
| **Flavor** | Content variant: `plain` (skeleton) or `withHelp` (with guidance) |
| **GFM** | GitHub Flavored Markdown |
| **Pandoc** | Universal document converter (50+ formats) |
| **req42** | Requirements documentation template (arc42-style for requirements) |
| **Submodule** | Git feature to embed one repo inside another |
| **Workspace** | Docker volume-mounted directory for outputs (`workspace/build/`, `workspace/dist/`) |

---

## Appendix: File Structure

```
arc42-template-build/
├── arc42-template/              # Git submodule (content)
│   ├── EN/
│   │   ├── arc42-template.adoc
│   │   ├── src/                 # Chapter includes
│   │   ├── images/              # Diagrams
│   │   └── version.properties
│   ├── DE/ ...
│   └── (other languages)
├── config/
│   └── build.yaml               # Main configuration
├── docker/
│   ├── Dockerfile               # Container definition
│   ├── custom-fonts/            # Optional custom fonts
│   └── pdf-themes/              # PDF styling themes
├── src/arc42_builder/
│   ├── __init__.py
│   ├── __main__.py              # Entry point
│   ├── cli.py                   # Click CLI commands
│   ├── config/
│   │   ├── loader.py            # YAML parsing
│   │   └── models.py            # Config data classes
│   ├── core/
│   │   ├── builder.py           # BuildPipeline
│   │   └── validator.py         # Validation logic
│   └── converters/
│       ├── __init__.py          # Converter registry
│       ├── base.py              # Abstract base class
│       ├── html.py
│       ├── pdf.py
│       ├── markdown.py
│       ├── markdown_mp.py       # Multi-page Markdown
│       ├── github_markdown.py
│       ├── github_markdown_mp.py
│       ├── rst.py
│       ├── textile.py
│       ├── confluence.py
│       ├── docx.py
│       └── asciidoc.py
├── workspace/                   # Gitignored, created at runtime
│   ├── build/                   # Generated artifacts
│   ├── dist/                    # ZIP distributions
│   └── logs/                    # Build logs
├── docs/                        # Documentation
│   ├── architecture-documentation.md  # This file
│   ├── requirements.md          # req42-style requirements
│   └── future-todos.md          # Planned improvements
├── docker-compose.yaml
├── Makefile                     # Convenience wrapper
├── requirements.txt             # Python dependencies
├── README.md                    # User guide
└── CLAUDE.md                    # AI assistant guide
```

---

**Document Information:**
- **Template:** arc42 Version 9.0
- **Format:** Markdown (single-page)
- **Authors:** arc42 core team, AI-assisted development
- **License:** CC BY-SA 4.0 (documentation), MIT (code)
