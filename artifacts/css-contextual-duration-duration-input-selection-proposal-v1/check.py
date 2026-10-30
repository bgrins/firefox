import difflib
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OLD = ROOT / 'artifacts/css-contextual-duration-masked-input-snapshot-proposal-v2'
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
roles = read(HERE / 'SOURCE-ROLES.json')
previous = read(OLD / 'SOURCE-ROLES.json')
manager = 'layout/style/nsAnimationManager.cpp'
assert set(roles) == set(previous) and len(roles) == 8
for path, digest in read(HERE / 'REFERENCES.json').items():
    assert sha(ROOT / path) == digest, path
for name, record in roles.items():
    assert record['base_capture'] == previous[name]['base_capture']
    assert record['base_sha256'] == previous[name]['base_sha256']
    for kind in ('base', 'candidate'):
        assert sha(ROOT / record[kind + '_capture']) == record[kind + '_sha256']
    if name != manager:
        assert record == previous[name]
base = (ROOT / previous[manager]['candidate_capture']).read_text()
actual = (ROOT / roles[manager]['candidate_capture']).read_text()
rebuilt = base
for edit in read(HERE / 'EDITS.json'):
    assert rebuilt.count(edit['before']) == 1
    rebuilt = rebuilt.replace(edit['before'], edit['after'])
assert rebuilt == actual
assert actual.count('aStyle.GetAnimationDuration(animIdx)') == 1
assert 'aDurationInput[animIdx % aDurationInput.Length()]' in actual
assert actual.count('BuildAnimation(') == base.count('BuildAnimation(') == 2
assert actual.count('BuildAnimations(') == base.count('BuildAnimations(') == 2
assert actual.count('ServoCSSAnimationBuilder builder(aComputedStyle);') == 1
expected_delta = ''.join(difflib.unified_diff(base.splitlines(True), actual.splitlines(True),
    fromfile='a/' + manager, tofile='b/' + manager))
assert (HERE / 'POLICY-DELTA.patch').read_text() == expected_delta
expected_full = ''.join(''.join(difflib.unified_diff(
    (ROOT / role['base_capture']).read_text().splitlines(True),
    (ROOT / role['candidate_capture']).read_text().splitlines(True),
    fromfile='a/' + name, tofile='b/' + name)) for name, role in sorted(roles.items()))
assert (HERE / 'native.patch').read_text() == expected_full

def patch(directory, name, reverse=False):
    command = ['patch', '--batch', '--fuzz=0', '-p1', '-i', str(HERE / name)]
    if reverse:
        command.append('-R')
    result = subprocess.run(command, cwd=directory, text=True, capture_output=True)
    assert result.returncode == 0, result.stdout + result.stderr

with tempfile.TemporaryDirectory(prefix='duration-input-policy-', dir='/private/tmp') as temporary:
    scratch = Path(temporary)
    for name, role in roles.items():
        target = scratch / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / role['base_capture']).read_bytes())
    patch(scratch, 'native.patch')
    assert all(sha(scratch / name) == role['candidate_sha256'] for name, role in roles.items())
    patch(scratch, 'native.patch', True)
    assert all(sha(scratch / name) == role['base_sha256'] for name, role in roles.items())
    (scratch / manager).write_text(base)
    patch(scratch, 'POLICY-DELTA.patch')
    assert (scratch / manager).read_text() == actual
    patch(scratch, 'POLICY-DELTA.patch', True)
    assert (scratch / manager).read_text() == base
assert not scratch.exists()
print(json.dumps({'roles': 8, 'changed_from_snapshot_v2': [manager], 'exact_edits': 5,
    'policy_patch_forward_reverse': True, 'full_patch_forward_reverse': True,
    'unchanged_other_source_roles': 7, 'native_compile_or_browser': False,
    'owned_scratch_removed': True}))
