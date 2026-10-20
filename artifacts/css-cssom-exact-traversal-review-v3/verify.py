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
    out = {}
    for key, value in items:
        assert key not in out
        out[key] = value
    return out

def read(path):
    return json.loads(path.read_text(), object_pairs_hook=pairs)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

if len(sys.argv) != 3 or sys.argv[1] != "--files-sha256":
    raise SystemExit("Usage: python3 -I -S verify.py --files-sha256 REVIEW_PIN")
assert sha(ROOT / "FILES.json") == sys.argv[2]
manifest = read(ROOT / "FILES.json")
directories = {"."}
for name, expected in manifest.items():
    path = Path(name)
    assert not path.is_absolute() and path.as_posix() == name and ".." not in path.parts
    assert stat.S_ISREG((ROOT / path).lstat().st_mode) and sha(ROOT / path) == expected, name
    directories.update(str(p) for p in path.parents)
actual = set()
for path in ROOT.rglob("*"):
    name = path.relative_to(ROOT).as_posix()
    mode = path.lstat().st_mode
    if stat.S_ISREG(mode):
        actual.add(name)
    else:
        assert stat.S_ISDIR(mode) and name in directories
assert actual == set(manifest) | {"FILES.json", "FREEZE.json"}
freeze = read(ROOT / "FREEZE.json")
assert freeze["files_sha256"] == sys.argv[2] and freeze["payload_count"] == len(manifest)
assert sha(ROOT / "producer-evidence/FILES.json") == "7f38aefc3a57825eff20508e95d183ae571514f128958bb2d0033228e134d6b6"
assert sha(ROOT / "source/FILES.json") == "993dde69e30ebadf821bafb8587baba61f010bfc537600fad61a0839652db5eb"
for name, expected in read(ROOT / "source/FILES.json").items():
    assert sha(ROOT / "source" / name) == expected
results = read(ROOT / "replay/RESULT.json")["runs"]
assert len(results) == 20
for result in results:
    assert (result["exit"] == 0) == (result["variant"] in {"original", "v2", "candidate", "mutant-overflow"})
for opt in ["-O0", "-O2"]:
    previous = (ROOT / f"replay/v2{opt}-run.log").read_text()
    candidate = (ROOT / f"replay/candidate{opt}-run.log").read_text()
    assert previous == candidate and "V1_DOMAIN_PASS 2048" in candidate
    rows = lambda name: [s for s in (ROOT / name).read_text().splitlines() if s.startswith("ROW ")]
    assert rows(f"replay/original{opt}-run.log") == rows(f"replay/candidate{opt}-run.log")
    assert len(rows(f"replay/candidate{opt}-run.log")) == 168
    for role in ["v2", "candidate"]:
        for number in range(1, 9):
            text = (ROOT / f"replay/{role}{opt}-injected-{number}.log").read_text()
            assert "NUMERIC_RESTART" in text and "INJECTED_GUARD_PASS" in text
    for number in [1, 5]:
        assert "FAIL 451" in (ROOT / f"replay/mutant-overflow{opt}-injected-{number}.log").read_text()
    for role in ["original", "v2", "candidate"]:
        assert "runtime error: signed integer overflow" in (ROOT / f"replay/{role}{opt}-crossdoc-restart.log").read_text()
    a = (ROOT / f"v2{opt}-extra-run.log").read_text()
    b = (ROOT / f"candidate{opt}-extra-run.log").read_text()
    assert a == b and "INDEPENDENT_PASS dispatch=48 masks=16 geometry=4 arithmetic=81" in b
    assert len([s for s in b.splitlines() if s.startswith("DISPATCH ")]) == 48
assert all(r["compile_exit"] == r["run_exit"] == 0 for r in read(ROOT / "EXTRA-RESULT.json")["runs"])
for name in ["nsIFrame.h", "nsLayoutUtils.cpp", "nsLayoutUtils.h", "DOMRect.cpp"]:
    assert (ROOT / "source/candidate" / name).read_bytes() == (ROOT / "source/v2" / name).read_bytes()
assert read(ROOT / "VERDICT.json")["status"] == "GO_REVERSIBLE_EXPERIMENT_ONLY"
print(json.dumps({"payloads": len(manifest), "producer_replay_runs": 20, "independent_runs": 4, "verdict": "GO_REVERSIBLE_EXPERIMENT_ONLY"}))
