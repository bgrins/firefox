import hashlib
import json
import os
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
AUTHOR = ROOT / 'artifacts/css-flex-mbp-accumulator-proof-20261111-v1'
REPLAY = ROOT / 'artifacts/css-flex-mbp-accumulator-proof-root-replay-20261111-v1'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def absent(pgid):
    try:
        os.killpg(pgid, 0)
    except ProcessLookupError:
        return True
    return False


assert sha(AUTHOR / 'FILES.json') == '7e3f33a4fbc73b1acafc9d13e7e22be6eef273830aa1eaad2111c69ca2a11d9b'
files = read(AUTHOR / 'FILES.json')
assert len(files) == 181
for name, expected in files.items():
    assert sha(AUTHOR / name) == expected, name
for name, expected in read(AUTHOR / 'ORIGINS.json').items():
    assert sha(ROOT / name) == expected, name
for name, origin in read(AUTHOR / 'TRANSPORT.json').items():
    assert sha(AUTHOR / name) == origin['sha256'] == sha(ROOT / origin['path'])
for name, expected in read(AUTHOR / 'TARGET-INPUTS.json').items():
    assert sha(AUTHOR / name) == expected
sources = {str(p.relative_to(AUTHOR / 'proof')): sha(p)
           for p in (AUTHOR / 'proof').rglob('*.lean')}
order = read(AUTHOR / 'ORDER.json')
refusals = read(AUTHOR / 'REFUSALS.json')
names = read(AUTHOR / 'AUDIT-NAMES.json')
assert len(order) == 11 and len(names) == 81 and len(refusals) == 7
lean = str(ROOT / 'artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean')
for run in [AUTHOR / 'verification-1', REPLAY]:
    result = read(run / 'RESULT.json')
    assert result == dict(status='PASS', commands=18, scope='full', audit_roots=81,
                         expected_refusals=7, scratch_removed=True, groups_absent=True)
    assert not (run / 'scratch').exists()
    assert read(run / 'SOURCES.json') == sources
    assert {str(p.relative_to(run / 'source')): sha(p)
            for p in (run / 'source').rglob('*.lean')} == sources
    commands = read(run / 'COMMANDS.json')
    assert [c['module'] for c in commands] == order + ['refusal-' + n for n in refusals]
    for c in commands:
        module = c['module']
        assert c['argv'] == [lean, '-j1', '-M4096', '-DwarningAsError=true',
                             '-o', module + '.olean', module + '.lean']
        assert c['group_absent'] and absent(c['pgid'])
        log = run / (module.replace('/', '-') + '.log')
        assert sha(log) == c['log_sha256']
        text = log.read_text()
        if module.startswith('refusal-'):
            assert c['exit'] == 1 and text.count('error:') == 1
            assert 'proved that the proposition' in text and 'is false' in text
        else:
            assert c['exit'] == 0
            if module != 'ProofAudit':
                assert text == ''
    found = []
    for line in (run / 'ProofAudit.log').read_text().splitlines():
        m = re.fullmatch(r"'([^']+)' (?:depends on axioms: \[(.*)\]|does not depend on any axioms)", line)
        assert m, line
        found.append(m[1])
        assert set(filter(None, (m[2] or '').split(', '))) <= {'propext', 'Classical.choice', 'Quot.sound'}
    assert found == names and len(set(found)) == 81
for group in read(AUTHOR / 'CLEANUP.json')['groups']:
    assert group['absent'] and absent(group['pgid'])
result = dict(status='ACCEPTED', scope='checked arithmetic model; no native correspondence',
              author_files=len(files), replay_session=53299, terminal='e73895', exit=0,
              modules=11, audits=81, semantic_refusals=7,
              author_manifest=sha(AUTHOR / 'FILES.json'),
              replay_commands=sha(REPLAY / 'COMMANDS.json'))
(HERE / 'RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
