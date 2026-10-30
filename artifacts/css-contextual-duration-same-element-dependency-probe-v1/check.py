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

page = 'css/css-animations/animation-duration-same-element-dependency.tentative.html'
handler = 'css/css-animations/duration-same-element-record.py'
source = (HERE / 'tests' / page).read_text()
dom = html5lib.parse(source, namespaceHTMLElements=False)
scripts = [node.text for node in dom.iter('script') if not node.get('src')]
assert len(scripts) == 1
assert [node.get('src') for node in dom.iter('script') if node.get('src')] == [
    '/resources/testharness.js', '/resources/testharnessreport.js']
window = source[source.index('  animations[0].currentTime = 750;'):source.index('  const beforeMembership = details(context);')]
assert all(word not in window for word in ('getAnimations', 'timing(', 'details(', 'getTiming', 'getComputedTiming'))
assert 'index <= 3' in window and 'value: read()' in window
assert source.index('await record("same-element-acyclic"') < source.index('assertAcyclic(literal,') < source.index('assertAcyclic(contextual,')
assert source.index('await record("same-element-feedback"') < source.index('assertLiteralFeedback(literal500,')
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
  const acyclic = vm.runInContext('assertAcyclic', c);
  const feedback = vm.runInContext('assertLiteralFeedback', c);
  function obs(duration, font, opacity, count) {
    const timings = count===2 ? [{duration:2000,time:750,state:'paused'},
      {duration,progress:opacity,time:750,state:'paused'}] : [{duration,time:750,state:'paused'}];
    const snapshot = {font,opacity,timings};
    return {samples: ['first-read','passive-frame-1','passive-frame-2','passive-frame-3'].map(phase=>({phase,value:count===2?opacity:font})),
      beforeMembership:snapshot,afterMembership:snapshot,
      membership:Array.from({length:count},()=>({animation:true,effect:true}))};
  }
  acyclic(obs(1375,22,6/11,2),'positive');
  feedback(obs(500,32,1,1),500,32,'positive');
  feedback(obs(1000,16,1,1),1000,16,'positive');
  const negatives=[];
  for (const [name, mutate] of [
    ['stale first', x=>x.samples[0].value=.75],
    ['stale effect', x=>x.beforeMembership.timings[1].duration=1000],
    ['stale font', x=>x.beforeMembership.font=16],
    ['wrong time', x=>x.beforeMembership.timings[0].time=0],
    ['lost identity', x=>x.membership[0].effect=false]]) {
    const x=obs(1375,22,6/11,2); mutate(x);
    let failed=false;try{acyclic(x,name);}catch(_){failed=true;}
    ok(failed);negatives.push(name);
  }
  process.stdout.write(JSON.stringify({names,numerical_positives:3,negative_controls:negatives}));
});
'''
result = json.loads(subprocess.run(['node', '-e', program], input=scripts[0], text=True,
                                 capture_output=True, check=True).stdout)
assert len(result['names']) == 2
spec = importlib.util.spec_from_file_location('receiver', HERE / 'tests' / handler)
receiver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(receiver)
old = (ROOT / 'artifacts/css-contextual-duration-lh-chain-probe-v1/duration-lh-progress-record.py').read_text()
assert (HERE / 'tests' / handler).read_text().split('def main(', 1)[1] == old.split('def main(', 1)[1]
payloads = []
for kind, modes, count in [('acyclic', ['contextual', 'literal'], 2),
                           ('feedback', ['contextual', 'literal500', 'literal1000'], 1)]:
    snapshot = {'font': None, 'opacity': -7, 'cssDuration': '0s', 'timings': [
        {'duration': 0, 'progress': None, 'time': 751, 'state': 'finished'} for _ in range(count)]}
    observations = {mode: {'kind': kind, 'mode': mode, 'initial': snapshot,
        'beforeMembership': snapshot, 'afterMembership': snapshot,
        'membership': [{'animation': False, 'effect': False} for _ in range(count)],
        'samples': [{'phase': phase, 'value': None} for phase in receiver.PHASES]}
        for mode in modes}
    value = {'kind': 'same-element-' + kind, 'observations': observations}
    receiver.validate(value)
    payloads.append(value)
bad_values = []
for mutate in [lambda v: v.update(kind='../escape'),
               lambda v: v['observations'].pop('literal'),
               lambda v: v['observations']['contextual']['samples'].pop(),
               lambda v: v['observations']['contextual']['samples'][0].update(phase='late'),
               lambda v: v['observations']['contextual']['samples'][0].update(value=float('nan')),
               lambda v: v['observations']['contextual']['membership'][0].update(effect=1)]:
    value = copy.deepcopy(payloads[0])
    mutate(value)
    try:
        receiver.validate(value)
    except (AssertionError, KeyError):
        bad_values.append(True)
    else:
        raise AssertionError('invalid transport accepted')
paths = sorted(str(p.relative_to(HERE / 'tests')) for p in (HERE / 'tests').rglob('*') if p.is_file())
manifest = Manifest(str(HERE / 'tests'), '/')
manifest.update([(path, None, True) for path in paths], parallel=False)
actual = json.loads(json.dumps(manifest.to_json()))
assert set(actual['items']['testharness']['css']['css-animations']) == {Path(page).name}
(HERE / 'MANIFEST.json').write_text(json.dumps(actual, indent=2, sort_keys=True) + '\n')
with tempfile.TemporaryDirectory(prefix='same-element-wpt-static-') as temporary:
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
result.update(lint_errors=0, transport_schema_positives=2, transport_schema_negatives=len(bad_values),
              wrong_numeric_and_null_values_retained=True, writer_tail_byte_identical=True,
              browser_executed=False, callback_bodies_executed=False, first_read_before_timing_membership=True)
(HERE / 'CHECK.json').write_text(json.dumps(result, indent=2) + '\n')
(HERE / 'ROSTER.json').write_text(json.dumps({'tests': {'/' + page: result['names']},
    'records': ['same-element-acyclic.json', 'same-element-feedback.json'], 'callbacks': 2}, indent=2) + '\n')
print(json.dumps(result, indent=2))
