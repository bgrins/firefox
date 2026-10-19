import hashlib
import json
import shutil
import subprocess
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


names = [
    "Sigma.lean", "check.py", "bridge.py", "bridge-prefix.cpp", "bridge-suffix.cpp",
    "icu-probe.cpp", "unicode-properties17.txt", "before-nsTextRunTransformations.cpp",
    "native-candidate.cpp", "prepare.py", "README.md", "TOOLCHAIN-v1.json",
    "SOURCE-v1.json", "tooling-paths-v1.txt",
]
compiler = Path(shutil.which("clang++"))
toolchain = {
    "clang_path": str(compiler), "clang_driver_sha256": sha(compiler),
    "clang_version": subprocess.check_output([compiler, "--version"], text=True),
    "lean_path": "artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean",
}
(BASE / "TOOLCHAIN-v1.json").write_text(json.dumps(toolchain, indent=2) + "\n")
(BASE / "tooling-paths-v1.txt").write_text("".join(str((BASE / n).relative_to(ROOT)) + "\n" for n in names))
paths = [BASE / n for n in names if n != "SOURCE-v1.json"]
paths += [ROOT / p for p in [
    toolchain["lean_path"], "mfbt/Utf16.h", "intl/components/src/String.h",
    "intl/icu/source/common/uprops.cpp", "intl/icu/source/common/ucase.cpp",
    "objdir-full.noindex/config/external/icu/common/ucase.o",
    "objdir-full.noindex/dist/include/unicode/uchar.h",
    "layout/generic/nsTextFrame.cpp", "layout/forms/nsComboboxControlFrame.cpp",
]]
manifest = {str(p.relative_to(ROOT)): sha(p) for p in paths}
(BASE / "SOURCE-v1.json").write_text(json.dumps(manifest, indent=2) + "\n")
print(json.dumps({"source_manifest_sha256": sha(BASE / "SOURCE-v1.json"),
                  "companion_files": len(names), "authenticated_inputs": len(manifest)}, indent=2))
