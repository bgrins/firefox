import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit("requires isolated nonoptimized no-site Python")
sys.dont_write_bytecode = True
import hashlib
import json
from pathlib import Path
import subprocess
ROOT = Path(__file__).resolve().parent
if len(sys.argv) != 3 or sys.argv[1] != "--files-sha256":
    raise SystemExit("Usage: verify.py --files-sha256 PIN")
assert hashlib.sha256((ROOT / "FILES.json").read_bytes()).hexdigest() == sys.argv[2]
manifest = json.loads((ROOT / "FILES.json").read_text())
paths = list(ROOT.rglob("*"))
assert not any(p.is_symlink() for p in paths)
assert {str(p.relative_to(ROOT)) for p in paths if p.is_file()} == set(manifest) | {"FILES.json", "FREEZE.json"}
for name, expected in manifest.items():
    assert not Path(name).is_absolute() and ".." not in Path(name).parts
    assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected, name
runs = {}
for phase in ["baseline", "candidate"]:
    raw = [json.loads(line) for line in (ROOT / phase / "raw.json").read_text().splitlines()]
    r = json.loads((ROOT / phase / "RUN.json").read_text())
    assert r["rows"] == [e for e in raw if e.get("action") == "test_status"]
    assert r["ends"] == [e for e in raw if e.get("action") == "test_end"]
    assert sum(e.get("action") == "suite_end" for e in raw) == 1
    assert r["complete"] and r["before"] == r["after"]
    assert len(r["rows"]) == 74 and len(r["ends"]) == 23
    runs[phase] = r
keys = lambda rows: {(r["test"], r["subtest"]): (r["status"], r.get("expected", r["status"])) for r in rows}
a, b = keys(runs["baseline"]["rows"]), keys(runs["candidate"]["rows"])
assert len(a) == len(b) == 74 and a.keys() == b.keys()
new = "/css/cssom-view/getBoundingClientRect-untransformed-edge-precision.html"
assert sum(key[0] == new for key in b) == 4
assert all(b[key] == (("PASS", "PASS") if key[0] == new else a[key]) for key in b)
ends = lambda r: {e["test"]: (e["status"], e.get("expected", e["status"])) for e in r["ends"]}
assert len(ends(runs["baseline"])) == 23
assert ends(runs["baseline"]) == ends(runs["candidate"])
result = subprocess.run([sys.executable, "-I", "-S", "-B", str(ROOT / "analyze-retained.py"), "--check"], capture_output=True, text=True)
assert result.returncode == 0, result.stdout + result.stderr
assert json.loads((ROOT / "DECISION.json").read_text())["status"] == "HOLD_NATIVE_REPAIR_ON_LOCAL_PERFORMANCE"
print(json.dumps({"verified_payloads": len(manifest), "subtests_per_variant": 74, "timing_runs": 6, "native_accepted": False}))
