import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda path: json.loads(path.read_bytes())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def load(name,path):
    spec = importlib.util.spec_from_file_location(name,path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def validate_actual_bindings(policy):
    assert policy['target_binding'] and policy['reduced_binding'] and policy['reduced_capsule']
    assert policy['prepared_state_evidence'] and policy['controls']['CURRENT-EPOCH.json'] and policy['prepared_application_metadata']
    load('actual_target_binding',HERE / 'target.py').verify(ROOT,policy,HERE)
    load('actual_reduced_binding',HERE / 'reduced.py').replay_all(ROOT,policy)


def validate_policy(policy):
    assert policy['execution_enabled'] == policy['candidate_execution_enabled']
    if policy['execution_enabled']:
        assert policy['activation_pending'] == []
        validate_actual_bindings(policy)
    else:
        assert policy['activation_pending']
    roles = read(HERE / 'SOURCE-ROLES.json')
    assert roles == read(ROOT / 'artifacts/css-contextual-duration-restyle-tristate-browser-v1/SOURCE-ROLES.json')
    assert set(roles) == set(policy['source_paths']) == {'dom/animation/EffectCompositor.cpp','dom/animation/EffectCompositor.h','servo/components/style/matching.rs'}
    assert policy['runtime_output'] == 'artifacts/css-contextual-duration-restyle-tristate-broader-runtime-1'
    assert set(policy['phases']) == {'normative','reftest','inactive','reduced'}
    assert policy['wpt'] == policy['phases']['normative']
    assert (policy['wpt']['expected_subtest_count'],policy['phases']['inactive']['expected_subtest_count']) == (49,1)
    assert 'feedback_transport' not in policy and 'record_kinds' not in policy
    predecessor = read(ROOT / 'artifacts/css-contextual-duration-restyle-tristate-browser-v1/POLICY.json')
    for key in ('accepted_current_payloads','accepted_epoch_records','source_context_pins','resource_policy','rebuilt_binaries','original_build','prepared_flag_hashes','source_equivalence'):
        assert policy[key] == predecessor[key], key
    proposal = ROOT / policy['proposal']['directory']
    assert sha(proposal / 'FILES.json') == policy['proposal']['manifest_sha256']
    for name,pin in read(proposal / 'FILES.json').items():
        assert sha(proposal / name) == (pin['sha256'] if isinstance(pin,dict) else pin)
    for name,record in roles.items():
        for kind in ('base','candidate'):
            assert sha(ROOT / record[kind + '_capture']) == record[kind + '_sha256']
        if name.startswith('dom/'):
            assert b'DURATION_RESTYLE_TRACE' not in (ROOT / record['candidate_capture']).read_bytes()
    projection = policy['restyle_projection']
    assert sha(ROOT / projection['manifest']) == projection['sha256']
    old = ROOT / policy['broader_predecessor']['directory']
    assert (HERE / 'wpt.py').read_bytes() == (old / 'wpt.py').read_bytes()
    assert (HERE / 'assess.py').read_bytes() == (old / 'assess.py').read_bytes()
    comparison = load('broader_comparison_checks',HERE / 'comparison.py')
    comparison.historical(ROOT,policy)
    reduced = load('reduced_source_join',HERE / 'reduced.py')
    reduced_source = read(ROOT / policy['reduced_capsule']['directory'] / 'POLICY.json')
    assert reduced_source['source_role_pins'] == reduced.joined_source_pins(policy,roles)
    conflict = copy.deepcopy(policy)
    conflict['source_context_pins']['servo/components/style/matching.rs'] = '0' * 64
    try:
        reduced.joined_source_pins(conflict,roles)
    except AssertionError:
        pass
    else:
        raise AssertionError('Conflicting context/overlay base accepted')
    for name in ('dom/animation/EffectCompositor.cpp','dom/animation/EffectCompositor.h'):
        missing = dict(reduced_source['source_role_pins']);missing.pop(name)
        assert missing != reduced.joined_source_pins(policy,roles)
    for kind in ('normative','reftest','inactive','reduced'):
        current = dict(policy,phase_kind=kind,wpt=policy['phases'][kind])
        assert comparison.expected_wpt(ROOT,current) == current['wpt']


def check():
    policy = read(HERE / 'POLICY.json')
    validate_policy(policy)
    for path in HERE.glob('*.py'):
        compile(path.read_bytes(),str(path),'exec')
    authenticated, deferred = 0, []
    for name,pin in policy['references'].items():
        if not name.startswith('artifacts/'):
            deferred.append(name)
            continue
        assert sha(ROOT / name) == pin, name
        authenticated += 1
    comparison = load('broader_saved_replay',HERE / 'comparison.py')
    comparison.replay_all(ROOT,policy)
    if policy['reduced_binding'] is None:
        try:
            validate_actual_bindings(policy)
        except AssertionError:
            pass
        else:
            raise AssertionError('Missing reduced baseline permitted activation')
    if policy['target_binding'] is not None:
        target = load('completed_target_binding',HERE / 'target.py')
        target.verify(ROOT,policy,HERE)
        for field in ('owner_sha256','manifest_sha256','terminal_sha256','result_sha256'):
            changed = copy.deepcopy(policy)
            changed['target_binding'][field] = '0' * 64
            try:
                target.verify(ROOT,changed,HERE)
            except AssertionError:
                pass
            else:
                raise AssertionError('Wrong target binding accepted: ' + field)
    load('broader_synthetic_assessment',HERE / 'check_assess.py')
    load('sealed_projection_saved_controls',ROOT / 'artifacts/css-contextual-duration-restyle-projection-v1/check.py')
    old = {'index':{'raw_index':'old','entries':'same'},'nested_index':{'raw_index':'unchanged'}}
    new = copy.deepcopy(old);new['index']['raw_index']='new'
    comparison.admit_snapshot(old,new)
    for key in ('entries','nested'):
        changed = copy.deepcopy(new)
        if key == 'entries': changed['index']['entries']='wrong'
        else: changed['nested_index']['raw_index']='wrong'
        try:
            comparison.admit_snapshot(old,changed)
        except AssertionError:
            pass
        else:
            raise AssertionError(key)
    print(json.dumps({'artifact_references_authenticated':authenticated,'deferred_nonartifact_references':deferred,'historical_raw_replayed':True,'actual_target_restoration_bound':policy['target_binding'] is not None,'actual_reduced_baseline_bound':policy['reduced_binding'] is not None,'live_guard_build_browser_or_native_execution':False},indent=2))


if __name__ == '__main__':
    check()
