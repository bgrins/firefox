#!/bin/sh
# Builds/fetches the runtime dependencies for the about:harness micro-VM
# into the objdir:
#   dist/bin/libkrun.dylib           built from vendored third_party/libkrun
#   dist/bin/libkrunfw.5.dylib       prebuilt guest kernel bundle (GPL; fetched,
#                                    never vendored - see third_party/libkrun/moz.yaml)
#   dist/bin/harness/rootfs-template/  Alpine minirootfs, copied per-profile at runtime
#
# Requires: rust with the aarch64-unknown-linux-musl target, lld (brew install lld).
set -eu

LIBKRUNFW_URL="https://github.com/libkrun/libkrunfw/releases/download/v5.5.0/libkrunfw-prebuilt-aarch64.tgz"
LIBKRUNFW_SHA256="5bfae6efee63dbdf04a8fac2a69d772d9f900af2f54c4429b4acdfd6d86b9979"
ALPINE_URL="https://dl-cdn.alpinelinux.org/alpine/v3.22/releases/aarch64/alpine-minirootfs-3.22.5-aarch64.tar.gz"
ALPINE_SHA256="3fbc6285032ed46821b511292633d7b2a6306a2e254f590e92bdafff56cf2f70"

TOPSRCDIR=$(cd "$(dirname "$0")/../../../.." && pwd)
if [ -z "${OBJDIR:-}" ]; then
    reldir=$(sed -n 's/^mk_add_options MOZ_OBJDIR=//p' "$TOPSRCDIR/mozconfig")
    OBJDIR="$TOPSRCDIR/${reldir#./}"
fi
BIN="$OBJDIR/dist/bin"
DEPS="$OBJDIR/harness-deps"
mkdir -p "$BIN" "$DEPS"

fetch() {
    url=$1; sha=$2; out=$3
    if [ ! -f "$out" ] || [ "$(shasum -a 256 "$out" | cut -d' ' -f1)" != "$sha" ]; then
        echo "Fetching $url"
        curl -fL -o "$out" "$url"
    fi
    actual=$(shasum -a 256 "$out" | cut -d' ' -f1)
    if [ "$actual" != "$sha" ]; then
        echo "sha256 mismatch for $out: $actual != $sha" >&2
        exit 1
    fi
}

if [ "$(uname -sm)" != "Darwin arm64" ]; then
    echo "harness VM deps are only supported on macOS arm64" >&2
    exit 1
fi

echo "=== libkrunfw (guest kernel) ==="
if [ ! -f "$BIN/libkrunfw.5.dylib" ] || [ "${FORCE:-}" = 1 ]; then
    fetch "$LIBKRUNFW_URL" "$LIBKRUNFW_SHA256" "$DEPS/libkrunfw-prebuilt.tgz"
    rm -rf "$DEPS/libkrunfw"
    tar -xzf "$DEPS/libkrunfw-prebuilt.tgz" -C "$DEPS"
    make -C "$DEPS/libkrunfw"
    cp "$DEPS/libkrunfw/libkrunfw.5.dylib" "$BIN/"
else
    echo "already built, skipping (FORCE=1 to rebuild)"
fi

echo "=== libkrun (from third_party/libkrun) ==="
command -v ld.lld >/dev/null || { echo "ld.lld not found: brew install lld" >&2; exit 1; }
LIBKRUN_DIR="$TOPSRCDIR/third_party/libkrun"
# Provision the Debian header sysroot the guest init blob is cross-compiled
# against (upstream Makefile rule); target/ and linux-sysroot/ are gitignored.
make -C "$LIBKRUN_DIR" linux-sysroot/.sysroot_ready
SYSROOT="$LIBKRUN_DIR/linux-sysroot"
GCC_LIB_DIR="$SYSROOT/usr/lib/gcc/aarch64-linux-gnu/12"
export CC_LINUX="/usr/bin/clang -target aarch64-linux-gnu -fuse-ld=lld -Wl,-strip-debug --sysroot $SYSROOT -B$GCC_LIB_DIR -L$GCC_LIB_DIR -Wno-c23-extensions"
# Build only the libkrun package: the full workspace includes bindgen-based
# optional crates (input/display) that require libclang and aren't needed.
(cd "$LIBKRUN_DIR" && cargo build --release -p libkrun)
cp "$LIBKRUN_DIR/target/release/libkrun.dylib" "$BIN/"

echo "=== guest-agent (static aarch64-linux, via the same sysroot) ==="
mkdir -p "$BIN/harness"
$CC_LINUX -O2 -static -Wall -Wextra \
    -I"$LIBKRUN_DIR/src/init_blob/init" \
    -o "$BIN/harness/guest-agent" \
    "$TOPSRCDIR/browser/components/harness/guest/guest-agent.c"

echo "=== Alpine rootfs template ==="
# Extra packages baked into the template (the guest has no network). Alpine
# apks are plain tarballs; extracted directly, no apk tool needed.
APK_BASE="https://dl-cdn.alpinelinux.org/alpine/v3.22/main/aarch64"
APKS="
sqlite-3.49.2-r1 23cc7ebfee1170d2e6be5740ef5eae1c522691e164e399629f9147705370e8c9
sqlite-libs-3.49.2-r1 204910bcbb13df4d517cb01acb178ebe14f12ff0e55a04b38d1565941780ee29
readline-8.2.13-r1 334af29dbf6b5a71a87af4d6a58e2967a8f711a51d00093de0e1498daf83ceb2
libncursesw-6.5_p20250503-r0 419b375e8a4345e7172b1f0f3a3c57db61374f5408cdb875d9e860bd4c243aca
ncurses-terminfo-base-6.5_p20250503-r0 3d37403e0b5ab9eb0c1ce269444e4a385faec9fe6af452c1c6956806b13d2bd6
"
if [ ! -d "$BIN/harness/rootfs-template" ] || [ "${FORCE:-}" = 1 ]; then
    fetch "$ALPINE_URL" "$ALPINE_SHA256" "$DEPS/alpine-minirootfs.tar.gz"
    rm -rf "$BIN/harness/rootfs-template"
    mkdir -p "$BIN/harness/rootfs-template"
    tar -xzf "$DEPS/alpine-minirootfs.tar.gz" -C "$BIN/harness/rootfs-template"
    echo "$APKS" | while read -r pkg sha; do
        [ -n "$pkg" ] || continue
        fetch "$APK_BASE/$pkg.apk" "$sha" "$DEPS/$pkg.apk"
        tar -xzf "$DEPS/$pkg.apk" -C "$BIN/harness/rootfs-template" \
            --exclude '.PKGINFO' --exclude '.SIGN.*' 2>/dev/null || true
    done
else
    echo "already extracted, skipping (FORCE=1 to redo)"
fi

echo "=== done ==="
ls -lh "$BIN/libkrun.dylib" "$BIN/libkrunfw.5.dylib"
