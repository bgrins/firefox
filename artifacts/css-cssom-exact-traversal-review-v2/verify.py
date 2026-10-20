import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit("Require python3 -I -S without optimization")
sys.dont_write_bytecode = True
import hashlib
import json
from pathlib import Path
import stat

ROOT = Path(__file__).resolve().parent

def pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError("Duplicate JSON key")
        result[key] = value
    return result

def read(path):
    return json.loads(path.read_text(), object_pairs_hook=pairs)

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

if len(sys.argv) != 3 or sys.argv[1] != "--files-sha256":
    raise SystemExit("Usage: python3 -I -S verify.py --files-sha256 PIN")
assert digest(ROOT / "FILES.json") == sys.argv[2]
manifest = read(ROOT / "FILES.json")
directories = {"."}
for name, expected in manifest.items():
    path = Path(name)
    assert not path.is_absolute() and path.as_posix() == name and ".." not in path.parts
    assert stat.S_ISREG((ROOT / path).lstat().st_mode)
    assert digest(ROOT / path) == expected, name
    directories.update(str(p) for p in path.parents)
files = set()
for path in ROOT.rglob("*"):
    mode = path.lstat().st_mode
    name = path.relative_to(ROOT).as_posix()
    if stat.S_ISREG(mode):
        files.add(name)
    else:
        assert stat.S_ISDIR(mode) and name in directories, name
assert files == set(manifest) | {"FILES.json", "FREEZE.json"}
freeze = read(ROOT / "FREEZE.json")
assert freeze["files_sha256"] == sys.argv[2] and freeze["payload_count"] == len(manifest)
assert digest(ROOT / "producer-evidence/FILES.json") == "b553dbebc08b6e82b635c30f2e90b254558d513faab385cad3e840abb9465f8c"
assert digest(ROOT / "producer-evidence/proposal.patch") == "9ecbf1c84bd59754bf343cd1324a6e6aa6c39eb664489e1aff0d4a614fe4451f"
assert digest(ROOT / "native-source/FILES.json") == "ccfc2946ea8a71b25f1c14edf3eb2022be3984f6b1019a79b8a145cbd0909da1"
for name, expected in read(ROOT / "native-source/FILES.json").items():
    assert digest(ROOT / "native-source" / name) == expected
receipt = read(ROOT / "native-replay/RESULT.json")
assert len(receipt["runs"]) == 14
for row in receipt["runs"]:
    assert (row["exit"] == 0) == (row["variant"] in {"original", "candidate"})
    if row["variant"] in {"original", "candidate"}:
        assert row["rows"] == 168
for opt in ["-O0", "-O2"]:
    original = (ROOT / f"native-replay/original{opt}-run.log").read_text().splitlines()
    candidate = (ROOT / f"native-replay/candidate{opt}-run.log").read_text().splitlines()
    assert [r for r in original if r.startswith("ROW ")] == [r for r in candidate if r.startswith("ROW ")]
    assert "V1_DOMAIN_PASS 2048" in candidate and "EXACT_CHECKS_PASS" in candidate
    assert (ROOT / f"challenges{opt}-run.log").read_text() == "INDEPENDENT_CHALLENGES_PASS 10\n"
    for role in ["original", "candidate"]:
        for witness in ["grouping", "rect-origin", "crossdoc-restart"]:
            text = (ROOT / f"native-replay/{role}{opt}-{witness}.log").read_text()
            if role == "original" or witness == "crossdoc-restart":
                assert "runtime error: signed integer overflow" in text
            else:
                assert "WIDE_WITNESS_PASS" in text
assert digest(ROOT / "bounds-review-v1/FILES.json") == "ce673bac1242338c35138309605cfe10d183530d957e894f1e5362e1873106e9"
assert read(ROOT / "VERDICT.json")["verdict"] == "GO_REVERSIBLE_EXPERIMENT_ONLY"
print(json.dumps({"payloads": len(manifest), "replay_runs": 14, "independent_cases_per_optimization": 10, "verdict": "GO_REVERSIBLE_EXPERIMENT_ONLY"}))
