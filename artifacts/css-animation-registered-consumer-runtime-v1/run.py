import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
PROPOSAL = ROOT / 'artifacts/css-animation-registered-consumer-calibration-v1'
TEST = 'testing/web-platform/tests/css/css-properties-values-api/at-property-animation.html'
TARGET = 'Registered properties referencing animated properties update correctly.'


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2) + '\n')


assert sha(PROPOSAL / 'FILES.json') == '532c6dc4b3323457f05b338973b27e6e7f9e8ade9f45a938904e02c9f03bb5dc'
for name, expected in json.loads((PROPOSAL / 'FILES.json').read_text()).items():
    assert sha(PROPOSAL / name) == expected, name
prior = json.loads((ROOT / 'artifacts/css-registered-token-boundary-fix-v2/RUN.json').read_text())
assert prior['phase'] == 'done' and prior['complete'] and prior['stable']
pins = prior['pins_after'].copy()
for name, expected in pins.items():
    assert sha(ROOT / name) == expected, name
for name in [
    'testing/web-platform/tests/css/css-properties-values-api/resources/utils.js',
    'testing/web-platform/meta/css/css-properties-values-api/at-property-animation.html.ini',
    'testing/web-platform/meta/css/__dir__.ini',
    'servo/components/style/properties_and_values/rule.rs',
]:
    pins[name] = sha(ROOT / name)
original = (PROPOSAL / 'original.html').read_bytes()
assert (ROOT / TEST).read_bytes() == original
save('INPUTS.json', {'pins': pins, 'proposal_manifest': sha(PROPOSAL / 'FILES.json')})
records = []
try:
    for variant in ['original', 'calibration-only', 'candidate']:
        output = HERE / variant
        output.mkdir()
        snapshot = PROPOSAL / (variant + '.html')
        (ROOT / TEST).write_bytes(snapshot.read_bytes())
        command = ['./mach', 'wpt', '--headless', '--processes=1',
                   '--log-raw=' + str(output / 'raw.json'), TEST]
        record = {'variant': variant, 'phase': 'running', 'command': command,
                  'test_sha256': sha(snapshot)}
        save(variant + '/RUN.json', record)
        with (output / 'wpt.log').open('w') as log:
            result = subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
                                    env={**os.environ, 'MOZ_SKIP_PATH_PERFORMANCE_CHECK': '1'})
        raw = [json.loads(line) for line in (output / 'raw.json').read_text().splitlines()]
        rows = [r for r in raw if r.get('action') == 'test_status']
        ends = [r for r in raw if r.get('action') == 'test_end']
        target = [r for r in rows if r['subtest'] == TARGET]
        stable = all(sha(ROOT / name) == expected for name, expected in pins.items())
        record.update(phase='done', exit=result.returncode, rows=rows, harness=ends,
                      target=target, stable=stable, test_stable=sha(ROOT / TEST) == sha(snapshot))
        save(variant + '/RUN.json', record)
        records.append(record)
        assert stable and record['test_stable']
        assert len(target) == 1 and len(ends) == 1 and ends[0]['status'] == 'OK'
        print(json.dumps({'variant': variant, 'exit': result.returncode,
                          'target': target, 'nonpasses': [r for r in rows if r['status'] != 'PASS']}), flush=True)
finally:
    (ROOT / TEST).write_bytes(original)
    save('RUN.json', {'phase': 'done', 'records': records, 'original_restored': (ROOT / TEST).read_bytes() == original})
