import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
inputs = json.loads((HERE / 'INPUTS.json').read_text())
roster = json.loads((HERE / 'ROSTER.json').read_text())
page, names = next(iter(roster.items()))
assert len(roster) == 1 and len(names) == len(set(names)) == 3
for record in inputs['resources'].values():
    assert sha(ROOT / record['path']) == record['sha256']
for record in json.loads((HERE / 'REFERENCES.json').read_text()):
    assert sha(ROOT / record['path']) == record['sha256']
source = json.loads((HERE / 'SOURCE.json').read_text())
for name, record in source['sources'].items():
    body = subprocess.check_output(['git', 'show', source['revision'] + ':' + name], cwd=ROOT)
    assert hashlib.sha256(body).hexdigest() == record['sha256']
    lines = body.decode().splitlines()
    for excerpt in record['excerpts']:
        assert '\n'.join(lines[excerpt['start'] - 1:excerpt['end']]) == excerpt['text']
html = (HERE / 'tests' / page.lstrip('/')).read_text()
scripts = re.findall(r'<script>([\s\S]*?)</script>', html)
assert len(scripts) == 1
js = scripts[0]
first = js.index('    const first = win.getComputedStyle(target).fontSize;')
settled = js.index('    const settled = win.getComputedStyle(target).fontSize;')
between = js[first:settled]
assert between.count('getComputedStyle') == 1 and 'getAnimations' not in between
assert between.count('await nextFrame(win);') == 2
assert js.index('    const rootSize =') > settled
assert js.index('    const rootAnimations =') > settled
assert js.index('window.rootFontInitialAnimationObservations.push') < js.index('    assert_equals(')
with tempfile.TemporaryDirectory(prefix='initial-root-font-wpt-') as temp:
    scratch = Path(temp)
    body = scratch / 'test.js'
    body.write_text(js)
    parsed = subprocess.run(['node', '--check', str(body)], capture_output=True, text=True)
    assert parsed.returncode == 0, parsed.stderr
    vm = '''const fs = require("fs"), vm = require("vm");
const names = [];
vm.runInNewContext(fs.readFileSync(process.argv[1], "utf8"), {
  window: {}, promise_test: (callback, name) => {
    if (typeof callback !== "function") throw new Error("missing callback");
    names.push(name);
  },
});
process.stdout.write(JSON.stringify(names));'''
    registered = subprocess.run(['node', '-e', vm, str(body)], capture_output=True, text=True)
    assert registered.returncode == 0, registered.stderr
    assert json.loads(registered.stdout) == names
    removed = str(scratch)
assert not Path(removed).exists()
tested = ['check_source.py', 'INPUTS.json', 'ROSTER.json', 'SOURCE.json', 'REFERENCES.json']
print(json.dumps({'syntax': True, 'inert_callbacks': names, 'callback_bodies_executed': False,
                  'sample_order_source_check': True, 'native_final_branch_observed': False,
                  'browser_run': False, 'wpt_lint_manifest': False,
                  'scratch': removed, 'scratch_removed': True,
                  'tested_inputs': {name: sha(HERE / name) for name in tested}}, indent=2))
