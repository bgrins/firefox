import importlib.util
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
PROPOSAL = ROOT / 'artifacts/css-steps-jump-none-isolation-v1'
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS='0', MOZ_HEADLESS='1',
           MOZ_SKIP_PATH_PERFORMANCE_CHECK='1', MOZ_OBJDIR=str(ROOT / 'objdir-full.noindex'))


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read(path):
    return json.loads(path.read_text())


def save(name, value):
    with (HERE / name).open('x') as stream:
        stream.write(json.dumps(value, indent=2, sort_keys=True) + '\n')


assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
h = load('preserve', ROOT / 'artifacts/css-keyframe-commit-styles-implicit-clean-comparison-v1/compare.py')
a = load('epoch', ROOT / 'artifacts/css-keyframe-operation-descriptor-post-signing-proposal-v2/epoch.py')
assert h.sha(PROPOSAL / 'FILES.json') == '047b506d664c23091917a301f966cf341eb47cb2ea62adb35734ec599517d298'
for name, expected in read(PROPOSAL / 'FILES.json').items():
    assert h.sha(PROPOSAL / name) == expected, name
epoch = read(ROOT / 'artifacts/css-keyframe-owner-runtime-v1/CURRENT-EPOCH.json')
before = a.verify_current(h, ROOT, ENV, epoch)
save('BEFORE.json', before)
binary_record = read(ROOT / 'artifacts/css-keyframe-owner-runtime-v1/BINARIES.json')
assert binary_record['before'] == binary_record['after']
assert binary_record['after'] == read(ROOT / 'artifacts/css-keyframe-transition-green-runtime-v1/BINARIES.json')['after']
save('BINARY-BINDING.json', {'binaries': binary_record['after'], 'source_build': 'artifacts/css-keyframe-transition-green-runtime-v1', 'owner_prototype_compiled': False})
test = 'css/css-easing/steps-jump-none-constant-calc.html'
fixtures = [test, 'css/css-easing/timing-functions-syntax-valid.html', 'css/css-easing/timing-functions-syntax-computed.html', 'css/css-easing/step-timing-functions-syntax.html']
source_dir = ROOT / 'testing/web-platform/tests'
inputs = {p: h.fingerprint(source_dir, p) for p in fixtures}
assert inputs[test] is None and all(inputs[p] for p in fixtures[1:])
fixture = source_dir / test
body = (PROPOSAL / 'steps-jump-none-constant-calc.html').read_bytes()
save('INPUTS.json', {'tests': fixtures, 'preimages': inputs, 'fixture_sha256': h.sha(PROPOSAL / 'steps-jump-none-constant-calc.html')})
command = ['/Users/bgrins/venvs/firefox/bin/python', './mach', 'wpt', '--headless', '--processes=1', '--binary=' + str(ROOT / 'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox'), '--config=' + str(ROOT / 'objdir-full.noindex/_tests/web-platform/wptrunner.local.ini'), '--prefs-root=' + str(ROOT / 'testing/profiles'), '--log-raw=' + str(HERE / 'raw.json'), *fixtures]
save('COMMAND.json', {'command': command, 'started': time.time()})
process = None
try:
    with fixture.open('xb') as stream:
        stream.write(body)
    with (HERE / 'wpt.log').open('x') as stream:
        process = subprocess.Popen(command, cwd=ROOT, env=ENV, stdout=stream, stderr=subprocess.STDOUT, start_new_session=True)
        save('PROCESS.json', {'pid': process.pid, 'group': process.pid})
        result = process.wait()
    save('EXECUTION.json', {'exit': result, 'finished': time.time(), 'log_sha256': h.sha(HERE / 'wpt.log')})
finally:
    if process is not None:
        def group_exists():
            try:
                os.killpg(process.pid, 0)
                return True
            except ProcessLookupError:
                return False
        if group_exists():
            os.killpg(process.pid, signal.SIGTERM)
            deadline = time.monotonic() + 10
            while group_exists() and time.monotonic() < deadline:
                time.sleep(0.1)
            if group_exists():
                os.killpg(process.pid, signal.SIGKILL)
                time.sleep(0.2)
        assert not group_exists(), 'owned process group remains'
    assert fixture.read_bytes() == body
    fixture.unlink()
    save('CLEANUP.json', {'fixture_absent': not fixture.exists(), 'owned_process_group_absent': True})
save('PRESERVATION.json', a.verify_current(h, ROOT, ENV, epoch))
assert {p: h.fingerprint(source_dir, p) for p in fixtures} == inputs
events = [json.loads(line) for line in (HERE / 'raw.json').read_text().splitlines()]
rows = [e for e in events if e.get('action') == 'test_status']
ends = [e for e in events if e.get('action') == 'test_end']
target_rows = [e for e in rows if e['test'] == '/' + test]
save('RESULT.json', {'status': 'BASELINE_CAPTURED_PENDING_REVIEW', 'mach_exit': result, 'target_rows': target_rows, 'all_rows': rows, 'ends': ends, 'new_accepted_bugs': 0})
assert len(target_rows) == 18 and len(ends) == 4 and all(e['status'] == 'OK' for e in ends)
print(json.dumps({'target': {s: sum(r['status'] == s for r in target_rows) for s in ['PASS', 'FAIL']}, 'all_subtests': len(rows), 'harnesses': len(ends), 'mach_exit': result, 'preservation': True}), flush=True)
