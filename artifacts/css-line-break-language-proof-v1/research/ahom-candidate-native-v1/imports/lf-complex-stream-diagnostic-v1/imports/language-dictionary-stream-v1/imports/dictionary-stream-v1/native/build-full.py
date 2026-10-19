import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
BRIDGE = ROOT / "provider-bridge-v1"
OUT = ROOT / "development-build/full"
OUT.mkdir(parents=True, exist_ok=True)
TOOL = Path("/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr")
SDK = Path("/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk")
commands = []

def run(name, args):
    args = list(map(str, args))
    p = subprocess.run(args, capture_output=True, text=True, timeout=60)
    (OUT / (name + ".log")).write_text(p.stdout + p.stderr)
    commands.append({"name": name, "args": args, "exit": p.returncode})
    (OUT / "commands.json").write_text(json.dumps(commands, indent=2) + "\n")
    print(name, p.returncode, flush=True)
    if p.returncode:
        print(p.stdout + p.stderr)
        raise SystemExit(p.returncode)

for name in ["provider", "locale", "glyph"]:
    run("extract-" + name, [sys.executable, BRIDGE / f"native/extract-{name}.py"])
run("extract-transform", [sys.executable, ROOT / "native/extract-transform.py"])
run("extract-range-providers", [sys.executable, ROOT / "native/extract-range-providers.py"])
run("extract-full", [sys.executable, ROOT / "native/extract-full.py"])
run("extract-range", [sys.executable, ROOT / "native/extract-range.py"])
flags = [TOOL / "bin/clang++", "-std=c++20", "-isysroot", SDK, "-isystem", TOOL / "include/c++/v1", "-g", "-O1", "-fsanitize=undefined", "-I", OUT, "-I", ROOT / "native", "-I", BRIDGE / "development-build/provider", "-I", BRIDGE / "provider-crates/icu_capi/bindings/cpp", "-I", BRIDGE / "source/providers/intl/icu/source/common", "-I", BRIDGE / "native/hyphen-producer-input", "-I", BRIDGE / "native"]
for name in ["provider", "locale"]:
    run("compile-" + name, [*flags, "-c", BRIDGE / f"native/{name}-library.cpp", "-o", OUT / f"{name}.o"])
for flavor in ["original", "candidate", "standalone"]:
    run("compile-" + flavor, [*flags, OUT / f"breaker-{flavor}.cpp", OUT / "provider.o", OUT / "locale.o", ROOT / "development-build/icu/debug/liblanguage_break_provider.a", ROOT / "development-build/rust/libmapped_hyph.a", "-licucore", "-framework", "CoreFoundation", "-framework", "Security", "-o", OUT / f"breaker-{flavor}"])

for flavor in ["original", "candidate", "standalone"]:
    run("range-" + flavor, [*flags, OUT / f"range-{flavor}.cpp", OUT / "provider.o", OUT / "locale.o", ROOT / "development-build/icu/debug/liblanguage_break_provider.a", ROOT / "development-build/rust/libmapped_hyph.a", "-licucore", "-framework", "CoreFoundation", "-framework", "Security", "-o", OUT / f"range-{flavor}"])

run("extract-filter", [sys.executable, ROOT / "native/extract-filter.py"])
run("compile-filter", [*flags, OUT / "filter.cpp", OUT / "provider.o", OUT / "locale.o", ROOT / "development-build/icu/debug/liblanguage_break_provider.a", ROOT / "development-build/rust/libmapped_hyph.a", "-licucore", "-framework", "CoreFoundation", "-framework", "Security", "-o", OUT / "filter"])
