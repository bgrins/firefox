import hashlib
import json
from pathlib import Path, PurePosixPath
import sys

assert sys.flags.isolated and sys.flags.no_site
ROOT = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


manifest = read(ROOT / 'MANIFEST.json')
for name, digest in manifest.items():
    rel = PurePosixPath(name)
    assert str(rel) == name and not rel.is_absolute() and '..' not in rel.parts
    path = ROOT / name
    assert path.is_file() and all(not p.is_symlink() for p in [path, *path.parents])
    assert sha(path) == digest, name
assert {p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file()} == set(manifest) | {'MANIFEST.json', 'FREEZE.json'}
assert not any(p.is_symlink() for p in ROOT.rglob('*'))
source = read(ROOT / 'SOURCE-INPUTS.json')
assert len({r['path'] for r in source}) == len(source)
for row in source:
    assert sha(ROOT / 'source' / row['path']) == row['sha256']
evidence = ROOT / 'evidence'
pins = read(evidence / 'baseline-input.json')
assert pins == read(evidence / 'baseline-before.json') == read(evidence / 'baseline-after.json')
result = read(evidence / 'baseline-result.json')
assert result['stable_pins'] and result['exit_code'] == 1
assert sha(evidence / 'baseline-raw.jsonl') == result['raw_sha256']
assert sha(evidence / 'baseline-console.log') == result['console_sha256']
assert pins['fixed']['testing/web-platform/tests/css/css-link-params/link-parameters-publication.html'] == sha(evidence / 'link-parameters-publication.html')
matched = []
for row in source:
    if row['path'] in pins['fixed']:
        assert row['sha256'] == pins['fixed'][row['path']]
        matched.append(row['path'])
assert len(matched) == 6
rows = [json.loads(line) for line in (evidence / 'baseline-raw.jsonl').read_text().splitlines()]
rows = [r for r in rows if r.get('action') in ('test_status', 'test_end')]
keys = {(r['action'], r['test'], r.get('subtest')): r for r in rows}
assert len(keys) == len(rows) == 26
tests = [r for r in rows if r['action'] == 'test_status']
failures = {r['subtest']: r for r in tests if r['status'] == 'FAIL'}
values = ['param(--a, var(--x, red))', 'param(--a, env(not-real, red))', 'param(--a, attr(data-x))']
assert set(failures) == {f'{operation}: {value}' for operation in ('new', 'remove') for value in values}
for name, row in failures.items():
    expected = 'expected 1 but got 2' if name.startswith('new:') else 'expected 0 but got 1'
    assert expected in row['message'] and row.get('expected') == 'PASS'
assert sum(r['status'] == 'PASS' for r in tests) == 19
assert [r['status'] for r in rows if r['action'] == 'test_end'] == ['OK']

import collections
import shutil
import subprocess
import tempfile

for dependency in read(ROOT / 'DEPENDENCIES.json'):
    base = ROOT.parent / dependency['path']
    assert sha(base / 'MANIFEST.json') == dependency['manifest']
    assert sha(base / 'FREEZE.json') == dependency['freeze']
    external = read(base / 'MANIFEST.json')
    assert len(external) == dependency['files']
    names = set()
    for row in external:
        name = row['path']
        rel = PurePosixPath(name)
        assert str(rel) == name and not rel.is_absolute() and '..' not in rel.parts
        assert name not in names
        names.add(name)
        assert sha(base / name) == row['sha256'], name
    assert not any(p.is_symlink() for p in base.rglob('*'))
    assert {p.relative_to(base).as_posix() for p in base.rglob('*') if p.is_file()} == names | {'MANIFEST.json', 'FREEZE.json'}

static = ROOT.parent / 'css-declaration-publication-static-v1'
browser = ROOT.parent / 'css-declaration-publication-final-browser-v1'
root = evidence / 'root'
original = (root / 'original-properties.rs').read_bytes()
candidate = (root / 'candidate-properties.rs').read_bytes()
needle = b'            ParseError::custom(style_traits::StyleParseErrorKind::UnspecifiedError)'
assert original.count(needle) == 1
assert candidate == original.replace(needle, b'            declarations.clear();\n' + needle)
assert sha(root / 'candidate-properties.rs') == '2ef96482f50b06dcf87a18abc4d1a9aa0109a9063aa71cadc53e7737022c094d'
assert original == (static / 'evidence/source/servo/components/style/properties/mod.rs').read_bytes()
assert candidate == (static / 'evidence/candidate-properties.rs').read_bytes()
source_path = 'servo/components/style/properties/mod.rs'
wpt_path = 'testing/web-platform/tests/css/css-link-params/link-parameters-publication.html'
phases = {}
phase_pins = {}
for phase in ['baseline', 'candidate']:
    inputs = read(browser / (phase + '-input.json'))
    assert inputs == read(browser / (phase + '-before.json')) == read(browser / (phase + '-after.json'))
    phase_pins[phase] = inputs
    result = read(browser / (phase + '-result.json'))
    assert result['stable_pins']
    assert result['raw_sha256'] == sha(browser / (phase + '-raw.jsonl'))
    assert result['console_sha256'] == sha(browser / (phase + '-console.log'))
    raw = [json.loads(line) for line in (browser / (phase + '-raw.jsonl')).read_text().splitlines()]
    normalized = [{k: v for k, v in r.items() if k in ['action', 'test', 'subtest', 'status', 'expected', 'message']} for r in raw if r.get('action') in ('test_status', 'test_end')]
    indexed = {(r['action'], r['test'], r.get('subtest')): r for r in normalized}
    assert len(indexed) == len(normalized) == 147
    assert normalized == result['rows']
    phases[phase] = indexed
    assert inputs['fixed'][wpt_path] == sha(browser / 'source' / wpt_path)
