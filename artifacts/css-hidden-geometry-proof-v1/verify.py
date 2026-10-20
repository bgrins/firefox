import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('Use python3 -I -S')
sys.dont_write_bytecode = True
import argparse
import hashlib
import json
from pathlib import Path
import re
import stat
import subprocess

root = Path(__file__).resolve().parent

def require(condition, why):
    if not condition: raise RuntimeError(why)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

parser = argparse.ArgumentParser()
parser.add_argument('--manifest-sha', required=True)
a = parser.parse_args()
for f in root.rglob('*'):
    require(stat.S_ISREG(f.lstat().st_mode) or stat.S_ISDIR(f.lstat().st_mode), 'nonregular entry')
require(sha(root / 'FILES.json') == a.manifest_sha, 'outer pin')
files = json.loads((root / 'FILES.json').read_text())['files']
require({str(f.relative_to(root)) for f in root.rglob('*') if f.is_file()} == set(files) | {'FILES.json', 'FREEZE.json'}, 'outer roster')
for n, digest in files.items():
    require(not Path(n).is_absolute() and '..' not in Path(n).parts, 'unsafe path')
    require(sha(root / n) == digest, 'outer payload ' + n)
require(json.loads((root / 'FREEZE.json').read_text()) == {'FILES_sha256': a.manifest_sha, 'payload_count': len(files)}, 'outer freeze')
c = root / 'capsule'
innerpin = 'a4dc6e88cf8bd4f431875a619017339a2d4ac658d0588ba3585def2d9e419c8c'
require(sha(c / 'FILES.json') == innerpin, 'inner pin')
result = subprocess.run([sys.executable, '-I', '-S', str(c / 'replay.py'), '--manifest-sha', innerpin, '--verify-only'], capture_output=True, text=True)
require(result.returncode == 0, result.stdout + result.stderr)
names = re.findall(r'^theorem ([A-Za-z0-9_]+)', (c / 'lean/Hidden.lean').read_text(), re.M)
expected_audits = ['Hidden.' + n for n in names]
require(len(expected_audits) == 30 and len(set(expected_audits)) == 30, 'theorem roster')
require(re.findall(r'#print axioms (Hidden\.\w+)', (c / 'lean/Audit.lean').read_text()) == expected_audits, 'audit input roster')
for label in ('replay-canonical', 'replay-relocated'):
    p = root / label
    summary = json.loads((p / 'SUMMARY.json').read_text())
    require(summary['outcome'] == 'PASS_SCOPED_MODEL_AND_CALIBRATION' and summary['manifest_sha256'] == innerpin, 'replay outcome')
    require(summary['audits'] == 30 and summary['bindings'] == 15, 'replay counts')
    audits = (p / 'lean-audits.stdout').read_text()
    require(re.findall(r"^'(Hidden\.\w+)'", audits, re.M) == expected_audits, 'exact audited names')
    for line in audits.splitlines():
        match = re.search(r'depends on axioms: \[(.*?)\]', line)
        require(match is not None or 'does not depend on any axioms' in line, 'axiom format')
        if match: require(set(match.group(1).split(', ')) <= {'propext', 'Classical.choice', 'Quot.sound'}, 'axiom set')
    rows = {}
    for variant in ('old', 'repaired'):
        rows[variant] = (p / ('lean-rows-' + variant + '.stdout')).read_text().splitlines()
        require(len(rows[variant]) == 192, 'row count')
        for i, row in enumerate(rows[variant]):
            fields = [int(v) for v in row.split(',')]
            require(len(fields) == 14 and fields[0] == i, 'row shape')
        for opt in ('O0', 'O2'):
            require((p / ('run-' + variant + '-' + opt + '.stdout')).read_text().splitlines() == rows[variant], 'native match')
            require(not (p / ('run-' + variant + '-' + opt + '.stderr')).read_text(), 'native stderr')
    require(sum(a != b for a, b in zip(rows['old'], rows['repaired'])) == 32, 'change count')
    require(len(summary['mutants']) == 12, 'mutant count')
    for mutant in summary['mutants']:
        stem = mutant['name'] + '-' + mutant['optimization']
        actual = (p / ('run-' + stem + '.stdout')).read_text().splitlines()
        require(len(actual) == 192 and not (p / ('run-' + stem + '.stderr')).read_text(), 'mutant runtime')
        changes = [{'row': i, 'expected': x, 'actual': y} for i, (x, y) in enumerate(zip(rows['repaired'], actual)) if x != y]
        require(changes and len(changes) == mutant['different_rows'] and changes[0] == mutant['first_difference'], 'mutant witness')
    commands = json.loads((p / 'COMMANDS.json').read_text())
    require(all(x['exit'] != 0 if x['name'].startswith('false-') else x['exit'] == 0 for x in commands), 'command outcomes')
    require(len(summary['falseclaims']) == 4, 'falseclaim count')
    for n in summary['falseclaims']:
        text = (p / ('false-' + n + '.stdout')).read_text()
        require('Tactic `decide` proved that the proposition' in text and '\nis false' in text, 'falseclaim reason')
    require(all(not (p / n).exists() for n in summary['removed_products']), 'products retained')
for n in ['lean-audits.stdout', 'lean-rows-old.stdout', 'lean-rows-repaired.stdout', 'CHANGES.json']:
    require((root / 'replay-canonical' / n).read_bytes() == (root / 'replay-relocated' / n).read_bytes(), 'relocation mismatch')
guards = json.loads((root / 'GUARDS.json').read_text())
require(len(guards) == 13, 'guards count')
for g in guards:
    logs = ''.join((root / 'guard-controls' / (g['name'] + ext)).read_text() for ext in ('.stdout', '.stderr'))
    require(g['exit'] != 0 and g['expected_gate'] in logs, 'guard witness')
print(json.dumps({'verified_payloads': len(files), 'inner_payloads': 30, 'audits': 30, 'source_bindings': 15, 'native_rows_per_replay': 768, 'semantic_mutant_runs_per_replay': 12, 'falseclaims_per_replay': 4, 'guards': 13, 'outcome': 'PASS_SCOPED_EVIDENCE'}))
