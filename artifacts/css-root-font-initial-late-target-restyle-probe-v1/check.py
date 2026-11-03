from pathlib import Path
import hashlib
import json
import re
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
relative = 'tests/web-animations/animation-model/keyframe-effects/initial-root-font-child-keyframes.html'
old = (ROOT / 'artifacts/css-root-font-initial-late-post-calibration-probe-v1' / relative).read_text()
new = (HERE / relative).read_text()
css = '      .target.force-target-restyle { background-color: rgb(1, 2, 3); }\n'
start = new.index('    const childBeforeRestyle = childAnimations[0];\n')
end = new.index('    assert_equals(doc.compatMode, "CSS1Compat", "fresh standards document");\n')
block = new[start:end]
assert new[:start].replace(css, '') + new[end:] == old
assert new.count(css) == 1
assert new.index('const afterCalibration =') < new.index('window.rootFontInitialAnimationObservations.push(') < start
assert block.count('classList.add') == 1 and 'await ' not in block
mutation = 'target.classList.add("force-target-restyle");\n'
assert block.split(mutation)[1].startswith('    const afterTargetRestyle = win.getComputedStyle(target).fontSize;\n')
assert 'childAfterRestyle[0] === childBeforeRestyle' in block
assert 'rootAfterRestyle[0] === rootBeforeRestyle' in block
assert '.targetRestyle = {' in block and 'value: afterTargetRestyle' in block
assert 'background: win.getComputedStyle(target).backgroundColor' in block
refs = json.loads((HERE / 'REFERENCES.json').read_text())
for name, pin in refs.items():
    assert sha(ROOT / name) == pin
for row in json.loads((HERE / 'INPUTS.json').read_text())['resources'].values():
    assert sha(ROOT / row['path']) == row['sha256']
scripts = re.findall(r'<script>([\s\S]*?)</script>', new)
assert len(scripts) == 1
with tempfile.TemporaryDirectory(prefix='target-restyle-syntax-', dir='/private/tmp') as temporary:
    script = Path(temporary) / 'fixture.js'
    script.write_text(scripts[0])
    subprocess.run(['node', '--check', str(script)], check=True)
    program = "const fs=require('fs'),vm=require('vm'),names=[];vm.runInNewContext(fs.readFileSync(process.argv[1],'utf8'),{window:{},promise_test:(_,n)=>names.push(n)});console.log(JSON.stringify(names));"
    names = json.loads(subprocess.check_output(['node', '-e', program, str(script)], text=True))
assert len(names) == len(set(names)) == 3
assert not Path(temporary).exists()
print(json.dumps({'success': True, 'exact_parent_erasure': True,
                  'original_assertions_and_observations_preserved': True,
                  'first_getter_after_mutation_is_target': True,
                  'animation_identity_comparisons_present': True,
                  'callbacks': names, 'references': len(refs),
                  'scratch': temporary, 'scratch_removed': True,
                  'browser_run': False, 'genuine_lint_manifest': False,
                  'tested_inputs': {name: sha(HERE / name) for name in
                                    [relative, 'check.py', 'REFERENCES.json', 'INPUTS.json']}}, indent=2))
