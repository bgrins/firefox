import importlib.util
import json
import os
import signal
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUNTIME = ROOT / 'artifacts/css-registered-number-native-runtime-v1'
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS='0', PYTHONDONTWRITEBYTECODE='1',
           MOZCONFIG=str(ROOT / 'mozconfig'), MOZ_OBJDIR=str(ROOT / 'objdir-full.noindex'),
           MOZ_HEADLESS='1', MOZ_SKIP_PATH_PERFORMANCE_CHECK='1')


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    assert len(sys.argv) == 2
    policy = json.loads((HERE / 'POLICY.json').read_bytes())
    assert policy['execution_enabled'] is True
    owned = load('final_owner', ROOT / 'artifacts/css-registered-number-source-transition-v4/transition.py')
    owned.authenticate(HERE, sys.argv[1])
    for name, pin in policy['references'].items():
        assert owned.digest((ROOT / name).read_bytes()) == pin
    guard = load('shadow_original_guard', HERE / 'guard.py')
    roles = json.loads((HERE / 'SOURCE-ROLES.json').read_bytes())
    state, env, controls, epoch, flags, verify = guard.guard(policy, owned, roles)
    before = verify()
    runner = load('move_paired_phase', HERE / 'phase.py')
    runtime = ROOT / policy['output']
    assert runtime.parent == ROOT / 'artifacts' and not runtime.exists() and not runtime.is_symlink()
    runtime.mkdir()
    state.save(runtime / 'BASELINE-PRE.json', {'snapshot': before, 'controls': policy['controls'], 'browser_build_performed': False})
    output = runtime / 'original-wpt'
    stopped = [False]
    def stop(signum, frame):
        stopped[0] = True
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, stop)
    owned_processes = {}
    error = None
    phase_result = None
    try:
        phase_result = runner.run_phase(ROOT, output, 'original', env, verify, owned_processes, lambda: stopped[0])
    except BaseException as caught:
        error = repr(caught)
    preservation_error = None
    try:
        assert owned_processes == {}, 'Owned WPT process registry not empty after cleanup'
        verify()
    except BaseException as caught:
        preservation_error = repr(caught)
    state.save(runtime / 'BASELINE-RESULT.json', {'success': error is None and preservation_error is None, 'error': error, 'preservation_error': preservation_error, 'preservation_verified': preservation_error is None, 'owned_processes': owned_processes, 'browser_build_performed': False, 'phase': phase_result, 'canonical_updated': False})
    assert error is None and preservation_error is None, (error, preservation_error)
    print('Supplemental shadow iframe baseline complete; no acceptance or canonical mutation')


if __name__ == '__main__':
    main()
