import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

D = Path(__file__).resolve().parent
ROOT = D.parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
out = args.output.resolve()
out.mkdir(parents=True, exist_ok=False)
bindings = json.loads((D / 'BINDINGS.json').read_text())
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
for name, digest in bindings['inputs'].items():
    assert sha(ROOT / name) == digest, name
assert sha(D / 'ClientRounding.lean') == bindings['module_sha256']
lean = ROOT / bindings['lean']
records = []
with tempfile.TemporaryDirectory(prefix='css-client-rounding-', dir='/private/tmp') as scratch:
    temp = Path(scratch)
    shutil.copyfile(ROOT / bindings['import'], temp / 'Rounding.lean')
    shutil.copyfile(D / 'ClientRounding.lean', temp / 'ClientRounding.lean')
    env = {**os.environ, 'LEAN_PATH': str(temp)}
    commands = [('import', ['-o', 'Rounding.olean', 'Rounding.lean']),
                ('client', ['-o', 'ClientRounding.olean', 'ClientRounding.lean'])]
    for name, argv in commands:
        result = subprocess.run([str(lean), *argv], cwd=temp, env=env, capture_output=True, text=True, timeout=120)
        (out / (name + '.stdout')).write_text(result.stdout)
        (out / (name + '.stderr')).write_text(result.stderr)
        assert result.returncode == 0 and not result.stderr
        assert 'warning:' not in result.stdout and 'sorryAx' not in result.stdout
        records.append({'name': name, 'exit': result.returncode, 'stdout_sha256': sha(out / (name + '.stdout'))})
    audit = (out / 'client.stdout').read_text().splitlines()
    assert len(audit) == 14 and all(line.startswith("'CSSOMClientRounding.") for line in audit)
    for line in audit:
        if 'does not depend on any axioms' in line:
            continue
        names = re.search(r'\[([^]]*)\]', line).group(1).split(', ')
        assert set(names) <= {'propext', 'Quot.sound', 'Classical.choice'}
    false_claims = {
        'negative_tie_away': 'CSSOMClientRounding.round (-30) = -1',
        'bias_fits_signed32': 'CSSOMRounding.input32 (CSSOMClientRounding.biased (-2147483648))'}
    for name, claim in false_claims.items():
        source = 'import ClientRounding\nexample : ' + claim + ' := by decide\n'
        (temp / 'FalseClaim.lean').write_text(source)
        result = subprocess.run([str(lean), 'FalseClaim.lean'], cwd=temp, env=env, capture_output=True, text=True, timeout=120)
        (out / (name + '.stdout')).write_text(result.stdout)
        (out / (name + '.stderr')).write_text(result.stderr)
        assert result.returncode != 0 and 'Tactic `decide` proved' in result.stdout and '\nis false' in result.stdout
        records.append({'name': name, 'exit': result.returncode, 'claim': claim, 'rejected': True})
assert not temp.exists()
receipt = {'status': 'PASS', 'local_theorems': 14, 'negative_claims_rejected': 2,
           'module_sha256': bindings['module_sha256'], 'records': records,
           'temporary_directory_removed': True, 'native_implementation': False,
           'native_compiler_browser_index_actions': False}
(out / 'SUMMARY.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps(receipt))
