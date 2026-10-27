import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WPT = ROOT / 'testing/web-platform/tests'
SOURCE = ROOT / 'artifacts/css-keyframe-css-duration-reactivation-repair-v1/css-duration-reactivation.html'
WORKER = ROOT / 'artifacts/css-round-parse-negative-zero-repair-v2/check.py'
PYTHON = WPT / '_venv3/bin/python3'
RELATIVE = 'css/css-animations/css-duration-reactivation.html'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
expected = '9ce483fa48f486af789ed436b73507103dde9364a8209b43a58cbb1d94a15d35'
assert sha(SOURCE) == expected
version = subprocess.run([str(PYTHON), '--version'], text=True, capture_output=True, check=True)
(HERE / 'python-version.log').write_text(version.stdout + version.stderr)
pins = {str(p.relative_to(ROOT)): sha(p) for p in [SOURCE, WORKER, WPT/'.gitignore', WPT/'lint.ignore']}
pins['resolved_python'] = {'path': str(PYTHON.resolve()), 'sha256': sha(PYTHON.resolve())}
wrapper = r"""import hashlib,json,pathlib,runpy,sys
worker, repository, relative, output, root = sys.argv[1:]
sys.argv = [worker, '--lint-worker', repository, relative]
try:
    runpy.run_path(worker, run_name='__main__')
finally:
    pins = {}
    for module in list(sys.modules.values()):
        value = getattr(module, '__file__', None)
        if not value:
            continue
        path = pathlib.Path(value).resolve()
        if path.is_file() and path.is_relative_to(root):
            pins[str(path.relative_to(root))] = hashlib.sha256(path.read_bytes()).hexdigest()
    pathlib.Path(output).write_text(json.dumps(pins, indent=2, sort_keys=True) + '\n')
"""
with tempfile.TemporaryDirectory(prefix='css-duration-wpt-lint-', dir='/private/tmp') as temporary:
    scratch = Path(temporary)
    init = subprocess.run(['git', 'init', '-q'], cwd=scratch, text=True, capture_output=True)
    (HERE/'git-init.log').write_text(init.stdout+init.stderr)
    assert init.returncode == 0
    for name in ['.gitignore', 'lint.ignore']:
        (scratch/name).write_bytes((WPT/name).read_bytes())
    fixture = scratch/RELATIVE
    fixture.parent.mkdir(parents=True)
    fixture.write_bytes(SOURCE.read_bytes())
    command = [str(PYTHON), '-B', '-I', '-c', wrapper, str(WORKER), str(scratch), RELATIVE,
               str(HERE/'LOADED-SOURCE-PINS.json'), str(ROOT)]
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', GIT_OPTIONAL_LOCKS='0')
    result = subprocess.run(command, cwd=scratch, env=env, text=True, capture_output=True, timeout=60)
    (HERE/'lint.stdout').write_text(result.stdout)
    (HERE/'lint.stderr').write_text(result.stderr)
    assert sha(fixture) == expected and sha(SOURCE) == expected
    for name, digest in pins.items():
        if name != 'resolved_python':
            assert sha(ROOT/name) == digest
    for name, digest in json.loads((HERE/'LOADED-SOURCE-PINS.json').read_text()).items():
        assert sha(ROOT/name) == digest
    execution = {'argv': command, 'cwd': str(scratch), 'exit': result.returncode,
                 'logical_path': RELATIVE, 'python_version': version.stdout.strip(),
                 'fixture_sha256': expected, 'bytecode_disabled': True, 'jobs': 1}
    (HERE/'EXECUTION.json').write_text(json.dumps(execution, indent=2)+'\n')
assert not scratch.exists()
(HERE/'SOURCE-PINS.json').write_text(json.dumps(pins, indent=2)+'\n')
(HERE/'CHECK.json').write_text(json.dumps({'status': 'DURATION_WPT_LINT_PASS' if result.returncode == 0 else 'DURATION_WPT_LINT_FINDINGS',
    'wpt_lint_exit': result.returncode, 'stdout_empty': result.stdout == '', 'stderr_empty': result.stderr == '',
    'fixture_unchanged': True, 'logical_path': RELATIVE, 'scratch_removed': True,
    'live_fixture_written': False, 'native_build': False, 'browser_executed': False}, indent=2)+'\n')
print(json.dumps({'exit': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr, 'scratch_removed': True}))
