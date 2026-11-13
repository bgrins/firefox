import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import time

inputs = Path('/inputs')
output = Path('/output')
work = Path('/work')
rows = []
shutil.copyfile('/certificate-checker-packages.txt', output / 'packages.txt')


def run(command, name, hashes):
    start = time.monotonic()
    try:
        result = subprocess.run(command, cwd=work, capture_output=True, timeout=120)
        stdout, stderr, code = result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired as error:
        stdout, stderr, code = error.stdout or b'', error.stderr or b'', None
    (output / (name + '.stdout')).write_bytes(stdout)
    (output / (name + '.stderr')).write_bytes(stderr)
    row = {
        'command': command,
        'input_sha256': hashes,
        'exit': code,
        'seconds': time.monotonic() - start,
    }
    rows.append(row)
    print(json.dumps(row), flush=True)


names = ['WeightTarget', 'Product', 'Addition', 'Weights']
sources = [inputs / (name + '.v') for name in names]
hashes = {s.name: hashlib.sha256(s.read_bytes()).hexdigest() for s in sources}
for source in sources:
    shutil.copyfile(source, work / source.name)
    run(['coqc', '-q', source.name], source.stem, {source.name: hashes[source.name]})
complete_source = all(('Print Assumptions ' + name + '.') in (inputs / 'Weights.v').read_text() for name in ['product_target', 'addition_target', 'ordered_target', 'prefix_target', 'factor_sum_target', 'full_weight_target']) and not any(token in (inputs / 'Weights.v').read_text()
                          for token in ['Abort.', 'Admitted.', 'Axiom ', 'Hypothesis '])
if complete_source and len(rows) == 4 and all(r['exit'] == 0 for r in rows):
    run(['coqchk', '-silent'] + [s.stem for s in sources], 'coqchk', hashes)
(output / 'RESULTS.json').write_text(json.dumps(rows, indent=2) + '\n')
raise SystemExit(0 if len(rows) == 5 and all(r['exit'] == 0 for r in rows) else 1)
