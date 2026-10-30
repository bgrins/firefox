import copy
import hashlib
import importlib.util
import json

read = lambda path: json.loads(path.read_bytes())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def historical(root, policy):
    directory = root / policy['broader_predecessor']['directory']
    assert sha(directory / 'FILES.json') == policy['broader_predecessor']['sha256']
    source = read(directory / 'POLICY.json')
    for key in ('head','accepted_current_payloads','accepted_epoch_records','source_context_pins','prepared_flag_hashes','original_build','baseline_capsule','baseline_binding','inactive_capsule','inactive_binding','restyle_baseline'):
        assert policy[key] == source[key], key
    for key in ('OWNED.json','ROLE.json'):
        assert policy['controls'][key] == source['controls'][key]
    for kind in ('normative','reftest','inactive'):
        assert policy['phases'][kind] == source['phases'][kind]
    helper = load('sealed_broader_comparison', directory / 'comparison.py')
    assert helper.original_metadata(source) == policy['historical_baseline_metadata']
    return helper, source


def expected_wpt(root, policy):
    kind = policy.get('phase_kind','normative')
    if kind == 'reduced':
        return load('reduced_comparison', root / policy['reduced_adapter']).expected_wpt(root, policy)
    helper, source = historical(root, policy)
    return helper.expected_wpt(root, dict(source,phase_kind=kind,wpt=source['phases'][kind]))


def phase_policy(settings):
    result = dict(settings,tests=settings['test_types'],held_subtests={})
    result['regression_subtests'] = {page:[name for name in names if name not in settings['target_subtests'].get(page,[])] for page,names in settings['expected_subtests'].items()}
    result['cardinality_description'] = 'Exact sealed target and control names; existing control failures retain full signatures.'
    return result


def admit_snapshot(historical_snapshot, current):
    expected = copy.deepcopy(historical_snapshot)
    expected['index']['raw_index'] = current['index']['raw_index']
    assert expected == current


def original_metadata(policy):
    saved = policy['historical_baseline_metadata']
    assert saved['revision'] == saved['build_revision'] == policy['wpt']['phase_revisions']['original']
    assert saved['harness_revision'] == policy['head'] and saved['source_role'] == 'original'
    app = policy['prepared_application_metadata']
    assert set(app) == {'browser_build_id','entry_identity','entry_type','identity','path','resolved','revision','sha256','symlink_target'}
    ignored = {'entry_identity','identity','build_revision','harness_revision','source_role'}
    assert {k:v for k,v in saved.items() if k not in ignored} == {k:v for k,v in app.items() if k not in ignored}
    return saved


def replay_original(root, policy, assessor, checks):
    kind = policy['phase_kind']
    assert policy['wpt'] == expected_wpt(root,policy)
    if kind == 'reduced':
        return load('reduced_comparison',root / policy['reduced_adapter']).replay_original(root,policy,assessor,checks)
    helper, source = historical(root,policy)
    return helper.replay_original(root,dict(source,phase_kind=kind,wpt=source['phases'][kind]),assessor,checks)


def replay_all(root, policy):
    helper, source = historical(root,policy)
    helper.replay_all(root,source)
    epoch = read(root / policy['source_equivalence']['historical_build_epoch'])
    assert epoch['semantic_index']['head'] == policy['source_equivalence']['build_revision']
    for name,pin in policy['source_equivalence']['required_base_pins'].items():
        assert epoch['pins'][name] == pin and name not in epoch['modified_native_paths']
    if policy['prepared_application_metadata'] is not None:
        original_metadata(policy)
    if policy['reduced_binding'] is not None:
        adapter = load('reduced_comparison',root / policy['reduced_adapter'])
        adapter.replay_all(root,policy)


def original_directory(root, policy):
    kind = policy['phase_kind']
    if kind == 'reduced':
        return root / policy['reduced_binding']['directory'] / 'original-wpt'
    helper, source = historical(root,policy)
    return helper.original_directory(root,dict(source,phase_kind=kind))
