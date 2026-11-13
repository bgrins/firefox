import hashlib
import json
import os
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
AUTHOR = ROOT / 'artifacts/css-flex-line-collection-native-policy-20261111-v1'
REPLAY = ROOT / 'artifacts/css-flex-line-collection-native-policy-root-replay-20261111-v1'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


manifest = json.loads((AUTHOR / 'FILES.json').read_text())
assert sha(AUTHOR / 'FILES.json') == '6c7462c26735a9de37fbf36fdf3d87ba67e29ce37c1167c16c34db88fe917612'
for name, entry in manifest.items():
    path = AUTHOR / name
    assert sha(path) == entry['sha256'] and path.stat().st_size == entry['bytes'], name
for name, expected in json.loads((AUTHOR / 'ORIGINS.json').read_text()).items():
    assert sha(ROOT / name) == expected, name
for name, expected in json.loads((AUTHOR / 'TARGET-INPUTS.json').read_text()).items():
    assert sha(AUTHOR / name) == expected, name
for name, entry in json.loads((AUTHOR / 'TRANSPORT.json').read_text()).items():
    assert sha(AUTHOR / name) == entry['sha256'] == sha(ROOT / entry['path']), name

sources = json.loads((REPLAY / 'SOURCES.json').read_text())
assert sources == {str(p.relative_to(AUTHOR / 'proof')): sha(p)
                   for p in (AUTHOR / 'proof').rglob('*.lean')}
assert sources == {str(p.relative_to(REPLAY / 'source')): sha(p)
                   for p in (REPLAY / 'source').rglob('*.lean')}
modules = json.loads((AUTHOR / 'ORDER.json').read_text())
refusals = json.loads((AUTHOR / 'REFUSALS.json').read_text())
records = json.loads((REPLAY / 'COMMANDS.json').read_text())
assert [r['module'] for r in records] == modules + ['refusal-' + n for n in refusals]
lean = ROOT / 'artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean'
assert sha(lean) == 'd1d9c26a539f54fe839d2aa7760bf1ac1dd76a30b26e2c9684bebf2900038fcf'
for record in records:
    module = record['module']
    assert record['argv'] == [str(lean), '-j1', '-M4096', '-DwarningAsError=true',
                              '-o', module + '.olean', module + '.lean']
    log = REPLAY / (module.replace('/', '-') + '.log')
    assert sha(log) == record['log_sha256']
    assert record['group_absent']
    try:
        os.killpg(record['pgid'], 0)
    except ProcessLookupError:
        pass
    else:
        raise AssertionError(('group still present', record['pgid']))
    if module.startswith('refusal-'):
        diagnostic = log.read_text()
        assert record['exit'] == 1 and diagnostic.count('error:') == 1
        assert 'proved that the proposition' in diagnostic and 'is false' in diagnostic
    else:
        assert record['exit'] == 0

names = []
for line in (REPLAY / 'Audit.log').read_text().splitlines():
    match = re.fullmatch(r"'([^']+)' (?:depends on axioms: \[(.*)\]|does not depend on any axioms)", line)
    assert match, line
    names.append(match[1])
    assert set(filter(None, (match[2] or '').split(', '))) <= {'propext', 'Classical.choice', 'Quot.sound'}
assert names == json.loads((AUTHOR / 'AUDIT-NAMES.json').read_text())
assert len(names) == len(set(names)) == 55
assert not (REPLAY / 'scratch').exists()
assert json.loads((REPLAY / 'RESULT.json').read_text()) == {
    'status': 'PASS', 'commands': 17, 'scope': 'full', 'audit_roots': 55,
    'expected_refusals': 6, 'scratch_removed': True, 'groups_absent': True}

acceptance = {
    'status': 'accepted', 'scope': 'source-shaped rational policy refinement',
    'author_files': len(manifest), 'modules': len(modules), 'audit_roots': len(names),
    'expected_refusals': len(refusals), 'commands': len(records),
    'replay_session': 22134, 'replay_terminal': '6d73b4', 'replay_exit': 0,
    'source_manifest_sha256': sha(AUTHOR / 'SOURCE-ONLY.json'),
    'result_sha256': sha(REPLAY / 'RESULT.json'),
    'commands_sha256': sha(REPLAY / 'COMMANDS.json'),
    'all_groups_freshly_absent': True, 'scratch_removed': True,
    'protected_comparator': False, 'native_integer_or_binary_refinement': False,
    'browser_tests_are_theorem_premises': False,
    'seconds': sum(r['seconds'] for r in records),
}
(HERE / 'ACCEPTANCE.json').write_text(json.dumps(acceptance, indent=2) + '\n')
print(json.dumps(acceptance, indent=2))
