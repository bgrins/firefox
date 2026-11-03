import hashlib
import importlib.util
import json

read = lambda path: json.loads(path.read_bytes())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
BASE = 'e86b64866cdc5e2260ba9be08c45756fd96e21bb'
PACKAGE = 'artifacts/css-selective-cancellation-after-font-publication-v1'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def require_font_receipt(receipt, stage):
    assert receipt['stage'] == 'font-units' and receipt['signature_verified'] is True
    assert receipt['files'] == sorted(stage['files'])
    assert receipt['app_rebuilt'] is False and receipt['accepted_fix_increment'] == 0
    for name in ('commit', 'parent'):
        value = receipt[name]
        assert isinstance(value, str) and len(value) == 40 and all(c in '0123456789abcdef' for c in value)
    assert receipt['commit'] != receipt['parent']
    assert isinstance(receipt['epoch_sha256'], str) and len(receipt['epoch_sha256']) == 64


def verify_font_history(git, allowed_signers, receipt, stage, tested_head):
    commit, parent = receipt['commit'], receipt['parent']
    assert git('rev-list', '--parents', '-n', '1', commit).decode().split() == [commit, parent]
    for revision in (parent, commit):
        git('-c', 'gpg.ssh.allowedSignersFile=' + allowed_signers, 'verify-commit', revision)
    assert sorted(git('diff', '--name-only', parent, commit).decode().splitlines()) == sorted(stage['files'])
    for path, record in stage['files'].items():
        assert hashlib.sha256(git('show', commit + ':' + path)).hexdigest() == record['sha256']
        if path in stage['head_preimages']:
            assert hashlib.sha256(git('show', parent + ':' + path)).hexdigest() == stage['head_preimages'][path]
        else:
            assert not git('ls-tree', parent, '--', path)
    assert not git('merge-base', '--is-ancestor', tested_head, parent)
    assert all(path.startswith('artifacts/') for path in git('diff', '--name-only', tested_head, parent).decode().splitlines())


def signatures(events, page, count):
    assert not any(row.get('action') == 'crash' for row in events)
    selected = [row for row in events if row.get('test') == page]
    rows = [row for row in selected if row.get('action') == 'test_status']
    starts = [row for row in selected if row.get('action') == 'test_start']
    ends = [row for row in selected if row.get('action') == 'test_end']
    assert len(starts) == len(ends) == 1 and ends[0]['status'] == 'OK'
    assert len(rows) == len({row['subtest'] for row in rows}) == count
    keys = ('test', 'subtest', 'status', 'expected', 'known_intermittent', 'message')
    clean = lambda row: {key: row[key] for key in keys if key in row}
    return [clean(row) for row in rows], clean(ends[0])


def compare_lane(old, new, old_end, new_end, targets):
    assert old_end == new_end
    before = {row['subtest']: row for row in old}
    after = {row['subtest']: row for row in new}
    assert list(before) == list(after)
    assert {name for name, row in before.items() if row['status'] == 'FAIL'} == targets
    changed, preserved = [], []
    for name, row in before.items():
        current = after[name]
        assert current['status'] == 'PASS'
        if name in targets:
            assert row.get('expected') == 'PASS'
            assert 'expected 46 +/- 0.06 but got 64' in row['message']
            changed.append({'before': row, 'after': current})
        else:
            assert row == current
            preserved.append(row)
    return changed, preserved


def events(path):
    return [json.loads(line) for line in path.read_bytes().splitlines() if line.strip()]


