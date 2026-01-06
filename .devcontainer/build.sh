#!/bin/bash
set -e

echo "Building Firefox devcontainer..."
docker build -t firefox-devcontainer:latest .devcontainer/

echo ""
echo "Build complete! Image: firefox-devcontainer:latest"
echo ""
echo "Next steps:"
echo "  - Run interactively: ./.devcontainer/run.sh"
echo "  - Run Claude: ./.devcontainer/run-claude.sh"
