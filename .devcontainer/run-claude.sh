#!/bin/bash
set -e

echo "Starting Firefox devcontainer with Claude Code..."
echo ""

docker run -it --rm \
  --cap-add=NET_ADMIN \
  --cap-add=NET_RAW \
  -v "$(pwd):/workspace" \
  -v firefox-commandhistory:/commandhistory \
  -v firefox-claude-config:/home/dev/.claude \
  -v firefox-mozbuild:/home/dev/.mozbuild \
  -v firefox-cargo:/home/dev/.cargo \
  -v firefox-rustup:/home/dev/.rustup \
  -w /workspace \
  -e MOZBUILD_STATE_PATH=/home/dev/.mozbuild \
  -e CLAUDE_CONFIG_DIR=/home/dev/.claude \
  firefox-devcontainer:latest \
  bash -c "sudo /usr/local/bin/init-firewall.sh && exec claude --dangerously-skip-permissions"
