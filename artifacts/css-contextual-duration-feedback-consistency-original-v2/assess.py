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
    assert original is None
    kind = policy['phase_kind']
    if kind == 'reftest':
        assert len(policy['tests']) == 1 and set(policy['tests'].values()) == {'reftest'}
        assert policy['expected_subtest_count'] == 0 and policy['expected_subtests'] == {next(iter(policy['tests'])):[]}
    else:
        assert set(policy['tests'].values()) == {'testharness'}
    result = base.assess(events, code, policy, checks, original=None, run_binding=run_binding)
    result['oracle_caveat'] = 'Original consistency observation: fixed literal/script and acquisition controls only; no self-dependent numeric or convergence oracle. Failed calibration is retained as failure.'
    return result
