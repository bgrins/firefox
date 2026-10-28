import ast
import copy
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
runner = load('final_runner_check', HERE / 'run.py')
bindings = load('final_bindings_check', HERE / 'bindings.py')
p = runner.read(HERE / 'POLICY.json')
baseline = runner.read(HERE / 'PROMOTION-BASELINE-EPOCH.json')
original = bindings.validate_original(ROOT, HERE, p, runner)
assert original['complete'] and original['observed_subtest_count'] == 34
candidate = copy.deepcopy(baseline)
font = bindings.FONT
ownership = {}
for i, (name, digest) in enumerate({font: p['source_roles']['candidate'][font], **p['live_oracle_sources']}.items()):
    candidate['pins'][name] = digest
    candidate['installed_identities'][name] = p['original_font_identity'] if name == font else [123, i+1]
    ownership[name] = {'path': name, 'owned_sha256': digest, 'identity': candidate['installed_identities'][name]}
candidate['modified_native_paths'] = sorted(baseline['modified_native_paths'] + [font])
candidate['counts'].update(roles=len(candidate['pins']), installed_identities=len(candidate['installed_identities']), native_modified_paths=2)
candidate['line_height_transition'] = {'role':'candidate','compiled':True,'accepted':False,
    'manifest_sha256':p['promotion_manifest_sha256'],'source_sha256':p['source_roles']['candidate'][font],
    'last_phase':'candidate-build-1','variant':'line-height-contextual-leaves'}
candidate['semantic_index']['working_diff'] = 'f'*64
candidate['raw_index_observation']['current'] = 'e'*64
for name in p['rebuilt_binaries']: candidate['pins'][name] = 'd'*64
bindings.project_promotion(candidate, baseline, p, ownership, runner)
mutations = {
    'unrelated_pin': lambda e: e['pins'].__setitem__('servo/components/style/custom_properties.rs','a'*64),
    'staging': lambda e: e['staged_working'].__setitem__('extra','a'*64),
    'index_entries': lambda e: e['semantic_index'].__setitem__('entries','a'*64),
    'cached_diff': lambda e: e['semantic_index'].__setitem__('cached_diff','a'*64),
    'nested': lambda e: e['nested_semantic_index'].__setitem__('head','a'*40),
    'marker_role': lambda e: e['line_height_transition'].__setitem__('role','original'),
    'marker_accepted': lambda e: e['line_height_transition'].__setitem__('accepted',True),
    'marker_uncompiled': lambda e: e['line_height_transition'].__setitem__('compiled',False),
    'font_body': lambda e: e['pins'].__setitem__(font,'a'*64),
    'test_body': lambda e: e['pins'].__setitem__(next(iter(p['live_oracle_sources'])),'a'*64),
    'test_identity': lambda e: e['installed_identities'].__setitem__(next(iter(p['live_oracle_sources'])),[123,999]),
    'extra_pin': lambda e: e['pins'].__setitem__('extra','a'*64),
    'counts': lambda e: e['counts'].__setitem__('untracked_native',0),
    'historical_marker': lambda e: e.__setitem__('reversible_line_height_phase',{}),
    'native_scope': lambda e: e['modified_native_paths'].append('extra.rs'),
    'raw_history': lambda e: e['raw_index_observation'].__setitem__('prior_comparison_raw_drift_cause','invented'),
}
for name, mutate in mutations.items():
    bad=copy.deepcopy(candidate); mutate(bad)
    try: bindings.project_promotion(bad,baseline,p,ownership,runner)
    except (RuntimeError,KeyError,AssertionError): pass
    else: raise AssertionError('accepted '+name)
for path in HERE.glob('*.py'): ast.parse(path.read_text())
report={'original_complete_publication_replay':True,'original_subtests':34,'original_source_provenance_retained':True,
        'projection_positive':1,'projection_rejections':list(mutations),'candidate_build_pins_pending':p['epoch_sha256']=='PENDING',
        'browser_or_live_guard_executed':False}
(HERE/'FINAL-BINDING-CONTROLS.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
