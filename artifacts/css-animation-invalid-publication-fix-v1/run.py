import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
TEST = 'testing/web-platform/tests/css/css-properties-values-api/animation-invalid-inherit-publication.html'
CALIBRATION = 'testing/web-platform/tests/css/css-properties-values-api/at-property-animation.html'


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    return json.loads(path.read_text())


def run(command, output):
    with output.open('w') as log:
        return subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
                              env={**os.environ, 'MOZ_SKIP_PATH_PERFORMANCE_CHECK': '1'}).returncode


baseline = read(ROOT / 'artifacts/css-animation-publication-runtime-v2/RUN.json')
assert baseline['phase'] == 'done' and baseline['stable'] and len(baseline['rows']) == 16
assert sum(row['status'] == 'FAIL' for row in baseline['rows']) == 10
original = read(HERE / 'ORIGINAL-PINS.json')
pins = baseline['pins'].copy()
for name, expected in pins.items():
    if name not in original:
        assert sha(ROOT / name) == expected, name
    else:
        assert original[name] == expected
for name, expected in original.items():
    relative = Path(name).relative_to('servo/components/style')
    assert sha(HERE / 'source/original' / relative) == expected
pins[CALIBRATION] = sha(ROOT / CALIBRATION)
assert pins[CALIBRATION] == '1cf32aa93b66803d4e2ddeecb0e404916002fd69191970201bd22414e153d126'
record = {'phase': 'formatting', 'complete': False, 'baseline': str(ROOT / 'artifacts/css-animation-publication-runtime-v2/RUN.json'),
          'baseline_sha256': sha(ROOT / 'artifacts/css-animation-publication-runtime-v2/RUN.json'),
          'pins_before': pins.copy(), 'native_original': original}


def save():
    (HERE / 'RUN.json').write_text(json.dumps(record, indent=2) + '\n')


save()
command = ['./mach', 'format', '--path', *original]
status = run(command, HERE / 'format.log')
record['format'] = {'command': command, 'exit': status}
save()
assert status == 0
for name in original:
    pins[name] = sha(ROOT / name)
    output = HERE / 'source/candidate' / Path(name).relative_to('servo/components/style')
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes((ROOT / name).read_bytes())
record.update(phase='building', native_candidate={name: pins[name] for name in original})
save()
command = ['./mach', 'build', 'binaries']
status = run(command, HERE / 'build.log')
record['build'] = {'command': command, 'exit': status}
save()
assert status == 0
for name in pins:
    if name.startswith('objdir-full.noindex/dist/Nightly.app/Contents/MacOS/'):
        pins[name] = sha(ROOT / name)
assert all(sha(ROOT / name) == expected for name, expected in pins.items())
previous = read(ROOT / 'artifacts/css-registered-token-boundary-fix-v2/RUN.json')
calibration = read(ROOT / 'artifacts/css-animation-registered-consumer-runtime-v1/candidate/RUN.json')
tests = [arg for arg in previous['command'] if arg.startswith('testing/')]
tests += [TEST, CALIBRATION]
assert len(tests) == len(set(tests)) == 20
command = ['./mach', 'wpt', '--headless', '--processes=1',
           '--setpref=layout.css.properties-and-values.enabled=true',
           '--log-raw=' + str(HERE / 'raw.json'), *tests]
record.update(phase='testing', pins_after=pins.copy(), command=command)
save()
status = run(command, HERE / 'wpt.log')
raw = [json.loads(line) for line in (HERE / 'raw.json').read_text().splitlines()]
rows = [r for r in raw if r.get('action') == 'test_status']
ends = [r for r in raw if r.get('action') == 'test_end']
key = lambda r: (r['test'], r['subtest'])
before = {key(r): (r['status'], r.get('message')) for r in previous['rows'] + baseline['rows'] + calibration['rows']}
after = {key(r): (r['status'], r.get('message')) for r in rows}
changes = [{'identity': list(k), 'before': before[k], 'after': after.get(k)} for k in before if before[k] != after.get(k)]
stable = all(sha(ROOT / name) == expected for name, expected in pins.items())
record.update(phase='done', exit=status, rows=rows, harness=ends, stable=stable, changes=changes)
record['complete'] = (status == 0 and len(before) == len(after) == len(rows) == 343
                      and before.keys() == after.keys() and len(changes) == 10
                      and all(change['before'][0] == 'FAIL' and change['after'][0] == 'PASS' for change in changes)
                      and len(ends) == 20 and all(r['status'] == 'OK' for r in ends)
                      and sum(r.get('action') == 'suite_end' for r in raw) == 1 and stable)
save()
print(json.dumps({'complete': record['complete'], 'exit': status, 'changes': changes,
                  'nonpasses': [{k: r[k] for k in ['test', 'subtest', 'status', 'message'] if k in r} for r in rows if r['status'] != 'PASS']}, indent=2))
assert record['complete']
