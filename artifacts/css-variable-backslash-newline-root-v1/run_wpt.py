import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
previous = json.loads((REPO / 'artifacts/css-variable-escaped-whitespace-root-v1/candidate-wpt-v1/RUN.json').read_text())
test = 'testing/web-platform/tests/css/css-variables/trailing-backslash-newline.html'
tests = [arg for arg in previous['command'] if arg.startswith('testing/')] + [test]
if len(tests) != 24 or len(set(tests)) != 24:
    raise RuntimeError('Unexpected test roster')
paths = list(json.loads((REPO / 'artifacts/css-attr-leading-whitespace-root-v1/BUILD-SOURCE-PINS.json').read_text())['pins'])
paths += tests
paths += ['objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox',
          'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/XUL']

def pins():
    result = {}
    for name in sorted(set(paths)):
        with (REPO / name).open('rb') as stream:
            result[name] = hashlib.file_digest(stream, 'sha256').hexdigest()
    return result

before = pins()
out = ROOT / 'candidate-wpt-v1'
out.mkdir(exist_ok=False)
command = ['./mach', 'wpt', '--headless', '--processes=1',
           '--setpref=layout.css.properties-and-values.enabled=true',
           '--log-raw=' + str(out / 'raw.json'), *tests]
record = {'phase': 'running', 'command': command, 'before': before, 'build_exit': 0}
(out / 'RUN.json').write_text(json.dumps(record, indent=2) + '\n')
with (out / 'wpt.log').open('w') as log:
    process = subprocess.run(command, cwd=REPO, stdout=log, stderr=subprocess.STDOUT,
                             env=dict(os.environ, MOZ_SKIP_PATH_PERFORMANCE_CHECK='1'))
raw = [json.loads(line) for line in (out / 'raw.json').read_text().splitlines()]
rows = [row for row in raw if row.get('action') == 'test_status']
ends = [row for row in raw if row.get('action') == 'test_end']
after = pins()
key = lambda row: (row['test'], row['subtest'])
old = {key(row): (row['status'], row.get('message')) for row in previous['rows']}
current = {key(row): (row['status'], row.get('message')) for row in rows}
changed = [{'identity': k, 'before': v, 'after': current.get(k)} for k, v in old.items() if current.get(k) != v]
new = [row for row in rows if key(row) not in old]
ok = (process.returncode == 0 and len(rows) == len(current) == 467 and len(ends) == 24
      and all(row['status'] == 'OK' for row in ends) and before == after and not changed
      and len(new) == 32 and all(row['status'] == 'PASS' for row in new)
      and sum(row.get('action') == 'suite_end' for row in raw) == 1)
record.update(phase='done', complete=ok, exit=process.returncode, after=after,
              stable=before == after, rows=rows, harness=ends, changed=changed,
              added=new, baseline_scope='435 prior candidate outcomes unchanged;32 backslash-newline cases with separately retained pre-fix baseline16FAIL16PASS.')
(out / 'RUN.json').write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps({'complete': ok, 'rows': len(rows), 'harnesses': len(ends),
                  'changes': changed, 'added': len(new), 'exit': process.returncode}))
if not ok:
    raise RuntimeError('WPT matrix did not meet its gates')
