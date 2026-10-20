import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
TEST = 'testing/web-platform/tests/css/css-properties-values-api/animation-invalid-inherit-publication.html'
PROBE = ROOT / 'artifacts/css-animation-invalid-publication-review-v1/proposed-final-wpt.html'


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


assert sha(PROBE) == '2e910cee4f7df43ca208fbe78d384c85e70571caec5ceb6e5e61bf748362c7ad'
fix = ROOT / 'artifacts/css-animation-invalid-publication-fix-v1'
prior = json.loads((fix / 'RUN.json').read_text())
assert prior['complete'] and prior['stable']
pins = prior['pins_after'].copy()
transfer = json.loads((fix / 'FORMAT-TRANSFER.json').read_text())
assert pins[transfer['path']] == transfer['compiled_sha256']
pins[transfer['path']] = transfer['landing_sha256']
for name, expected in pins.items():
    assert sha(ROOT / name) == expected, name
(ROOT / TEST).write_bytes(PROBE.read_bytes())
pins[TEST] = sha(PROBE)
command = ['./mach', 'wpt', '--headless', '--processes=1',
           '--log-raw=' + str(HERE / 'raw.json'), TEST]
record = {'phase': 'running', 'command': command, 'pins': pins,
          'scope': 'Six added suppression/valid-empty controls are candidate-only; original16 have paired runtime evidence.'}


def save():
    (HERE / 'RUN.json').write_text(json.dumps(record, indent=2) + '\n')


save()
with (HERE / 'wpt.log').open('w') as log:
    status = subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
                            env={**os.environ, 'MOZ_SKIP_PATH_PERFORMANCE_CHECK': '1'}).returncode
raw = [json.loads(line) for line in (HERE / 'raw.json').read_text().splitlines()]
rows = [r for r in raw if r.get('action') == 'test_status']
ends = [r for r in raw if r.get('action') == 'test_end']
stable = all(sha(ROOT / name) == expected for name, expected in pins.items())
record.update(phase='done', exit=status, rows=rows, harness=ends, stable=stable)
record['complete'] = status == 0 and stable and len(rows) == 22 and all(r['status'] == 'PASS' for r in rows) and len(ends) == 1 and ends[0]['status'] == 'OK'
save()
print(json.dumps({'complete': record['complete'], 'rows': len(rows), 'failures': [r for r in rows if r['status'] != 'PASS']}, indent=2))
assert record['complete']
