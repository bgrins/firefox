import difflib
import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
for name in ['REFERENCES.json', 'LIBRARY-PINS.json']:
    for path, expected in json.loads((HERE / name).read_text()).items():
        assert sha(ROOT / path) == expected, path
parent = ROOT / 'artifacts/css-font-metric-computed-size-producer-v1/candidate/servo/components/style/custom_properties.rs'
candidate = HERE / 'candidate/servo/components/style/custom_properties.rs'
assert candidate.read_text() == parent.read_text() + '\n' + (HERE / 'CONTINUATION.rs').read_text() + '\n' + (HERE / 'ADAPTER.rs').read_text()
diff = (HERE / 'PARENT-DELTA.patch').read_text()
lines = diff.splitlines()
assert diff == ''.join(difflib.unified_diff(parent.read_text().splitlines(True), candidate.read_text().splitlines(True), fromfile=lines[0][4:], tofile=lines[1][4:]))
report = json.loads((HERE / 'TEST-FINAL-RESULT.json').read_text())
assert report['source_sha256'] == sha(parent)
assert report['extracted_sha256'] == sha(HERE / 'EXTRACTED.rs')
for name, expected in report['test_inputs'].items():
    assert sha(HERE / name) == expected, name
for name in ['CONTINUATION.rs', 'ADAPTER.rs', 'Tests.rs']:
    assert (HERE / name).read_text() in (HERE / 'EXTRACTED.rs').read_text()
positives = []
negatives = []
for row in report['records']:
    if '--test' in row['command']:
        assert row['exit'] == 0
    if row.get('variant') and '--nocapture' in row['command']:
        if row['variant'] == 'positive':
            assert row['exit'] == 0 and '12 passed' in row['stdout']
            positives.append(row['variant'])
        else:
            assert row['exit'] != 0 and 'test result: FAILED' in row['stdout']
            negatives.append(row['variant'])
assert len(positives) == 1 and len(negatives) == 7
attempts = list(HERE.glob('TEST-*-RESULT.json'))
for path in attempts:
    assert not Path(json.loads(path.read_text())['scratch']).exists()
fmt = Path('/Users/bgrins/.rustup/toolchains/1.97.1-aarch64-apple-darwin/bin/rustfmt')
command = [str(fmt), '--check', '--edition', '2024', '--config-path', str(ROOT / 'artifacts/css-registered-selected-color-union-only-proposal-v1/rustfmt.toml'), str(candidate)]
formatted = subprocess.run(command, capture_output=True, text=True)
assert formatted.returncode == 0, formatted.stdout + formatted.stderr
print(json.dumps({'candidate_sha256': sha(candidate), 'parent_sha256': sha(parent), 'exact_append_and_delta': True, 'positive_tests': 12, 'compiled_false_controls': 7, 'absent_scratch_directories': len(attempts), 'format': True, 'native_typecheck': False}))
