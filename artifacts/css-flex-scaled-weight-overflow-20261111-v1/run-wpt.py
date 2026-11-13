import hashlib
import json
import os
from pathlib import Path
import runpy
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
phase = sys.argv[1]
assert phase in ['before', 'after']
out = HERE / phase
out.mkdir(exist_ok=False)
test = 'testing/web-platform/tests/css/css-flexbox/flex-shrink-large-finite-scaled-weights.html'
tests = [test]
old = ROOT / 'artifacts/css-flex-measured-base-repair-20261111-v2'
if phase == 'before':
    for name, expected in json.loads((old / 'AFTER-INPUTS.json').read_text()).items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected, name
else:
    tests += [a for a in json.loads((old / 'AFTER-COMMAND.json').read_text())
              if a.startswith('testing/web-platform/tests/')]
    tests.append('testing/web-platform/tests/css/css-flexbox/flex-shrink-large-value-crash.html')
assert len(tests) == len(set(tests))
paths = tests + ['layout/generic/nsFlexContainerFrame.cpp',
    'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox',
    'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/XUL',
    'objdir-full.noindex/dist/Nightly.app/Contents/Resources/application.ini']
pins = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in paths}
(out / 'INPUTS.json').write_text(json.dumps(pins, indent=2) + '\n')
argv = ['/Users/bgrins/venvs/firefox/bin/python', './mach', 'wpt', '--headless',
        '--no-pause-after-test', '--processes=1',
        '--log-raw=' + str(out / 'raw.log'),
        '--log-wptreport=' + str(out / 'wptreport.json'), *tests]
(out / 'ARGV.json').write_text(json.dumps(argv, indent=2) + '\n')
helper = runpy.run_path(str(ROOT / 'artifacts/css-flex-main-positioning-target-20261111-v2/process.py'))
runner = helper['Runner'](out)
env = dict(os.environ, MOZ_SKIP_PATH_PERFORMANCE_CHECK='1',
           MOZCONFIG=str(ROOT / 'mozconfig'), MOZ_OBJDIR=str(ROOT / 'objdir-full.noindex'),
           GIT_OPTIONAL_LOCKS='0')
record, _ = runner.run(argv, ROOT, env, 'wpt', timeout=1200)
assert all(hashlib.sha256((ROOT / n).read_bytes()).hexdigest() == h for n, h in pins.items())
(out / 'RESULT.json').write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps(record))
sys.exit(record['exit'])
