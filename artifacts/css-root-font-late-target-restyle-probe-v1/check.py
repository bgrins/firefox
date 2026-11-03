from pathlib import Path
import hashlib
import json
import re
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
relative = 'tests/web-animations/animation-model/keyframe-effects/initial-root-font-child-keyframes.html'
old = (ROOT / 'artifacts/css-root-font-initial-late-target-restyle-probe-v1' / relative).read_text()
new = (HERE / relative).read_text()
removed = '  ["active", "initial root32px CSS animation and child2rem CSS animation"],\n  ["constant", "literal root32px and initial child2rem CSS animation"],\n'
assert old.count(removed) == 1 and old.replace(removed, '') == new
for path, pin in json.loads((HERE / 'REFERENCES.json').read_text()).items():
    assert sha(ROOT / path) == pin
for row in json.loads((HERE / 'INPUTS.json').read_text())['resources'].values():
    assert sha(ROOT / row['path']) == row['sha256']
scripts = re.findall(r'<script>([\s\S]*?)</script>', new)
assert len(scripts) == 1
with tempfile.TemporaryDirectory(prefix='late-cohort-check-', dir='/private/tmp') as temporary:
    script = Path(temporary) / 'fixture.js'
    script.write_text(scripts[0])
    subprocess.run(['node', '--check', str(script)], check=True)
    program = "const fs=require('fs'),vm=require('vm'),names=[];vm.runInNewContext(fs.readFileSync(process.argv[1],'utf8'),{window:{},promise_test:(_,n)=>names.push(n)});console.log(JSON.stringify(names));"
    names = json.loads(subprocess.check_output(['node', '-e', program, str(script)], text=True))
    assert names == ['pre-styled root23px then simultaneous root32px and child2rem CSS animations']
    program = """const fs=require('fs'),vm=require('vm'),assert=require('assert');
const source=fs.readFileSync(process.argv[1],'utf8');
const row={mode:'late',first:'46px',targetRestyle:{value:'64px'}};
const input=[row], before=JSON.stringify(input);
const read=vm.runInNewContext('('+source+')',{window:{rootFontInitialAnimationObservations:input}});
assert.strictEqual(JSON.stringify(read()),before);assert.strictEqual(JSON.stringify(input),before);
assert.notStrictEqual(read()[0],row);
for(const rows of [[],[row,row],[{mode:'active',targetRestyle:{}}],[{mode:'late'}]]) {
const bad=vm.runInNewContext('('+source+')',{window:{rootFontInitialAnimationObservations:rows}});
assert.throws(bad);
}
console.log('read-only extractor: one accepted shape, four rejected shapes');"""
    subprocess.run(['node', '-e', program, str(HERE / 'observe.js')], check=True)
assert not Path(temporary).exists()
print(json.dumps({'exact_only_change': 'remove two non-late case entries',
                  'callback_body_assertions_and_observations': 'byte-identical parent',
                  'inert_callbacks': names, 'extractor_positive': 1,
                  'extractor_rejections': 4, 'scratch_removed': temporary,
                  'browser_run': False, 'genuine_lint_manifest': False,
                  'tested_inputs': {n: sha(HERE / n) for n in [relative, 'observe.js', 'check.py', 'INPUTS.json', 'REFERENCES.json', 'PARENT-DELTA.patch']}}, indent=2))
