import hashlib
import json
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
inputs = read(HERE / 'INPUTS.json')
for path, pin in read(HERE / 'REFERENCES.json').items():
    assert sha(ROOT / path) == pin['sha256']
for resource in inputs['resources'].values():
    assert sha(ROOT / resource['path']) == resource['sha256']
url, expected = next(iter(inputs['expected_subtests'].items()))
html = (ROOT / inputs['resources'][url]['path']).read_text()
script, = re.findall(r'<script>(.*?)</script>', html, re.S)
parent = (ROOT / 'artifacts/css-root-font-cancellation-normal-handoff-fix-v1/tests/web-animations/animation-model/keyframe-effects/root-font-cancel-child-animation.html').read_text()
for begin, end in [('function paused(', '\nfor (const {'),
                   ('    const disturbance = paused', '    if (kind === "new-child")'),
                   ('    const animation = paused', '    const expected =')]:
    old = parent[parent.index(begin):parent.index(end, parent.index(begin))]
    if end == '    if (kind === "new-child")':
        new = html[html.index(begin):html.index('    const target = child;')]
    else:
        new = html[html.index(begin):html.index(end, html.index(begin))]
    assert old == new, begin
assert html.index('frame.srcdoc =') < html.index('await loaded;') < html.index('const wrappers =') < html.index('const disturbance =')
assert html.index('first =') < html.index('await animation.ready') < html.index('settled =') < html.index('assert_approx_equals(first')
collector = '''const vm = require('node:vm');
let input = ''; process.stdin.on('data', x => input += x); process.stdin.on('end', () => {
 const names = []; const sandbox = {window:{}, promise_test: (_body,name) => names.push(name)};
 vm.runInNewContext(input, sandbox, {timeout:1000});
 process.stdout.write(JSON.stringify(names));
});'''
result = subprocess.run(['node', '-e', collector], input=script, text=True, capture_output=True, check=True)
names = json.loads(result.stdout)
assert names == expected and len(names) == len(set(names)) == 4
print(json.dumps({'success': True, 'source_checks_only': True, 'callbacks_registered_without_execution': names,
 'preserved_paused_helper_disturbance_barrier_and_sampling': True,
 'browser_run': False, 'wpt_lint_or_manifest_run': False,
 'test_sha256': inputs['resources'][url]['sha256'], 'checker_sha256': sha(HERE / 'check_source.py')}))
