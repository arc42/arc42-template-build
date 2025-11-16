# Makefile for arc42-template-build
#
# This Makefile provides a modern and flexible way to manage the build process.
#

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
.PHONY: all build update-submodule help

# The default target executed when you run `make`.
all: build

# Display help information.
help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Available targets:"
	@echo "  all                - (Default) Alias for 'build'."
	@echo "  build              - Build the Docker image and run the main build process to generate templates."
	@echo "  update-submodule   - Initializes and/or updates the 'arc42-template' git submodule."
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

