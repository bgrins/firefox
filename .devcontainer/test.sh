#!/bin/bash
set -e

echo "Testing Firefox devcontainer..."
echo ""

echo "1. Checking if image exists..."
if docker image inspect firefox-devcontainer:latest &> /dev/null; then
  echo "   ✓ Image found"
else
  echo "   ✗ Image not found. Run ./devcontainer/build.sh first"
  exit 1
fi

echo ""
echo "2. Testing container startup..."
docker run --rm \
  --cap-add=NET_ADMIN \
  --cap-add=NET_RAW \
  -v "$(pwd):/workspace" \
  -w /workspace \
  firefox-devcontainer:latest \
  bash -c "whoami && pwd"

echo ""
echo "3. Testing Claude Code CLI..."
docker run --rm \
  --cap-add=NET_ADMIN \
  --cap-add=NET_RAW \
  -v "$(pwd):/workspace" \
  -w /workspace \
  firefox-devcontainer:latest \
  bash -c "claude --version"

echo ""
echo "4. Testing firewall (this will take ~30 seconds)..."
docker run --rm \
  --cap-add=NET_ADMIN \
  --cap-add=NET_RAW \
  -v "$(pwd):/workspace" \
  -w /workspace \
  firefox-devcontainer:latest \
  bash -c "timeout 30 sudo /usr/local/bin/init-firewall.sh 2>&1 | tail -10"

echo ""
echo "All tests passed!"
echo ""
echo "To use the container:"
echo "  - Interactive shell: ./.devcontainer/run.sh"
echo "  - Run Claude: ./.devcontainer/run-claude.sh"
