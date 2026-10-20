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
assert sha(ROOT / "producer-evidence/FILES.json") == "9cb90bc4e1739c482b2b20785389b002cfeb297bc958b42684e58d37fa4e4770"
assert sha(ROOT / "source/FILES.json") == "e5171412e9d35ae3280fe194e803b3a2a6674242d262e70abdc4ddee62b1f720"
for name, expected in read(ROOT / "producer-evidence/FILES.json").items():
    path = ROOT / "source" / name[len("capsule/"):] if name.startswith("capsule/") else ROOT / "producer-evidence" / name
    assert sha(path) == expected, name
for name, expected in read(ROOT / "source/FILES.json").items():
    assert sha(ROOT / "source" / name) == expected
results = read(ROOT / "replay/RESULT.json")["runs"]
assert len(results) == 26
variants = ['original','v2','v3','candidate','mutant-position','mutant-svg','mutant-flags','mutant-cache','mutant-self','mutant-dispatch','mutant-overflow','mutant-null-flags','mutant-null-visual']
assert [(x['variant'],x['optimization']) for x in results] == [(v,o) for v in variants for o in ['-O0','-O2']]
failures = {'mutant-position':220,'mutant-svg':103,'mutant-flags':100,'mutant-cache':320,'mutant-self':339,'mutant-null-flags':270,'mutant-null-visual':277}
for opt in ['-O0','-O2']:
    rows = lambda role: [s for s in (ROOT / f"replay/{role}{opt}-run.log").read_text().splitlines() if s.startswith("ROW ")]
    original = rows('original')
    assert len(original) == 168
    previous = (ROOT / f"replay/v2{opt}-run.log").read_text()
    for role in ['v2','v3','candidate']:
        text = (ROOT / f"replay/{role}{opt}-run.log").read_text()
        assert text == previous and 'V1_DOMAIN_PASS 2048' in text
        assert rows(role) == original
        for number in range(1,9):
            text = (ROOT / f"replay/{role}{opt}-injected-{number}.log").read_text()
            assert 'NUMERIC_RESTART' in text and 'INJECTED_GUARD_PASS' in text
    for result in [r for r in results if r['optimization']==opt]:
        role=result['variant']; actual=rows(role)
        differences=sum(a!=b for a,b in zip(actual,original))+abs(len(actual)-len(original))
        assert differences==result['row_differences_from_original']
        assert result['rows']==len(actual)
        text=(ROOT / f"replay/{role}{opt}-run.log").read_text()
        if role in failures:
            assert result['exit']==1 and f"FAIL {failures[role]}" in text
        else:
            assert result['exit']==0
        if role=='mutant-dispatch':
            assert differences==49 and len(actual)==168
    for number in [1,5]:
        assert 'FAIL 451' in (ROOT / f"replay/mutant-overflow{opt}-injected-{number}.log").read_text()
    for role in ['original','v2','v3','candidate']:
        assert 'runtime error: signed integer overflow' in (ROOT / f"replay/{role}{opt}-crossdoc-restart.log").read_text()
    a=(ROOT / f"v3{opt}-extra-run.log").read_text()
    b=(ROOT / f"candidate{opt}-extra-run.log").read_text()
    assert a==b and 'NULL_BOUNDARIES_PASS' in b
    assert 'INDEPENDENT_PASS dispatch=48 masks=16 geometry=4 arithmetic=81' in b
    assert len([s for s in b.splitlines() if s.startswith('DISPATCH ')])==48
assert len(read(ROOT/'EXTRA-RESULT.json')['runs'])==4
assert all(r['compile_exit']==r['run_exit']==0 for r in read(ROOT/'EXTRA-RESULT.json')['runs'])
for name in ['nsIFrame.h','nsLayoutUtils.cpp','nsLayoutUtils.h','DOMRect.cpp']:
    assert (ROOT/'source/candidate'/name).read_bytes()==(ROOT/'source/v3'/name).read_bytes()
assert read(ROOT/'SOURCE-CHECKS.json')['exact_dispatch_replacement']
assert read(ROOT/'VERDICT.json')['status']=='GO_REVERSIBLE_EXPERIMENT_ONLY'
assert read(ROOT/'CLEANUP.json')['no_active_compilers']
print(json.dumps({'payloads':len(manifest),'producer_replay_runs':26,'independent_runs':4,'force_common_original_row_differences':49,'verdict':'GO_REVERSIBLE_EXPERIMENT_ONLY'}))