def archived(root, directory, policy, runner, snapshot, source_hashes):
    assert policy['native_sources'] == source_hashes
    assert policy['snapshot_sha256'] == sha(snapshot)
    assert policy['archive_application'] == read(snapshot)['application']
    assert read(directory / 'ARCHIVE-PRE.json') == read(directory / 'ARCHIVE-POST.json')
    archive = read(directory / 'ARCHIVE-PRE.json')
    saved_snapshot = read(snapshot)
    assert archive == {'application': saved_snapshot['application'], 'files': len(saved_snapshot['files']),
                       'bytes': saved_snapshot['bytes'], 'manifest_sha256': hashlib.sha256(json.dumps(saved_snapshot['files'], sort_keys=True).encode()).hexdigest()}
    result = read(directory / 'RESULT.json')
    assert result['success'] and result['execution_error'] is None
    assert result['archive_preserved'] and result['staged_preserved']
    assert result['source_role'] == 'archived-candidate'
    terminal = read(directory / 'ROOT-TERMINAL.json')
    assert terminal['result_sha256'] == sha(directory / 'RESULT.json')
    if 'owner_exit' in terminal:
        assert terminal['owner_exit'] == 0 and terminal['wpt_exit'] == result['exit']
    else:
        assert terminal['terminal'] is True and terminal['exit'] == 0
    assessment = runner.assess(events(directory / 'raw.jsonl'), read(root / policy['roster']), result['exit'])
    assert assessment == read(directory / 'ASSESSMENT.json') and assessment['complete']
    assert all(sha(directory / name) == pin for name, pin in read(directory / 'STAGED-RESOURCES.json').items())
    cleanup = read(directory / 'CLEANUP.json')
    assert cleanup['owned_group_absent'] and cleanup['temporary_root_removed']
    return assessment


