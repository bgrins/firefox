import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
first = json.loads((HERE / 'cycle-model-receipt.json').read_text())
assert first['signature_verified'] and first['working_bodies_and_nested_index_preserved']
for name in ['initial-independence', 'provider-observations', 'provider-repair']:
    with (HERE / (name + '-driver.log')).open('x') as stream:
        subprocess.run([sys.executable, '-I', '-S', '-B', str(HERE / 'commit.py'), str(HERE / (name + '-selection.json'))], cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT, check=True)
    print('Completed', name, flush=True)
files = [HERE / n for n in ['commit.py', 'finish.py', 'synchronize.py', 'CHECKPOINT.md', 'DRAFTS.json', 'INITIAL-EPOCH.json', 'BEFORE.json', 'resume-first.py', 'cycle-model-driver.log.attempt-1', 'cycle-model-commit.log.attempt-1', 'cycle-model-commit.log.attempt-2', 'cycle-model-retry-driver.log.attempt-2', 'SIGNING-STATUS.json']]
for group in json.loads((HERE / 'DRAFTS.json').read_text()).values():
    for name, info in group['files'].items():
        path = ROOT / name
        assert hashlib.sha256(path.read_bytes()).hexdigest() == info['sha256']
        files.append(path)
for name in ['cycle-model', 'initial-independence', 'provider-observations', 'provider-repair']:
    for suffix in ['-selection.json', '-item.json', '-message.txt', '-receipt.json', '-commit.log', '-signature.log']:
        files.append(HERE / (name + suffix))
previous = ROOT / 'artifacts/css-local-signing-20261027-v25'
for name in ['checkpoint-receipt.json', 'checkpoint-signature.log', 'checkpoint-commit.log', 'FINAL-CHECK.json']:
    files.append(previous / name)
pins = {}
for path in files:
    assert path.is_file() and not path.is_symlink()
    pins[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
item = {'id': 'checkpoint', 'files': sorted(pins), 'source_pins': pins, 'message': 'No bug - Preserve provider research drafts and signing checkpoint. r?#firefox-style-system-reviewers'}
selection = HERE / 'checkpoint-selection.json'
with selection.open('x') as stream:
    json.dump(item, stream, indent=2, sort_keys=True)
    stream.write('\n')
with (HERE / 'checkpoint-driver.log').open('x') as stream:
    subprocess.run([sys.executable, '-I', '-S', '-B', str(HERE / 'commit.py'), str(selection)], cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT, check=True)
print('Completed checkpoint', flush=True)
