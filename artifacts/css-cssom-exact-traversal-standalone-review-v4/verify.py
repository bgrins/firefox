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
r=read(ROOT/'DRIVER-REVIEW.json')
assert r['status']=='GO_REVERSIBLE_STANDALONE_RUNTIME'
assert sha(ROOT/'driver-snapshot/experiment.py')==r['driver_sha256']=='5811759c90c8ef16e025a152618075f812187d5d64bc4d0e06a03214e36e66b5'
assert sha(ROOT/'driver-snapshot/INPUTS.json')==r['INPUTS_sha256']=='527dbf449b80d114c79f0fe81f81ac9b1ddbad13eac6416603871f846777f943'
assert r['prepared_inputs']==400 and r['staged_paths_expected']==229
assert r['all_prepared_hashes_match'] and r['output_directory_collision_fixed']
assert r['oracle_exact_historical_rows_ends_exit'] and not r['execution_performed']
oracle=read(ROOT/'driver-snapshot/ORACLE.json')
rows={(x['test'],x['subtest']):(x['status'],x.get('expected',x['status'])) for x in oracle['rows']}
assert len(rows)==len(oracle['rows'])==74 and len(oracle['ends'])==23 and oracle['exit']==1
assert sum(v[0]=='PASS' for v in rows.values())==70
assert sum(v[0]!=v[1] for v in rows.values())==2
print(json.dumps({'payloads':len(manifest),'verdict':r['status'],'driver_authenticated':True,'executed':False}))
