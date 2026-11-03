from pathlib import Path
import difflib
import hashlib
import json
import re
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
relative = 'tests/web-animations/animation-model/keyframe-effects/initial-root-font-depth.html'
parent = ROOT / 'artifacts/css-root-font-startup-depth-probe-v1/tests/web-animations/animation-model/keyframe-effects/root-font-startup-depth.html'
new = (HERE / relative).read_text()
transformed = parent.read_text()
for before, after in json.loads((HERE / 'TRANSFORM.json').read_text()):
    assert before in transformed
    transformed = transformed.replace(before, after)
assert transformed == new
assert ''.join(difflib.unified_diff(parent.read_text().splitlines(True), new.splitlines(True),
    fromfile=str(parent.relative_to(ROOT)), tofile=str((HERE / relative).relative_to(ROOT)))) == (HERE / 'PARENT-DELTA.patch').read_text()
for row in json.loads((HERE / 'REFERENCES.json').read_text()):
    assert sha(ROOT / row['path']) == row['sha256']
for row in json.loads((HERE / 'INPUTS.json').read_text())['resources'].values():
    assert sha(ROOT / row['path']) == row['sha256']
scripts = re.findall(r'<script>([\s\S]*?)</script>', new)
assert len(scripts) == 1
source = scripts[0]
boundaries = [
    'const precondition = null;',
    'const firstLeaf =', 'const settledNodes =', 'const rootSize =',
    'const plainSize =', 'const afterCalibrationNodes =', 'const rootAnimations =',
    'window.rootFontInitialDepthObservations.push(observation)',
    'leaf.classList.add("force-target-restyle")', 'const afterTargetRestyle =',
    'const restyleNodes =', 'const afterAnimations =', 'assert_true(observation.standards',
]
positions = [source.index(part) for part in boundaries]
assert positions == sorted(positions)
assert source[source.index('const firstLeaf ='):source.index('const settledNodes =')].count('await nextFrame(win);') == 2
assert source.count('win.getComputedStyle(') == 1
assert '<html class="${mode} active">' in source
assert 'root.classList.add("active")' not in source
assert 'pre-root' not in source and 'pre-node' not in source
assert source.index('const firstLeaf =') < source.index('root.getAnimations()')
assert source.index('const firstLeaf =') < source.index('nodes.map(node => node.getAnimations())')
assert source[source.index('const precondition ='):source.index('const firstLeaf =')].strip() == 'const precondition = null;'
assert 'nodes.map((node, index) => ({node, level: index + 1})).reverse()' in source
assert 'const value = win.getComputedStyle(target)[property];' in source
assert source.index('const value = win.getComputedStyle(target)[property];') < source.index('styleReadOrder.push(')
assert '@keyframes rem-size { from, to { font-size: 2rem; } }' in source
assert '@keyframes em-size { from, to { font-size: 2em; } }' in source
with tempfile.TemporaryDirectory(prefix='initial-depth-check-', dir='/private/tmp') as temporary:
    script = Path(temporary) / 'fixture.js'
    script.write_text(source)
    subprocess.run(['node', '--check', str(script)], check=True)
    program = "const fs=require('fs'),vm=require('vm'),names=[];vm.runInNewContext(fs.readFileSync(process.argv[1],'utf8'),{window:{},promise_test:(_,n)=>names.push(n)});console.log(JSON.stringify(names));"
    names = json.loads(subprocess.check_output(['node', '-e', program, str(script)], text=True))
    assert names == json.loads((HERE / 'ROSTER.json').read_text())
    program = """const fs=require('fs'),vm=require('vm'),assert=require('assert');
const source=fs.readFileSync(process.argv[1],'utf8');
const rows=[['animated',2],['literal',2],['animated',4],['literal',4]].map(([mode,depth])=>({mode,depth,startup:'initial-stylesheet',precondition:null,targetRestyle:{},styleReadOrder:[{phase:'first-leaf'}]}));
function reader(input) {return vm.runInNewContext('('+source+')',{window:{rootFontInitialDepthObservations:input}});}
const before=JSON.stringify(rows),read=reader(rows),result=read();
assert.strictEqual(JSON.stringify(result),before);assert.strictEqual(JSON.stringify(rows),before);
assert.notStrictEqual(result[0],rows[0]);
for(const bad of [[],rows.slice(0,3),[...rows,rows[0]],[rows[1],rows[0],...rows.slice(2)],rows.map((r,i)=>i? r:{...r,depth:3}),rows.map((r,i)=>i? r:{...r,targetRestyle:null}),rows.map((r,i)=>i? r:{...r,styleReadOrder:null}),rows.map((r,i)=>i? r:{...r,startup:'late'}),rows.map((r,i)=>i? r:{...r,precondition:{}}),rows.map((r,i)=>i? r:{...r,styleReadOrder:[{phase:'pre-root'}]})]) assert.throws(reader(bad));
console.log('read-only stored extraction: 1 accepted shape, 10 rejected shapes');"""
    subprocess.run(['node', '-e', program, str(HERE / 'observe.js')], check=True)
assert not Path(temporary).exists()
print(json.dumps({'inert_callbacks': names, 'source_order_boundaries': len(boundaries),
    'extractor_positive': 1, 'extractor_rejections': 10, 'parent_delta_exact': True,
    'scratch_removed': temporary, 'browser_run': False, 'genuine_lint_manifest': False,
    'tested': {n: sha(HERE / n) for n in [relative, 'observe.js', 'check.py', 'INPUTS.json', 'REFERENCES.json', 'ROSTER.json', 'PARENT-DELTA.patch', 'TRANSFORM.json']}}, indent=2))
