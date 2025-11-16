# arc42-template-build Proof of Concept

Proof-of-concept for a different approach to creating the complex build matrix for the arc42 template


## Overview
This is a proof of concept for the new arc42 build system using Python and Docker.

## Current PoC Scope
- Languages: EN, DE only
- Flavor: withHelp only  
- Formats: HTML, PDF, DOCX

## Prerequisites
- Docker
- Docker Compose
- Git

## Setup
```bash
# Clone and initialize
git clone [your-repo-url] arc42-build
cd arc42-build
git submodule update --init --recursive

# Build and run
./build.sh

# Test outputs
./test.sh
```

## Project Structure
```
arc42-build/
├── arc42-template/        # Submodule with content
├── docker/               # Docker configuration
├── src/arc42_builder/    # Python build system
├── workspace/            # Build outputs
│   └── build/           # Generated files
├── build.sh             # Main build script
└── docker-compose.yml   # Docker orchestration
```

## Next Steps
- [ ] Add plain flavor support
- [ ] Add more languages (FR, ZH, UKR, RU, CZ)
- [ ] Add more formats (Markdown, Confluence)
- [ ] Implement proper plugin architecture
- [ ] Add configuration file support
- [ ] Add parallel builds
- [ ] Create ZIP packaging