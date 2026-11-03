import hashlib
import importlib.util
import json
from collections import Counter

read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
ROLE = 'servo/components/style/custom_properties.rs'
TYPED_TEST = 'testing/web-platform/tests/css/css-values/attr-taint-registration-transition.html'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def require_comparison(baseline, rows, ends):
    key = lambda row: (row['test'], row['kind'], row.get('subtest') or '')
    old = {key(row): row for row in baseline['rows'] + baseline['ends']}
    new = {key(row): row for row in rows + ends}
    assert len(rows) == len(baseline['rows']) == 82
    assert len(ends) == len(baseline['ends']) == 7
    assert len(old) == len(new) == 89 and set(old) == set(new)
    assert all(row['status'] == 'PASS' for row in rows)
    assert all(row['status'] == 'OK' for row in ends)
    preserved = [identity for identity, row in old.items() if row['status'] == 'PASS' or row['kind'] == 'test_end']
    assert len(preserved) == 76 and all(old[identity] == new[identity] for identity in preserved)
    differences = [{'identity': identity, 'original': old[identity], 'candidate': new[identity]} for identity in sorted(old) if old[identity] != new[identity]]
    assert len(differences) == 13
    assert all(row['original']['status'] == 'FAIL' and row['candidate']['status'] == 'PASS' for row in differences)
    assert Counter(row['candidate']['test'] for row in differences) == Counter({
        '/css/css-values/attr-fallback-taint.html': 11,
        '/css/css-values/attr-fallback-taint-registration-transition.html': 2,
    })
    return differences


def verify_completed(root, binding, stage):
    assert binding is not None
    expected = read(root / 'artifacts/css-attr-fallback-post-font-after-reparse-publication-v1/PAIR-BINDING.json')
    assert set(binding) == set(expected)
    for key in ('historical_standalone', 'combined_refresh_owner', 'combined_outcome'):
        assert binding[key] == expected[key]
    source = read(root / 'artifacts/css-explicit-attribute-taint-typed-reparse-fix-v1/SOURCE.json')
    old_dir = root / 'artifacts/css-attr-fallback-publication-v1'
    old_stage, = read(old_dir / 'STAGES.json')['stages']
    intended = json.loads(json.dumps(old_stage))
    intended['head_preimages'][ROLE] = source['roles'][ROLE]['candidate']['sha256']
    intended['files'][ROLE] = source['after_fallback']['candidate']
    assert stage == intended
    historical = load('historical_fallback28', old_dir / 'evidence.py').verify(root, binding['historical_standalone'], old_stage)
    assert (historical['original_PASS'], historical['original_FAIL'], historical['candidate_PASS']) == (17, 11, 28)
    owner = load('saved_publication_ownership', root / 'artifacts/css-registered-number-source-transition-v4/transition.py')
    refresh = binding['combined_refresh_owner']
    refresh_dir = root / refresh['directory']
    owner.authenticate(refresh_dir, refresh['manifest_sha256'])
    saved = load('completed_combined_restoration', refresh_dir / 'run.py')
    policy = read(refresh_dir / 'POLICY.json')
    saved.saved(policy)
    outcome = binding['combined_outcome']
    outcome_dir = root / outcome['directory']
    owner.authenticate(outcome_dir, outcome['manifest_sha256'])
    report = read(outcome_dir / 'RESULT.json')
    native_owner = root / policy['owner']['directory']
    runtime = root / policy['runtime']
    baseline = read(native_owner / 'BASELINE82.json')
    assessor = load('combined_signature', native_owner / 'assess.py')
    rows, ends = [], []
    for lane in ('reparse', 'fallback', 'controls', 'composition'):
        phase = runtime / ('candidate-wpt-' + lane)
        assessment = read(phase / 'ASSESSMENT.json')
        rows.extend(assessor.signature(row) for row in assessment['rows'])
        ends.extend(assessor.signature(row) for row in assessment['ends'])
        assert report['lanes'][lane]['raw_sha256'] == sha(phase / 'raw.jsonl')
        assert report['lanes'][lane]['assessment_sha256'] == sha(phase / 'ASSESSMENT.json')
    differences = require_comparison(baseline, rows, ends)
    assert json.loads(json.dumps(differences)) == report['differences']
    assert report['comparison_passed'] and report['candidate_pass'] == 82
    assert (report['preserved_pass_signatures'], report['preserved_ending_signatures'], report['fail_to_pass']) == (69, 7, 13)
    assert report['baseline_source'] == baseline['source_sha256'] == stage['head_preimages'][ROLE]
    assert report['candidate_sources'] == {ROLE: stage['files'][ROLE]['sha256']}
    assert report['build_sha256'] == sha(runtime / 'candidate-build/RESULT.json')
    assert report['baseline_sha256'] == sha(native_owner / 'BASELINE82.json')
    return {'tested_head': source['head'], 'source': source, 'candidate_pass': 82,
            'preserved_pass_signatures': 69, 'preserved_ending_signatures': 7,
            'fail_to_pass': 13, 'historical_standalone': historical,
            'root_live_restoration_verified': True}


def require_future(binding, receipt, capture, source):
    assert binding['typed_native_receipt'] and binding['typed_parent_research'] and binding['current_capture'] and binding['current_epoch_sha256'], 'pending typed native receipt/current capture/epoch'
    assert receipt['stage'] == 'reparse' and receipt['signature_verified'] is True
    assert receipt['files'] == sorted([ROLE, TYPED_TEST]) and receipt['app_rebuilt'] is False
    assert receipt['accepted_fix_increment'] == 0
    assert isinstance(receipt['commit'], str) and len(receipt['commit']) == 40
    assert isinstance(receipt['parent'], str) and len(receipt['parent']) == 40
    assert capture['full_current_state_verified'] and capture['source_transition_lock_absent']
    assert capture['sources_match_head']
    assert capture['controls']['CURRENT-EPOCH.json'] == binding['current_epoch_sha256']
    claim = capture['payload_claims'][ROLE]
    assert claim['path'] == ROLE and claim['owned_sha256'] == source['roles'][ROLE]['candidate']['sha256']
    assert claim == capture['sources'][ROLE]
    assert claim['identity'] == capture['installed_identities'][ROLE]
    assert claim['owned_sha256'] == capture['epoch_payload_pins'][ROLE]
    assert capture['snapshot']['index']['cached_diff'] == capture['snapshot']['index']['working_diff'] == hashlib.sha256(b'').hexdigest()


def require_typed_parent(receipt, research):
    assert research['head'] == receipt['parent']
    assert research['committed'] is True and research['signature_verified'] is True
    assert research['accepted_fix_increment'] == 0 and research['native_working_diff_preserved'] is True


def verify(root, binding, stage):
    assert binding and binding['typed_native_receipt'] and binding['typed_parent_research'] and binding['current_capture'] and binding['current_epoch_sha256'], 'pending typed native receipt/current capture/epoch'
    result = verify_completed(root, binding, stage)
    values = {}
    for key in ('typed_native_receipt', 'typed_parent_research', 'current_capture'):
        record = binding[key]
        path = root / record['path']
        assert sha(path) == record['sha256']
        values[key] = read(path)
    require_typed_parent(values['typed_native_receipt'], values['typed_parent_research'])
    require_future(binding, values['typed_native_receipt'], values['current_capture'], result['source'])
    return dict(result, pair_head=values['typed_native_receipt']['commit'],
                typed_native=values['typed_native_receipt'], current_capture=values['current_capture'],
                typed_parent_research=values['typed_parent_research'])
