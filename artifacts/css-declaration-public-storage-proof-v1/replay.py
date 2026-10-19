import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

assert sys.flags.isolated and sys.flags.no_site
ROOT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
out = args.output.resolve()
assert not out.exists() and not out.is_relative_to(ROOT)
config = json.loads((ROOT / 'CHECKPOINT.json').read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
for name, pin in config['sources'].items():
    assert sha(ROOT / name) == pin, name
assert sha(Path(config['lean'])) == config['lean_sha256']
text = (ROOT / 'lean/PublicStorage.lean').read_text()
assert not re.search(r'\b(sorry|axiom|admit|native_decide)\b', text)
names = ['PublicStorage.' + n for n in re.findall(r'^theorem\s+(\w+)', text, re.M)]
assert names == config['theorems']
out.mkdir(parents=True)
for name in ['AllOrder', 'PublicStorage']:
    shutil.copyfile(ROOT / 'lean' / (name + '.lean'), out / (name + '.lean'))
(out / 'Audit.lean').write_text('import PublicStorage\n' + ''.join('#print axioms ' + n + '\n' for n in names))
env = {k: v for k, v in os.environ.items() if not k.startswith(('LEAN_', 'PYTHON'))}
env['LEAN_PATH'] = str(out)
commands = []
for name in ['AllOrder', 'PublicStorage', 'Audit']:
    command = [config['lean'], '-o', str(out / (name + '.olean')), str(out / (name + '.lean'))]
    run = subprocess.run(command, cwd=out, env=env, capture_output=True, text=True)
    commands.append(dict(command=command, exit=run.returncode, stdout=run.stdout, stderr=run.stderr))
    (out / 'COMMANDS.json').write_text(json.dumps(commands, indent=2) + '\n')
    assert run.returncode == 0, commands[-1]
axioms = commands[-1]['stdout']
rows = re.findall(r"^'([^']+)' (?:depends on axioms: \[([^]]*)\]|does not depend on any axioms)$", axioms, re.M)
assert [name for name, _ in rows] == names
for _, group in rows:
    assert set(filter(None, (x.strip() for x in group.split(',')))) <= {'propext', 'Quot.sound', 'Classical.choice'}
(out / 'AXIOMS.txt').write_text(axioms)
result = dict(theorem_audits=len(names), source_pins=config['sources'],
              scope='Universal model of parse, remove and clear histories; native binding and CSSOM composition pending')
(out / 'RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result))
