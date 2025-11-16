# arc42 Build Process - Solution Proposal

## Executive Summary

This document proposes a **Python-based, Docker-containerized build system** for the arc42 template that fulfills all requirements while maintaining simplicity, maintainability, and extensibility. The solution uses a plugin-based architecture for format converters, YAML-based configuration, and provides both CLI and CI/CD integration.

**Key Technology Choices:**
- **Orchestration**: Python 3.11+ with Click CLI framework
- **Containerization**: Docker with multi-stage builds containing ALL required fonts
- **Primary Conversion Tools**: Asciidoctor, Pandoc, WeasyPrint
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
│  │  Asciidoctor | Pandoc | WeasyPrint | wkhtmltopdf   │   │
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
| **CLI Orchestrator** | Main entry point, coordinates build process |
| **Config Loader** | Parses and validates YAML configuration |
| **Validator** | Pre-build validation of sources and dependencies |
| **Build Controller** | Manages the build pipeline execution |
| **Format Plugins** | Format-specific conversion logic |
| **Flavor Processor** | Handles plain/withHelp content filtering |
| **Packager** | Creates ZIP archives for distribution |

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
│   │   │   ├── flavor.py        # Flavor processing
│   │   │   └── packager.py      # ZIP packaging
│   │   ├── converters/
│   │   │   ├── base.py          # Abstract converter
│   │   │   ├── html.py          # HTML converter
│   │   │   ├── pdf.py           # PDF converter
│   │   │   ├── docx.py          # DOCX converter
│   │   │   ├── markdown.py      # Markdown converter
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
├── scripts/
│   ├── build.sh                 # Local build script
│   ├── test.sh                  # Test runner
│   └── release.sh              # Release script
├── .github/
│   └── workflows/
│       ├── build.yml           # CI build workflow
│       └── release.yml         # Release workflow
├── docker-compose.yml
├── Makefile                    # Alternative to scripts
├── README.md
└── LICENSE
```

### 3.2 Runtime Directory Structure

```
workspace/                      # Working directory
├── arc42-template/            # Cloned/linked template repo
├── build/                     # Build outputs
│   ├── EN/
│   │   ├── plain/
│   │   │   ├── html/
│   │   │   │   └── arc42-template-EN-plain.html
│   │   │   ├── pdf/
│   │   │   │   └── arc42-template-EN-plain.pdf
│   │   │   └── docx/
│   │   │       └── arc42-template-EN-plain.docx
│   │   └── withHelp/
│   │       └── ...
│   └── DE/
│       └── ...
├── dist/                      # Distribution ZIPs
│   ├── arc42-template-EN-plain-html.zip
│   ├── arc42-template-EN-plain-pdf.zip
│   └── ...
└── logs/
    └── build-20250116-120000.log
```

---

## 4. Core Implementation Details

### 4.1 Configuration Model

```yaml
# config/build.yaml
version: "1.0"
template:
  repository: "https://github.com/arc42/arc42-template.git"
  ref: "main"  # or tag/commit
  path: "./arc42-template"  # local path if already cloned

languages:
  - EN
  - DE
  - FR
  # Add more as needed: CZ, ES, IT, NL, PT, RU, UKR, ZH

formats:
  html:
    enabled: true
    priority: 1
    options:
      single_page: true
      toc_levels: 3
      stylesheet: "default"
  pdf:
    enabled: true
    priority: 1
    options:
      page_size: "A4"
      # Default font (used if no language-specific theme found)
      default_font: "Noto Sans"
      # Language-specific theme detection
      use_language_themes: true  # Look for {lang}-theme.yml files
      theme_search_paths:
        - "${language}/asciidoc/pdf-theme"
        - "docker/pdf-themes"  # Fallback themes
      # Override themes for specific languages (optional)
      language_overrides:
        ZH:
          scripts: "cjk"
          text_align: "left"
        UKR:
          scripts: "cyrillic"
        RU:
          scripts: "cyrillic"
  docx:
    enabled: true
    priority: 1
    options:
      template: null  # Use pandoc default
      # Pandoc will use system fonts from Docker
  markdown:
    enabled: true
    priority: 1
    options:
      variant: "gfm"  # GitHub Flavored Markdown
      single_file: true

flavors:
  - plain
  - withHelp

build:
  parallel: true
  max_workers: 4
  validate: true
  clean_before: true
  create_zips: true
  # Font validation at startup
  verify_fonts: true

logging:
  level: "INFO"
  file: true
  console: true
```

### 4.2 Plugin Architecture for Converters

```python
# src/arc42_builder/converters/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any

@dataclass
class BuildContext:
    language: str
    flavor: str
    source_dir: Path
    output_dir: Path
    version_props: Dict[str, str]
    config: Dict[str, Any]

