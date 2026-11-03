import hashlib
import importlib.util
import json

read = lambda path: json.loads(path.read_bytes())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
PARENT = 'artifacts/css-root-self-animation-publication-v1'
HERE = 'artifacts/css-root-self-animation-publication-v3'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_stage(root, binding, stage):
    prior = read(root / PARENT / 'PAIR-BINDING.json')
    assert {key: binding[key] for key in prior} == prior
    old_stage, = read(root / PARENT / 'STAGES.json')['stages']
    wpt = read(root / 'artifacts/css-root-self-smil-delivery-preparation-v1/WPT-STAGE.json')
    expected = dict(old_stage, files=old_stage['files'] | wpt['files'],
                    create_tests=wpt['create_tests'], testharness_paths=wpt['testharness_paths'],
                    support_paths=wpt['support_paths'])
    assert stage == expected
    assert len(stage['files']) == 5 and len(stage['head_preimages']) == 1
    source = root / binding['smil_source']['directory']
    inputs = read(source / 'INPUTS.json')
    expected_smil = {name.removeprefix('testing/web-platform/tests/'): row
                     for name, row in wpt['files'].items() if '/svg/' in name}
    assert set(inputs) == set(expected_smil)
    for name, record in inputs.items():
        assert record['sha256'] == expected_smil[name]['sha256']
        assert sha(source / 'tests' / name) == record['sha256']
    for record in stage['files'].values():
        assert sha(root / record['path']) == record['sha256']
    return prior, old_stage


def verify(root, binding, stage):
    expected = read(root / HERE / 'PAIR-BINDING.json')
    assert binding == expected and all(binding.values()), 'pending completed SMIL evidence'
    owner = load('smil_publication_ownership', root / 'artifacts/css-registered-number-source-transition-v4/transition.py')
    for record in binding.values():
        owner.authenticate(root / record['directory'], record['manifest_sha256'])
    prior, old_stage = verify_stage(root, binding, stage)
    parent = load('root_identity_publication_evidence', root / PARENT / 'evidence.py')
    old_result = parent.verify(root, prior, old_stage)
    roles = read(root / binding['source']['directory'] / 'SOURCE-ROLES.json')
    refresh_dir = root / binding['smil_restoration_verifier']['directory']
    saved = load('completed_smil_restoration', refresh_dir / 'run.py')
    policy = read(refresh_dir / 'POLICY.json')
    _, restored, pre, post, raw = saved.saved(policy)
    assert policy['head'] == old_result['pair_head']
    assert restored['source_identities'] == {
        path: {'sha256': row['original_sha256'], 'identity': pre['sources'][path]['identity']}
        for path, row in roles.items()}
    outcome = root / binding['smil_outcome']['directory']
    comparison = load('saved_smil_comparison', outcome / 'compare.py')
    bindings = read(outcome / 'BINDINGS.json')
    assert bindings['owner_directory'] == policy['owner']['directory']
    assert bindings['owner_manifest'] == policy['owner']['manifest_sha256']
    assert bindings['runtime_directory'] == policy['runtime']
    assert bindings['runtime_manifest'] == policy['runtime_manifest_sha256']
    original_dir = root / 'artifacts/css-root-self-smil-archived-original-runtime-v1'
    assert root / bindings['baseline']['directory'] == original_dir
    assert bindings['baseline']['manifest_sha256'] == '8f93fb7911a968a0f58599c14b15720dccb9fbbc0ca26f920a8fac614b2bd1ac'
    comparison.authenticate(original_dir, bindings['baseline']['manifest_sha256'])
    assert root / bindings['baseline']['path'] == original_dir / 'ASSESSMENT.json'
    assert sha(original_dir / 'ASSESSMENT.json') == bindings['baseline']['sha256']
    for key in ('owner_terminal', 'owner_result', 'build_result', 'restoration'):
        record = bindings[key]
        assert sha(root / record['path']) == record['sha256']
    native_owner = root / policy['owner']['directory']
    runtime = root / policy['runtime']
    assert read(root / bindings['owner_terminal']['path'])['result_sha256'] == sha(runtime / 'RESULT.json')
    assert bindings['owner_result']['path'] == str((runtime / 'RESULT.json').relative_to(root))
    assert bindings['build_result']['path'] == str((runtime / 'candidate-build/RESULT.json').relative_to(root))
    assert bindings['restoration']['path'] == str((runtime / 'RESTORATION.json').relative_to(root))
    assert read(native_owner / 'POLICY.json')['lane_order'] == ['smil']
    actual_roles = read(native_owner / 'SOURCE-ROLES.json')
    assert set(actual_roles) == set(roles)
    assert all(actual_roles[path]['base_sha256'] == row['original_sha256'] and
               actual_roles[path]['candidate_sha256'] == row['candidate_sha256'] for path, row in roles.items())
    assessor = load('saved_smil_signatures', native_owner / 'assess.py')
    original = read(original_dir / 'ASSESSMENT.json')
    assert original['complete'] and original['counts'] == {'PASS': 5, 'FAIL': 2}
    baseline = {'rows': [assessor.signature(row) for row in original['subtests']],
                'ends': [assessor.signature(row) for row in original['endings']]}
    phase = runtime / 'candidate-wpt-smil'
    assessment = read(phase / 'ASSESSMENT.json')
    report = read(outcome / 'RESULT.json')
    rows = [assessor.signature(row) for row in assessment['rows']]
    ends = [assessor.signature(row) for row in assessment['ends']]
    actual = comparison.compare_signatures(baseline, rows, ends)
    assert actual['candidate_pass'] == 7 and actual['fail_to_pass'] == 2
    assert actual['preserved_pass_signatures'] == 5 and actual['preserved_ending_signatures'] == 1
    assert all(report[key] == json.loads(json.dumps(value)) for key, value in actual.items())
    assert set(report['lanes']) == {'smil'}
    assert report['lanes']['smil']['raw_sha256'] == sha(phase / 'raw.jsonl')
    assert report['lanes']['smil']['assessment_sha256'] == sha(phase / 'ASSESSMENT.json')
    candidate_sources = {path: row['candidate_sha256'] for path, row in roles.items()}
    assert report['candidate_sources'] == candidate_sources
    assert read(runtime / 'candidate-build/RESULT.json')['native_sources'] == candidate_sources
    assert report['build_sha256'] == sha(runtime / 'candidate-build/RESULT.json')
    assert report['baseline_sha256'] == bindings['baseline']['sha256'] and not report['baseline_projection']
    assert read(runtime / 'RESULT.json')['build_revision'] == old_result['pair_head']
    for name, record in read(root / binding['smil_source']['directory'] / 'INPUTS.json').items():
        assert sha(phase / 'tests' / name) == sha(original_dir / 'tests' / name) == record['sha256']
    return dict(old_result, smil_candidate_pass=7, smil_fail_to_pass=2,
                smil_preserved_pass_signatures=5, smil_preserved_endings=1,
                same_native_candidate_verified=True, separate_builds=True,
                combined_observations=68, distinct_target_callbacks=21)
