import hashlib
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


target = (HERE / 'Target.lean').read_text()
proof = (HERE / 'Proof.lean').read_text()
names = re.findall(r'^  (\w+) :', target.split('structure Obligations : Prop where')[1], re.M)
assert len(names) == 10
names += ['obligations']
combined = target + '\n' + proof.removeprefix('import Target\n') + '\n'
combined += ''.join('#print axioms BaselineFeedback.' + n + '\n' for n in names)
assert (HERE / 'Strength.lean').read_text() == combined
assert not re.search(r'\b(sorry|sorryAx|axiom|native_decide|unsafe)\b', combined)
for name, digest in read(HERE / 'TARGET-FREEZE.json').items():
    assert sha(HERE / name) == digest


def audit(text):
    lines = text.splitlines()
    assert len(lines) == len(names)
    result = {}
    for name, line in zip(names, lines, strict=True):
        prefix = "'BaselineFeedback." + name + "' "
        assert line.startswith(prefix)
        suffix = line[len(prefix):]
        axioms = []
        if suffix != 'does not depend on any axioms':
            match = re.fullmatch(r'depends on axioms: \[(.*)\]', suffix)
            assert match
            axioms = match[1].split(', ')
            assert len(axioms) == len(set(axioms))
            assert set(axioms) <= {'propext', 'Classical.choice', 'Quot.sound'}
        result[name] = axioms
    return result


out = HERE / sys.argv[1]
assert out.parent == HERE
for name in ['Target.lean', 'Proof.lean', 'Strength.lean', 'TARGET-FREEZE.json', 'run.py', 'process.py']:
    assert (out / name).read_bytes() == (HERE / name).read_bytes()
for path, digest in read(out / 'INPUTS.json').items():
    assert sha(Path(path)) == digest
commands = read(out / 'COMMANDS.json')
assert len(commands) == 1
command = commands[0]
lean = ROOT / 'artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean'
assert command['argv'] == [str(lean), '-j1', '-M2048', str(out / 'Strength.lean')]
assert command['cwd'] == str(ROOT) and command['exit'] == 0
assert command['group_absent'] and command['safe_cleanup']
assert read(out / 'RESULT.json') == dict(exit=0, inputs_unchanged=True,
    groups_absent=True, output_cache_created=False)
text = (out / 'strength.log').read_text()
audits = audit(text)
lines = text.splitlines()
mutants = {
    'missing': '\n'.join(lines[:-1]),
    'duplicate': '\n'.join(lines + [lines[-1]]),
    'reordered': '\n'.join(list(reversed(lines))),
    'forbidden': '\n'.join(lines[:-1] + ["'BaselineFeedback.obligations' depends on axioms: [sorryAx]"]),
    'extra': text + 'unrecognized output\n',
}
refused = []
for name, value in mutants.items():
    try:
        audit(value)
    except AssertionError:
        refused.append(name)
    else:
        raise AssertionError(name)
assert not list(HERE.rglob('*.olean'))
print(json.dumps(dict(status='PASS retained source and kernel receipts', fields=10,
    audits=audits, parser_refusals=refused, native_refinement=False,
    protected_comparator=False), indent=2))
