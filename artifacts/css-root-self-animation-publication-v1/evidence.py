import hashlib
import importlib.util
import json

read = lambda path: json.loads(path.read_bytes())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify(root, binding, stage):
    expected = read(root / 'artifacts/css-root-self-animation-publication-v1/PAIR-BINDING.json')
    assert binding == expected and all(binding.values()), 'pending completed evidence'
    owner = load('publication_saved_ownership', root / 'artifacts/css-registered-number-source-transition-v4/transition.py')
    for record in binding.values():
        owner.authenticate(root / record['directory'], record['manifest_sha256'])
    source = root / binding['source']['directory']
    roles = read(source / 'SOURCE-ROLES.json')
    assert set(roles) == {'servo/ports/geckolib/glue.rs'}
    inputs = read(source / 'INPUTS.json')
    assert len(inputs) == 1
    name, test_record = next(iter(inputs.items()))
    assert name == 'web-animations/animation-model/keyframe-effects/root-font-self-reference.html'
    test = 'testing/web-platform/tests/' + name
    files = {path: {'path': str((source / 'candidate' / path).relative_to(root)),
                    'sha256': row['candidate_sha256']} for path, row in roles.items()}
    files[test] = {'path': str((source / 'tests' / name).relative_to(root)), 'sha256': test_record['sha256']}
    assert stage == {'stage': 'root-identity', 'files': files,
                     'head_preimages': {path: row['original_sha256'] for path, row in roles.items()},
                     'adopt_existing_tests': [], 'create_tests': [test]}
    refresh_dir = root / binding['restoration_verifier']['directory']
    saved = load('completed_font_unit_restoration', refresh_dir / 'run.py')
    policy = read(refresh_dir / 'POLICY.json')
    _, restored, pre, post, raw = saved.saved(policy)
    assert restored['source_identities'] == {
        path: {'sha256': row['original_sha256'], 'identity': pre['sources'][path]['identity']}
        for path, row in roles.items()}
    outcome = root / binding['outcome']['directory']
    comparison = load('saved_font_unit_comparison', outcome / 'compare.py')
    bindings = read(outcome / 'BINDINGS.json')
    assert bindings['owner_directory'] == policy['owner']['directory']
    assert bindings['owner_manifest'] == policy['owner']['manifest_sha256']
    assert bindings['runtime_directory'] == policy['runtime']
    assert bindings['runtime_manifest'] == policy['runtime_manifest_sha256']
    comparison.authenticate(root / bindings['baseline']['directory'], bindings['baseline']['manifest_sha256'])
    assert sha(root / bindings['baseline']['path']) == bindings['baseline']['sha256']
    for key in ('owner_terminal', 'owner_result', 'build_result', 'restoration'):
        record = bindings[key]
        assert sha(root / record['path']) == record['sha256']
    native_owner = root / policy['owner']['directory']
    runtime = root / policy['runtime']
    assessor = load('saved_font_unit_signatures', native_owner / 'assess.py')
    original = read(root / bindings['baseline']['path'])
    assert original['counts'] == {'PASS': 54, 'FAIL': 7} and original['projection_only']
    baseline = {'rows': [assessor.signature(row) for row in original['rows']],
                'ends': [assessor.signature(row) for row in original['endings']]}
    report = read(outcome / 'RESULT.json')
    rows, ends = [], []
    for lane in ('root_identity', 'controls'):
        phase = runtime / ('candidate-wpt-' + lane)
        assessment = read(phase / 'ASSESSMENT.json')
        rows.extend(assessor.signature(row) for row in assessment['rows'])
        ends.extend(assessor.signature(row) for row in assessment['ends'])
        assert report['lanes'][lane]['raw_sha256'] == sha(phase / 'raw.jsonl')
        assert report['lanes'][lane]['assessment_sha256'] == sha(phase / 'ASSESSMENT.json')
    actual = comparison.compare_signatures(baseline, rows, ends)
    assert all(report[key] == json.loads(json.dumps(value)) for key, value in actual.items())
    assert report['candidate_sources'] == {path: row['candidate_sha256'] for path, row in roles.items()}
    assert report['build_sha256'] == sha(runtime / 'candidate-build/RESULT.json')
    assert report['baseline_sha256'] == bindings['baseline']['sha256']
    assert report['baseline_projection'] and read(runtime / 'RESULT.json')['build_revision'] == policy['head']
    return {'pair_head': policy['head'], 'candidate_pass': 61, 'target_pass': 14,
            'preserved_pass_signatures': 54, 'preserved_endings': 5, 'fail_to_pass': 7,
            'root_live_restoration_verified': True, 'native_publication_performed': False}
