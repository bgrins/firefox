import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser()
parser.add_argument('--package', type=Path, default=Path(__file__).resolve().parent)
HERE = parser.parse_args().package.resolve()
assert HERE.parent == ROOT / 'artifacts'
config = json.loads((HERE / 'DELTA.json').read_text())
previous = ROOT / config['predecessor']
assert hashlib.sha256((previous / 'FILES.json').read_bytes()).hexdigest() == config['predecessor_manifest_sha256']
for name, value in json.loads((previous / 'FILES.json').read_text()).items():
    expected = value['sha256'] if isinstance(value, dict) else value
    assert hashlib.sha256((previous / name).read_bytes()).hexdigest() == expected, name
inputs = json.loads((HERE / 'INPUTS.json').read_text())
for entry in inputs['resources'].values():
    assert hashlib.sha256((ROOT / entry['path']).read_bytes()).hexdigest() == entry['sha256']
page = config['page']
source = (HERE / page).read_text()
assert source.count(config['addition']) == 1
assert source.replace(config['addition'], '') == (previous / page).read_text()
assert source.index(config['addition']) == source.index(config['record_call']) + len(config['record_call'])
assert (HERE / 'ROSTER.json').read_bytes() == (previous / 'ROSTER.json').read_bytes()
WPT = ROOT / 'testing/web-platform/tests'
sys.path[:0] = [str(p) for p in (WPT / 'tools/third_party').iterdir() if p.is_dir()] + [
    str(WPT / 'tools'), str(WPT), str(ROOT / 'third_party/python/pyyaml/lib')]
import html5lib
from manifest.manifest import Manifest
from tools.lint import lint

dom = html5lib.parse(source, namespaceHTMLElements=False)
scripts = [node.text for node in dom.iter('script') if not node.get('src')]
assert len(scripts) == 1
program = r'''
const vm = require('vm');
let text = '';
process.stdin.on('data', part => text += part);
process.stdin.on('end', () => {
  const input = JSON.parse(text), names = [];
  const context = vm.createContext({promise_test: (_, name) => names.push(name),
    assert_approx_equals: (a,b,e) => {
      if (!Number.isFinite(a) || Math.abs(a-b)>e) throw Error('numeric assertion');
    }});
  vm.runInContext(input.script, context);
  if (vm.runInContext('final.opacity', context) !== 6/11) throw Error('oracle');
  const check = vm.runInContext('(value) => { const samples=[{opacity:value}]; const trace="synthetic";' + input.addition + '}', context);
  check(6/11); check(0.545455);
  let rejected = 0;
  for (const value of [3/7, null, NaN, Infinity, 0.54]) {
    try { check(value); } catch (_) { rejected++; continue; }
    throw Error('false control accepted');
  }
  process.stdout.write(JSON.stringify({names, assertion_positives:2, assertion_negatives:rejected}));
});
'''
result = subprocess.run(['node', '-e', program], input=json.dumps({'script': scripts[0], 'addition': config['addition']}), text=True, capture_output=True, check=True)
checks = json.loads(result.stdout)
roster = json.loads((HERE / 'ROSTER.json').read_text())
assert checks['names'] == roster['tests']['/css/css-animations/' + page]
with tempfile.TemporaryDirectory(prefix='duration-first-read-manifest-') as temporary:
    scratch = Path(temporary)
    paths = []
    for relative, entry in inputs['resources'].items():
        if relative.startswith('css/css-animations/'):
            target = scratch / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / entry['path'], target)
            paths.append(relative)
    (scratch / 'lint.ignore').write_text('')
    manifest = Manifest(str(scratch), '/')
    manifest.update([(path, None, True) for path in paths], parallel=False)
    actual = json.loads(json.dumps(manifest.to_json()))
    old = json.loads((previous / 'SUBSET-MANIFEST.json').read_text())
    changed = actual['items']['testharness']['css']['css-animations'][page]
    prior = old['items']['testharness']['css']['css-animations'][page]
    assert changed[0] != prior[0] and changed[1:] == prior[1:]
    actual['items']['testharness']['css']['css-animations'][page] = prior
    assert actual == old
    actual['items']['testharness']['css']['css-animations'][page] = changed
    (HERE / 'SUBSET-MANIFEST.json').write_text(json.dumps(actual, indent=2, sort_keys=True) + '\n')
    cwd = os.getcwd()
    try:
        os.chdir(scratch)
        assert lint.lint(str(scratch), paths, 'normal', jobs=1) == 0
    finally:
        os.chdir(cwd)
assert not scratch.exists()
inputs['manifest']['sha256'] = hashlib.sha256((HERE / 'SUBSET-MANIFEST.json').read_bytes()).hexdigest()
(HERE / 'INPUTS.json').write_text(json.dumps(inputs, indent=2, sort_keys=True) + '\n')
checks.update(exact_added_assertion_only=True, collection_and_transport_unchanged=True,
              manifest_changed_only_fixture_blob=True, lint_errors=0, scratch_removed=True,
              callback_bodies_executed=False, browser_executed=False, native_acceptance=False)
(HERE / 'CHECK.json').write_text(json.dumps(checks, indent=2, sort_keys=True) + '\n')
print(json.dumps(checks, indent=2))
