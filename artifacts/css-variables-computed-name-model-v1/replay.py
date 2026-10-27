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
parser = argparse.ArgumentParser()
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
out = args.output.resolve()
assert not out.exists() and not out.is_symlink()
for name, pin in json.loads((HERE / 'MODEL-PINS.json').read_text()).items():
    assert sha(HERE / name) == pin, name
inputs = json.loads((HERE / 'INPUTS.json').read_text())
compiler = ROOT / inputs['compiler']
assert sha(compiler) == inputs['compiler_sha256']
pins = json.loads((HERE / 'IMPORT-PINS.json').read_text())
for path, expected in pins.items():
    assert sha(ROOT / path) == expected, path
expected_logs = json.loads((HERE / 'EXPECTED-LOGS.json').read_text())
negative = ['early-fallback', 'lost-name-marks', 'own-cycle-rescued']


def rejects_claim(name, code, log):
    expected = expected_logs[name]
    assert 'error: Tactic `decide` proved that the proposition\n' in expected
    assert expected.endswith('\nis false\n')
    return code == 1 and log == expected


gate_checks = 0
for name in negative:
    assert rejects_claim(name, 1, expected_logs[name])
    for code, log in [
        (0, expected_logs[name]),
        (1, 'error: Tactic `decide` failed to reduce the proposition to true or false\n'),
        (1, 'error: unknown identifier observed\n'),
        (1, expected_logs[name] + 'error: unrelated failure\n'),
        (2, expected_logs[name]),
        (1, expected_logs[name].replace('is false', 'failed to reduce to true or false')),
    ]:
        assert not rejects_claim(name, code, log)
        gate_checks += 1

out.mkdir()
records = []
with tempfile.TemporaryDirectory(prefix='computed-name-replay-', dir='/private/tmp') as temp:
    scratch = Path(temp)
    env = dict(os.environ, LEAN_NUM_THREADS='1',
               LEAN_PATH=temp + ':' + str(ROOT / inputs['canonical_olean_root']))
    for name in ['Names', 'Examples', 'Audit'] + negative:
        positive = name not in negative
        source = HERE / (name + '.lean') if positive else HERE / 'false' / (name + '.lean')
        shutil.copyfile(source, scratch / (name + '.lean'))
        command = [str(compiler), '-j1'] + (['-o', name + '.olean'] if positive else []) + [name + '.lean']
        run = subprocess.run(command, cwd=scratch, env=env, text=True, capture_output=True, timeout=90)
        log = run.stdout + run.stderr
        (out / (name + '.log')).write_text(log)
        records.append({'name': name, 'exit': run.returncode, 'command': command})
        if positive:
            assert run.returncode == 0 and log == expected_logs.get(name, ''), log
        else:
            assert rejects_claim(name, run.returncode, log), log
    assert len(expected_logs['Audit'].splitlines()) == 25
    for line in expected_logs['Audit'].splitlines():
        if 'does not depend on any axioms' in line:
            continue
        assert set(line.split('[')[1].split(']')[0].split(', ')) <= {
            'propext', 'Quot.sound', 'Classical.choice'}
assert not scratch.exists()
for path, expected in pins.items():
    assert sha(ROOT / path) == expected, path
result = {'status': 'COMPUTED_NAME_GUARDED_MODEL_REPLAY_PASS', 'records': records,
          'audited_statements': 25, 'positive_examples': 12, 'decisive_false_controls': 3,
          'negative_log_gate_rejection_cases': gate_checks, 'compiler_threads': 1,
          'canonical_imports_unchanged': True, 'scratch_removed': True,
          'native_refinement': False, 'normative_coverage_increment': 0}
(out / 'CHECK.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result))
