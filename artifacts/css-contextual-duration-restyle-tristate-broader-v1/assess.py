import copy
import importlib.util
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
path = ROOT / "artifacts/css-minmax-relative-infinity-broader-browser-v5/assess.py"
spec = importlib.util.spec_from_file_location("executed_strict_assessor", path)
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
signature = base.signature
bound_run_info = base.bound_run_info


def assess(events, code, policy, checks, original=None, run_binding=None):
    kind = policy['phase_kind']
    if kind == 'reftest':
        assert len(policy['tests']) == 1 and set(policy['tests'].values()) == {'reftest'}
        assert policy['expected_subtest_count'] == 0 and policy['expected_subtests'] == {next(iter(policy['tests'])):[]}
    else:
        assert set(policy['tests'].values()) == {'testharness'}
    if kind == 'reftest' and original is not None:
        result = base.assess(events, code, policy, checks, run_binding=run_binding)
        try:
            projected_events = copy.deepcopy(events)
            endings = [event for event in projected_events if event.get('action') == 'test_end']
            assert len(endings) == 1
            endings[0]['message'] = normalized_reftest_message(endings[0])
            projected_original = copy.deepcopy(original)
            assert len(projected_original['regression_signature']) == 1 and len(projected_original['ends']) == 1
            original_end = projected_original['ends'][0]
            normalized = normalized_reftest_message(original_end)
            assert projected_original['regression_signature'][0] == base.signature(original_end)
            projected_original['regression_signature'][0]['message'] = normalized
            compared = base.assess(projected_events, code, policy, checks, original=projected_original, run_binding=run_binding)
            assert compared['errors'] == result['errors']
            result['comparison_errors'] = compared['comparison_errors']
            result['comparison_gate_passed'] = compared['comparison_gate_passed']
        except (AssertionError, KeyError, TypeError, ValueError) as error:
            result['comparison_errors'] = ['Invalid exact successful reftest server-port diagnostic: ' + repr(error)]
            result['comparison_gate_passed'] = False
    else:
        result = base.assess(events, code, policy, checks, original=original, run_binding=run_binding)
    result['oracle_caveat'] = ('Original reftest rendering result, separately retained.' if kind == 'reftest' else
        'Completion and acquisition only; feedback values have no fixed-point or numeric equality oracle.' if kind == 'feedback' else
        'Fresh original normative roster/outcomes; existing failures are retained for exact later comparison.')
    return result


def normalized_reftest_message(event):
    page = '/css/css-animations/animation-duration-infinite.html'
    reference = '/css/css-animations/animation-duration-infinite-ref.html'
    assert event['action'] == 'test_end' and event['test'] == page and event['status'] == 'PASS'
    assert event.get('expected', 'PASS') == 'PASS'
    pattern = r'Testing http://web-platform\.test:([0-9]{1,5})' + re.escape(page) + r' == http://web-platform\.test:\1' + re.escape(reference) + r'\n'
    match = re.fullmatch(pattern, event['message'])
    assert match is not None and 1 <= int(match[1]) <= 65535
    port = match[1]
    return event['message'].replace('web-platform.test:' + port + '/', 'web-platform.test:<port>/')
