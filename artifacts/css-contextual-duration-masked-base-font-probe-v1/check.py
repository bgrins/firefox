import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import shutil
import tempfile
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WPT = ROOT / 'testing/web-platform/tests'
sys.path[:0] = [str(p) for p in (WPT / 'tools/third_party').iterdir() if p.is_dir()] + [
    str(WPT / 'tools'), str(WPT), str(ROOT / 'third_party/python/pyyaml/lib')]
import html5lib
from manifest.manifest import Manifest
from tools.lint import lint

page = 'css/css-animations/animation-duration-masked-base-font-change.tentative.html'
handler = 'css/css-animations/duration-masked-base-record.py'
source = (HERE / 'tests' / page).read_text()
dom = html5lib.parse(source, namespaceHTMLElements=False)
scripts = [node.text for node in dom.iter('script') if not node.get('src')]
assert len(scripts) == 1
urls = [node.get('src') for node in dom.iter('script') if node.get('src')]
assert urls == ['/resources/testharness.js', '/resources/testharnessreport.js']
for url in urls:
    assert (HERE / 'tests' / url.lstrip('/')).is_file()
window = source[source.index('  target.style.fontSize = "32px";'):source.index('  const beforeMembership = details(context);')]
assert all(word not in window for word in ('getAnimations', 'timing(', 'details(', 'getTiming', 'getComputedTiming'))
assert window.count('getComputedStyle') == 1 and 'index <= 3' in window
assert source.index('await record({contextual, literal})') < source.index('assertTrajectory(literal,') < source.index('assertTrajectory(contextual,')
assert 'from { font-size: 32px; } to { font-size: 32px; }' in source
assert 'animation-duration: 2s, calc(1em / 16px * 1s)' in source
assert 'if (mode === "literal") target.style.animationDuration = "2s, 2s";' in source
assert 'animation.updateTiming' not in source and 'setKeyframes' not in source
program = r'''
const vm = require('vm');
let input = '';
process.stdin.on('data', x => input += x);
process.stdin.on('end', () => {
  const names = [];
  const ok = x => { if (!x) throw Error('assertion'); };
  const c = vm.createContext({promise_test: (_, name) => names.push(name), assert_true: ok,
    assert_equals: (a,b) => ok(a===b),
    assert_approx_equals: (a,b,e) => ok(Number.isFinite(a)&&Math.abs(a-b)<=e)});
  vm.runInContext(input, c);
  const check = vm.runInContext('assertTrajectory', c);
  function snapshot(duration, opacity) {
    return {font:32,opacity,cssDuration:'2s, 2s',timings:[
      {duration:2000,progress:.375,time:750,state:'paused'},
      {duration,progress:opacity,time:750,state:'paused'}]};
  }
  function obs(mode) {
    return {kind:'acyclic',mode,initial:snapshot(1000,.75),
      samples:['first-read','passive-frame-1','passive-frame-2','passive-frame-3'].map(phase=>({phase,value:.375})),
      beforeMembership:snapshot(2000,.375),afterMembership:snapshot(2000,.375),
      membership:[{animation:true,effect:true},{animation:true,effect:true}]};
  }
  const contextual=obs('contextual'),literal=obs('literal');
  check(contextual,'positive');check(literal,'positive');
  const negatives=[];
  for (const [name, mutate] of [
    ['initial uses composed timing', x=>{x.initial.opacity=.375;x.initial.timings[1].duration=2000;x.initial.timings[1].progress=.375;}],
    ['stale first despite later repair', x=>x.samples[0].value=.75],
    ['stale passive sample', x=>x.samples[2].value=.75],
    ['stale applied timing', x=>x.beforeMembership.timings[1].duration=1000],
    ['wrong progress', x=>x.afterMembership.timings[1].progress=.75],
    ['font animation no longer masks', x=>x.beforeMembership.font=16],
    ['font duration changed', x=>x.beforeMembership.timings[0].duration=1000],
    ['animation replaced', x=>x.membership[1].animation=false],
    ['effect replaced', x=>x.membership[1].effect=false],
    ['time changed', x=>x.afterMembership.timings[1].time=751],
    ['animation resumed', x=>x.afterMembership.timings[1].state='running']]) {
    const x=obs('contextual');mutate(x);let failed=false;
    try{check(x,name);}catch(_){failed=true;}ok(failed);negatives.push(name);
  }
  process.stdout.write(JSON.stringify({names,numerical_positives:2,negative_controls:negatives,
    schema_example:{kind:'masked-base-acyclic',observations:{contextual,literal}}}));
});
'''
result = json.loads(subprocess.run(['node', '-e', program], input=scripts[0], text=True,
                                 capture_output=True, check=True).stdout)
