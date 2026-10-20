import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
TEST = 'testing/web-platform/tests/css/css-properties-values-api/animation-invalid-inherit-publication.html'
PROBE = ROOT / 'artifacts/css-animation-publication-reachability-v1/probe-v2.html'


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


assert sha(PROBE) == 'b79063a603b26163c2a271dc915f806db5ad75a52b008047a80e2fdbc9d845c4'
prior = json.loads((ROOT / 'artifacts/css-animation-registered-consumer-runtime-v1/INPUTS.json').read_text())
pins = prior['pins'].copy()
for name, digest in pins.items():
    assert sha(ROOT / name) == digest, name
assert sha(ROOT / TEST) == '87592fa329c56420bb90c1967cf1ee03c8171ff7d0a1bef3a95dac1acde0ff9e'
(ROOT / TEST).write_bytes(PROBE.read_bytes())
pins[TEST] = sha(PROBE)
command = ['./mach', 'wpt', '--headless', '--processes=1',
           '--log-raw=' + str(HERE / 'raw.json'), TEST]
record = {'phase': 'running', 'command': command, 'pins': pins,
          'scope': 'Static registration; literal inherit and neutral animated endpoints; direct invalid substitution, initial, valid-parent and unresolved-declaration controls; independent of fix72.'}
(HERE / 'RUN.json').write_text(json.dumps(record, indent=2) + '\n')
with (HERE / 'wpt.log').open('w') as log:
    status = subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
                            env={**os.environ, 'MOZ_SKIP_PATH_PERFORMANCE_CHECK': '1'}).returncode
raw = [json.loads(line) for line in (HERE / 'raw.json').read_text().splitlines()]
rows = [r for r in raw if r.get('action') == 'test_status']
ends = [r for r in raw if r.get('action') == 'test_end']
stable = all(sha(ROOT / name) == expected for name, expected in pins.items())
record.update(phase='done', exit=status, rows=rows, harness=ends, stable=stable)
(HERE / 'RUN.json').write_text(json.dumps(record, indent=2) + '\n')
assert stable and len(rows) == 16 and len(ends) == 1 and ends[0]['status'] == 'OK'
print(json.dumps({'exit': status, 'rows': [{k: r[k] for k in ['subtest', 'status', 'message'] if k in r} for r in rows]}, indent=2))
