#!/bin/bash
# PoC build script

echo "Building arc42 PoC (EN, DE, withHelp only)..."

# Ensure submodule is up to date
git submodule update --init --recursive

# Build Docker image
docker-compose build

# Run the build
docker-compose run --rm builder

echo "Build complete! Check workspace/build/ for outputs"