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
    SKIP_BINARY=1
fi

tarball="$DEPS/codex-app-server-$CODEX_VERSION.tar.gz"
if [ "${SKIP_BINARY:-}" != 1 ]; then
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
fi

# Model catalog for third-party provider slugs: codex only offers its
# apply_patch editing tool (and accurate context windows) to models with
# catalog metadata, so clone the pinned upstream entries under the
# OpenRouter slugs we route to them.
MODELS_URL="https://raw.githubusercontent.com/openai/codex/rust-v0.145.0/codex-rs/models-manager/models.json"
MODELS_SHA256="497d7653bb22358baa29ebd4a70be55ce990b73a64896848a59179485b37db9d"
models_json="$DEPS/codex-models-$CODEX_VERSION.json"
if [ ! -f "$models_json" ] || [ "$(shasum -a 256 "$models_json" | cut -d' ' -f1)" != "$MODELS_SHA256" ]; then
    curl -fL -o "$models_json" "$MODELS_URL"
fi
actual=$(shasum -a 256 "$models_json" | cut -d' ' -f1)
if [ "$actual" != "$MODELS_SHA256" ]; then
    echo "sha256 mismatch for $models_json: $actual != $MODELS_SHA256" >&2
    exit 1
fi
uv run --no-project python3 - "$models_json" "$DEST/model-catalog.json" <<'PYEOF'
import json, sys
catalog = json.load(open(sys.argv[1]))
by_slug = {m["slug"]: m for m in catalog["models"]}
def clone(base, slug):
    entry = dict(by_slug[base])
    entry["slug"] = slug
    entry["display_name"] = slug
    entry["visibility"] = "hide"
    # These models are reached through a third-party proxy of the plain
    # OpenAI API: first-party-only server tools must stay off or the
    # backend rejects the request (e.g. "Tool 'tool_search' is not
    # supported with gpt-5-mini").
    entry["supports_search_tool"] = False
    entry["experimental_supported_tools"] = []
    entry["tool_mode"] = None
    return entry
catalog["models"] += [
    clone("gpt-5.4", "openai/gpt-5"),
    clone("gpt-5.4", "openrouter/auto"),
    clone("gpt-5.4-mini", "openai/gpt-5-mini"),
    clone("gpt-5.4-mini", "openai/gpt-5-nano"),
]
json.dump(catalog, open(sys.argv[2], "w"))
PYEOF
echo "installed: $DEST/model-catalog.json"
