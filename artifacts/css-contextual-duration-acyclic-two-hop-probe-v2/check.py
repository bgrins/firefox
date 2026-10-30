import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WPT = ROOT / 'testing/web-platform/tests'
sys.path[:0] = [str(p) for p in (WPT / 'tools/third_party').iterdir() if p.is_dir()] + [
    str(WPT / 'tools'), str(WPT), str(ROOT / 'third_party/python/pyyaml/lib')]
import html5lib
from manifest.manifest import Manifest
from tools.lint import lint

page = 'animation-duration-acyclic-two-hop.tentative.html'
source = (HERE / page).read_text()
dom = html5lib.parse(source, namespaceHTMLElements=False)
scripts = [node.text for node in dom.iter('script') if not node.get('src')]
assert len(scripts) == 1
assert [node.get('src') for node in dom.iter('script') if node.get('src')] == [
    '/resources/testharness.js', '/resources/testharnessreport.js']
assert source.index('Middle font established before child insertion') < source.index('middle.append(child)')
start = source.index('  if (driver) driver.currentTime = 1000;')
end = source.index('  const beforeMembership = details(context);', start)
first_window = source[start:end]
assert first_window.count('getComputedStyle(child).opacity') == 2
assert all(word not in first_window for word in ['getAnimations', 'details(', 'timing(', 'getTiming', 'getComputedTiming', 'currentTime = 750', 'currentTime = 751'])
assert 'index <= 3' in first_window
assert source.index('const afterSeek = details(context);') < source.index('const trace = JSON.stringify') < source.index('After three sampled frames, before membership;')
assert 'console.' not in source and 'updateTiming(' not in source
predecessor = ROOT / "artifacts/css-contextual-duration-acyclic-two-hop-probe-v1"
record = (ROOT / "artifacts/css-contextual-duration-progress-transport-v1/record-function.js").read_text()
call = '  await record("two-hop-" + mode, trace);\n'
assert source.count(record) == 1 and source.count(call) == 1
assert source.replace(record, "").replace(call, "") == (predecessor / page).read_text()
assert source.index('const trace = JSON.stringify') < source.index(call)
program = r'''
const vm = require('vm');
let text = '';
process.stdin.on('data', part => text += part);
process.stdin.on('end', () => {
  const names = [];
  const assert = b => { if (!b) throw Error('assertion'); };
  const context = vm.createContext({promise_test: (_, name) => names.push(name),
    assert_true: assert, assert_equals: (a,b) => assert(a===b),
    assert_approx_equals: (a,b,e) => assert(Number.isFinite(a) && Math.abs(a-b)<=e)});
  vm.runInContext(text, context);
  const verify = vm.runInContext('assertValues', context);
  const initial = vm.runInContext('initial', context), final = vm.runInContext('final', context);
  function observation(expected) { return {rootFont: expected.root, middleFont: expected.middle,
    middleDuration: expected.middleDuration, childDuration: expected.childDuration,
    childOpacity: expected.opacity,
    middle: {duration: expected.middleDuration, time:750,state:'paused'},
    child: {duration: expected.childDuration,progress:expected.opacity,time:750,state:'paused'}}; }
  for (const expected of [initial, final]) verify(observation(expected), expected, 'synthetic');
  assert(initial.middle === 16 + 16 * 750 / initial.middleDuration);
  assert(final.middle === 16 + 16 * 750 / final.middleDuration);
  assert(initial.childDuration === initial.middle / 16 * 1000);
  assert(final.childDuration === final.middle / 16 * 1000);
  assert(initial.opacity === 750 / initial.childDuration);
  assert(final.opacity === 750 / final.childDuration);
  const negatives=[];
  function reject(name, mutate) { const x=observation(final); mutate(x);
    try {verify(x, final, name);} catch (_) {negatives.push(name);return;}
    throw Error('false control passed '+name); }
  reject('root driver unchanged', x=>x.rootFont=16);
  reject('middle CSS duration stale', x=>x.middleDuration=1000);
  reject('middle effect duration stale', x=>x.middle.duration=1000);
  reject('middle composed font stale', x=>x.middleFont=28);
  reject('child CSS duration stale', x=>x.childDuration=1750);
  reject('child effect duration stale', x=>x.child.duration=1750);
  reject('child progress stale', x=>x.child.progress=3/7);
  reject('child opacity stale', x=>x.childOpacity=3/7);
  reject('time shifted', x=>x.child.time=751);
  reject('animation running', x=>x.middle.state='running');
  process.stdout.write(JSON.stringify({names, numerical_positives:2, negative_controls:negatives}));
});
'''
checks = json.loads(subprocess.run(['node', '-e', program], input=scripts[0], text=True, capture_output=True, check=True).stdout)
assert checks['names'] == [
    'Literal duration changes calibrate a paused two-hop font and opacity chain',
    'Ordinary root font changes propagate through a paused two-hop duration chain',
    'Animated root font changes propagate through a paused two-hop duration chain']
with tempfile.TemporaryDirectory(prefix='duration-two-hop-manifest-') as temporary:
    scratch = Path(temporary)
    folder = scratch / 'css/css-animations'
    folder.mkdir(parents=True)
    shutil.copyfile(HERE / page, folder / page)
    shutil.copyfile(ROOT / 'artifacts/css-contextual-duration-progress-transport-v1/duration-progress-record.py', folder / 'duration-progress-record.py')
    (scratch / 'lint.ignore').write_text('')
    paths = ['css/css-animations/' + page, 'css/css-animations/duration-progress-record.py']
    manifest = Manifest(str(scratch), '/')
    manifest.update([(path, None, True) for path in paths], parallel=False)
    actual = json.loads(json.dumps(manifest.to_json()))
    assert set(actual['items']['testharness']['css']['css-animations']) == {page}
    (HERE / 'SUBSET-MANIFEST.json').write_text(json.dumps(actual, indent=2, sort_keys=True) + '\n')
    cwd = os.getcwd()
    try:
        os.chdir(scratch)
        assert lint.lint(str(scratch), paths, 'normal', jobs=1) == 0
    finally:
        os.chdir(cwd)
assert not scratch.exists()
checks.update(lint_errors=0, scratch_removed=True, browser_executed=False, callback_bodies_executed=False,
              synthetic_assertion_checks_only=True, first_child_read_precedes_effect_and_membership=True,
              passive_child_only_samples=4, first_sample_is_not_asserted_to_converge=True,
              staged_initial_middle_before_child=True)
(HERE / 'CHECK.json').write_text(json.dumps(checks, indent=2, sort_keys=True) + '\n')
(HERE / 'ROSTER.json').write_text(json.dumps({'tests': {'/css/css-animations/' + page: checks['names']}, 'callbacks':3, 'browser_executed':False}, indent=2) + '\n')
print(json.dumps(checks, indent=2))