assert len(result['names']) == 1
spec = importlib.util.spec_from_file_location('receiver', HERE / 'tests' / handler)
receiver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(receiver)
old_handler = ROOT / 'artifacts/css-contextual-duration-same-element-dependency-probe-v1/tests/css/css-animations/duration-same-element-record.py'
expected_handler = old_handler.read_text().replace('("same-element-acyclic", "same-element-feedback")', '("masked-base-acyclic",)').replace('acyclic = kind == "same-element-acyclic"', 'acyclic = kind == "masked-base-acyclic"')
assert (HERE / 'tests' / handler).read_text() == expected_handler
assert (HERE / 'tests' / handler).read_text().split('def main(', 1)[1] == old_handler.read_text().split('def main(', 1)[1]
payload = result.pop('schema_example')
assert receiver.validate(payload) == 'masked-base-acyclic'
wrong = copy.deepcopy(payload)
wrong['observations']['contextual']['samples'][0]['value'] = -7
wrong['observations']['contextual']['initial']['opacity'] = None
assert receiver.validate(wrong) == 'masked-base-acyclic'
negatives = 0
for mutate in [lambda v: v.update(kind='../escape'),
               lambda v: v.update(kind='same-element-acyclic'),
               lambda v: v['observations'].pop('literal'),
               lambda v: v['observations']['contextual']['samples'].pop(),
               lambda v: v['observations']['contextual']['samples'][0].update(phase='late'),
               lambda v: v['observations']['contextual']['samples'][0].update(value=float('nan')),
               lambda v: v['observations']['contextual']['membership'][0].update(effect=1)]:
    invalid = copy.deepcopy(payload)
    mutate(invalid)
    try:
        receiver.validate(invalid)
    except (AssertionError, KeyError):
        negatives += 1
    else:
        raise AssertionError('invalid transport accepted')
paths = sorted(str(p.relative_to(HERE / 'tests')) for p in (HERE / 'tests').rglob('*') if p.is_file())
manifest = Manifest(str(HERE / 'tests'), '/')
manifest.update([(path, None, True) for path in paths], parallel=False)
actual = json.loads(json.dumps(manifest.to_json()))
assert set(actual['items']['testharness']['css']['css-animations']) == {Path(page).name}
(HERE / 'MANIFEST.json').write_text(json.dumps(actual, indent=2, sort_keys=True) + '\n')
with tempfile.TemporaryDirectory(prefix='masked-base-font-static-') as temporary:
    scratch = Path(temporary)
    shutil.copytree(HERE / 'tests', scratch / 'tests')
    cwd = os.getcwd()
    try:
        os.chdir(scratch / 'tests')
        assert lint.lint(str(scratch / 'tests'), [page, handler], 'normal', jobs=1) == 0
    finally:
        os.chdir(cwd)
assert not scratch.exists()
for path, digest in json.loads((HERE / 'REFERENCES.json').read_text()).items():
    assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest
result.update(lint_errors=0, transport_schema_positives=2, transport_schema_negatives=negatives,
              wrong_numeric_and_null_values_retained=True, receiver_two_line_kind_adaptation=True, writer_tail_byte_identical=True,
              browser_executed=False, callback_bodies_executed=False,
              first_read_before_timing_membership=True, record_before_numeric_assertions=True,
              all_script_urls_resolved=True)
(HERE / 'CHECK.json').write_text(json.dumps(result, indent=2) + '\n')
(HERE / 'ROSTER.json').write_text(json.dumps({'tests': {'/' + page: result['names']},
    'records': ['masked-base-acyclic.json'], 'callbacks': 1}, indent=2) + '\n')
print(json.dumps(result, indent=2))
