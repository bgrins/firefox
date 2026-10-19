import argparse
import difflib
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

parser = argparse.ArgumentParser()
parser.add_argument('--output', type=Path)
args = parser.parse_args()
freeze = json.loads((ROOT / 'FREEZE.json').read_text())
assert digest(ROOT / 'MANIFEST.json') == freeze['manifest_sha256']
manifest = json.loads((ROOT / 'MANIFEST.json').read_text())
for name, expected in manifest.items():
    path = ROOT / name
    assert path.is_file() and not path.is_symlink(), name
    assert digest(path) == expected, name
assert digest(ROOT / 'check.py') == freeze['checker_sha256']
print(f'Authenticated {len(manifest)} inputs before helper execution', flush=True)
binding = json.loads((ROOT / 'SOURCE-BINDING.json').read_text())
original = ROOT / 'original/third_party/rust/cssparser/src/parser.rs'
candidate = ROOT / 'candidate/third_party/rust/cssparser/src/parser.rs'
assert digest(original) == binding['original_parser']
assert digest(candidate) == binding['candidate_parser']
before, after = original.read_text(), candidate.read_text()
call = binding['added_line']
assert after.count(call) == 1 and after.replace(call, '') == before
patch = ''.join(difflib.unified_diff(before.splitlines(True), after.splitlines(True), fromfile='a/third_party/rust/cssparser/src/parser.rs', tofile='b/third_party/rust/cssparser/src/parser.rs'))
assert patch == (ROOT / 'native.patch').read_text()
assert after[after.index("pub fn parse_nested_block<'i, F, T, E>("):] == (ROOT / 'evidence/complete-nested-and-cleanup.rs').read_text()
assert original.read_bytes() == (ROOT / 'vendor/cssparser/src/parser.rs').read_bytes()
for name, expected in json.loads((ROOT / 'SOURCE-PINS.json').read_text()).items():
    assert digest(ROOT / 'source' / name) == expected, name
names = json.loads((ROOT / 'THEOREMS.json').read_text())
model = (ROOT / 'lean/Recovery.lean').read_text()
assert names == ['Recovery.' + n for n in re.findall(r'^theorem\s+(\w+)', model, re.M)]
assert not re.search(r'\b(sorry|axiom|admit|native_decide)\b', model)
if args.output is None:
    sys.exit(0)
out = args.output.resolve()
out.mkdir(parents=True, exist_ok=False)
config = json.loads((ROOT / 'TOOLCHAIN.json').read_text())
for tool in ['rustc', 'lean', 'node']:
    assert digest(Path(config[tool])) == config[tool + '_sha256']
commands = []
env = dict(os.environ, LEAN_PATH=str(out))
def run(command, fail=False):
    result = subprocess.run(command, cwd=out, capture_output=True, text=True, env=env)
    commands.append({'command': command, 'exit': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr})
    (out / 'COMMANDS.json').write_text(json.dumps(commands, indent=2) + '\n')
    assert (result.returncode != 0) if fail else (result.returncode == 0), result.stdout + result.stderr
    return result.stdout + result.stderr

run([sys.executable, str(ROOT / 'native/build.py'), '--output', str(out / 'native')])
for variant in ['original', 'candidate']:
    actual = [json.loads(s) for s in (out / 'native' / variant / 'OBSERVATIONS.jsonl').read_text().splitlines()]
    expected = [json.loads(s) for s in (ROOT / 'evidence' / (variant + '-observations.jsonl')).read_text().splitlines()]
    assert actual == expected and len(actual) == 24
(out / 'Recovery.lean').write_text(model)
run([config['lean'], '-o', str(out / 'Recovery.olean'), str(out / 'Recovery.lean')])
audit = out / 'Audit.lean'
audit.write_text('import Recovery\n' + ''.join('#print axioms ' + n + '\n' for n in names))
report = run([config['lean'], str(audit)])
for name in names:
    assert report.count("'" + name + "'") == 1, name
for group in re.findall(r'depends on axioms:\s*\[([^\]]*)\]', report):
    assert set(re.findall(r'[A-Za-z_][\w.]*', group)) <= {'propext', 'Quot.sound', 'Classical.choice'}, group
assert report.count('depends on axioms:') + report.count('does not depend on any axioms') == len(names)
(out / 'AXIOMS.txt').write_text(report)
mutations = {
    'omit-cleanup': ('input := cleanup k s.input', 'input := s.input', 'limit_recovery'),
    'pop-mismatch': ('if c = k then stack else k :: stack', 'stack', 'leaf_advance'),
}
for name, (old, new, target) in mutations.items():
    assert model.count(old) == 1
    folder = out / name
    folder.mkdir()
    path = folder / 'Recovery.lean'
    path.write_text(model.replace(old, new))
    raw = run([config['lean'], str(path)], fail=True)
    assert 'error:' in raw
    (folder / 'TARGET.json').write_text(json.dumps({'changed': old, 'expected_contract': target, 'status': 'rejected'}, indent=2) + '\n')
html = (ROOT / 'depth-limit-padding-recovery.html').read_text()
scripts = re.findall(r'<script>(.*?)</script>', html, re.S)
assert len(scripts) == 1
js = out / 'probe.js'
js.write_text(scripts[0])
run([config['node'], '--check', str(js)])
(out / 'CHECK.json').write_text(json.dumps({'inputs': len(manifest), 'lean_modules': 1, 'standard_axiom_reports': len(names), 'native_rows_per_variant': 24, 'native_mutants_rejected': 2, 'lean_mutants_rejected': 2, 'browser_execution': False}, indent=2) + '\n')
print('PASS: source/native recovery, universal grammar component, axiom audit and four semantic mutants')
