import hashlib
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parents[1] / 'artifacts/css-contextual-easing-reversible-browser-v4/assess.py'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == '06d5ad95c7df382df31182406e3d310b4fafae261e2cb01b399bfde59ab86a9a'
spec = importlib.util.spec_from_file_location('shadow_iframe_assessor', SOURCE)
implementation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(implementation)
signature = implementation.signature
bound_run_info = implementation.bound_run_info


def assess(events, code, policy, checks, original=None, run_binding=None):
    result = implementation.assess(events, code, policy, checks, original=original, run_binding=run_binding)
    targets = {(test, name) for test, names in policy['target_subtests'].items() for name in names}
    assert len(targets) == 2
    controls = [r for r in result['rows'] if (r['test'], r['subtest']) not in targets]
    if len(result['rows']) != 8 or len(result['ends']) != 1:
        result['errors'].append('supplement requires exactly eight callbacks and one ending')
    if len(controls) != 6 or any(row['status'] != 'PASS' for row in controls):
        result['errors'].append('all six supplemental preservation/reset controls must pass')
    if original is not None:
        if code != 0 or any(row['status'] != 'PASS' for row in result['rows']):
            result['comparison_errors'].append('supplemental candidate requires eight PASS and child exit0')
    result['complete'] = not result['errors']
    result['comparison_gate_passed'] = original is not None and result['complete'] and not result['comparison_errors']
    result['oracle_caveat'] = 'Separate shadow iframe supplement: fresh original observations, two targets and six strict controls; no primary98 metric changes.'
    return result
