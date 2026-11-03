import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
source = json.loads((HERE / 'SOURCE.json').read_text())
for path, pin in json.loads((HERE / 'REFERENCES.json').read_text()).items():
    assert sha(ROOT / path) == pin['sha256']
target, role = next(iter(source['roles'].items()))
for pair in [role, source['after_fallback']]:
    for pin in pair.values():
        assert sha(ROOT / pin['path']) == pin['sha256']
test = source['test']
assert sha(ROOT / test['source']) == test['sha256']
assert not (ROOT / test['target']).exists()
base = (ROOT / role['base']['path']).read_text()
candidate = (ROOT / role['candidate']['path']).read_text()
assert candidate == base.replace((HERE / 'SUBSTITUTE-BASE.rs').read_text(), (HERE / 'SUBSTITUTE-CANDIDATE.rs').read_text())
combined = (ROOT / source['after_fallback']['candidate']['path']).read_text()
assert combined == (ROOT / source['after_fallback']['base']['path']).read_text().replace((HERE / 'SUBSTITUTE-BASE.rs').read_text(), (HERE / 'SUBSTITUTE-CANDIDATE.rs').read_text())
records = []
scratch = Path(tempfile.mkdtemp(prefix='explicit-taint-patch-', dir='/private/tmp'))
try:
    for patch, pair, adds_test in [('native.patch', role, True), ('AFTER-FALLBACK.patch', source['after_fallback'], True), ('FALLBACK-COMPOSITION.patch', {'base': role['candidate'], 'candidate': source['after_fallback']['candidate']}, False)]:
        file = scratch / target
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_bytes((ROOT / pair['base']['path']).read_bytes())
        for reverse in [False, True]:
            command = ['patch', '-p1', '--fuzz=0', '--batch', '-i', str(HERE / patch)]
            if reverse:
                command.append('-R')
            result = subprocess.run(command, cwd=scratch, capture_output=True, text=True)
            records.append({'patch': patch, 'reverse': reverse, 'exit': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr})
            assert result.returncode == 0 and 'offset' not in result.stdout and 'fuzz' not in result.stdout
            assert sha(file) == pair['base' if reverse else 'candidate']['sha256']
            if adds_test:
                if reverse:
                    assert not (scratch / test['target']).exists()
                else:
                    assert sha(scratch / test['target']) == test['sha256']
    preparation = json.loads((HERE / 'PREPARE-RESULT.json').read_text())
    assert preparation['success'] and preparation['scratch_removed'] and preparation['callbacks'] == 4
    tests = json.loads((HERE / 'TEST-RESULT.json').read_text())
    assert tests['scratch_removed'] and len(tests['records']) == 5
    assert tests['records'][0]['exit'] == 0
    assert all(row['compile_exit'] == 0 and row['exit'] == 101 for row in tests['records'][1:])
    for label, body in [('method', (HERE / 'SUBSTITUTE-CANDIDATE.rs').read_bytes()), ('support', (HERE / 'TestSupport.rs').read_bytes())]:
        assert hashlib.sha256(body).hexdigest() == tests[label + '_sha256']
finally:
    shutil.rmtree(scratch)
    report = {'records': records, 'scratch': str(scratch), 'scratch_removed': not scratch.exists(),
              'native_compilation': False, 'browser_execution': False}
    (HERE / 'CHECK-RESULT.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))
