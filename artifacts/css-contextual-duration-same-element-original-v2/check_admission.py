import copy
import importlib.util
import json
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('same_element_saved_admission', HERE / 'admission.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
policy = json.loads((HERE / 'POLICY.json').read_text())
module.validate(policy)
active = copy.deepcopy(policy)
active.update(execution_enabled=True, activation_pending=[])
module.validate(active)
negative = []
for label, mutate in [
    ('wrong head', lambda p: p.update(head='0' * 40)),
    ('wrong epoch', lambda p: p['controls'].update({'CURRENT-EPOCH.json': '0' * 64})),
    ('stale app entry', lambda p: p['prepared_application_metadata'].update(entry_identity=[0, 0])),
    ('stale app target', lambda p: p['prepared_application_metadata'].update(identity=[0, 0])),
    ('wrong BuildID', lambda p: p['prepared_application_metadata'].update(browser_build_id='wrong')),
    ('wrong build revision', lambda p: p['wpt']['phase_revisions'].update(original='0' * 40)),
    ('research success invented', lambda p: p['admission_binding'].update(mode='signed-research')),
    ('source base changed', lambda p: p['source_role_pins'].update({'servo/components/style/matching.rs': '0' * 64})),
    ('accepted claim removed', lambda p: p['accepted_current_payloads'].pop(next(iter(p['accepted_current_payloads'])))),
    ('candidate enabled', lambda p: p.update(candidate_execution_enabled=True)),
    ('activation still pending', lambda p: p.update(execution_enabled=True)),
]:
    changed = copy.deepcopy(policy)
    mutate(changed)
    try:
        module.validate(changed)
    except AssertionError:
        negative.append(label)
    else:
        raise AssertionError(label)
print(json.dumps({'saved_binding_positives': 2, 'binding_negatives': negative,
                  'live_guard_executed': False, 'policy_modified': False}, indent=2))
