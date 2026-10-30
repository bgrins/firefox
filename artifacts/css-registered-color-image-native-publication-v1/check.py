import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_bytes())
spec = importlib.util.spec_from_file_location('transform', HERE / 'transform.py')
t = importlib.util.module_from_spec(spec)
spec.loader.exec_module(t)
policy, stages = read(HERE / 'POLICY.json'), read(HERE / 'STAGES.json')['stages']
assert policy['stage'] is None and policy['bindings'] is None and policy['enabled_modes'] == []
for name, pin in policy['references'].items():
    assert sha(ROOT / name) == pin, name
for path in HERE.glob('*.py'):
    compile(path.read_bytes(), str(path), 'exec')
saved = ROOT / 'artifacts/css-native-publication-preparation-state-20261030-v1'
assert sha(saved / 'FILES.json') == '8b75bf9045e3646fda796d2291eacaa59687884a25cf39b3f99f34443b74c753'
for name, record in read(saved / 'FILES.json').items():
    assert sha(saved / name) == record['sha256']
epoch, owned, role = (read(saved / n) for n in ('CURRENT-EPOCH.json', 'OWNED.json', 'ROLE.json'))
initial = copy.deepcopy((epoch, owned, role))
negative = []


def reject(label, fn):
    try:
        fn()
    except AssertionError:
        negative.append(label)
    else:
        raise AssertionError(label)


for number, stage in enumerate(stages):
    original = copy.deepcopy((epoch, owned, role))
    claims = {p: {'path': p, 'owned_sha256': r['sha256'],
                  'identity': epoch['installed_identities'].get(p, [1, 100 + number])}
              for p, r in stage['files'].items()}
    index = {'raw_index': {'synthetic': 'installed-' + stage['stage']}}
    semantic = copy.deepcopy(epoch['semantic_index'])
    semantic['working_diff'] = 'synthetic installed diff'
    current, new_owned, new_role = t.installed(epoch, owned, role, stage, claims, index, semantic, 'synthetic-manifest', 'artifacts/synthetic-output')
    assert (epoch, owned, role) == original
    assert current['modified_native_paths'] == sorted(stage['head_preimages'])
    assert not new_role['built'] and 'last_build' not in new_role and 'last_install' not in new_role
    assert not current['prototype_overlay_state']['installed']
    if number == 1:
        assert current['prototype_overlay_state'] == epoch['prototype_overlay_state']
    assert current['registered_number_transition']['role'] == new_role['role']
    for name in ('pins', 'staged_working', 'committed_research_working_payloads', 'installed_identities'):
        assert {p:v for p,v in current[name].items() if p not in stage['files']} == {p:v for p,v in epoch[name].items() if p not in stage['files']}
    for name in ('untracked_native', 'nested_semantic_index', 'canonical_application'):
        assert current[name] == epoch[name]
    assert {k:v for k,v in current.items() if k.startswith('accepted_')} == {k:v for k,v in epoch.items() if k.startswith('accepted_')}
    assert all(current['pins'][p] == r['sha256'] and new_owned[p] == claims[p] for p,r in stage['files'].items())
    for path in stage['files']:
        bad = copy.deepcopy(claims)
        bad[path]['owned_sha256'] = 'wrong'
        reject(stage['stage'] + ' wrong claim ' + path, lambda: t.installed(epoch, owned, role, stage, bad, index, semantic, 'synthetic', 'synthetic'))
    commit = 'synthetic-' + stage['stage'] + '-commit'
    semantic['head'] = commit
    semantic['working_diff'] = ''
    result = t.committed(current, stage['stage'], {'raw_index': {'synthetic': commit}}, semantic, commit)
    assert result['modified_native_paths'] == [] and result['counts']['native_modified_paths'] == 0
    assert result['registered_color_image_publication'][stage['stage']]['native_commit'] == commit
    assert result['registered_number_transition']['paired_head'] == commit
    assert current['registered_color_image_publication'][stage['stage']].get('native_commit') is None
    assert result['pins'] == current['pins'] and result['installed_identities'] == current['installed_identities']
    epoch, owned, role = result, new_owned, new_role
assert initial == tuple(read(saved / n) for n in ('CURRENT-EPOCH.json', 'OWNED.json', 'ROLE.json'))
assert stages[0]['working_preimages']['servo/components/style/custom_properties.rs'] == '2675b33b30ac43db5b758d5a80f42fa4530856c32d5a0923882a15f8a8bc5774'
assert stages[0]['head_preimages']['servo/components/style/custom_properties.rs'] == '8a4adc903e7d88e218ee087cbe44cc3548df70fac9353dd923d5c32de2c458f9'
assert len(stages[0]['files']) == 4 and len(stages[1]['files']) == 2
for stage in stages:
    for path, record in stage['files'].items():
        assert sha(ROOT / record['path']) == record['sha256']
    assert sha(ROOT / stage['native_patch']) == stage['native_patch_sha256']
    assert sha(ROOT / stage['wpt_patch']) == stage['wpt_patch_sha256']
print(json.dumps({'references': len(policy['references']), 'pure_saved_control_transforms': 2,
                  'negative_claims': negative, 'source_working_vs_HEAD_preimage_distinct': True,
                  'actual_binding': None, 'native_git_browser_actions': False,
                  'saved_control_bytes_unchanged': True}))
