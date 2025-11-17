# Makefile for arc42-template-build
#
# This Makefile provides a modern and flexible way to manage the build process.
#

# --- Configuration ---
# Note: The template directory is currently hardcoded here for the 'check' target.
# If you change it in config/build.yaml, you must also update it here.
TEMPLATE_DIR = arc42-template

# Use shell to find an available docker compose command
DOCKER_COMPOSE ?= $(shell command -v docker-compose 2> /dev/null)
ifeq ($(DOCKER_COMPOSE),)
DOCKER_COMPOSE = $(shell command -v docker 2> /dev/null) compose
endif

# Ensure we found a docker compose command
ifeq ($(DOCKER_COMPOSE),)
    $(error "docker-compose or docker compose not found. Please install Docker Compose.")
endif

# Phony targets prevent conflicts with files of the same name.
.PHONY: all build update-submodule clean check help

# The default target executed when you run `make`.
all: build

# Display help information.
help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Available targets:"
	@echo "  all                - (Default) Alias for 'build'."
	@echo "  build              - Build the Docker image and run the main build process to generate templates."
	@echo "  update-submodule   - Initializes and/or updates the git submodule defined in config/build.yaml (e.g., arc42-template)."
	@echo "  check              - Verifies the project setup and submodule status on the host."
	@echo "  clean              - Removes all generated build artifacts and log files."
	@echo ""
	@echo "Example:"
	@echo "  make build         - Runs the complete build process."


# Build the Docker image and then run the builder service.
build:
	@echo "--> Building Docker image for the builder service..."
	$(DOCKER_COMPOSE) build builder
	@echo "--> Running the build process inside Docker..."
	$(DOCKER_COMPOSE) run --rm builder
	@echo "--> Build finished. Check the 'workspace/build' directory for artifacts."

# Update the git submodule.
update-submodule:
	@echo "--> Initializing and updating git submodule..."
	git submodule update --init --recursive
	@echo "--> Submodule update complete."

# Perform system and dependency checks on the host.
check:
	@echo "--> Performing system checks on host..."
	@FAIL=0; \
	echo "    (Using template directory: $(TEMPLATE_DIR))"; \
	REQUIRED_DIRS="$(TEMPLATE_DIR) docker src config"; \
	for dir in $$REQUIRED_DIRS; do \
		if [ -d "$$dir" ]; then \
			echo "  [OK]      Directory '$$dir' found."; \
		else \
			echo "  [MISSING] Directory '$$dir' not found."; \
			FAIL=1; \
		fi; \
	done; \
	\
	REQUIRED_FILES="docker-compose.yaml config/build.yaml Makefile"; \
	for file in $$REQUIRED_FILES; do \
		if [ -f "$$file" ]; then \
			echo "  [OK]      File '$$file' found."; \
		else \
			echo "  [MISSING] File '$$file' not found."; \
			FAIL=1; \
		fi; \
	done; \
	\
	if [ $$FAIL -eq 1 ]; then \
		echo ""; \
		echo "!!! System check failed. Please ensure all required files and directories are present."; \
		exit 1; \
	fi;
	@echo ""
	@echo "--> Checking submodule status ($(TEMPLATE_DIR))..."
	@if [ ! -d "$(TEMPLATE_DIR)" ]; then \
		echo "  [ERROR] Directory '$(TEMPLATE_DIR)' not found. Run 'make update-submodule'."; \
		exit 1; \
	fi
	@if ! (cd $(TEMPLATE_DIR) && git rev-parse --is-inside-work-tree > /dev/null 2>&1); then \
		echo "  [ERROR] '$(TEMPLATE_DIR)' is not a valid Git repository. Run 'make update-submodule'."; \
		exit 1; \
	fi
	@cd $(TEMPLATE_DIR) && \
	git fetch > /dev/null 2>&1 && \
	STATUS=$$(git status -uno) && \
	if echo "$$STATUS" | grep -q "Your branch is up to date"; then \
		echo "  [OK]      Submodule is up to date."; \
	elif echo "$$STATUS" | grep -q "Your branch is behind"; then \
		echo "  [WARNING] Submodule is behind origin. Run 'make update-submodule'."; \
	else \
		echo "  [INFO]    Submodule status: $$STATUS"; \
	fi;
	@echo ""
	@echo "--> System checks complete."


# Clean up the workspace.
clean:
	@echo "--> Cleaning up build artifacts and logs..."
	rm -rf workspace build dist logs temp
	@echo "--> Cleanup complete."
