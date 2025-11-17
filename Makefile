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
.PHONY: all build build-image check validate test test-build-artifacts dist clean shell help update-submodule update-submodule-latest

# --- Default Target ---
all: build

# --- Help ---
help:
	@echo "arc42-template-build - Docker-only build system"
	@echo ""
	@echo "Requirements: Docker (or Docker Compose) - nothing else!"
	@echo ""
	@echo "Available targets:"
	@echo "  all                    - (Default) Runs 'build'"
	@echo "  build                  - Build Docker image and generate all templates"
	@echo "  build-image            - Build Docker image only (no template generation)"
	@echo "  check                  - Verify Docker is available and submodule exists"
	@echo "  validate               - Run pre-build validation (inside Docker)"
	@echo "  test                   - Run tests (inside Docker)"
	@echo "  test-build-artifacts   - Validate build artifacts for syntax and missing images"
	@echo "  dist                   - Create ZIP distributions of build artifacts"
	@echo "  clean                  - Remove all generated artifacts"
	@echo "  shell                  - Open a shell inside the Docker container (for debugging)"
	@echo "  update-submodule       - Initialize/update to commit referenced in parent repo"
	@echo "  update-submodule-latest - Update to latest from branch (default: master)"
	@echo ""
	@echo "Examples:"
	@echo "  make build                         - Full build (all languages, formats, flavors)"
	@echo "  make validate                      - Validate configuration and dependencies"
	@echo "  make test                          - Run test suite"
	@echo "  make shell                         - Debug inside container"
	@echo "  make update-submodule              - Safe update (no parent repo changes)"
	@echo "  make update-submodule-latest       - Update to latest from master branch"
	@echo "  make update-submodule-latest SUBMODULE_BRANCH=9.0-draft - Update to latest from specific branch"
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

# --- Test Build Artifacts (runs inside Docker) ---
test-build-artifacts: build-image
	@echo "==> Validating build artifacts inside Docker..."
	$(DC_RUN) test-artifacts
	@echo "==> Build artifact validation complete"

# --- Create Distribution ZIPs (runs inside Docker) ---
dist: build-image
	@echo "==> Creating ZIP distributions inside Docker..."
	$(DC_RUN) dist
	@echo "==> Distribution packages created in workspace/dist/"

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
# Updates submodule to the commit referenced in parent repo (safe, no changes to parent)
update-submodule:
	@echo "==> Initializing and updating git submodule..."
	@if ! command -v git > /dev/null 2>&1; then \
		echo "[ERROR] Git not found. Please install git."; \
		exit 1; \
	fi
	@# Try standard submodule update first
	@if git submodule update --init --recursive 2>/dev/null; then \
		echo "==> Submodule updated successfully to commit: $$(cd $(TEMPLATE_DIR) && git rev-parse --short HEAD)"; \
	else \
		echo "    [WARNING] Standard submodule update failed. Attempting recovery..."; \
		echo "    [INFO] Removing and re-cloning submodule..."; \
		rm -rf $(TEMPLATE_DIR); \
		git submodule update --init --recursive || { \
			echo "    [ERROR] Failed to initialize submodule. The referenced commit may not exist."; \
			echo "    [HINT] Try 'make update-submodule-latest' to update to latest from master branch."; \
			exit 1; \
		}; \
		echo "==> Submodule recovered and updated to commit: $$(cd $(TEMPLATE_DIR) && git rev-parse --short HEAD)"; \
	fi

# Updates submodule to latest commit from specified branch (updates parent repo reference)
# Usage: make update-submodule-latest [BRANCH=master]
SUBMODULE_BRANCH ?= master
update-submodule-latest:
	@echo "==> Updating submodule to latest from branch '$(SUBMODULE_BRANCH)'..."
	@if ! command -v git > /dev/null 2>&1; then \
		echo "[ERROR] Git not found. Please install git."; \
		exit 1; \
	fi
	@# Ensure submodule is initialized
	@if [ ! -d "$(TEMPLATE_DIR)/.git" ]; then \
		echo "    [INFO] Submodule not initialized. Cloning..."; \
		rm -rf $(TEMPLATE_DIR); \
		git clone https://github.com/arc42/arc42-template.git $(TEMPLATE_DIR); \
	fi
	@# Show current commit
	@echo "    [INFO] Current commit: $$(cd $(TEMPLATE_DIR) && git rev-parse --short HEAD 2>/dev/null || echo 'unknown')"
	@# Fetch and checkout latest from branch
	@cd $(TEMPLATE_DIR) && \
		git fetch origin $(SUBMODULE_BRANCH) && \
		git checkout $(SUBMODULE_BRANCH) && \
		git pull origin $(SUBMODULE_BRANCH) && \
		echo "    [INFO] Updated to commit: $$(git rev-parse --short HEAD) ($$(git log -1 --format='%s'))"
	@# Check if parent repo needs updating
	@if git diff --quiet $(TEMPLATE_DIR); then \
		echo "==> Submodule already at latest commit from $(SUBMODULE_BRANCH)"; \
	else \
		echo "    [INFO] Submodule reference changed in parent repo"; \
		echo "    [ACTION REQUIRED] Stage and commit the change:"; \
		echo "        git add $(TEMPLATE_DIR)"; \
		echo "        git commit -m 'Update arc42-template submodule to latest from $(SUBMODULE_BRANCH)'"; \
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
