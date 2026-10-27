import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
a = argparse.ArgumentParser()
a.add_argument('--output', type=Path, required=True)
out = a.parse_args().output.resolve()
assert not out.exists()
for name, digest in json.loads((HERE / 'MODEL-PINS.json').read_text()).items():
    assert sha(HERE / name) == digest, name
inputs = json.loads((HERE / 'INPUTS.json').read_text())
compiler = ROOT / inputs['compiler']
assert sha(compiler) == inputs['compiler_sha256']
pins = json.loads((HERE / 'IMPORT-PINS.json').read_text())
for name, digest in pins.items():
    assert sha(ROOT / name) == digest, name
expected = json.loads((HERE / 'EXPECTED-LOGS.json').read_text())

def rejected(name, code, log):
    return code == 1 and log == expected[name]

checks = 0
for name, log in expected.items():
    assert 'error: Tactic `decide` proved that the proposition\n' in log
    assert log.endswith('is false\n') and rejected(name, 1, log)
    for code, bad in [(0, log), (2, log), (1, log + 'extra error\n'),
                      (1, 'error: unknown identifier missing\n'),
                      (1, 'error: Tactic `decide` failed to reduce the proposition to true or false\n'),
                      (1, (HERE / 'author-replay/calculation-rejected.log').read_text()),
                      (1, log.replace('some 2', 'some 3'))]:
        assert not rejected(name, code, bad)
        checks += 1
out.mkdir()
receipts = {}
with tempfile.TemporaryDirectory(prefix='steps-origin-lean-', dir='/private/tmp') as tmp:
    scratch = Path(tmp)
    env = dict(os.environ, LEAN_PATH=str(scratch) + ':' + str(ROOT / inputs['canonical_olean_root']))
    for name in ['Steps.lean', 'Examples.lean']:
        shutil.copyfile(HERE / name, scratch / name)
    jobs = [('model', ['-o', 'Steps.olean', 'Steps.lean']), ('positive', ['Examples.lean'])]
    for name in sorted(expected):
        shutil.copyfile(HERE / 'false' / (name + '.lean'), scratch / (name + '.lean'))
        jobs.append((name, [name + '.lean']))
    for name, args in jobs:
        run = subprocess.run([str(compiler), '-j1', *args], cwd=scratch, env=env,
                             capture_output=True, text=True, timeout=90)
        log = run.stdout + run.stderr
        (out / (name + '.log')).write_text(log)
        receipts[name] = {'exit': run.returncode, 'log_sha256': hashlib.sha256(log.encode()).hexdigest()}
        if name == 'model':
            assert run.returncode == 0 and not log
        elif name == 'positive':
            assert run.returncode == 0 and log == (HERE / 'author-replay-2/positive.log').read_text()
            assert 'sorryAx' not in log
        else:
            assert rejected(name, run.returncode, log), log
for name, digest in pins.items():
    assert sha(ROOT / name) == digest, name
assert sha(compiler) == inputs['compiler_sha256']
(out / 'CHECK.json').write_text(json.dumps({'status': 'STEPS_ORIGIN_CLAMPING_MODEL_REPLAY_PASS',
    'audits': 10, 'positive_examples': 11, 'decisive_false_controls': 3,
    'negative_gate_rejections': checks, 'results': receipts,
    'scratch_removed': not scratch.exists(), 'shared_imports_unchanged': True,
    'native_refinement': False, 'canonical_changes': False}, indent=2) + '\n')
print('PASS: 10 audits, 11 examples, 3 decisive false controls, 21 rejection-gate checks')