def verify_completed(root, binding, stage):
    expected = read(root / PACKAGE / 'PAIR-BINDING.json')
    assert set(binding) == set(expected)
    assert all(binding[key] == value for key, value in expected.items() if key != 'font_native_receipt')
    owner = load('saved_ownership', root / 'artifacts/css-registered-number-source-transition-v4/transition.py')
    for key, record in binding.items():
        if key != 'font_native_receipt':
            owner.authenticate(root / record['directory'], record['manifest_sha256'])
    font_dir = root / binding['font_publisher']['directory']
    font_stage, = read(font_dir / 'STAGES.json')['stages']
    source = root / binding['source']['directory']
    roles = read(source / 'SOURCE-ROLES.json')
    assert roles['revision'] == BASE
    source_hashes = {path: row['candidate_sha256'] for path, row in roles['roles'].items()}
    pack = root / binding['packaging']['directory']
    intended = read(pack / 'STAGES.json')['stages'][1]
    intended.pop('requires')
    intended['adopt_existing_tests'] = []
    assert stage == intended
    for path, row in roles['roles'].items():
        if row['parent_sha256'] != row['candidate_sha256']:
            assert stage['head_preimages'][path] == row['parent_sha256']
            assert stage['files'][path]['sha256'] == row['candidate_sha256']
        else:
            assert font_stage['files'][path]['sha256'] == row['candidate_sha256']
    verifier = root / binding['restoration_verifier']['directory']
    saved = load('selective_saved_restoration', verifier / 'run.py')
    policy = read(verifier / 'POLICY.json')
    saved.saved(policy)
    runtime = root / policy['runtime']
    native_owner = root / policy['owner']['directory']
    assert policy['head'] == BASE
    assert {path: row['candidate_sha256'] for path, row in read(native_owner / 'SOURCE-ROLES.json').items()} == source_hashes
    snapshot = runtime / 'ARCHIVE-SNAPSHOT.json'
    depth_dir = root / binding['depth_runtime']['directory']
    depth_policy = read(root / binding['depth_policy']['directory'] / 'POLICY.json')
    assert depth_policy['completed_runtime'] == {'directory': policy['runtime'], 'manifest_sha256': policy['runtime_manifest_sha256']}
    depth_runner = load('depth_archive_assessor', root / binding['depth_owner']['directory'] / 'run.py')
    archived(root, depth_dir, depth_policy, depth_runner, snapshot, source_hashes)
    comparison = root / binding['comparison']['directory']
    report = read(comparison / 'RESULT.json')
    assert report['comparison_passed']
    for lane, recorded in zip(read(comparison / 'INPUTS.json'), report['lanes'], strict=True):
        original = root / 'artifacts' / lane['original']
        candidate = root / 'artifacts' / lane['candidate']
        assert candidate == (runtime / 'candidate-wpt-cancellation/raw.jsonl' if lane['label'] == 'cancellation' else depth_dir / 'raw.jsonl')
        before, old_end = signatures(events(original), lane['page'], lane['count'])
        after, new_end = signatures(events(candidate), lane['page'], lane['count'])
        targets = ({'existing-child rem keyframes after root em cancellation with none', 'root-pseudo rem keyframes after root em cancellation with none'} if lane['label'] == 'cancellation' else {f'existing-child rem keyframes through {depth} fixed ancestors after root em cancellation with none' for depth in (1, 4)})
        changed, preserved = compare_lane(before, after, old_end, new_end, targets)
        assert recorded == {**lane, 'original_sha256': sha(original), 'candidate_sha256': sha(candidate), 'changed': changed, 'preserved': preserved, 'preserved_ending': old_end}
        test_path = 'testing/web-platform/tests' + lane['page']
        phase = runtime / 'candidate-wpt-cancellation' if lane['label'] == 'cancellation' else depth_dir
        assert sha(phase / 'tests' / lane['page'].lstrip('/')) == stage['files'][test_path]['sha256']
    assert sum(len(row['changed']) for row in report['lanes']) == 4
    assert sum(len(row['preserved']) for row in report['lanes']) == 8
    font_runtime = root / binding['font_runtime']['directory']
    font_owner = root / binding['font_archive_owner']['directory']
    font_policy = read(font_owner / 'POLICY-candidate.json')
    assert font_policy['completed_runtime'] == depth_policy['completed_runtime']
    font_runner = load('font_archive_assessor', font_owner / 'run.py')
    assessment = archived(root, font_runtime, font_policy, font_runner, snapshot, source_hashes)
    assert assessment['all_14_pass']
    audit = read(font_runtime / 'ROOT-INDEPENDENT-AUDIT.json')
    terminal = read(font_runtime / 'ROOT-AUDIT-TERMINAL.json')
    assert terminal['exit'] == 0 and terminal['audit_result_sha256'] == sha(font_runtime / 'ROOT-INDEPENDENT-AUDIT.json')
    assert audit['success'] and audit['archive_processes_absent']
    assert audit['audit_script_sha256'] == sha(root / binding['font_audit']['directory'] / 'audit.py')
    assert audit['preserved_pass_signatures'] == 14 and audit['preserved_ending_signatures'] == 1
    assert audit['owner_result_sha256'] == sha(font_runtime / 'RESULT.json')
    assert audit['owner_terminal_sha256'] == sha(font_runtime / 'ROOT-TERMINAL.json')
    old_raw = root / 'artifacts/css-keyframe-font-unit-candidate-browser-runtime-v1/candidate-wpt-font_units/raw.jsonl'
    assert sha(old_raw) == audit['original_raw_sha256']
    assert sha(font_runtime / 'raw.jsonl') == audit['current_raw_sha256']
    page, = read(root / font_policy['roster'])
    assert signatures(events(old_raw), page, 14) == signatures(events(font_runtime / 'raw.jsonl'), page, 14)
    assert sha(font_runtime / 'tests' / page.lstrip('/')) == font_stage['files']['testing/web-platform/tests' + page]['sha256']
    return {'tested_head': BASE, 'font_stage': font_stage, 'cancellation_depth_pass': 12,
            'fail_to_pass': 4, 'preserved_pass_signatures': 8, 'preserved_endings': 2,
            'font_pass_preserved': 14, 'font_endings_preserved': 1,
            'root_identity_lane_verified': False, 'startup_fix_claimed': False}


def verify(root, binding, stage):
    assert binding and binding['font_native_receipt'], 'pending signed font-unit native predecessor'
    result = verify_completed(root, binding, stage)
    record = binding['font_native_receipt']
    assert sha(root / record['path']) == record['sha256']
    receipt = read(root / record['path'])
    require_font_receipt(receipt, result['font_stage'])
    return dict(result, font_native=receipt)
