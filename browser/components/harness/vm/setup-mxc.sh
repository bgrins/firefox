#!/bin/sh
# Builds the pinned MXC (Microsoft eXecution Container) macOS backend binary
# into the objdir:
#   dist/bin/harness/mxc/mxc-exec-mac   Seatbelt sandbox wrapper
#
# This is the host-execution alternative to the libkrun micro-VM (see
# docs/mxc-spike.md). Source is fetched at a pinned commit, sha256-verified,
# and built with the repo's pinned Rust toolchain. Never committed, never
# resolved to "latest"; bump the pins here deliberately.
set -eu

MXC_COMMIT="32a4c44a0fdff828786f24bcbfe5ec257fe89c94"
MXC_SHA256="e6e2d7b987e366f0189ffe528f0ac7af1ff48b9938c1ae002ab6d1c9150c3d44"
MXC_URL="https://github.com/microsoft/mxc/archive/$MXC_COMMIT.tar.gz"

TOPSRCDIR=$(cd "$(dirname "$0")/../../../.." && pwd)
if [ -z "${OBJDIR:-}" ]; then
    reldir=$(sed -n 's/^mk_add_options MOZ_OBJDIR=//p' "$TOPSRCDIR/mozconfig")
    OBJDIR="$TOPSRCDIR/${reldir#./}"
fi
DEST="$OBJDIR/dist/bin/harness/mxc"
# Build outside the Firefox tree: cargo walks parent directories for
# .cargo/config.toml, and the tree's crates-io source replacement
# (third_party/rust) breaks the mxc dependency graph.
DEPS="${MXC_DEPS:-$HOME/.mozbuild/harness-mxc-deps}"
mkdir -p "$DEST" "$DEPS"

if [ "$(uname -sm)" != "Darwin arm64" ]; then
    echo "mxc spike targets macOS arm64 only" >&2
    exit 1
fi

if [ -x "$DEST/mxc-exec-mac" ] && [ "${FORCE:-}" != 1 ] &&
    [ "$(cat "$DEST/.mxc-commit" 2>/dev/null)" = "$MXC_COMMIT" ]; then
    echo "mxc-exec-mac @$MXC_COMMIT already installed, skipping (FORCE=1 to rebuild)"
    exit 0
fi

tarball="$DEPS/mxc-$MXC_COMMIT.tar.gz"
if [ ! -f "$tarball" ] || [ "$(shasum -a 256 "$tarball" | cut -d' ' -f1)" != "$MXC_SHA256" ]; then
    echo "Fetching $MXC_URL"
    curl -fL -o "$tarball" "$MXC_URL"
fi
actual=$(shasum -a 256 "$tarball" | cut -d' ' -f1)
if [ "$actual" != "$MXC_SHA256" ]; then
    echo "sha256 mismatch for $tarball: $actual != $MXC_SHA256" >&2
    exit 1
fi

srcdir="$DEPS/mxc-$MXC_COMMIT"
if [ ! -d "$srcdir" ]; then
    tar -xzf "$tarball" -C "$DEPS"
fi

echo "Building mxc_darwin (rust toolchain pinned by the mxc repo)"
(cd "$srcdir/src" && cargo build --release -p mxc_darwin --target aarch64-apple-darwin)

cp "$srcdir/src/target/aarch64-apple-darwin/release/mxc-exec-mac" "$DEST/mxc-exec-mac"
chmod 555 "$DEST/mxc-exec-mac"
echo "$MXC_COMMIT" > "$DEST/.mxc-commit"
echo "installed: $DEST/mxc-exec-mac (@$MXC_COMMIT)"