class ConverterPlugin(ABC):
    """Abstract base for all format converters"""
    
    def __init__(self, name: str, priority: int = 1):
        self.name = name
        self.priority = priority
    
    @abstractmethod
    def check_dependencies(self) -> bool:
        """Verify required tools are available"""
        pass
    
    @abstractmethod
    def convert(self, context: BuildContext) -> Path:
        """Execute conversion and return output path"""
        pass
    
    @abstractmethod
    def get_output_extension(self) -> str:
        """Return file extension for this format"""
        pass

# src/arc42_builder/converters/html.py
import subprocess
from pathlib import Path
from .base import ConverterPlugin, BuildContext

class HtmlConverter(ConverterPlugin):
    def __init__(self):
        super().__init__("html", priority=1)
    
    def check_dependencies(self) -> bool:
        try:
            result = subprocess.run(
                ["asciidoctor", "--version"],
                capture_output=True,
                check=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def convert(self, context: BuildContext) -> Path:
        output_file = context.output_dir / f"arc42-template-{context.language}-{context.flavor}.html"
        
        # Build asciidoctor command
        cmd = [
            "asciidoctor",
            "-b", "html5",
            "-a", f"revnumber={context.version_props['revnumber']}",
            "-a", f"revdate={context.version_props['revdate']}",
            "-a", f"flavor={context.flavor}",
            "-D", str(context.output_dir),
            "-o", str(output_file),
            str(context.source_dir / "arc42-template.adoc")
        ]
        
        # Add custom attributes for flavor filtering
        if context.flavor == "plain":
            cmd.extend(["-a", "hide-help-text"])
        
        subprocess.run(cmd, check=True)
        return output_file
    
    def get_output_extension(self) -> str:
        return ".html"
```

### 4.3 Flavor Processing

```python
# src/arc42_builder/core/flavor.py
from pathlib import Path
import re
from typing import List

class FlavorProcessor:
    """Handles plain/withHelp content filtering"""
    
    HELP_MARKERS = {
        'start': ['// tag::help[]', '// help-start'],
        'end': ['// end::help[]', '// help-end']
    }
    
    def preprocess_for_flavor(self, 
                             source_dir: Path, 
                             temp_dir: Path, 
                             flavor: str) -> Path:
        """
        Create flavor-specific version of sources
        """
        # Copy all files to temp directory
        import shutil
        shutil.copytree(source_dir, temp_dir, dirs_exist_ok=True)
        
        if flavor == "plain":
            # Remove help text from all .adoc files
            for adoc_file in temp_dir.rglob("*.adoc"):
                self._filter_help_text(adoc_file)
        
        return temp_dir
    
    def _filter_help_text(self, file_path: Path):
        """Remove help text blocks from file"""
        content = file_path.read_text(encoding='utf-8')
        
        # Remove content between help markers
        pattern = r'// tag::help\[\].*?// end::help\[\]'
        filtered = re.sub(pattern, '', content, flags=re.DOTALL)
        
        file_path.write_text(filtered, encoding='utf-8')
```

### 4.4 Build Pipeline Controller

```python
# src/arc42_builder/core/builder.py
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import List, Dict
import logging

from ..converters import get_converter
from ..config.models import BuildConfig
from .flavor import FlavorProcessor
from .validator import Validator
from .packager import Packager

class BuildPipeline:
    def __init__(self, config: BuildConfig):
        self.config = config
        self.validator = Validator()
        self.flavor_processor = FlavorProcessor()
        self.packager = Packager()
        self.logger = logging.getLogger(__name__)
    
    def run(self) -> Dict[str, List[Path]]:
        """Execute complete build pipeline"""
        results = {}
        
        # Phase 1: Validation
        self.logger.info("Phase 1: Validating sources...")
        if not self.validator.validate_template(self.config.template_path):
            raise ValueError("Template validation failed")
        
        # Phase 2: Build matrix generation
        build_matrix = self._generate_build_matrix()
        self.logger.info(f"Phase 2: Generated {len(build_matrix)} build tasks")
        
        # Phase 3: Parallel execution
        self.logger.info("Phase 3: Executing builds...")
        if self.config.build.parallel:
            with ThreadPoolExecutor(max_workers=self.config.build.max_workers) as executor:
                futures = [
                    executor.submit(self._build_single, task)
                    for task in build_matrix
                ]
                results = [f.result() for f in futures]
        else:
            results = [self._build_single(task) for task in build_matrix]
        
        # Phase 4: Packaging
        if self.config.build.create_zips:
            self.logger.info("Phase 4: Creating distribution packages...")
            self.packager.create_packages(results)
        
        return results
    
    def _generate_build_matrix(self) -> List[Dict]:
        """Generate all language/flavor/format combinations"""
        matrix = []
        for lang in self.config.languages:
            for flavor in self.config.flavors:
                for format_name, format_config in self.config.formats.items():
                    if format_config.enabled:
                        matrix.append({
                            'language': lang,
                            'flavor': flavor,
                            'format': format_name,
                            'config': format_config
                        })
        return matrix
    
    def _build_single(self, task: Dict) -> Path:
        """Build single artifact"""
        self.logger.info(
            f"Building: {task['language']}/{task['flavor']}/{task['format']}"
        )
        
        # Get converter plugin
        converter = get_converter(task['format'])
        
        # Create build context
        context = BuildContext(
            language=task['language'],
            flavor=task['flavor'],
            source_dir=self.config.template_path / task['language'] / 'asciidoc',
            output_dir=Path('build') / task['language'] / task['flavor'] / task['format'],
            version_props=self._load_version_props(task['language']),
            config=task['config']
        )
        
        # Ensure output directory exists
        context.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Preprocess for flavor
        temp_source = self.flavor_processor.preprocess_for_flavor(
            context.source_dir,
            Path('temp') / f"{task['language']}_{task['flavor']}",
            task['flavor']
        )
        context.source_dir = temp_source
        
        # Execute conversion
        output_path = converter.convert(context)
        self.logger.info(f"Created: {output_path}")
        
        return output_path
```

---

## 4.5 Font and Internationalization Handling

### Overview for Non-Python Developers

**Key Concept**: The build system handles fonts through a combination of:
1. **Docker-installed fonts** - All required fonts are pre-installed in the container
2. **PDF theme files** - Language-specific YAML configurations (similar to your current Groovy approach)
3. **Automatic detection** - The system automatically finds and applies the correct theme for each language

### 4.5.1 Language-Specific Font Requirements

| Language | Script Type | Required Fonts | Special Settings |
|----------|------------|----------------|------------------|
| **EN, DE** | Latin | Noto Sans, Liberation Sans | Standard settings |
| **CZ** | Latin Extended-A | Noto Sans, FreeFonts | Standard settings |
| **RU, UKR** | Cyrillic | Noto Sans (with Cyrillic) | `scripts: cyrillic` |
| **ZH** | CJK (Chinese) | Noto Sans CJK SC, WenQuanYi | `scripts: cjk`, line-height: 1.5 |

### 4.5.2 PDF Theme File Structure

Each language can have its own PDF theme file at: `{LANG}/asciidoc/pdf-theme/{lang}-theme.yml`

Example for Chinese (ZH):
```yaml
# ZH/asciidoc/pdf-theme/zh-theme.yml
extends: default
font:
  catalog:
    # Map font family names to actual font files
    Noto Sans CJK SC:
      normal: NotoSansCJKsc-Regular.ttf
      bold: NotoSansCJKsc-Bold.ttf
      italic: NotoSansCJKsc-Regular.ttf  # CJK fonts often lack italic
      bold_italic: NotoSansCJKsc-Bold.ttf
  fallbacks:
    - Noto Sans CJK SC
base:
  font-family: Noto Sans CJK SC
  font-size: 10.5
  line-height: 1.5  # More spacing for CJK readability
heading:
  font-family: Noto Sans CJK SC
  font-weight: bold
code:
  font-family: Noto Sans Mono CJK SC
# Language-specific attributes
attributes:
  scripts: cjk
  text-align: left
```

Example for Ukrainian (UKR):
```yaml
# UKR/asciidoc/pdf-theme/ukr-theme.yml
extends: default
font:
  catalog:
    Noto Sans:
      normal: NotoSans-Regular.ttf
      bold: NotoSans-Bold.ttf
      italic: NotoSans-Italic.ttf
      bold_italic: NotoSans-BoldItalic.ttf
  fallbacks:
    - Noto Sans
base:
  font-family: Noto Sans
  font-size: 11
heading:
  font-family: Noto Sans
  font-weight: bold
code:
  font-family: Noto Sans Mono
attributes:
  scripts: cyrillic
```

### 4.5.3 Enhanced PDF Converter Implementation

The PDF converter automatically detects and applies language-specific themes:

```python
# src/arc42_builder/converters/pdf.py
import subprocess
from pathlib import Path
from typing import Dict, Optional
import logging

class PdfConverter(ConverterPlugin):
    """
    PDF converter with automatic font/theme detection.
    This is similar to your Groovy code but in Python.
    """
    
    def convert(self, context: BuildContext) -> Path:
        """
        Main conversion method - equivalent to your Gradle task
        """
        output_file = context.output_dir / f"arc42-template-{context.language}-{context.flavor}.pdf"
        
        # Start building the asciidoctor-pdf command
        # This is like: asciidoctor-pdf [options] input.adoc
        cmd = [
            "asciidoctor-pdf",
            "-b", "pdf",
            "-D", str(context.output_dir),
            "-o", str(output_file)
        ]
        
        # Add version attributes from version.properties
        # Equivalent to your Groovy: attributes asciidocAttributes
        attributes = {
            'revnumber': context.version_props.get('revnumber', ''),
            'revdate': context.version_props.get('revdate', ''),
            'revremark': context.version_props.get('revremark', ''),
            'flavor': context.flavor
        }
        
        # Check for PDF theme file - this is your Groovy logic translated
        # Equivalent to: def pdfThemeYmlFile = file("${language}/asciidoc/pdf-theme/...")
        theme_yml_path = (
            context.source_dir.parent / "pdf-theme" / 
            f"{context.language.lower()}-theme.yml"
        )
        fonts_dir = context.source_dir.parent / "pdf-theme" / "fonts"
        
        if theme_yml_path.exists():
            # Found theme file - apply it
            self.logger.info(f"Loading PDF theme from {theme_yml_path}")
            
            # Add theme attributes - equivalent to your Groovy block
            attributes['pdf-theme'] = str(theme_yml_path.absolute())
            
            if fonts_dir.exists():
                attributes['pdf-fontsdir'] = str(fonts_dir.absolute())
            
            # Add CJK settings if this is a CJK language
            if context.language in ['ZH', 'JA', 'KO']:
                attributes['scripts'] = 'cjk'
                attributes['text-align'] = 'left'
            
            # Add Cyrillic settings
            elif context.language in ['RU', 'UKR']:
                attributes['scripts'] = 'cyrillic'
        
        # Convert attributes dict to command line arguments
        # This creates: -a key=value -a key2=value2 etc.
        for key, value in attributes.items():
            if value:
                cmd.extend(["-a", f"{key}={value}"])
            else:
                cmd.extend(["-a", key])
        
        # Add the source file
        cmd.append(str(context.source_dir / "arc42-template.adoc"))
        
        # Log the command for debugging (like Gradle's --debug)
        self.logger.debug(f"Executing: {' '.join(cmd)}")
        
        # Run the conversion
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise RuntimeError(f"PDF generation failed: {result.stderr}")
        
        return output_file
```

### 4.5.4 Directory Structure for Fonts and Themes

```
arc42-template/          # Template repository
├── EN/
│   └── asciidoc/
│       └── pdf-theme/   # Optional - EN usually uses defaults
├── ZH/
│   └── asciidoc/
│       └── pdf-theme/
│           ├── zh-theme.yml
│           └── fonts/   # Optional - custom fonts if not using system fonts
│               ├── NotoSansCJKsc-Regular.ttf
│               └── NotoSansCJKsc-Bold.ttf
├── UKR/
│   └── asciidoc/
│       └── pdf-theme/
│           └── ukr-theme.yml  # Fonts come from Docker container
└── RU/
    └── asciidoc/
        └── pdf-theme/
            └── ru-theme.yml

arc42-build/             # Build repository  
└── docker/
    ├── pdf-themes/      # Default themes if not in template repo
    │   └── default-theme.yml
    └── custom-fonts/    # Additional fonts not in Ubuntu repos
        └── (empty by default - all fonts from packages)
```

### 4.5.5 How It Works (Step by Step)

1. **Docker container starts** - All fonts are already installed via apt-get
2. **Build process runs** for language X:
   - Looks for `X/asciidoc/pdf-theme/x-theme.yml`
   - If found: uses it (like your Groovy code)
   - If not found: uses default fonts (Noto Sans family)
3. **Asciidoctor PDF** receives:
   - `--pdf-theme`: path to theme file
   - `--pdf-fontsdir`: path to fonts directory
   - `--scripts`: cjk or cyrillic as needed
4. **Result**: PDF with correct fonts for the language

### 4.5.6 Testing Font Support

```python
# src/arc42_builder/utils/font_check.py
import subprocess

def verify_fonts_installed():
    """
    Verify all required fonts are installed in the container.
    Run this during build initialization.
    """
    required_fonts = [
        "Noto Sans",          # Latin, Cyrillic
        "Noto Sans CJK SC",   # Chinese
        "Noto Sans Mono",     # Monospace
        "Liberation Sans",    # Fallback
    ]
    
    # Use fc-list command to check installed fonts
    result = subprocess.run(
        ["fc-list", ":", "family"], 
        capture_output=True, 
        text=True
    )
    
    installed_fonts = result.stdout
    missing = []
    
    for font in required_fonts:
        if font not in installed_fonts:
            missing.append(font)
    
    if missing:
        raise RuntimeError(
            f"Missing required fonts: {missing}\n"
            f"Please rebuild the Docker container"
        )
    
    return True
```

---

## 5. Docker Configuration

### 5.1 Dockerfile (Multi-stage) with Complete Font Support

```dockerfile
# docker/Dockerfile
# Stage 1: Base tools with comprehensive font support
FROM ubuntu:22.04 AS base

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
# Ensure Asciidoctor PDF uses our fonts
ENV RUBYOPT="-Eutf-8"

# Install system dependencies and ALL required fonts
RUN apt-get update && apt-get install -y \
    # Basic tools
    curl wget git make zip unzip \
    # Ruby for Asciidoctor
    ruby ruby-dev build-essential \
    # Python for orchestrator
    python3.11 python3-pip python3-venv \
    # Pandoc for format conversions
    pandoc \
    # PDF tools
    wkhtmltopdf \
    # Font management tools
    fontconfig \
    # ============ COMPREHENSIVE FONT INSTALLATION ============ \
    # Core Latin fonts (EN, DE, CZ base support)
    fonts-liberation \
    fonts-dejavu-core \
    fonts-liberation2 \
    # Noto fonts - Google's comprehensive Unicode font family
    fonts-noto-core \           # Basic Latin + extensions
    fonts-noto-ui-core \         # UI variants with better screen rendering
    fonts-noto-extra \           # Additional scripts
    # CJK (Chinese, Japanese, Korean) fonts
    fonts-noto-cjk \             # Main CJK fonts
    fonts-noto-cjk-extra \       # Additional CJK variants
    # Specific Chinese fonts (ZH)
    fonts-wqy-microhei \         # WenQuanYi Chinese font
    fonts-wqy-zenhei \           # Alternative Chinese font
    # Cyrillic fonts (RU, UKR)
    fonts-noto \                 # Includes Cyrillic
    # Czech specific (CZ) - Latin Extended-A
    fonts-freefont-ttf \         # Good Czech support
    # Monospace fonts for code blocks
    fonts-noto-mono \            # Noto Mono for all scripts
    fonts-firacode \             # Programming font with ligatures
    # Clean up
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    # Update font cache
    && fc-cache -f -v

# Install Asciidoctor and extensions with specific versions
RUN gem install asciidoctor:2.0.20 \
    asciidoctor-pdf:2.3.10 \
    asciidoctor-diagram:2.2.14 \
    asciidoctor-confluence:0.0.2 \
    # Additional PDF fonts support
    && asciidoctor-pdf -v

# Copy custom PDF themes and fonts (if any)
# This allows adding commercial or special fonts not in Ubuntu repos
COPY docker/custom-fonts/ /usr/share/fonts/truetype/custom/
COPY docker/pdf-themes/ /opt/arc42/pdf-themes/

# Rebuild font cache with custom fonts
RUN fc-cache -f -v && \
    # Verify critical fonts are installed
    fc-list | grep -i noto > /tmp/font-check.txt && \
    echo "Installed Noto fonts:" && cat /tmp/font-check.txt

# Stage 2: Python environment
FROM base AS python-env

WORKDIR /app

# Copy Python requirements
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Stage 3: Application
FROM python-env AS app

# Copy application code
COPY src/ /app/src/
COPY config/ /app/config/
COPY scripts/ /app/scripts/

# Make scripts executable
RUN chmod +x /app/scripts/*.sh

# Create directories for templates and outputs
RUN mkdir -p /workspace /workspace/build /workspace/dist /workspace/logs

# Set working directory
WORKDIR /workspace

# Entry point
ENTRYPOINT ["python3", "-m", "arc42_builder"]
CMD ["--help"]
```

### 5.2 Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  builder:
    build:
      context: .
      dockerfile: docker/Dockerfile
    volumes:
      - ./arc42-template:/workspace/arc42-template:ro
      - ./build:/workspace/build
      - ./dist:/workspace/dist
      - ./logs:/workspace/logs
      - ./config/build.yaml:/app/config/build.yaml:ro
    environment:
      - LOG_LEVEL=${LOG_LEVEL:-INFO}
      - BUILD_CONFIG=${BUILD_CONFIG:-/app/config/build.yaml}
    command: build --all

  test:
    build:
      context: .
      dockerfile: docker/Dockerfile
      target: python-env
    volumes:
      - ./:/app
    command: pytest tests/
```

---

## 6. CLI Interface

### 6.1 Command Structure

```bash
# Main commands
arc42-builder build --all                    # Build everything
arc42-builder build --lang EN --format pdf   # Specific build
arc42-builder validate                       # Validate only
arc42-builder list-formats                   # Show available formats
arc42-builder clean                          # Clean build artifacts

# Options
--config FILE         # Custom config file
--template PATH       # Template directory
--output PATH         # Output directory
--parallel / --serial # Parallel execution
--verbose            # Verbose output
--quiet             # Minimal output
```

### 6.2 CLI Implementation

```python
# src/arc42_builder/cli.py
import click
from pathlib import Path
from .core.builder import BuildPipeline
from .config.loader import ConfigLoader

@click.group()
@click.option('--config', type=Path, default='config/build.yaml')
@click.option('--verbose', is_flag=True)
@click.pass_context
def cli(ctx, config, verbose):
    """arc42 template build system"""
    ctx.ensure_object(dict)
    ctx.obj['config'] = ConfigLoader().load(config)
    ctx.obj['verbose'] = verbose

@cli.command()
@click.option('--all', is_flag=True, help='Build all configured outputs')
@click.option('--lang', multiple=True, help='Language(s) to build')
@click.option('--format', 'formats', multiple=True, help='Format(s) to build')
@click.option('--flavor', multiple=True, help='Flavor(s) to build')
@click.pass_context
def build(ctx, all, lang, formats, flavor):
    """Build arc42 templates"""
    config = ctx.obj['config']
    
    # Override config with CLI options
    if lang:
        config.languages = list(lang)
    if formats:
        config.formats = {f: config.formats[f] for f in formats}
    if flavor:
        config.flavors = list(flavor)
    
    pipeline = BuildPipeline(config)
    results = pipeline.run()
    
    click.echo(f"✓ Built {len(results)} artifacts")

@cli.command()
@click.pass_context
def validate(ctx):
    """Validate template sources"""
    from .core.validator import Validator
    validator = Validator()
    
    if validator.validate_template(ctx.obj['config'].template_path):
        click.echo("✓ Validation passed")
    else:
        click.echo("✗ Validation failed", err=True)
        ctx.exit(1)

@cli.command()
def list_formats():
    """List available output formats"""
    from .converters import list_converters
    
    click.echo("Available formats:")
    for name, converter in list_converters().items():
        click.echo(f"  • {name} (priority: {converter.priority})")
```

---

## 7. Testing Strategy

### 7.1 Test Structure

```python
# tests/unit/test_converters.py
import pytest
from pathlib import Path
from arc42_builder.converters.html import HtmlConverter
from arc42_builder.converters.base import BuildContext

class TestHtmlConverter:
    def test_check_dependencies(self):
        converter = HtmlConverter()
        assert converter.check_dependencies()
    
    def test_get_output_extension(self):
        converter = HtmlConverter()
        assert converter.get_output_extension() == ".html"
    
    @pytest.fixture
    def build_context(self, tmp_path):
        return BuildContext(
            language="EN",
            flavor="plain",
            source_dir=tmp_path / "source",
            output_dir=tmp_path / "output",
            version_props={"revnumber": "9.0", "revdate": "2025"},
            config={}
        )
    
    def test_convert(self, build_context, mocker):
        # Mock subprocess.run
        mock_run = mocker.patch('subprocess.run')
        
        converter = HtmlConverter()
        result = converter.convert(build_context)
        
        assert mock_run.called
        assert result.suffix == ".html"

# tests/integration/test_pipeline.py
import pytest
from arc42_builder.core.builder import BuildPipeline

@pytest.mark.docker
class TestBuildPipeline:
    def test_full_build(self, sample_config, tmp_path):
        """Test complete build pipeline with real tools"""
        pipeline = BuildPipeline(sample_config)
        results = pipeline.run()
        
        assert len(results) > 0
        # Verify outputs exist
        for result in results:
            assert result.exists()
```

### 7.2 Test Execution

```bash
# Unit tests (fast, no Docker)
pytest tests/unit/

# Integration tests (requires Docker)
docker-compose run test pytest tests/integration/

# Full test suite
./scripts/test.sh
```

---

## 8. CI/CD Integration

### 8.1 GitHub Actions Workflow

```yaml
# .github/workflows/build.yml
name: Build arc42 Templates

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:
    inputs:
      languages:
        description: 'Languages to build (comma-separated)'
        required: false
        default: 'EN,DE'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Checkout template
        uses: actions/checkout@v3
        with:
          repository: arc42/arc42-template
          path: arc42-template
      
      - name: Build Docker image
        run: docker build -t arc42-builder -f docker/Dockerfile .
      
      - name: Validate sources
        run: |
          docker run --rm \
            -v $PWD/arc42-template:/workspace/arc42-template:ro \
            arc42-builder validate

  build:
    needs: validate
    runs-on: ubuntu-latest
    strategy:
      matrix:
        language: [EN, DE, FR]
        flavor: [plain, withHelp]
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Checkout template
        uses: actions/checkout@v3
        with:
          repository: arc42/arc42-template
          path: arc42-template
      
      - name: Build Docker image
        run: docker build -t arc42-builder -f docker/Dockerfile .
      
      - name: Build ${{ matrix.language }}-${{ matrix.flavor }}
        run: |
          docker run --rm \
            -v $PWD/arc42-template:/workspace/arc42-template:ro \
            -v $PWD/build:/workspace/build \
            -v $PWD/dist:/workspace/dist \
            arc42-builder build \
              --lang ${{ matrix.language }} \
              --flavor ${{ matrix.flavor }}
      
      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: arc42-${{ matrix.language }}-${{ matrix.flavor }}
          path: dist/

  release:
    if: startsWith(github.ref, 'refs/tags/')
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Download all artifacts
        uses: actions/download-artifact@v3
      
      - name: Create Release
        uses: softprops/action-gh-release@v1
        with:
          files: |
            arc42-*/arc42-template-*.zip
          generate_release_notes: true
```

---

## 9. Extension Points

### 9.1 Adding New Format Converter

```python
# src/arc42_builder/converters/epub.py
from .base import ConverterPlugin, BuildContext

class EpubConverter(ConverterPlugin):
    def __init__(self):
        super().__init__("epub", priority=2)
    
    def check_dependencies(self) -> bool:
        # Check for pandoc or asciidoctor-epub3
        pass
    
    def convert(self, context: BuildContext) -> Path:
        # Implement EPUB conversion
        pass
    
    def get_output_extension(self) -> str:
        return ".epub"

# Register in __init__.py
CONVERTERS['epub'] = EpubConverter()
```

### 9.2 Adding New Template (req42)

```yaml
# config/req42-build.yaml
version: "1.0"
template:
  repository: "https://github.com/arc42/req42-template.git"
  ref: "main"
  path: "./req42-template"

# Rest similar to arc42 config...
```

### 9.3 Custom Validation Rules

```python
# src/arc42_builder/validators/custom.py
from ..core.validator import ValidationRule

class Req42StructureRule(ValidationRule):
    def validate(self, template_path: Path) -> bool:
        # Check req42-specific structure
        required_sections = [
            "01_introduction",
            "02_stakeholders",
            "03_context",
            # ...
        ]
        return all(
            (template_path / f"{section}.adoc").exists()
            for section in required_sections
        )
```

---

## 10. Implementation Roadmap

### Phase 1: Foundation (Week 1-2)
- [ ] Set up repository structure
- [ ] Create Dockerfile with all required fonts (Noto family for all languages)
- [ ] Verify font installation for DE, EN, CZ, UKR, RU, ZH
- [ ] Implement configuration loader and validation
- [ ] Basic CLI skeleton with Click
- [ ] Unit test framework

### Phase 2: Core Converters (Week 2-3)
- [ ] Implement HTML converter
- [ ] Implement PDF converter with theme detection
- [ ] Test PDF generation for all languages (especially ZH, UKR)
- [ ] Implement DOCX converter via Pandoc
- [ ] Implement Markdown converter
- [ ] Flavor processing (plain/withHelp)

### Phase 3: Build Pipeline (Week 3-4)
- [ ] Build controller with parallel execution
- [ ] Pre-build validation
- [ ] Version properties integration
- [ ] ZIP packaging
- [ ] Logging and error handling

### Phase 4: Testing & CI (Week 4-5)
- [ ] Integration tests with sample data
- [ ] GitHub Actions workflow
- [ ] Docker Compose setup
- [ ] Documentation

### Phase 5: Advanced Features (Week 5-6)
- [ ] Additional format converters (Priority 2/3)
- [ ] Performance optimizations
- [ ] Advanced configuration options
- [ ] Release automation

---

## 11. Key Design Decisions

### 11.1 Why Python?
- **Pros**: Excellent ecosystem, readable code, good Docker integration, strong CLI libraries
- **Cons**: Slightly slower than compiled languages (acceptable for build system)
- **Alternative considered**: Node.js (similar pros, but Python has better Pandoc integration)

### 11.2 Why Docker?
- **Pros**: Reproducible builds, tool version management, works everywhere
- **Cons**: Requires Docker installation, slightly slower startup
- **Mitigation**: Provide native fallback for development

### 11.3 Why Plugin Architecture?
- **Pros**: Easy to extend, clear separation of concerns, parallel development
- **Cons**: Slightly more complex initial setup
- **Justification**: Requirements explicitly ask for extensibility

### 11.4 Flavor Processing Strategy
- **Decision**: Preprocess AsciiDoc files before conversion
- **Alternative**: Post-process output files
- **Rationale**: Cleaner, works consistently across all formats

---

## 12. Open Questions Resolution

| Question | Proposed Solution |
|----------|------------------|
| **Diagram regeneration** | Treat as static initially, add draw.io support in Phase 5 |
| **Diagram localization** | Support language-specific image directories with fallback |
| **Translation sync** | Add optional validation rule with warnings |
| **PDF toolchain** | Use Asciidoctor PDF as primary, LaTeX as alternative |
| **Per-format config** | Expose common options, allow raw command args for advanced |
| **req42 integration** | Same build system, separate config file |

---

## Appendix A: Sample Commands

```bash
# Local development
./scripts/build.sh --lang EN --format pdf --flavor plain

# Docker execution
docker-compose run builder build --all

# CI build
docker run -v $PWD/arc42-template:/workspace/arc42-template \
           arc42-builder build --config custom.yaml

# Test specific converter
pytest tests/unit/test_converters.py::TestPdfConverter -v

# Clean and rebuild
make clean && make build

# Release build
./scripts/release.sh --version 9.0 --sign
```

## Appendix B: Error Handling Examples

```python
# Clear error messages
class ValidationError(Exception):
    """Raised when template validation fails"""
    pass

# In validator
if not version_file.exists():
    raise ValidationError(
        f"Missing version.properties for language {lang}\n"
        f"Expected at: {version_file}\n"
        f"Please ensure the template repository is complete."
    )

# In converter
if not self.check_dependencies():
    raise DependencyError(
        f"Required tool 'asciidoctor' not found.\n"
        f"Please ensure Docker image is built correctly.\n"
        f"Run: docker build -t arc42-builder docker/"
    )
```

## Appendix C: Font Troubleshooting Guide

### For Non-Python Developers

This section explains font handling in terms familiar to Java/Groovy developers.

### C.1 How Fonts Work in This System

**Key Points:**
1. **All fonts are in Docker** - You never need to install fonts on your machine
2. **Theme files work like your Groovy config** - Same YAML format, same attributes
3. **Automatic detection** - The system finds theme files just like your Gradle build

### C.2 Common Font Issues and Solutions

| Problem | Solution |
|---------|----------|
| **Chinese text shows as boxes** | Ensure `ZH/asciidoc/pdf-theme/zh-theme.yml` exists |
| **Russian/Ukrainian text broken** | Check that Docker image was built with latest Dockerfile |
| **PDF generation fails** | Run `docker exec [container] fc-list` to verify fonts |
| **Custom font needed** | Add `.ttf` file to `docker/custom-fonts/` and rebuild |

### C.3 Testing Fonts

```bash
# Verify fonts in container (like checking Java classpath)
docker-compose run builder bash -c "fc-list | grep Noto"

# Test single language PDF generation
docker-compose run builder build --lang ZH --format pdf

# Check if theme file is detected (verbose mode)
docker-compose run builder build --lang UKR --format pdf --verbose

# Debug mode (shows all Asciidoctor commands)
LOG_LEVEL=DEBUG docker-compose run builder build --lang ZH --format pdf
```

### C.4 Adding New Language Support

Example: Adding Japanese (JA) support

1. **Create theme file**: `JA/asciidoc/pdf-theme/ja-theme.yml`
```yaml
extends: default
font:
  catalog:
    Noto Sans CJK JP:
      normal: NotoSansCJKjp-Regular.ttf
      bold: NotoSansCJKjp-Bold.ttf
attributes:
  scripts: cjk
  text-align: left
```

2. **Update config**: Add 'JA' to languages in `build.yaml`

3. **Rebuild and test**:
```bash
docker-compose build
docker-compose run builder build --lang JA --format pdf
```

### C.5 Comparison with Gradle Approach

| Your Gradle Code | Python Equivalent | Location |
|------------------|-------------------|----------|
| `def pdfThemeYmlFile = file(...)` | `theme_yml_path = Path(...)` | `pdf.py` line 31 |
| `if(pdfThemeYmlFile.exists())` | `if theme_yml_path.exists():` | `pdf.py` line 35 |
| `attributes asciidocAttributes + [...]` | `attributes['pdf-theme'] = ...` | `pdf.py` line 38 |
| `'pdf-fontsdir': file(...).absolutePath` | `attributes['pdf-fontsdir'] = str(...)` | `pdf.py` line 41 |
| `'script': 'cjk'` | `attributes['scripts'] = 'cjk'` | `pdf.py` line 45 |

### C.6 Font File Locations

```
# In Docker container (not on host):
/usr/share/fonts/           # System fonts (from apt-get)
├── truetype/
│   ├── noto/              # Noto fonts for all languages
│   ├── liberation/        # Liberation fonts
│   └── custom/            # Your custom fonts (if any)

# In template repository:
arc42-template/
└── ZH/asciidoc/pdf-theme/
    ├── zh-theme.yml       # Theme configuration (like your Groovy)
    └── fonts/             # Optional: override fonts
```

### C.7 Quick Validation Script

Create `test-fonts.sh`:
```bash
#!/bin/bash
# Test that all language PDFs can be generated

LANGUAGES="EN DE ZH UKR RU CZ"

for lang in $LANGUAGES; do
    echo "Testing $lang..."
    docker-compose run builder build \
        --lang $lang \
        --format pdf \
        --flavor plain
    
    if [ $? -eq 0 ]; then
        echo "✓ $lang PDF generated successfully"
    else
        echo "✗ $lang PDF generation failed"
        exit 1
    fi
done

echo "All language PDFs generated successfully!"
```

---

## Summary: Font Handling Approach

### The Complete Solution

This build system handles internationalization and fonts through a **fully self-contained Docker container** that:

1. **Pre-installs all required fonts** via Ubuntu packages (Noto font family covers all languages)
2. **Never depends on host machine fonts** - everything runs inside Docker
3. **Auto-detects language-specific PDF themes** - same approach as your current Groovy build
4. **Falls back gracefully** - if no theme file exists, uses sensible defaults

### Key Benefits Over Current Approach

- **Zero host dependencies** - Works identically on any machine with Docker
- **Easier maintenance** - Fonts updated via Dockerfile, not individual machines
- **Better debugging** - Clear error messages when fonts are missing
- **Extensible** - Adding new languages just requires a theme file

### Migration from Gradle/Groovy

Your existing PDF theme files (`{lang}-theme.yml`) work without modification. The Python code reads them the same way your Groovy code does. The main difference is that all tools and fonts live inside Docker, making the build 100% reproducible.

---

This solution proposal provides a comprehensive, implementable approach that fulfills all requirements while maintaining simplicity and extensibility. The modular architecture allows for parallel development and easy maintenance.
