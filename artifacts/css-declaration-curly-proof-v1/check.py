import sys
assert sys.flags.isolated and sys.flags.no_site
import argparse, hashlib, json, subprocess
from pathlib import Path, PurePosixPath
R = Path(__file__).resolve().parent
p = argparse.ArgumentParser()
p.add_argument('--output', type=Path)
a = p.parse_args()
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
records = json.loads((R / 'MANIFEST.json').read_text())
seen = set()
for rec in records:
    name = rec['path']
    rel = PurePosixPath(name)
    assert str(rel) == name and not rel.is_absolute() and '..' not in rel.parts
    assert name not in seen
    seen.add(name)
    path = R / name
    assert path.is_file() and not path.is_symlink()
    for parent in path.parents:
        if parent == R:
            break
        assert not parent.is_symlink()
    assert sha(path) == rec['sha256'], name
actual = {str(path.relative_to(R)) for path in R.rglob('*') if path.is_file()}
assert actual - {'MANIFEST.json', 'FREEZE.json'} == seen
assert not any(path.is_symlink() for path in R.rglob('*'))
audit = R / 'evidence/audit'
assert sha(audit / 'MANIFEST.json') == 'be11ba093332bb80969efac104d8c61113d02f25592395e82deda65c30cf8299'
assert sha(audit / 'check.py') == '63558c27ad2e92448bcc6cd279e0938939deaf707abff7c6e84a8c26a1ca8e91'
assert sha(audit / 'FREEZE.json') == 'bb69319b1e6c4917c3c747439ac0ee30602f3d9f434dcc8309d57cc171b9eedd'
subprocess.run([sys.executable, '-I', '-S', str(audit / 'check.py')], check=True)
before = (audit / 'evidence/source/servo/components/style/properties/mod.rs').read_text()
needle = '    // Look for var(), env() and top-level curly blocks after the error.\n'
assert before.count(needle) == 1
after = before.replace(needle, '    input.reset(start);\n\n    // Look for var(), env() and top-level curly blocks in the whole value.\n')
candidate = R / 'evidence/candidate-properties.rs'
assert candidate.read_text() == after
assert sha(candidate) == '6754d46e612a369fa6b3853151dc6179a60a92beb25a0a2dc1b8827b80669f92'
b = R / 'evidence/final-browser'
assert sha(b / 'MANIFEST.json') == 'fb7ad93158892a1163537020d224d3a830a1fd66f8c668c6a3570fe32c6cb2b4'
assert sha(b / 'FREEZE.json') == '7d506ad6b395eeccc090646d760d14feee43878592a3b5a0f05345ab171707d1'
for name, expected in json.loads((b / 'MANIFEST.json').read_text()).items():
    assert sha(b / name) == expected
assert (b / 'candidate-properties.rs').read_bytes() == candidate.read_bytes()
assert (b / 'original-properties.rs').read_text() == before
assert (b / 'declaration-curly-fallback.html').read_bytes() == (audit / 'declaration-curly-fallback.html').read_bytes()
def outcomes(mode):
    rows = [json.loads(line) for line in (b / (mode + '-raw.jsonl')).read_text().splitlines()]
    rows = [x for x in rows if x['action'] in ['test_status', 'test_end']]
    keyed = {(x['action'], x['test'], x.get('subtest')): x['status'] for x in rows}
    assert len(keyed) == len(rows) == 94
    assert json.loads((b / (mode + '-before.json')).read_text()) == json.loads((b / (mode + '-after.json')).read_text())
    return keyed
old, new = outcomes('baseline'), outcomes('candidate')
assert old.keys() == new.keys()
changed = [key for key in old if old[key] != new[key]]
assert len(changed) == 24 and all(old[key] == 'FAIL' and new[key] == 'PASS' for key in changed)
assert sum(v == 'PASS' for v in new.values()) == 89
assert sum(v == 'OK' for v in new.values()) == 5
if a.output:
    output = a.output.resolve()
    assert not output.exists() and not output.is_relative_to(R)
    subprocess.run([sys.executable, '-I', '-S', str(R / 'replay.py'), '--output', str(output)], check=True)
print(json.dumps(dict(authenticated_files=len(records), candidate_source_binding=True, root_browser_fixed=24, root_browser_pass=89)))
