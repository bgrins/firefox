import difflib
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PARENT = ROOT / 'artifacts/css-font-metric-computed-size-producer-v1'
BASE = ROOT / 'artifacts/css-font-metric-synthesis-producer-v1/base'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
for name, record in json.loads((HERE / 'REFERENCES.json').read_text()).items():
    path = ROOT / name
    assert sha(path) == record['sha256'] and path.stat().st_size == record['bytes'], name
role = 'servo/components/style/properties/cascade.rs'
source = (HERE / 'candidate' / role).read_text()
restored = source.replace((HERE / 'DIAGNOSTIC.rs').read_text(), '')
for old, new in reversed(json.loads((HERE / 'SOURCE-INSERTIONS.json').read_text())):
    assert restored.count(new) == 1
    restored = restored.replace(new, old, 1)
assert restored == (PARENT / 'candidate' / role).read_text()
assert (HERE / 'PARENT-DELTA.patch').read_text() == ''.join(difflib.unified_diff(
    restored.splitlines(True), source.splitlines(True),
    fromfile=str((PARENT / 'candidate' / role).relative_to(ROOT)),
    tofile=str((HERE / 'candidate' / role).relative_to(ROOT))))
provider = 'servo/components/style/custom_properties.rs'
assert (HERE / 'candidate' / provider).read_bytes() == (PARENT / 'candidate' / provider).read_bytes()
fixture = HERE / 'font-size-form-typed-attr-diagnostic.html'
restored = fixture.read_text()
for old, new in reversed(json.loads((HERE / 'JS-INSERTIONS.json').read_text())):
    assert restored.count(new) == 1
    restored = restored.replace(new, old, 1)
original = ROOT / 'artifacts/css-font-size-form-typed-attr-probe-v1/tests/css/css-ui/font-size-form-typed-attr.tentative.html'
assert restored == original.read_text()
assert (HERE / 'FIXTURE-DELTA.patch').read_text() == ''.join(difflib.unified_diff(
    restored.splitlines(True), fixture.read_text().splitlines(True),
    fromfile=str(original.relative_to(ROOT)), tofile=str(fixture.relative_to(ROOT))))
script = fixture.read_text().split('<script>')[1].split('</script>')[0]
syntax = subprocess.run(['node', '--check'], input=script, text=True, capture_output=True)
assert syntax.returncode == 0, syntax.stderr
marker = subprocess.run(['node', str(HERE / 'MARKER-TEST.js')], text=True, capture_output=True)
assert marker.returncode == 0, marker.stderr
assert (HERE / 'MARKERS.js').read_text() in script
assert (HERE / 'MARKERS.js').read_text() in (HERE / 'MARKER-TEST.js').read_text()
report = json.loads((HERE / 'TEST-RESULT.json').read_text())
assert report['candidate_sha256'] == sha(HERE / 'candidate' / role)
assert report['provider_sha256'] == sha(HERE / 'candidate' / provider)
for name, pin in report['test_inputs_sha256'].items():
    assert sha(HERE / name) == pin
assert report['records']['positive']['run_exit'] == 0
assert '30 passed' in report['records']['positive']['stdout']
assert len(report['records']) == 3
for name, record in report['records'].items():
    assert record['compile_exit'] == 0
    assert (record['run_exit'] == 0) == (name == 'positive')
    if name != 'positive':
        assert 'assertion failed' in record['stdout']
for name in ['TEST-THIRD-RESULT.json', 'TEST-RESULT.json']:
    record = json.loads((HERE / name).read_text())
    assert record['scratch_removed'] and not Path(record['scratch']).exists()
config = json.loads((HERE / 'TOOLCHAIN.json').read_text())
assert sha(Path(config['rustfmt'])) == config['rustfmt_sha256']
formatting = subprocess.run([config['rustfmt'], '--check', '--edition', '2024',
    '--config-path', str(ROOT / config['config']), str(HERE / 'candidate' / role)],
    capture_output=True, text=True)
assert formatting.returncode == 0, formatting.stderr
with tempfile.TemporaryDirectory(prefix='sizeforms-diagnostic-patch-', dir='/private/tmp') as directory:
    scratch = Path(directory)
    for name in [role, provider]:
        target = scratch / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((BASE / name).read_bytes())
    for reverse in [False, True]:
        result = subprocess.run(['patch', '-p1', '--fuzz=0'] + (['-R'] if reverse else []),
            input=(HERE / 'native.patch').read_bytes(), cwd=scratch, capture_output=True)
        assert result.returncode == 0, result.stderr
        assert not any(word in result.stdout.lower() for word in [b'offset', b'fuzz', b'failed'])
        for name in [role, provider]:
            expected = BASE / name if reverse else HERE / 'candidate' / name
            assert (scratch / name).read_bytes() == expected.read_bytes()
assert not scratch.exists()
print(json.dumps({'source_diagnostic_removal_exact': True, 'fixture_marker_removal_exact': True,
    'provider_unchanged': True, 'positive_tests': 30, 'compiled_false_controls': 2,
    'marker_controls': True, 'syntax': True, 'format': True, 'patch_roundtrip': True,
    'scratch_removed': True, 'native_build_or_browser_run': False}))
