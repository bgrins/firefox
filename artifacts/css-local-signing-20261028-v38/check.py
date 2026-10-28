import ast
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(HERE / 'commit.py') == 'ef3b5cafed2f379372c2cc6948fee914a6a90d176ae9151baee9b34d89ca8ceb'
config = read(HERE / 'EXECUTION.json')
assert config['receipt_ids'] == ['research', 'checkpoint']
assert config['accepted_fixes'] == 141 and config['tracked_fixes'] == 142
for name,pin in config['previous_evidence'].items():
    assert sha(ROOT/name) == pin
selection = read(HERE / 'research-selection.json')
assert set(selection['files']) == set(selection['source_pins'])
for name,pin in selection['source_pins'].items():
    assert name.startswith('artifacts/') and not name.startswith('artifacts/css-spec-lean/')
    assert not (ROOT/name).is_symlink() and sha(ROOT/name) == pin
inventory = read(HERE / 'INVENTORY.json')
pins = {}
for package in inventory['packages']:
    path = ROOT / package['path']
    assert sha(path/'FILES.json') == package['manifest_sha256']
    entries = read(path/'FILES.json')
    entries = entries.get('files', entries)
    for name,record in entries.items():
        assert not Path(name).is_absolute() and '..' not in Path(name).parts
        pin = record['sha256'] if isinstance(record,dict) else record
        assert sha(path/name) == pin
        pins[str((path/name).relative_to(ROOT))] = pin
    pins[str((path/'FILES.json').relative_to(ROOT))] = package['manifest_sha256']
assert pins == selection['source_pins']
roadmap = read(HERE/'ROADMAP-PUBLICATION.json')
assert sha(HERE/'ROADMAP-PUBLICATION.json') == config['roadmap_publication_sha256']
assert roadmap['target'] == 'artifacts/css-continuation-roadmap-20261028-v1/PLAN.md'
assert roadmap['target'] not in selection['files']
assert sha(HERE/roadmap['preimage']) == roadmap['before_sha256']
assert sha(HERE/roadmap['postimage']) == roadmap['after_sha256']
assert (HERE/roadmap['postimage']).read_bytes().endswith((HERE/roadmap['preimage']).read_bytes())
assert roadmap['detailed_roadmap_sha256'] == sha(HERE/'ROADMAP.md')
for path in HERE.glob('*.py'):
    ast.parse(path.read_text(), filename=str(path))
if config['execution_enabled']:
    assert config['initial_epoch_binding'] and config['pre_signing_evidence']
    assert sha(ROOT/config['initial_epoch_binding']) == config['expected_initial_epoch']
    for name,pin in config['pre_signing_evidence'].items():
        assert sha(ROOT/name) == pin
    old = read(ROOT/config['previous_signing']/'CURRENT-EPOCH.json')
    new = read(ROOT/config['initial_epoch_binding'])
    old['raw_index_observation']['current'] = new['raw_index_observation']['current']
    assert old == new
print(json.dumps({'research_files':len(pins),'packages':len(inventory['packages']),
                  'previous_evidence':len(config['previous_evidence']),
                  'execution_enabled':config['execution_enabled'],
                  'unchanged_commit_helper':True,'syntax_valid':True,
                  'main_or_live_guard_executed':False},indent=2))
