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

page = 'animation-duration-property-only-wakeup.tentative.html'
source = (HERE / page).read_text()
dom = html5lib.parse(source, namespaceHTMLElements=False)
scripts = [node.text for node in dom.iter('script') if not node.get('src')]
assert len(scripts) == 1
assert [node.get('src') for node in dom.iter('script') if node.get('src')] == [
    '/resources/testharness.js', '/resources/testharnessreport.js']
assert source.index('for (let index = 0; index < 3; index++) await frame(win);') < source.index('Initial calibration after setup frames')
start = source.index('  if (driver) driver.currentTime = 1000;')
end = source.index('  const beforeMembership = read(context);', start)
window = source[start:end]
assert window.count('getComputedStyle(child).width') == 2
assert all(word not in window for word in ['getAnimations', 'read(context)', 'getTiming', 'getComputedTiming', 'currentTime = 750', 'currentTime = 751', 'updateTiming'])
assert source.count('effect.updateTiming({duration: 2000});') == 1
assert source.index('const afterSeek = read(context);') < source.index('const trace = JSON.stringify')
assert 'console.' not in source
predecessor = ROOT / "artifacts/css-contextual-duration-property-only-wakeup-probe-v1"
record = (ROOT / "artifacts/css-contextual-duration-progress-transport-v1/record-function.js").read_text()
call = '  await record("property-only-" + mode, trace);\n'
assert source.count(record) == 1 and source.count(call) == 1
assert source.replace(record, "").replace(call, "") == (predecessor / page).read_text()
assert source.index('const trace = JSON.stringify') < source.index(call)
program = r'''
const vm = require('vm');
let text = '';
process.stdin.on('data', part => text += part);
process.stdin.on('end', () => {
  const names=[]; const assert=b=>{if(!b)throw Error('assertion');};
  const context=vm.createContext({promise_test:(_,name)=>names.push(name),
    assert_true:assert,assert_equals:(a,b)=>assert(a===b),
    assert_approx_equals:(a,b,e)=>assert(Number.isFinite(a)&&Math.abs(a-b)<=e)});
  vm.runInContext(text,context);const verify=vm.runInContext('assertValues',context);
  const sample=(font,width)=>({width,parentFont:font,cssDuration:font/16*1000,
    duration:2000,progress:.375,time:750,state:'paused'});
  for(const [font,width] of [[16,28],[16,56],[32,56]])verify(sample(font,width),font,width,'synthetic');
  assert(16+(48-16)*.375===28);assert(32+(96-32)*.375===56);
  const negatives=[];
  const reject=(label,change)=>{const x=sample(32,56);change(x);
    try{verify(x,32,56,label);}catch(_){negatives.push(label);return;}throw Error(label);};
  reject('stale width',x=>x.width=28);reject('stale font',x=>x.parentFont=16);
  reject('stale CSS duration',x=>x.cssDuration=1000);
  reject('script duration ignored',x=>x.duration=1000);
  reject('stale effect progress',x=>x.progress=.75);
  reject('seek not restored',x=>x.time=751);reject('running animation',x=>x.state='running');
  process.stdout.write(JSON.stringify({names,numerical_positives:3,negative_controls:negatives}));
});
'''
checks = json.loads(subprocess.run(['node', '-e', program], input=scripts[0], text=True, capture_output=True, check=True).stdout)
assert checks['names'] == [
    'Literal width keyframes stay calibrated while CSS duration changes under script ownership',
    'Ordinary inherited font changes update width keyframes with script-owned duration',
    'Animated inherited font changes update width keyframes with script-owned duration']
with tempfile.TemporaryDirectory(prefix='duration-property-only-manifest-') as temporary:
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
              setup_frames_precede_initial_calibration=True)
(HERE / 'CHECK.json').write_text(json.dumps(checks, indent=2, sort_keys=True) + '\n')
(HERE / 'ROSTER.json').write_text(json.dumps({'tests': {'/css/css-animations/' + page: checks['names']}, 'callbacks':3, 'browser_executed':False}, indent=2) + '\n')
print(json.dumps(checks, indent=2))
