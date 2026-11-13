import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


for name, digest in read(HERE / 'TARGET-FREEZE.json').items():
    assert sha(HERE / name) == digest
for name, digest in read(HERE / 'SOURCE-HASHES.json').items():
    assert sha(HERE / 'source' / name) == digest == sha(ROOT / name)
grid = (HERE / 'source/layout/generic/nsGridContainerFrame.cpp').read_text()
reflow = (HERE / 'source/layout/generic/ReflowInput.cpp').read_text()
assert grid.count((HERE / 'PRODUCER.cpp').read_text().rstrip()) == 1
assert reflow.count((HERE / 'CONSUMER.cpp').read_text().rstrip()) == 1
target = (HERE / 'Target.lean').read_text()
proof = (HERE / 'Proof.lean').read_text()
strength = (HERE / 'Strength.lean').read_text()
assert proof.startswith(target) and strength.startswith(proof)
assert not re.search(r'\b(sorry|axiom|native_decide|unsafe)\b', strength)
fields = re.findall(r'^  (\w+) : ', target, re.M)
assert len(fields) == 16
names = fields + ['complete', 'removing_clamp_breaks_range',
                  'moving_clamp_breaks_last', 'retaining_zero_breaks_presence']
out = HERE / 'proof-2'
lines = (out / 'strength.log').read_text().splitlines()
assert len(lines) == len(names) == 20
for name, line in zip(names, lines, strict=True):
    prefix = "'BaselinePadding." + name + "' "
    assert line.startswith(prefix)
    suffix = line[len(prefix):]
    if suffix != 'does not depend on any axioms':
        match = re.fullmatch(r'depends on axioms: \[(.*)\]', suffix)
        assert match
        axioms = match[1].split(', ')
        assert len(axioms) == len(set(axioms))
        assert set(axioms) <= {'propext', 'Classical.choice', 'Quot.sound'}
for name in ['Target.lean', 'Proof.lean', 'Strength.lean', 'TARGET-FREEZE.json', 'run.py']:
    assert (out / name).read_bytes() == (HERE / name).read_bytes()
for path, digest in read(out / 'INPUTS.json').items():
    assert sha(Path(path)) == digest
commands = read(out / 'COMMANDS.json')
assert len(commands) == 1
command = commands[0]
lean = ROOT / 'artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean'
assert command['argv'] == [str(lean), str(out / 'Strength.lean')]
assert command['cwd'] == str(ROOT) and command['exit'] == 0
assert command['group_absent'] and command['safe_cleanup']
assert read(out / 'RESULT.json') == dict(exit=0, inputs_unchanged=True,
    groups_absent=True, output_cache_created=False)
old = HERE / 'proof-1'
assert (old / 'Proof.lean').read_text().startswith(target)
assert (old / 'Proof.lean').read_text() != proof
for path, digest in read(old / 'INPUTS.json').items():
    original = Path(path)
    snapshot = old / original.name
    assert sha(snapshot if snapshot.exists() else original) == digest
assert read(old / 'COMMANDS.json')[0]['exit'] == 1
assert 'sorryAx' in (old / 'proof.log').read_text()
assert not list(HERE.rglob('*.olean'))
print(json.dumps(dict(status='PASS retained source and Lean receipts', fields=16,
    aggregate=1, model_counterexamples=3, standard_axiom_audits=20,
    native_refinement=False, protected_comparator=False, fresh_kernel_execution=False), indent=2))
