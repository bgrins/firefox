import importlib.util
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
    result = base.assess(events, code, policy, checks, original=original, run_binding=run_binding)
    result['oracle_caveat'] = ('Original reftest rendering result, separately retained.' if kind == 'reftest' else
        'Completion and acquisition only; feedback values have no fixed-point or numeric equality oracle.' if kind == 'feedback' else
        'Fresh original normative roster/outcomes; existing failures are retained for exact later comparison.')
    return result
