import hashlib
import json
import os
from pathlib import Path
import runpy
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OLD = ROOT / 'artifacts/css-flex-measured-base-repair-20261111-v1'
tests = [arg for arg in json.loads((OLD / 'AFTER-2-COMMAND.json').read_text())
         if arg.startswith('testing/web-platform/tests/')]
tests.append('testing/web-platform/tests/css/css-flexbox/flex-shrink-wide-target-violation.html')
assert len(tests) == len(set(tests)) == 28
relative = HERE.relative_to(ROOT)
argv = ['/Users/bgrins/venvs/firefox/bin/python', './mach', 'wpt', '--headless',
        '--no-pause-after-test', '--processes=1',
        '--log-raw=' + str(relative / 'after.raw.log'),
        '--log-wptreport=' + str(relative / 'after.wptreport.json'), *tests]
for name in ['after.log', 'after.raw.log', 'after.wptreport.json', 'AFTER-COMMAND.json']:
    assert not (HERE / name).exists(), name
pins = json.loads((HERE / 'AFTER-INPUTS.json').read_text())
for name, expected in pins.items():
    assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected, name
(HERE / 'AFTER-COMMAND.json').write_text(json.dumps(argv, indent=2) + '\n')
(HERE / 'AFTER-TESTS.json').write_text(json.dumps({
    name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in tests}, indent=2) + '\n')
helper = runpy.run_path(str(ROOT / 'artifacts/css-flex-main-positioning-target-20261111-v2/process.py'))
runner = helper['Runner'](HERE)
env = dict(os.environ, MOZ_SKIP_PATH_PERFORMANCE_CHECK='1',
           MOZCONFIG=str(ROOT / 'mozconfig'), MOZ_OBJDIR=str(ROOT / 'objdir-full.noindex'),
           GIT_OPTIONAL_LOCKS='0')
record, _ = runner.run(argv, ROOT, env, 'after', timeout=1200)
(HERE / 'AFTER-EXIT.json').write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps(record))
sys.exit(record['exit'])
