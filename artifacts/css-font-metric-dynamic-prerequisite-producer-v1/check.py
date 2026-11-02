import difflib
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PARENT = ROOT / 'artifacts/css-font-metric-ordinary-ownership-v1'
BASE = ROOT / 'artifacts/css-font-metric-synthesis-producer-v1/base'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
for path, pin in json.loads((HERE / 'REFERENCES.json').read_bytes()).items():
    assert sha(ROOT / path) == pin, path
roles = ['servo/components/style/properties/cascade.rs', 'servo/components/style/custom_properties.rs']
delta = ''
for role in roles:
    before, after = PARENT / 'candidate' / role, HERE / 'candidate' / role
    delta += ''.join(difflib.unified_diff(before.read_text().splitlines(True), after.read_text().splitlines(True), fromfile=str(before.relative_to(ROOT)), tofile=str(after.relative_to(ROOT))))
assert delta == (HERE / 'PARENT-DELTA.patch').read_text()
assert (HERE / 'candidate' / roles[1]).read_bytes() == (PARENT / 'candidate' / roles[1]).read_bytes()
report = json.loads((HERE / 'TEST-RESULT.json').read_bytes())
assert report['candidate_sha256'] == sha(HERE / 'candidate' / roles[0])
assert report['provider_sha256'] == sha(HERE / 'candidate' / roles[1])
assert report['servo_arc_sha256'] == sha(ROOT / 'servo/components/servo_arc/lib.rs')
assert report['stable_deref_trait_sha256'] == sha(ROOT / 'third_party/rust/stable_deref_trait/src/lib.rs')
assert report['generated_data_sha256'] == sha(ROOT / 'servo/components/style/properties/data.py')
assert 'final_loop' in report['parts_sha256']
assert (HERE / 'candidate' / roles[0]).read_text().count('.ensure_prioritary_property(') == 3
for name, pin in report['test_inputs_sha256'].items():
    assert sha(HERE / name) == pin
assert report['scratch_removed'] and not Path(report['scratch']).exists()
assert report['records']['positive']['compile_exit'] == report['records']['positive']['run_exit'] == 0
assert '21 passed' in report['records']['positive']['stdout']
compile_failures = set()
for name, row in report['records'].items():
    if name in compile_failures:
        assert row['compile_exit'] != 0 and ('E0369' in row['compile_stderr'] or 'E0277' in row['compile_stderr'])
    else:
        assert row['compile_exit'] == 0
        assert (row['run_exit'] == 0) == (name == 'positive')
config = json.loads((HERE / 'TOOLCHAIN.json').read_bytes())
assert sha(Path(config['rustfmt'])) == config['rustfmt_sha256']
assert sha(ROOT / config['config']) == config['config_sha256']
format_result = subprocess.run([config['rustfmt'], '--check', '--edition', '2024', '--config-path', str(ROOT / config['config']), str(HERE / 'candidate' / roles[0])], capture_output=True, text=True)
assert format_result.returncode == 0, format_result.stderr
with tempfile.TemporaryDirectory(prefix='metric-ordinary-ownership-patch-') as temporary:
    scratch = Path(temporary)
    for role in roles:
        target = scratch / role
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((BASE / role).read_bytes())
    patch = (HERE / 'native.patch').read_bytes()
    results = []
    for reverse in (False, True):
        result = subprocess.run(['patch', '-p1', '--fuzz=0'] + (['-R'] if reverse else []), input=patch, cwd=scratch, capture_output=True)
        assert result.returncode == 0, result.stderr
        assert not any(word in result.stdout.lower() for word in (b'offset', b'fuzz', b'failed', b'reject'))
        for role in roles:
            expected = BASE / role if reverse else HERE / 'candidate' / role
            assert (scratch / role).read_bytes() == expected.read_bytes()
        results.append(result.stdout.decode())
assert not scratch.exists()
print(json.dumps({'candidate_sha256': report['candidate_sha256'], 'provider_unchanged': True, 'tests': 21, 'behavioral_mutants': 9, 'trait_compile_fail_controls': 0, 'patch_roundtrip': results, 'format_check': True, 'scratch_removed': True, 'native_retry_performed': False}))
