import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit("Require python3 -I -S without optimization")
sys.dont_write_bytecode = True
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess

ROOT = Path(__file__).resolve().parent
EXPECTED = {"AUDITS.json", "REPORT.md", "SOURCE.json", "TOOL.json", "replay.py",
            "lean/ProviderReadiness.lean", "lean/Audit.lean",
            "source/Update.before.cpp", "source/Update.candidate.cpp",
            "falseclaims/dirty_ancestor_suffices.lean",
            "falseclaims/provider_substitution_preserves_ancestry.lean"}

def require(ok, message):
    if not ok:
        raise RuntimeError(message)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

parser = argparse.ArgumentParser()
parser.add_argument("--manifest-sha", required=True)
parser.add_argument("--out", required=True, type=Path)
args = parser.parse_args()
expected_dirs = {"lean", "source", "falseclaims"}
seen_files, seen_dirs = set(), set()
for parent, dirs, files in os.walk(ROOT, followlinks=False):
    for name in dirs + files:
        p = Path(parent) / name
        mode = p.lstat().st_mode
        n = str(p.relative_to(ROOT))
        if stat.S_ISDIR(mode):
            require(n in expected_dirs, "Unexpected directory")
            seen_dirs.add(n)
        else:
            require(stat.S_ISREG(mode), "Nonregular input")
            seen_files.add(n)
require(seen_dirs == expected_dirs and seen_files == EXPECTED | {"FILES.json", "FREEZE.json"}, "Input roster")
require(sha(ROOT / "FILES.json") == args.manifest_sha, "External manifest pin")
manifest = json.loads((ROOT / "FILES.json").read_text())
require(set(manifest) == EXPECTED, "Manifest roster")
for n, h in manifest.items():
    require(sha(ROOT / n) == h, "Input hash: " + n)
require(json.loads((ROOT / "FREEZE.json").read_text()) == {"FILES_sha256": args.manifest_sha, "payloads": len(EXPECTED)}, "Seal")
model = (ROOT / "lean/ProviderReadiness.lean").read_text()
require(not re.search(r"\b(sorry|admit|axiom|unsafe|native_decide)\b", model), "Proof escape")
names = ["ColumnReadiness." + n for n in re.findall(r"^theorem ([A-Za-z0-9_]+)", model, re.M)]
require(names == json.loads((ROOT / "AUDITS.json").read_text()) and len(names) == 11, "Theorem roster")
require(re.findall(r"#print axioms ([A-Za-z0-9_.]+)", (ROOT / "lean/Audit.lean").read_text()) == names, "Audit source roster")
bindings = json.loads((ROOT / "SOURCE.json").read_text())["bindings"]
for binding in bindings:
    require(sha(ROOT / "source" / ("Update." + binding["role"] + ".cpp")) == binding["complete_body_sha256"], "Bound body")
a = (ROOT / "source/Update.before.cpp").read_text()
b = (ROOT / "source/Update.candidate.cpp").read_text()
marker = "  nsIFrame* topmostFrameWithContentHidden = nullptr;"
require(a.split(marker, 1)[1] == b.split(marker, 1)[1], "Unchanged ancestry/scheduling suffix")
tool = json.loads((ROOT / "TOOL.json").read_text())
require(sha(Path(tool["path"])) == tool["sha256"], "Lean executable")
require(subprocess.check_output([tool["path"], "--version"], text=True) == tool["version"], "Lean version")
out = args.out.resolve()
require(not out.exists() and out != ROOT and ROOT not in out.parents and out not in ROOT.parents, "Absent disjoint output")
out.mkdir(parents=True)
env = {k: os.environ[k] for k in ("HOME", "PATH", "TMPDIR") if k in os.environ}
env["LEAN_PATH"] = str(out)
commands = []
product = out / "ProviderReadiness.olean"
summary = {"status": "INCOMPLETE"}

def run(name, argv, expected):
    result = subprocess.run(argv, cwd=ROOT / "lean", env=env, capture_output=True, text=True, timeout=60)
    (out / (name + ".stdout")).write_text(result.stdout)
    (out / (name + ".stderr")).write_text(result.stderr)
    commands.append({"name": name, "argv": argv, "exit": result.returncode})
    require((result.returncode == 0) == expected, "Exit: " + name)
    require(not result.stderr, "Stderr: " + name)
    return result.stdout

try:
    result = run("model", [tool["path"], "-o", str(product), str(ROOT / "lean/ProviderReadiness.lean")], True)
    require(not result, "Model diagnostics")
    audit = run("audit", [tool["path"], str(ROOT / "lean/Audit.lean")], True)
    require(re.findall(r"^'([A-Za-z0-9_.]+)'", audit, re.M) == names, "Exact printed audits")
    for line in audit.splitlines():
        match = re.search(r"depends on axioms: \[(.*?)\]", line)
        require(match is not None or "does not depend on any axioms" in line, "Audit grammar")
        if match:
            require(set(match.group(1).split(", ")) <= {"propext", "Quot.sound", "Classical.choice"}, "Axiom allowlist")
    for n in ["dirty_ancestor_suffices", "provider_substitution_preserves_ancestry"]:
        result = run(n, [tool["path"], str(ROOT / "falseclaims" / (n + ".lean"))], False)
        require("Tactic `decide` proved that the proposition" in result and "is false" in result, "False claim reason")
    summary = {"status": "PASS_LOCAL_MODEL", "audits": names, "falseclaims": 2, "manifest": args.manifest_sha,
               "native_translation": "manual source correspondence only", "full_layout_freshness": "open"}
finally:
    if product.exists():
        summary["removed_product"] = {"name": product.name, "bytes": product.stat().st_size, "sha256": sha(product)}
        product.unlink()
    (out / "COMMANDS.json").write_text(json.dumps(commands, indent=2) + "\n")
    (out / "RESULT.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps(summary))
