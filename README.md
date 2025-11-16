# arc42 Build System

This repository contains the automated build system for the [arc42 template](https://github.com/arc42/arc42-template). 
It uses a Python-based orchestrator running inside a self-contained Docker container to generate the template in multiple languages and formats.

## Overview

The goal of this build system is to provide a modern, maintainable, and reproducible way to generate all arc42-template artifacts. 
It is designed to be run both locally by developers and in automated CI/CD pipelines.

**Key Features:**
- **Dockerized:** The entire toolchain, including all required fonts for every language, is packaged in a Docker image for maximum reproducibility.
- **Python-based:** A flexible and extensible Python application orchestrates the entire build process.
- **Configurable:** A simple YAML file (`config/build.yaml`) allows you to control which languages, formats, and flavors are built.
- **Extensible:** A plugin-based architecture makes it easy to add new output formats.

## Prerequisites

- **Docker:** The build system runs entirely within Docker. You must have Docker installed.
- **Docker Compose:** Required to orchestrate the build.
- **Make:** The `Makefile` provides convenient shortcuts for common tasks.
- **Git:** Required to clone this repository and the `arc42-template` submodule.

## Quick Start

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/arc42/arc42-template-build.git
    cd arc42-template-build
    ```

2.  **Initialize the template submodule:**
    This will pull down the `arc42-template` source files.
    ```bash
    make update-submodule
    ```

3.  **Run the build:**
    This command builds the Docker image and runs the build process as defined in `config/build.yaml`.
    ```bash
    make build
    ```

4.  **Find the artifacts:**
    Generated files will be placed in the `build/` directory, organized by language and flavor.

## Makefile Targets

This project uses a `Makefile` to simplify common operations.

- `make build`: (Default) Builds the Docker image and runs the container to generate all configured artifacts.
- `make update-submodule`: Initializes or updates the `arc42-template` git submodule. Run this after cloning or to get the latest template changes.
- `make clean`: Removes all generated files and logs (`build/`, `dist/`, `logs/`, `temp/`).
- `make help`: Displays a list of all available targets.

## Architecture

The build system consists of a Python CLI application that acts as an orchestrator, running inside a Docker container.

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
```

- **Orchestrator:** The main Python application that reads the configuration and manages the build matrix (language × format × flavor).
- **Converter Plugins:** Each output format (HTML, PDF, etc.) is handled by a dedicated plugin. This makes the system easy to extend.
- **Docker Container:** The container holds all dependencies: `asciidoctor`, `pandoc`, Python libraries, and a comprehensive set of fonts to support all languages, including Chinese, Russian, and Ukrainian.

## Configuration

The entire build process is controlled by `config/build.yaml`. You can customize it to build only the artifacts you need.

### Example 1: EN and DE, "withHelp" flavor only

This configuration is useful for a quick build of the primary languages.

```yaml
# config/build.yaml

# Only build German and English
languages:
  - EN
  - DE

# Only build the 'withHelp' flavor
flavors:
  - withHelp

# Enable a subset of formats
formats:
  html:
    enabled: true
  pdf:
    enabled: true
  docx:
    enabled: true
  markdown:
    enabled: false
  asciidoc:
    enabled: false

# Other settings (can be left as default)
build:
  parallel: true
  validate: true
  clean_before: true
```

### Example 2: EN, ZH, FR with both flavors

This example shows how to build for English, Chinese, and French, generating both `plain` and `withHelp` versions.

```yaml
# config/build.yaml

# Build a mix of languages, including one with CJK fonts
languages:
  - EN
  - ZH
  - FR

# Build both flavors
flavors:
  - plain
  - withHelp

# Enable all priority 1 formats
formats:
  html:
    enabled: true
  pdf:
    enabled: true
  docx:
    enabled: true
  markdown:
    enabled: true
  asciidoc:
    enabled: true

# Other settings (can be left as default)
build:
  parallel: true
  validate: true
  clean_before: true
```

## Extending the Build

To add a new output format, you need to:
1.  Create a new converter plugin in `src/arc42_builder/converters/`.
2.  Implement the `ConverterPlugin` interface, which involves calling the required command-line tools (e.g., `pandoc`).
3.  Register the new plugin in `src/arc42_builder/converters/__init__.py`.
4.  Add the new format to `config/build.yaml`.
