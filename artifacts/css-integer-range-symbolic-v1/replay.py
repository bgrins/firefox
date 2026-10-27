import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
parser = argparse.ArgumentParser()
parser.add_argument('--output', type=Path, required=True)
out = parser.parse_args().output.resolve()
assert not out.exists()
inputs = json.loads((HERE / 'INPUTS.json').read_text())
solver = Path(inputs['solver'])
assert sha(solver) == inputs['solver_sha256']
for name, digest in json.loads((HERE / 'REFERENCES.json').read_text()).items():
    assert sha(ROOT / name) == digest, name
for name, item in inputs['queries'].items():
    assert sha(HERE / (name + '.smt2')) == item['sha256'], name
out.mkdir()
version = subprocess.check_output([str(solver), '--version'], text=True, timeout=10).strip()
results = {}
for name, item in inputs['queries'].items():
    start = time.monotonic()
    try:
        result = subprocess.run([str(solver), '-T:55', str(HERE / (name + '.smt2'))],
                                capture_output=True, text=True, timeout=60)
        code, stdout, stderr = result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired as error:
        code = None
        stdout = (error.stdout or b'').decode()
        stderr = (error.stderr or b'').decode()
    (out / (name + '.stdout')).write_text(stdout)
    (out / (name + '.stderr')).write_text(stderr)
    status = stdout.splitlines()[0] if stdout else 'no result'
    results[name] = {'exit': code, 'status': status, 'expected': item['expected'],
                     'elapsed_seconds': time.monotonic() - start,
                     'passed': code == 0 and not stderr and status == item['expected']
                               and '(error' not in stdout,
                     'query_sha256': item['sha256']}
    (out / 'RESULT.json').write_text(json.dumps({
        'solver': version, 'solver_sha256': sha(solver), 'queries': results,
        'all_passed': len(results) == len(inputs['queries']) and all(v['passed'] for v in results.values()),
        'lean_checked_certificate': False, 'compiler_refinement': False,
        'same_resolved_leaf_premise': True,
    }, indent=2) + '\n')
assert all(item['passed'] for item in results.values()), results
print('PASS: five UNSAT obligations and three SAT omission witnesses.')