assert phase_pins['baseline']['fixed'][source_path] == sha(root / 'original-properties.rs')
assert phase_pins['candidate']['fixed'][source_path] == sha(root / 'candidate-properties.rs')
assert phase_pins['baseline']['tests'] == phase_pins['candidate']['tests']
assert {k for k in phase_pins['baseline']['fixed'] if phase_pins['baseline']['fixed'][k] != phase_pins['candidate']['fixed'][k]} == {source_path}
assert phase_pins['baseline']['binaries'] != phase_pins['candidate']['binaries']
assert phases['baseline'].keys() == phases['candidate'].keys()
changed = {k for k in phases['baseline'] if phases['baseline'][k] != phases['candidate'][k]}
expected_names = {f'{op}, priority {json.dumps(priority)}: {value}' for op in ['new', 'remove'] for priority in ['', 'important'] for value in values}
assert {k[2] for k in changed} == expected_names and len(changed) == 12
for key in changed:
    assert phases['baseline'][key]['status'] == 'FAIL' and phases['candidate'][key]['status'] == 'PASS'
    if key[2].startswith('remove'):
        message = phases['baseline'][key]['message']
        assert 'got [1, "link-parameters", "link-parameters:' in message
        assert message.endswith('"", ""])')
for phase, expected in [('baseline', {'PASS':128, 'FAIL':13, 'OK':6}), ('candidate', {'PASS':140, 'FAIL':1, 'OK':6})]:
    assert dict(collections.Counter(r['status'] for r in phases[phase].values())) == expected
new_rows = [r for r in phases['candidate'].values() if r['test'].endswith('/link-parameters-publication.html') and r['action'] == 'test_status']
assert len(new_rows) == 49 and all(r['status'] == 'PASS' for r in new_rows)
remaining = [r for r in phases['candidate'].values() if r['status'] == 'FAIL']
assert len(remaining) == 1 and 'ident(' in remaining[0]['subtest']
metadata = browser / 'source/testing/web-platform/meta/css/css-link-params/link-parameters-computed.html.ini'
assert remaining[0]['subtest'] in metadata.read_text() and 'expected: FAIL' in metadata.read_text()
assert read(browser / 'candidate-result.json')['exit_code'] == 0
for build in read(browser / 'candidate-build-result.json'):
    assert build['exit_code'] == 0
    assert build['log_sha256'] == sha(browser / ('candidate-' + ('force-rust' if build['phase'] == 'force-rust' else 'link') + '.log'))
assert (browser / 'candidate-link.log').read_text().count("KeyError: 'export'") == 4
assert read(browser / 'candidate-build-before.json')['fixed'] == read(browser / 'candidate-build-after.json')['fixed'] == phase_pins['candidate']['fixed']
assert read(browser / 'candidate-build-after.json')['binaries'] == phase_pins['candidate']['binaries']

patch = root / 'native-wpt.patch'
assert sha(patch) == 'e9c2db7b54f48220053b76f02b5377b9ab78fa039eb461e828db3e38a48e7fae'
with tempfile.TemporaryDirectory(prefix='publication-independent-patch-') as temp:
    target = Path(temp)
    path = target / source_path
    path.parent.mkdir(parents=True)
    path.write_bytes(original)
    (target / wpt_path).parent.mkdir(parents=True)
    for reverse in [False, True]:
        command = ['patch', '--batch', '-p1', '-i', str(patch)] + (['-R'] if reverse else [])
        result = subprocess.run(command, cwd=target, capture_output=True, text=True)
        assert result.returncode == 0, result.stdout + result.stderr
        assert path.read_bytes() == (original if reverse else candidate)
        if not reverse:
            assert (target / wpt_path).read_bytes() == (browser / 'source' / wpt_path).read_bytes()
        else:
            assert not (target / wpt_path).exists()
old = [json.loads(x) for x in (evidence / 'replay/original.jsonl').read_text().splitlines()]
new = [json.loads(x) for x in (evidence / 'replay/clear-candidate.jsonl').read_text().splitlines()]
assert len(old) == len(new) == 13
changes = [(a,b) for a,b in zip(old,new) if a != b]
assert len(changes) == 4
for a,b in changes:
    assert a['scratch'] == ['ordinary', 'with-variables'] and b['scratch'] == ['with-variables']
    assert {k:v for k,v in a.items() if k != 'scratch'} == {k:v for k,v in b.items() if k != 'scratch'}
assert all(r['exit'] == 0 for r in read(evidence / 'replay/COMMANDS.json'))
print(json.dumps({'authenticated_review_files':len(manifest), 'dependencies':[201,31], 'native_rows_per_variant':13, 'native_changes':4, 'browser_keys':147, 'improvements':12, 'unchanged':135, 'new_PASS':49, 'expected_FAIL':1, 'patch_apply_reverse':'PASS', 'recommendation':'accept scoped native/WPT repair'}, indent=2))
