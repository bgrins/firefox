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
    "$TOPSRCDIR/browser/components/harness/guest/guest-agent.c" -lutil

echo "=== Alpine rootfs template ==="
# Extra packages baked into the template (the guest has no unrestricted
# network, so everything ships pre-installed). Alpine apks are plain
# tarballs; extracted directly, no apk tool needed. Format: repo pkg-ver sha.
APK_BASE="https://dl-cdn.alpinelinux.org/alpine/v3.22"
APKS="
main sqlite-3.49.2-r1 23cc7ebfee1170d2e6be5740ef5eae1c522691e164e399629f9147705370e8c9
main sqlite-libs-3.49.2-r1 204910bcbb13df4d517cb01acb178ebe14f12ff0e55a04b38d1565941780ee29
main readline-8.2.13-r1 334af29dbf6b5a71a87af4d6a58e2967a8f711a51d00093de0e1498daf83ceb2
main libncursesw-6.5_p20250503-r0 419b375e8a4345e7172b1f0f3a3c57db61374f5408cdb875d9e860bd4c243aca
main ncurses-terminfo-base-6.5_p20250503-r0 3d37403e0b5ab9eb0c1ce269444e4a385faec9fe6af452c1c6956806b13d2bd6
main jq-1.8.1-r0 efcf639087298473a6337ced807b0d6f9a2bca02b6bfc9ec380e9f2d99a36cf7
main oniguruma-6.9.10-r0 486a30ba898571f8f391958494ef3982494dffbc56d368d477293c5159c5c192
main pcre2-10.46-r0 62fdc4a3d6b48ca211cf6480c5da55664b489ec2b192ca8942e5b1d60ebe9496
main libgcc-14.2.0-r6 ba1835eec3ad8a120efd3d5020e561d53553a0513763a08f509e3ce6d4baa9ca
main nodejs-22.23.0-r0 8320f5e9cd6d37225d19a8fa66e437589c14300bc0386841b7f88ec44b74da20
main ada-libs-2.9.2-r4 58147891c4ae32752fd81792dfec19c71b8d88661c4aa30db3f26600df33bb28
main brotli-libs-1.1.0-r2 b05f9d2839bb89f28325890ffbd7d94025af6b301344ae0255f08617a6036c65
main c-ares-1.34.8-r0 e293f056615fff3cf6050a423c090179daf48516317912daf1e133a1095a2f65
main icu-libs-76.1-r1 6c9dd2e6b0ddc6e7d5fd2a21b427799d7ca4f7e8b5aad72d17e84520db3cd249
main icu-data-en-76.1-r1 2c2d36d47c82d0f6cff1b549044fe3562f327f944971ef367b9c40eeb35aa6e8
main nghttp2-libs-1.69.0-r0 19db967a36f1e041e96240484d94063354f5c837e36d50daa017c2e96393a5e7
main simdjson-3.12.0-r0 5605c691ab62e5a0071d065b5afdd5c3740d763821d689a6bf54e46c95916974
main simdutf-7.2.1-r0 b20688ad72d096ba903bc77ea92165153427dcf5d25b5b9dcf27e7b4ca7046b9
main libstdc++-14.2.0-r6 0d2f054057a4f932e985a129eccb79908b40964185139a0a609aed3032aba064
main zlib-1.3.2-r0 7a39a917e4dab3c7a45537210ee5b5f17bf75f5e7777809a20cddd0afe074187
main zstd-libs-1.5.7-r0 a0e92d2225941a514eb0b2325b137fe6444ef9171627aae8129b74a6ad934ac4
main libx11-1.8.11-r0 727ebb88fd3162b667dfd8a0cf3c33034329b6549cf80d52cfccf6acf349ca2a
main libxext-1.3.6-r2 350f7644ff73f655f448f3df8c8ef98310fbcdeb64ddf22672b75dab66d4efc0
main libxcb-1.17.0-r0 c7d7f55f5ea61eefc749201a041e774ad60a5e0ca4d59acc89eb56f6c201b08f
main libxau-1.0.12-r0 1dcbaf3a2995c60ba9f442e580eea9e03a1d68898b54bdc9eeba25a68124888b
main libxdmcp-1.1.5-r1 6988bfc23df3e551de62de498bbe661963f13bac2c48b501d82ddd0a3d3eafe5
main libbz2-1.0.8-r6 1d588037cc45108acafdbb1507e9f683019a8816fb74d9aba9b0a2dc099463c4
main fontconfig-2.15.0-r3 a8bb31f32197dc18297aa3a618f630ed7c3efdfb875caa8a7b1fc2648834cbea
main freetype-2.13.3-r0 0cb7c95edd545b634912d869ff6c50deeedde9b0d18cdc4f934ff9ef816bb1b3
main lcms2-2.19-r0 2272564c0d72b789650c7af3ba24a0fb60f57d12a5ba3d4de2a82aed6eb98535
main libltdl-2.5.4-r1 19c00459c5eefe59eb65ec45da84c3d84e6872eaf1a12eac1c6a767463d2c29b
main libgomp-14.2.0-r6 97a2f9a89d8b3cc7714e1d5a0ab2e01bce711e8a3b330db36b5f876d9aa4ec8c
main xz-libs-5.8.3-r0 9de7f0fb5f4b6abbe7b7097e94d2787978569c5e143cd144d314e6776382db7c
main libpng-1.6.57-r0 4d871a688175d16437e47dc3502e80f4cbaf927680383d221379c26b03523345
main libxml2-2.13.9-r1 e358e1c32ba6923386263dd641a6e4bcb56a0345fecadef9ef1103892cf3d81d
main fftw-double-libs-3.3.10-r6 e9ccb8ec20e085c1e8d254959f7abca4c54f03130e0b5aa9656e9fc327a179a3
main libexpat-2.8.2-r0 48926478e6c1351251550fc38749cb14aab0933b998ffc919f6b0a5ff25bbdb2
main libbsd-0.12.2-r0 8a51acec613887f12a294685465c17b0d03f2c9b1adfae805d8e6b8d8421cd77
main libmd-1.1.0-r0 b1624431ed1932069c17b02f21e1fb2c8d4db42c3be1e2f8c5a22ccac27b78aa
community ripgrep-14.1.1-r0 f9c145aca9868a3a90d57d4eb89a4c1c92bc4f06870311d230856f68cf6e58bd
community yq-go-4.47.2-r3 02474d93a7b5c82e31c5d3de4fca43e145545dc9dfa0145d7e3003c2e1448882
community imagemagick-7.1.2.15-r0 0235c89fe5a71a374742d430afb95f3f6262ea7f63c8746fcd62c49102836a13
community imagemagick-libs-7.1.2.15-r0 3168293ea5af18c20c7800a54e22394234a37205c0ccc44361fafd8aed6578ff
"
# Static musl binaries fetched outside apk.
UV_VERSION="0.11.31"
UV_URL="https://github.com/astral-sh/uv/releases/download/0.11.31/uv-aarch64-unknown-linux-musl.tar.gz"
UV_SHA256="49cb5ffce40cc9c85355caa8104f7b61c40a8daac7334f4bc841cad1a7bb359e"
# CPython for uv: the guest has no unrestricted network, so uv cannot
# download an interpreter on demand; bake one into the image instead
# (dynamically linked against musl, so musllinux wheels load).
PYTHON_URL="https://github.com/astral-sh/python-build-standalone/releases/download/20260718/cpython-3.13.14+20260718-aarch64-unknown-linux-musl-install_only_stripped.tar.gz"
PYTHON_SHA256="4d43ada1f37d09c118b4a205b5baafd03bac279b07cdedd382aa1a4367f8c15f"
# Bun: preferred script runtime; runs TS directly and auto-installs npm
# dependencies from bare imports without a package.json.
BUN_URL="https://github.com/oven-sh/bun/releases/download/bun-v1.3.14/bun-linux-aarch64-musl.zip"
BUN_SHA256="b98e0ad3625c5c00d1d5b5ff55605c7adddbfae151861e68ade57b2d3b8703bb"
# The stamp ties a built template to this script's contents: the template is
# re-extracted when the script changes, and HarnessVM re-copies a profile
# rootfs whose stamp no longer matches the template's.
STAMP=$(shasum -a 256 "$0" | cut -c1-16)
CURRENT_STAMP=$(cat "$BIN/harness/rootfs-template/.rootfs-stamp" 2>/dev/null || true)
if [ "$CURRENT_STAMP" != "$STAMP" ] || [ "${FORCE:-}" = 1 ]; then
    fetch "$ALPINE_URL" "$ALPINE_SHA256" "$DEPS/alpine-minirootfs.tar.gz"
    rm -rf "$BIN/harness/rootfs-template"
    mkdir -p "$BIN/harness/rootfs-template"
    tar -xzf "$DEPS/alpine-minirootfs.tar.gz" -C "$BIN/harness/rootfs-template"
    echo "$APKS" | while read -r repo pkg sha; do
        [ -n "$pkg" ] || continue
        fetch "$APK_BASE/$repo/aarch64/$pkg.apk" "$sha" "$DEPS/$pkg.apk"
        tar -xzf "$DEPS/$pkg.apk" -C "$BIN/harness/rootfs-template" \
            --exclude '.PKGINFO' --exclude '.SIGN.*' 2>/dev/null || true
    done
    fetch "$UV_URL" "$UV_SHA256" "$DEPS/uv-$UV_VERSION.tar.gz"
    tar -xzf "$DEPS/uv-$UV_VERSION.tar.gz" -C "$DEPS"
    mkdir -p "$BIN/harness/rootfs-template/usr/local/bin"
    cp "$DEPS/uv-aarch64-unknown-linux-musl/uv" \
        "$DEPS/uv-aarch64-unknown-linux-musl/uvx" \
        "$BIN/harness/rootfs-template/usr/local/bin/"
    fetch "$PYTHON_URL" "$PYTHON_SHA256" "$DEPS/cpython-linux-musl.tar.gz"
    mkdir -p "$BIN/harness/rootfs-template/usr/local"
    tar -xzf "$DEPS/cpython-linux-musl.tar.gz" \
        -C "$BIN/harness/rootfs-template/usr/local"
    ln -sf ../python/bin/python3 \
        "$BIN/harness/rootfs-template/usr/local/bin/python3"
    fetch "$BUN_URL" "$BUN_SHA256" "$DEPS/bun-linux-musl.zip"
    unzip -o -q "$DEPS/bun-linux-musl.zip" -d "$DEPS"
    cp "$DEPS/bun-linux-aarch64-musl/bun" \
        "$BIN/harness/rootfs-template/usr/local/bin/"
    ln -sf bun "$BIN/harness/rootfs-template/usr/local/bin/bunx"
    printf '%s' "$STAMP" > "$BIN/harness/rootfs-template/.rootfs-stamp"
else
    echo "already extracted and current, skipping (FORCE=1 to redo)"
fi

echo "=== done ==="
ls -lh "$BIN/libkrun.dylib" "$BIN/libkrunfw.5.dylib"
