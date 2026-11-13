import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
AUTHOR = ROOT / 'artifacts/css-flex-total-violation-proof-20261111-v1'
TARGET = ROOT / 'artifacts/css-flex-total-violation-target-20261111-v2'
REPLAY = HERE / 'replay'


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


assert sys.flags.isolated and not sys.flags.optimize
assert sha(AUTHOR / 'FILES.json') == '484b4bdccd797355be3bdad85fb012a92c15d9f58bea27b22663d5df3720e12c'
for name, digest in read(AUTHOR / 'FILES.json').items():
    assert sha(AUTHOR / name) == digest, name
assert sha(TARGET / 'FILES.json') == '35da97fd01118325fb0dbf706fe60dae24cf95f712e1e316f26134b38c321190'
for name, digest in read(TARGET / 'FILES.json').items():
    assert sha(TARGET / name) == digest, name
for name in ['Model.lean', 'Target.lean']:
    assert (AUTHOR / 'proof/FlexViolation' / name).read_bytes() == (TARGET / 'proof/FlexViolation' / name).read_bytes()
sources = read(REPLAY / 'SOURCES.json')
actual = {str(p.relative_to(REPLAY / 'source')): sha(p) for p in (REPLAY / 'source').rglob('*') if p.is_file()}
assert actual == sources
assert sources == {str(p.relative_to(AUTHOR / 'proof')): sha(p) for p in (AUTHOR / 'proof').rglob('*.lean')}
assert len(sources) == 9 and not (REPLAY / 'scratch').exists()
assert read(REPLAY / 'RESULT.json') == dict(status='PASS', commands=15, scope='full', audit_roots=85, expected_refusals=6, scratch_removed=True, groups_absent=True)
commands = read(REPLAY / 'COMMANDS.json')
order = read(AUTHOR / 'ORDER.json')
refusals = read(AUTHOR / 'REFUSALS.json')
assert len(order) == 9 and len(refusals) == 6
assert [r['module'] for r in commands] == order + ['refusal-' + n for n in refusals]
lean = ROOT / 'artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean'
assert sha(lean) == 'd1d9c26a539f54fe839d2aa7760bf1ac1dd76a30b26e2c9684bebf2900038fcf'
for row in commands:
    module = row['module']
    assert row['argv'] == [str(lean), '-j1', '-M4096', '-DwarningAsError=true', '-o', module + '.olean', module + '.lean']
    assert row['group_absent'] is True and 0 <= row['seconds'] < 185
    log = REPLAY / (module.replace('/', '-') + '.log')
    assert sha(log) == row['log_sha256']
    if module.startswith('refusal-'):
        assert row['exit'] == 1 and log.read_text().count('error:') == 1
        assert 'proved that the proposition' in log.read_text() and 'is false' in log.read_text()
    else:
        assert row['exit'] == 0
        if module != 'ProofAudit':
            assert log.read_bytes() == b''
names = read(AUTHOR / 'AUDIT-NAMES.json')
found = []
for line in (REPLAY / 'ProofAudit.log').read_text().splitlines():
    match = re.fullmatch(r"'([^']+)' (?:depends on axioms: \[(.*)\]|does not depend on any axioms)", line)
    assert match, line
    assert set(filter(None, (match[2] or '').split(', '))) <= {'propext', 'Quot.sound', 'Classical.choice'}
    found.append(match[1])
assert found == names and len(set(found)) == 85
assert 'FlexViolation.universal_target' in found
processes = subprocess.run(['ps', '-axo', 'pid=,pgid=,comm='], capture_output=True, text=True, timeout=10)
assert processes.returncode == 0 and processes.stdout.strip()
owned = {r['pgid'] for r in commands}
for line in processes.stdout.splitlines():
    fields = line.split(None, 2)
    assert len(fields) == 3 and fields[0].isdecimal() and fields[1].isdecimal()
    assert int(fields[1]) not in owned
result = dict(status='PASS independent original V2 model proof acceptance', target_conjuncts=7,
    modules=9, audit_roots=85, semantic_refusals=6, source_files=9,
    target_unchanged=True, groups_freshly_absent=True, scratch_removed=True,
    native_refinement=False, historical_binary_disproof=False,
    author_manifest_sha256=sha(AUTHOR / 'FILES.json'))
(HERE / 'ACCEPTANCE.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result))
