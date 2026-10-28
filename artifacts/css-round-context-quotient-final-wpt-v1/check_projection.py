import copy
import hashlib
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

def need(value, message):
    if not value:
        raise AssertionError(message)

spec = importlib.util.spec_from_file_location('round_final_projection', HERE / 'bindings.py')
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
baseline = json.loads((ROOT / 'artifacts/css-local-signing-20261028-v39/CURRENT-EPOCH.json').read_bytes())
p = json.loads((HERE / 'POLICY.json').read_bytes())
p['promotion_manifest_sha256'] = 'a' * 64
p['original_source_identity'] = baseline['installed_identities'].get(b.SOURCE, [1, 2])
epoch = copy.deepcopy(baseline)
ownership = {}
for index, (name, digest) in enumerate({b.SOURCE: p['source_roles']['candidate'][b.SOURCE], **p['live_oracle_sources']}.items()):
    identity = p['original_source_identity'] if name == b.SOURCE else [10, index]
    ownership[name] = {'path': name, 'owned_sha256': digest, 'identity': identity}
    epoch['pins'][name] = digest
    epoch['installed_identities'][name] = identity
for name in p['rebuilt_binaries']:
    epoch['pins'][name] = 'b' * 64
epoch['modified_native_paths'] = sorted(baseline['modified_native_paths'] + [b.SOURCE])
epoch['semantic_index']['working_diff'] = 'c' * 64
epoch['raw_index_observation']['current'] = 'd' * 64
epoch['counts'].update(roles=len(epoch['pins']), installed_identities=len(epoch['installed_identities']), native_modified_paths=len(epoch['modified_native_paths']))
epoch['round_quotient_transition'] = {'role': 'candidate', 'compiled': True, 'accepted': False, 'manifest_sha256': p['promotion_manifest_sha256'], 'source_sha256': p['source_roles']['candidate'][b.SOURCE], 'last_phase': 'candidate-build-1', 'variant': 'round-context-quotient'}
h = SimpleNamespace(need=need)
b.project_promotion(epoch, baseline, p, ownership, h)
mutations = {
    'accepted premature': lambda e: e['round_quotient_transition'].update(accepted=True),
    'uncompiled': lambda e: e['round_quotient_transition'].update(compiled=False),
    'held provider changed': lambda e: e['pins'].__setitem__('servo/components/style/custom_properties.rs', 'e' * 64),
    'accepted linear changed': lambda e: e['accepted_linear_guard'].update(fix=999),
    'unrelated pin': lambda e: e['pins'].__setitem__('unrelated', 'f' * 64),
    'unrelated epoch field': lambda e: e.__setitem__('unrelated', True),
    'extra native': lambda e: e['modified_native_paths'].append('unrelated.rs'),
    'wrong source identity': lambda e: e['installed_identities'].__setitem__(b.SOURCE, [9, 9]),
    'wrong test body': lambda e: e['pins'].__setitem__(next(iter(p['live_oracle_sources'])), 'f' * 64),
}
rejected = []
for label, mutate in mutations.items():
    bad = copy.deepcopy(epoch)
    mutate(bad)
    try:
        b.project_promotion(bad, baseline, p, ownership, h)
    except AssertionError:
        rejected.append(label)
    else:
        raise AssertionError('accepted bad projection: ' + label)
print(json.dumps({'positive_controls': 1, 'rejected_controls': rejected, 'saved_baseline_sha256': hashlib.sha256((ROOT / 'artifacts/css-local-signing-20261028-v39/CURRENT-EPOCH.json').read_bytes()).hexdigest(), 'live_checks': False}, indent=2))
