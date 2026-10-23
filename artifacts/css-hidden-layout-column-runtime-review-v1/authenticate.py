import sys

if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit("Run with python3 -I -S and without -O")

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
roots = {
    'css-hidden-layout-column-runtime-v1': '95f4290b6c8d5cc27afac52c94fb20e501282c7cea239caf455d71f52fe2f3e8',
    'css-hidden-layout-column-analysis-v1': 'c5fef6c3896e0e76ace2eaf4efd2650ee395a133dfc71ce413fcd269849f29fa',
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


receipt = {}
for name, pin in roots.items():
    root = HERE.parent / name
    assert digest(root / 'FILES.json') == pin
    manifest = json.loads((root / 'FILES.json').read_text())
    for relative, expected in manifest.items():
        path = root / relative
        assert not path.is_symlink() and path.is_file() and digest(path) == expected, relative
    actual = {str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()}
    seals = {'FILES.json', 'FREEZE.json'} if name.endswith('runtime-v1') else {'FILES.json'}
    assert actual == set(manifest) | seals
    receipt[name] = {'manifest_sha256': pin, 'payloads': len(manifest), 'closed': True}
runtime = HERE.parent / 'css-hidden-layout-column-runtime-v1'
before = json.loads((runtime / 'BEFORE.json').read_text())
final = json.loads((runtime / 'FINAL.json').read_text())
state = json.loads((runtime / 'STATE.json').read_text())
assert before == final
assert state['status'] == 'terminal' and state['restored']
assert state['restore_build_exit'] == 0 and not state['recovery_errors']
assert before['index_diff_sha256'] == hashlib.sha256(b'').hexdigest()
config = json.loads((runtime / 'CONFIG.json').read_text())
assert len(before['sources']) == 28
live = {name: digest(REPO / name) for name in before['sources']}
assert live == before['sources']
assert len(config['must_be_absent']) == 10
assert all(not (REPO / path).exists() for path in config['must_be_absent'])
for phase in ['baseline', 'both']:
    assert state['phases'][phase]['build_exit'] == 0
assert json.loads((runtime/'trace-both-column-build.json').read_text())['exit']==0
root_check = json.loads((runtime / 'ROOT-FINAL-CHECK.json').read_text())
assert root_check['experiment_exit'] == 0 and root_check['status'] == 'PASS'
receipt['restoration'] = {'historical_before_equals_final': True, 'live_28_sources_match': True,
    'historical_head': before['head'], 'index_empty_at_terminal': True,
    'temporary_paths_absent': 10, 'restore_build_exit': 0, 'recovery_errors': []}
(HERE / 'AUTHENTICATION.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps(receipt, indent=2))
