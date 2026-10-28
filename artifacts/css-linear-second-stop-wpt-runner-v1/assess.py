from collections import Counter


def signature(event):
    return {'kind': event['action'], 'test': event['test'],
            'subtest': event.get('subtest'), 'status': event['status'],
            'expected': event.get('expected', event['status']),
            'expected_field_present': 'expected' in event,
            'known_intermittent': event.get('known_intermittent', []),
            'intermittent_field_present': 'known_intermittent' in event,
            'message': event.get('message'), 'message_field_present': 'message' in event}


def bound_run_info(run_info, binding):
    return (isinstance(run_info, dict) and isinstance(binding, dict)
            and len(binding.get('sha256', '')) == 64
            and binding.get('path') and binding.get('resolved')
            and binding.get('browser_build_id')
            and len(binding.get('revision', '')) == 40
            and run_info.get('browser_build_id') == binding['browser_build_id']
            and run_info.get('revision') == binding['revision'])


def assess(events, code, policy, checks, original=None, run_binding=None):
    phase, tests = policy['phase'], policy['tests']
    target = next(iter(policy['target_subtests']))
    crashing = phase == 'original-crash-1'
    rows = [e for e in events if e.get('action') == 'test_status']
    starts = [e for e in events if e.get('action') == 'test_start']
    ends = [e for e in events if e.get('action') == 'test_end']
    suites = [e for e in events if e.get('action') == 'suite_start']
    crashes = [e for e in events if e.get('action') == 'crash']
    errors = []
    config = {'expected_subtests': dict.fromkeys(tests, []), 'reftests': []}
    if not checks.lifecycle(events, config):
        errors.append('invalid ordered lifecycle')
    if Counter(e.get('test') for e in starts) != Counter(tests.keys()) or Counter(e.get('test') for e in ends) != Counter(tests.keys()):
        errors.append('selected starts/endings differ')
    identities = [(r.get('test'), r.get('subtest')) for r in rows]
    if len(identities) != len(set(identities)):
        errors.append('duplicate subtest')
    if any(r.get('test') not in tests or not isinstance(r.get('subtest'), str) or r.get('status') not in ('PASS', 'FAIL') for r in rows):
        errors.append('invalid subtest')
    expected = dict(policy['regression_subtests'], **policy['calibration_subtests'], **policy['target_subtests'])
    if crashing:
        if tests != {target: 'testharness'} or len(ends) != 1 or ends[0].get('status') != 'CRASH':
            errors.append('only exact target CRASH is admitted')
        prefix = policy['target_subtests'][target][:len(rows)]
        if len(rows) > 3 or [r.get('subtest') for r in rows] != prefix or any(r.get('status') != 'PASS' for r in rows):
            errors.append('unexpected partial pre-trigger results')
        if len(crashes) != 1 or crashes[0].get('test') != target or not crashes[0].get('process') or not crashes[0].get('minidump_path') or not (crashes[0].get('signature') or crashes[0].get('stackwalk_stdout')):
            errors.append('missing exact target process/minidump crash evidence')
        elif len(starts) == len(ends) == 1:
            if not events.index(starts[0]) < events.index(crashes[0]) < events.index(ends[0]):
                errors.append('crash outside active target interval')
            browser_pid = ends[0].get('extra', {}).get('browser_pid')
            if browser_pid is not None and str(browser_pid) != str(crashes[0]['process']):
                errors.append('crash process differs from target browser')
    else:
        for name in tests:
            if Counter(r.get('subtest') for r in rows if r.get('test') == name) != Counter(expected[name]):
                errors.append('subtest roster differs: ' + name)
        if any(e.get('status') != 'OK' for e in ends):
            errors.append('non-OK test ending')
        required_pass = set(policy['calibration_subtests'])
        if phase == 'candidate-1':
            required_pass.add(target)
        if any(r['status'] != 'PASS' for r in rows if r.get('test') in required_pass):
            errors.append('target or feature calibration failure')
    run_info = suites[0].get('run_info') if len(suites) == 1 else None
    if not isinstance(run_info, dict) or not {'os', 'debug'} <= set(run_info):
        errors.append('missing platform run_info')
    if not bound_run_info(run_info, run_binding):
        errors.append('unbound run_info BuildID/revision')
    faults = checks.infrastructure_faults(events)
    unexplained = [e for e in faults if not (crashing and e.get('action') == 'crash' and e.get('test') == target)]
    if unexplained:
        errors.append('unexplained infrastructure faults')
    if not checks.exit_matches_results(code, rows + ends):
        errors.append('exit/outcome mismatch')
    regression = [signature(e) for e in rows + ends if e.get('test') != target]
    regression.sort(key=lambda e: (e['test'], e['kind'], e['subtest'] or ''))
    comparison_errors = []
    if phase == 'candidate-1':
        if not original or set(original) != {'baseline', 'crash'}:
            comparison_errors.append('missing paired original baseline/crash evidence')
        else:
            baseline, crash = original['baseline'], original['crash']
            if not baseline.get('complete') or not baseline.get('phase_gate_passed') or not crash.get('phase_gate_passed') or crash.get('complete'):
                comparison_errors.append('original phase gates not satisfied')
            if regression != baseline.get('regression_signature'):
                comparison_errors.append('regression/calibration signatures changed')
            for observed in (baseline, crash):
                if not bound_run_info(observed.get('run_info'), observed.get('run_binding')):
                    comparison_errors.append('unbound original run metadata')
                if observed.get('run_binding', {}).get('revision') != (run_binding or {}).get('revision'):
                    comparison_errors.append('original revision changed')
                stable = lambda x: {k: v for k, v in (x or {}).items() if k != 'browser_build_id'}
                if stable(observed.get('run_info')) != stable(run_info):
                    comparison_errors.append('run_info changed beyond BuildID')
    phase_passed = not errors and not comparison_errors
    return {'complete': not crashing and not errors, 'phase_gate_passed': phase_passed,
            'errors': errors, 'comparison_errors': comparison_errors,
            'comparison_gate_passed': phase == 'candidate-1' and phase_passed,
            'run_info': run_info, 'run_binding': run_binding, 'rows': rows,
            'starts': starts, 'ends': ends, 'crashes': crashes,
            'observed_subtest_count': len(rows), 'infrastructure_faults': faults,
            'unexplained_infrastructure_faults': unexplained,
            'regression_signature': regression,
            'original_crash_is_not_complete_test_execution': crashing}
