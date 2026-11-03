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
    assert binding is not None and set(binding) == {'review', 'audit_owner', 'audit_terminal'}
    assert all(binding.values()), 'pending actual outcome/restoration'
    template = root / 'artifacts/css-explicit-taint-typed-reparse-outcome-review-v2'
    review = load('typed_reparse_saved_outcome', template / 'review.py')
    expected = read(template / 'BINDINGS.json')
    actual = binding['review']
    expected.update(execution_enabled=True, candidate=actual['candidate'], audit=actual['audit'], audit_report=actual['audit_report'])
    assert actual == expected
    assert actual['audit'] == actual['candidate'] and actual['audit_report'] == 'ROOT-LIVE-RESTORATION.json'
    fixture = review.authenticated(actual['source'])
    source = read(fixture / 'SOURCE.json')
    role = 'servo/components/style/custom_properties.rs'
    test = source['test']['target']
    assert stage == {'stage': 'reparse', 'files': {role: source['roles'][role]['candidate'],
                     test: {'path': source['test']['source'], 'sha256': source['test']['sha256']}},
                     'head_preimages': {role: source['roles'][role]['base']['sha256']},
                     'adopt_existing_tests': [], 'create_tests': [test]}
    outcome = review.review(actual)
    assert outcome['complete_authenticated_observations'] and outcome['comparison_passed']
    runtime = root / actual['candidate']['directory']
    audit_owner = review.authenticated(binding['audit_owner'])
    assert (audit_owner / 'audit.py').read_bytes() == (root / 'artifacts/css-explicit-taint-typed-reparse-root-audit-v2/audit.py').read_bytes()
    terminal_path = root / binding['audit_terminal']['path']
    assert sha(terminal_path) == binding['audit_terminal']['sha256']
    terminal = read(terminal_path)
    live = read(runtime / 'ROOT-LIVE-RESTORATION.json')
    assert terminal['terminal'] and terminal['exit'] == 0
    assert terminal['report_sha256'] == sha(runtime / 'ROOT-LIVE-RESTORATION.json')
    assert live['audit_script_sha256'] == sha(audit_owner / 'audit.py')
    assert live['backup_removed'] and not live['retained_backup_inventory_verified']
    assert live['snapshot'] == read(runtime / 'POST.json')
    assert live['owner_terminal'] == read(runtime / 'ROOT-OWNER-TERMINAL.json')
    launch = read(root / actual['launch']['path'])
    groups = [read(runtime / entry['path'])['pgid'] for entry in live['process_records']]
    assert sorted(groups + [launch['pgid']]) == sorted(live['independently_absent_process_groups'])
    restored = read(runtime / 'RESTORATION.json')
    assert not restored['errors'] and not restored['owned_processes']
    assert restored['sources'][role]['sha256'] == stage['head_preimages'][role]
    cleanup = read(runtime / 'BACKUP-CLEANUP.json')
    assert cleanup['removed'] and cleanup['verified_original_restoration'] and not cleanup['retained_after_failure']
    return {'pair_head': source['head'], 'target_original_PASS': 3, 'target_original_FAIL': 1,
            'target_candidate_PASS': 4, 'preserved_control_callbacks': 75,
            'preserved_endings': 6, 'full_baseline_signatures_preserved': True,
            'root_live_restoration_verified': True, 'native_publication_performed': False}
