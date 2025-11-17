# Makefile for arc42-template-build
#
# This Makefile provides a Docker-only build system.
# Requirements: Docker (or Docker Compose) - nothing else!
#
# Works in:
# - Local development (Linux, macOS, Windows with Docker Desktop)
# - GitHub Codespaces
# - Any CI/CD system with Docker support

# --- Configuration ---
TEMPLATE_DIR = arc42-template

# Detect docker compose command (handles both old and new syntax)
DOCKER_COMPOSE ?= $(shell command -v docker-compose 2> /dev/null)
ifeq ($(DOCKER_COMPOSE),)
DOCKER_COMPOSE = $(shell command -v docker 2> /dev/null) compose
endif

# Ensure we found a docker compose command
ifeq ($(DOCKER_COMPOSE),)
    $(error "Docker Compose not found. Please install Docker: https://docs.docker.com/get-docker/")
endif

# Docker Compose run command (removes container after execution)
DC_RUN = $(DOCKER_COMPOSE) run --rm builder

# Phony targets
.PHONY: all build build-image check validate test clean shell help update-submodule

# --- Default Target ---
all: build

# --- Help ---
help:
	@echo "arc42-template-build - Docker-only build system"
	@echo ""
	@echo "Requirements: Docker (or Docker Compose) - nothing else!"
	@echo ""
	@echo "Available targets:"
	@echo "  all                - (Default) Runs 'build'"
	@echo "  build              - Build Docker image and generate all templates"
	@echo "  build-image        - Build Docker image only (no template generation)"
	@echo "  check              - Verify Docker is available and submodule exists"
	@echo "  validate           - Run pre-build validation (inside Docker)"
	@echo "  test               - Run tests (inside Docker)"
	@echo "  clean              - Remove all generated artifacts"
	@echo "  shell              - Open a shell inside the Docker container (for debugging)"
	@echo "  update-submodule   - Initialize/update git submodules"
	@echo ""
	@echo "Examples:"
	@echo "  make build                    - Full build (all languages, formats, flavors)"
	@echo "  make validate                 - Validate configuration and dependencies"
	@echo "  make test                     - Run test suite"
	@echo "  make shell                    - Debug inside container"
	@echo ""
	@echo "Advanced (override docker compose command):"
	@echo "  $(DC_RUN) build --lang EN --format pdf --flavor withHelp"

# --- Main Build Target ---
build: check build-image
	@echo "==> Running build process inside Docker container..."
	$(DC_RUN)
	@echo ""
	@echo "==> Build complete! Outputs in workspace/build/"

# --- Build Docker Image Only ---
build-image:
	@echo "==> Building Docker image..."
	$(DOCKER_COMPOSE) build builder
	@echo "==> Docker image built successfully"

# --- Validation (runs inside Docker) ---
validate: build-image
	@echo "==> Running validation inside Docker..."
	$(DC_RUN) validate
	@echo "==> Validation complete"

# --- Tests (runs inside Docker) ---
test: build-image
	@echo "==> Running tests inside Docker..."
	$(DC_RUN) test
	@echo "==> Tests complete"

# --- Host-level Checks (minimal, Docker-only) ---
check:
	@echo "==> Checking prerequisites (host)..."
	@echo "    [1/3] Checking Docker availability..."
	@if ! command -v docker > /dev/null 2>&1; then \
		echo "    [ERROR] Docker not found. Install from: https://docs.docker.com/get-docker/"; \
		exit 1; \
	fi
	@echo "    [OK] Docker found: $$(docker --version)"
	@echo "    [2/3] Checking Docker Compose availability..."
	@if [ -z "$(DOCKER_COMPOSE)" ]; then \
		echo "    [ERROR] Docker Compose not found."; \
		exit 1; \
	fi
	@echo "    [OK] Docker Compose found"
	@echo "    [3/3] Checking template submodule..."
	@if [ ! -d "$(TEMPLATE_DIR)/.git" ]; then \
		echo "    [WARNING] Template submodule not initialized. Run 'make update-submodule'."; \
	else \
		echo "    [OK] Template submodule present"; \
	fi
	@echo ""
	@echo "==> Prerequisites check complete. Docker-only setup verified!"

# --- Update Submodules ---
update-submodule:
	@echo "==> Initializing and updating git submodule..."
	@if command -v git > /dev/null 2>&1; then \
		git submodule update --init --recursive; \
		echo "==> Submodule update complete"; \
	else \
		echo "[ERROR] Git not found. Please install git or run in a container with git."; \
		exit 1; \
	fi

# --- Clean ---
clean:
	@echo "==> Cleaning build artifacts..."
	rm -rf workspace/build workspace/dist workspace/logs
	@echo "==> Clean complete"

# --- Shell (for debugging) ---
shell: build-image
	@echo "==> Opening shell in Docker container..."
	@echo "    Tip: You can run 'python3 -m src.arc42_builder --help' inside"
	$(DOCKER_COMPOSE) run --rm builder /bin/bash
