import copy
import difflib
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_bytes())


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def reject(action):
    try:
        action()
    except AssertionError:
        return
    raise AssertionError('invalid state accepted')


for ref in read(HERE / 'REFERENCES.json'):
    assert sha(ROOT / ref['path']) == ref['sha256']
for name in ['css-prioritary-selected-declaration-proposal-v4',
             'css-registered-color-image-commit-packaging-v1',
             'css-prioritary-selection-candidate-runtime-3']:
    directory = ROOT / 'artifacts' / name
    for path, row in read(directory / 'FILES.json').items():
        assert sha(directory / path) == row['sha256']
        assert (directory / path).stat().st_size == row['bytes']
roles = read(HERE / 'SOURCE-ROLES.json')
for rel, row in roles.items():
    for kind in ('base', 'candidate'):
        assert sha(ROOT / row[kind + '_capture']) == row[kind + '_sha256']
    assert row['modified'] == (row['base_sha256'] != row['candidate_sha256'])
    assert sha(ROOT / 'artifacts/css-registered-color-image-commit-packaging-v1/narrow-candidate' / rel) == row['base_sha256']
assert sum(row['modified'] for row in roles.values()) == 1
rel = 'servo/components/style/properties/cascade.rs'
v4 = ROOT / 'artifacts/css-prioritary-selected-declaration-proposal-v4'
source = (v4 / 'candidate' / rel).read_text()
image_patch = (ROOT / 'artifacts/css-registered-color-image-commit-packaging-v1/02-narrow-image-after-union.patch').read_text()
for chunk in re.split(r'^@@[^\n]*\n', image_patch, flags=re.M)[1:]:
    lines = chunk.splitlines(True)
    before = ''.join(line[1:] for line in lines if line[0] in ' -')
    after = ''.join(line[1:] for line in lines if line[0] in ' +')
    assert source.count(before) == 1
    source = source.replace(before, after, 1)
assert source == (HERE / 'candidate' / rel).read_text()
for patch, before in [('native.patch', HERE / 'base' / rel),
                      ('V4-IMAGE-DELTA.patch', v4 / 'candidate' / rel)]:
    expected = ''.join(difflib.unified_diff(before.read_text().splitlines(True), source.splitlines(True), fromfile='a/' + rel, tofile='b/' + rel))
    assert (HERE / patch).read_text() == expected
    with tempfile.TemporaryDirectory(prefix='css-prioritary-rebase-') as temporary:
        scratch = Path(temporary)
        target = scratch / rel
        target.parent.mkdir(parents=True)
        shutil.copyfile(before, target)
        for reverse in [False, True]:
            command = ['patch', '--fuzz=0'] + (['-R'] if reverse else []) + ['-p1', '-i', str(HERE / patch)]
            result = subprocess.run(command, cwd=scratch, capture_output=True, text=True)
            assert result.returncode == 0, result
            assert target.read_bytes() == (before.read_bytes() if reverse else source.encode())
    assert not scratch.exists()
tool = read(v4 / 'TOOLCHAIN.json')
assert sha(Path(tool['rustfmt'])) == tool['sha256']
result = subprocess.run([tool['rustfmt'], '--check', '--config-path', str(v4 / 'rustfmt.toml'), str(HERE / 'candidate' / rel)], capture_output=True, text=True)
assert result.returncode == 0 and not result.stderr, result
mock = load('mock_guard', ROOT / 'artifacts/css-prioritary-intermediate-guard-proposal-v1/check.py')
original = load('old_guard', ROOT / 'artifacts/css-prioritary-selection-candidate-v4/intermediate.py')
new = load('new_guard', HERE / 'intermediate.py')


class Checks(mock.MockChecks):
    def __init__(self, field=None, target_call=3):
        super().__init__()
        self.field, self.target_call = field, target_call

    def index_state(self, path, env):
        result = super().index_state(path, env)
        result['working_diff'] = 'W'
        if self.calls == self.target_call and self.field:
            result[self.field] = 'changed'
        return result


epoch = {'raw_index_observation': {'current': 'R'},
         'semantic_index': {'head': 'H', 'entries': 'E', 'cached_diff': 'D', 'working_diff': 'W'},
         'nested_semantic_index': {'head': 'H', 'entries': 'E', 'cached_diff': 'D', 'working_diff': 'W'},
         'pins': {'native': 'N'}, 'staged_working': {'staged': 'S'},
         'installed_identities': {'native': [1, 2]},
         'modified_native_paths': ['native'], 'untracked_native': ['untracked']}
args = (mock.MockPath(), {}, epoch, {'consumed': 'C'})
records = []
assert new.verify_intermediate(Checks(), *args, records.append) == original.verify_intermediate(Checks(), *args)
assert records == []
for repository, call in [('root', 3), ('nested', 4)]:
    for field in ('head', 'entries', 'cached_diff', 'working_diff', 'raw_index'):
        records = []
        reject(lambda: new.verify_intermediate(Checks(field, call), *args, records.append))
        assert len(records) == 1
        record = records[0]
        assert record['repository'] == repository and record['changed_fields'] == [field]
        assert record['after'][field] == 'changed' and record['before'][field] != 'changed'
        reject(lambda: new.verify_intermediate(Checks(field, call), *args))
records = []
checks = Checks()
checks.bodies['consumed'] = 'changed'
reject(lambda: new.verify_intermediate(checks, *args, records.append))
assert records == []
runtime = ROOT / 'artifacts/css-prioritary-selection-candidate-runtime-3'
observations = read(HERE / 'OBSERVATIONS.json')
snapshots = [read(runtime / path) for path in observations['successful_snapshot_files']]
snapshots[0] = snapshots[0]['snapshot']
assert all(snapshot == snapshots[0] for snapshot in snapshots)
assert snapshots[-1]['index'] == observations['last_successful_index']
assert 'assert after == before' in read(runtime / 'FAILURE-TRACEBACK.json')['traceback']
assert not (runtime / 'INTERMEDIATE-INDEX-MISMATCH.json').exists()
print(json.dumps({'source_roles': 3, 'modified_roles': 1, 'published_image_hunks_preserved': 5,
                  'patch_roundtrips': 2, 'rustfmt_check': True, 'success_result_unchanged': True,
                  'diagnostic_mismatch_cases': 10, 'mismatches_without_callback_still_rejected': 10,
                  'consumed_drift_still_rejected': True, 'saved_equal_snapshots': len(snapshots),
                  'scratch_removed': True, 'native_build': False, 'browser_run': False}))
