import importlib.util
import json
from pathlib import Path
import hashlib


def verify(root, inputs):
    read = lambda p: json.loads(p.read_bytes())
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    def load(name, path):
        spec = importlib.util.spec_from_file_location(name, root / path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    for name, pin in inputs['evidence_pins'].items():
        assert sha(root / name) == pin, name
    owner = root / 'artifacts/css-hypot-finite-scale-final-wpt-v2'
    policy = read(owner / 'POLICY.json')
    final = root / policy['runtime_output']
    terminal = read(final / 'ROOT-REPORTED-TERMINAL.json')
    assert terminal['root_observed_terminal'] and terminal['exit'] == 0
    assert terminal['session_id'] == 94240 and terminal['terminal_tool'] == 'f4ad48'
    assert terminal['result_sha256'] == sha(final / 'RESULT.json')
    result = read(final / 'RESULT.json')
    assert result['success'] and result['preservation_verified'] and result['lint_passed']
    assert not result['native_fix_acceptance'] and not result['canonical_updated']
    assert read(final / 'PRE.json') == read(final / 'POST.json')
    assessor = load('hypot_acceptance_assessor', str((owner / 'assess.py').relative_to(root)))
    checks = load('hypot_acceptance_checks', policy['wpt']['checks_helper'])
    original = None
    for role, phase in [('original', root / policy['baseline_runtime'] / 'original-wpt'), ('candidate', final / 'candidate-wpt')]:
        record = read(phase / 'RESULT.json')
        assert record['success'] and record['preservation_verified'] and record['execution_error'] is None
        assert read(phase / 'PRE.json') == read(phase / 'POST.json')
        cleanup = read(phase / 'CLEANUP.json')
        assert cleanup['owned_group_absent'] and cleanup['temporary_root_removed']
        replay = assessor.assess([json.loads(line) for line in (phase / 'raw.jsonl').read_text().splitlines()], record['exit'], read(phase / 'ASSESSMENT-POLICY.json'), checks, original=original, run_binding=read(phase / 'APPLICATION-METADATA.json'))
        assert json.loads(json.dumps(replay)) == read(phase / 'ASSESSMENT.json')
        assert replay['complete'] and not replay['errors'] and not replay['fixture_setup_errors']
        assert replay['observed_subtest_count'] == 227 and len(replay['regression_signature']) == 215
        assert len(replay['ends']) == 4 and all(row['status'] == 'OK' for row in replay['ends'])
        if role == 'original':
            original = replay
        else:
            assert replay['comparison_gate_passed'] and not replay['comparison_errors']
            assert replay['regression_signature'] == original['regression_signature']
            rows = [row for row in replay['rows'] if row['test'] == '/css/css-values/hypot-finite-scale.html']
            assert len(rows) == 30 and all(row['status'] == 'PASS' for row in rows)
            assert sum(row['status'] == 'PASS' for row in replay['rows']) == 215
            assert sum(row['status'] == 'FAIL' for row in replay['rows']) == 12
            assert result['phase'] == {'assessment_sha256': sha(phase / 'ASSESSMENT.json'), 'raw_sha256': sha(phase / 'raw.jsonl'), 'result_sha256': sha(phase / 'RESULT.json')}
    return {'callbacks': 227, 'new_page_pass': 30, 'targets_pass': 16, 'control_end_signatures': 215, 'accepted': False}
