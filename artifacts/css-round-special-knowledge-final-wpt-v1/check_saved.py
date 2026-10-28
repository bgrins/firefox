import copy
import importlib.util
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

h = load('check_runner', HERE / 'run.py')
b = load('check_bindings', HERE / 'bindings.py')
p = h.read(HERE / 'POLICY.json')
baseline = h.read(HERE / 'PROMOTION-BASELINE-EPOCH.json')
epoch = copy.deepcopy(baseline)
source = b.SOURCE
test = next(iter(p['installed_tests']))
claims = {source: {'path': source, 'owned_sha256': p['source_roles']['candidate'][source], 'identity': p['original_source_identity']},
          test: {'path': test, 'owned_sha256': p['installed_tests'][test], 'identity': [123, 456]}}
for name, claim in claims.items():
    epoch['pins'][name] = claim['owned_sha256']
    epoch['installed_identities'][name] = claim['identity']
epoch['modified_native_paths'] = sorted(baseline['modified_native_paths'] + [source])
epoch['counts'] = dict(baseline['counts'], roles=len(epoch['pins']), installed_identities=len(epoch['installed_identities']), native_modified_paths=len(epoch['modified_native_paths']))
epoch['round_special_knowledge_transition'] = {'role': 'candidate', 'compiled': True, 'accepted': False, 'manifest_sha256': p['promotion_manifest_sha256'], 'source_sha256': p['source_roles']['candidate'][source], 'last_phase': 'candidate-build-1', 'variant': 'round-infinite-step-knowledge'}
b.project_promotion(epoch, baseline, p, claims, h)
mutations = [
    lambda e: e['round_special_knowledge_transition'].update(compiled=False),
    lambda e: e['round_special_knowledge_transition'].update(accepted=True),
    lambda e: e['round_special_knowledge_transition'].update(last_phase='another-build'),
    lambda e: e['round_special_knowledge_transition'].update(source_sha256='0' * 64),
    lambda e: e['pins'].update({source: '0' * 64}),
    lambda e: e['pins'].update({test: '0' * 64}),
    lambda e: e['installed_identities'].update({source: [999, 888]}),
    lambda e: e['installed_identities'].update({test: [999, 888]}),
    lambda e: e['counts'].update(roles=0),
    lambda e: e['modified_native_paths'].append('servo/foreign.rs'),
    lambda e: e['semantic_index'].update(head='0' * 40),
    lambda e: e['semantic_index'].update(cached_diff='0' * 64),
    lambda e: e['staged_working'].update({'foreign': '0' * 64}),
    lambda e: e['pins'].update({'servo/foreign.rs': '0' * 64}),
    lambda e: e['accepted_line_height'].update(accepted=False),
    lambda e: e['accepted_random_counter'].update(accepted=False),
    lambda e: e['accepted_linear_guard'].update(accepted=False),
]
for index, mutate in enumerate(mutations):
    changed = copy.deepcopy(epoch)
    mutate(changed)
    try:
        b.project_promotion(changed, baseline, p, claims, h)
    except (RuntimeError, AssertionError, KeyError):
        pass
    else:
        raise AssertionError(('accepted projection mutant', index))
prior = h.read(ROOT / p['paired_runtime'] / 'candidate-wpt/ASSESSMENT.json')
b.validate_final_assessment(ROOT, HERE, p, prior, h)
for field, replacement in [('status', 'FAIL'), ('expected', 'SKIP'), ('message', 'changed'), ('known_intermittent', ['FAIL'])]:
    changed = copy.deepcopy(prior)
    changed['rows'][0][field] = replacement
    try:
        b.validate_final_assessment(ROOT, HERE, p, changed, h)
    except RuntimeError:
        pass
    else:
        raise AssertionError(('accepted signature mutant', field))
original = b.validate_original(ROOT, HERE, p, h)
assert len(original['rows']) == 712
print({'saved_original_candidate_publication_replay': True, 'projection_positive': 1, 'projection_rejects': len(mutations), 'signature_positive': 1, 'signature_rejects': 4, 'synthetic_projection_only': True, 'live_execution': False})
