import sys
assert sys.flags.isolated and sys.flags.no_site
import argparse, hashlib, json, os, re, subprocess
from pathlib import Path
R = Path(__file__).resolve().parent
p = argparse.ArgumentParser()
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
out = a.output.resolve()
out.mkdir(parents=True, exist_ok=False)
cfg = json.loads((R / 'TOOLCHAIN.json').read_text())
for tool in ['rustc', 'lean']:
    assert hashlib.sha256(Path(cfg[tool]).read_bytes()).hexdigest() == cfg[tool + '_sha256']
env = {k: v for k, v in os.environ.items() if not k.startswith(('LEAN_', 'PYTHON'))}
env['LEAN_PATH'] = str(out)
commands = []
def run(cmd):
    p = subprocess.run(cmd, cwd=out, env=env, capture_output=True, text=True)
    commands.append(dict(command=cmd, exit=p.returncode, stdout=p.stdout, stderr=p.stderr))
    (out / 'COMMANDS.json').write_text(json.dumps(commands, indent=2) + '\n')
    assert p.returncode == 0, p.stdout + p.stderr
    return p.stdout
source = (R / 'lean/Publication.lean').read_text()
assert not re.search(r'\b(sorry|axiom|admit|native_decide)\b', source)
names = ['Publication.' + n for n in re.findall(r'^theorem\s+(\w+)', source, re.M)]
assert names == json.loads((R / 'THEOREMS.json').read_text())
(out / 'Publication.lean').write_text(source)
run([cfg['lean'], '-o', str(out / 'Publication.olean'), str(out / 'Publication.lean')])
(out / 'Audit.lean').write_text('import Publication\n' + ''.join('#print axioms ' + n + '\n' for n in names))
axioms = run([cfg['lean'], str(out / 'Audit.lean')])
for name in names:
    assert axioms.count("'" + name + "'") == 1
for group in re.findall(r'depends on axioms:\s*\[([^\]]*)\]', axioms):
    assert set(re.findall(r'[A-Za-z_][\w.]*', group)) <= {'propext', 'Quot.sound', 'Classical.choice'}
assert axioms.count('depends on axioms:') + axioms.count('does not depend on any axioms') == len(names)
(out / 'AXIOMS.txt').write_text(axioms)
run([sys.executable,'-I','-S',str(R/'native/build.py'),'--output',str(out/'native')])
result=json.loads((out/'native/RESULT.json').read_text())
for witness in result['mutation_witnesses']:
    assert witness['kernel_witness'] in names
for variant in result['variants']:
    for suffix in ['.rs','.jsonl','-bindings.json']:
        assert (out/'native'/(variant+suffix)).read_bytes()==(R/'receipts/native'/(variant+suffix)).read_bytes()
result['theorems']=len(names)
result['source_only']=True
(out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
