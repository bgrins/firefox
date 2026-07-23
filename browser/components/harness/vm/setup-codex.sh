#!/bin/sh
# Fetches the pinned Codex App Server binary (see docs/codex-integration-plan.md)
# into the objdir:
#   dist/bin/harness/codex/codex-app-server   pinned, sha256-verified sidecar
#
# The binary is never committed and never resolved to "latest" at runtime;
# bump the pins here deliberately and regenerate the protocol schema when
# doing so.
set -eu

CODEX_VERSION="0.145.0"
CODEX_URL="https://github.com/openai/codex/releases/download/rust-v0.145.0/codex-app-server-aarch64-apple-darwin.tar.gz"
CODEX_SHA256="4a62b65e37fa2b16e0f77b11ff199f10e446ed46278c5178a86787d14c16fa2e"

TOPSRCDIR=$(cd "$(dirname "$0")/../../../.." && pwd)
if [ -z "${OBJDIR:-}" ]; then
    reldir=$(sed -n 's/^mk_add_options MOZ_OBJDIR=//p' "$TOPSRCDIR/mozconfig")
    OBJDIR="$TOPSRCDIR/${reldir#./}"
fi
DEST="$OBJDIR/dist/bin/harness/codex"
DEPS="$OBJDIR/harness-deps"
mkdir -p "$DEST" "$DEPS"

if [ "$(uname -sm)" != "Darwin arm64" ]; then
    echo "pinned codex asset is macOS arm64 only" >&2
    exit 1
fi

if [ -x "$DEST/codex-app-server" ] && [ "${FORCE:-}" != 1 ] &&
    "$DEST/codex-app-server" --version | grep -q "$CODEX_VERSION"; then
    echo "codex-app-server $CODEX_VERSION already installed, skipping (FORCE=1 to refetch)"
    exit 0
fi

tarball="$DEPS/codex-app-server-$CODEX_VERSION.tar.gz"
if [ ! -f "$tarball" ] || [ "$(shasum -a 256 "$tarball" | cut -d' ' -f1)" != "$CODEX_SHA256" ]; then
    echo "Fetching $CODEX_URL"
    curl -fL -o "$tarball" "$CODEX_URL"
fi
actual=$(shasum -a 256 "$tarball" | cut -d' ' -f1)
if [ "$actual" != "$CODEX_SHA256" ]; then
    echo "sha256 mismatch for $tarball: $actual != $CODEX_SHA256" >&2
    exit 1
fi

workdir=$(mktemp -d)
tar -xzf "$tarball" -C "$workdir"
mv "$workdir/codex-app-server-aarch64-apple-darwin" "$DEST/codex-app-server"
rmdir "$workdir"
chmod 555 "$DEST/codex-app-server"

version=$("$DEST/codex-app-server" --version)
if [ "$version" != "codex-app-server $CODEX_VERSION" ]; then
    echo "unexpected version: $version" >&2
    exit 1
fi
echo "installed: $DEST/codex-app-server ($version)"
