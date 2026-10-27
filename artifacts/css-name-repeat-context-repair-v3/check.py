import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OLD = ROOT / 'artifacts/css-name-repeat-context-repair-v1'
OUT = Path(sys.argv[1]).resolve()
OUT.mkdir(exist_ok=False)

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def run(args, cwd, log):
    r = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=60)
    (OUT / log).write_text(r.stdout + r.stderr)
    assert r.returncode == 0, (args, r.returncode)
    return r

for n,h in json.loads((HERE/'REFERENCES.json').read_text()).items():
    p=ROOT/n
    assert sha(p)==h
    for child,digest in json.loads(p.read_text()).items():
        assert sha(p.parent/child)==digest
original=(OLD/'subgrid-contextual-name-repeat.html').read_text()
before=(HERE/'BEFORE.txt').read_text();after=(HERE/'AFTER.txt').read_text()
body=(HERE/'subgrid-contextual-name-repeat.html').read_text()
assert original.count(before)==1 and body==original.replace(before,after)
assert after.count('CSS.supports("z-index", "sibling-index()")') == 1
assert 'zIndex' not in body and '"z-index"' not in body.replace('CSS.supports("z-index", "sibling-index()")', '')
assert after.count('Array.prototype.indexOf.call(f.grid.children, f.subject) + 1') == 3
assert after.index('"initial DOM sibling index"') < after.index('"target name-repeat"')
assert after.index('f.grid.prepend(preceding);') < after.index('"inserted DOM sibling index"')
assert after.index('preceding.remove();') < after.index('"reset DOM sibling index"')
assert body.count('test(t => {')==original.count('test(t => {')
paths=['servo/components/style/values/generics/grid.rs','servo/components/style/values/specified/grid.rs']
wpt='testing/web-platform/tests/css/css-grid/subgrid/subgrid-contextual-name-repeat.html'
with tempfile.TemporaryDirectory(prefix='name-repeat-v2-') as tmp:
    scratch=Path(tmp)
    for base in ['head90','installed']:
        patch=(HERE/(base+'-standalone.patch')).read_text()
        assert patch.startswith((OLD/(base+'-native.patch')).read_text()+'diff --git a/'+wpt)
        tree=scratch/base;tree.mkdir()
        run(['git','init','-q'],tree,base+'-init.log')
        orig=OLD/('head' if base=='head90' else 'original-installed')
        for n in paths:
            p=tree/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((orig/n).read_bytes())
        run(['git','apply','--check',str(HERE/(base+'-standalone.patch'))],tree,base+'-check.log')
        run(['git','apply',str(HERE/(base+'-standalone.patch'))],tree,base+'-apply.log')
        for n in paths:assert sha(tree/n)==sha(OLD/'candidate'/n)
        assert sha(tree/wpt)==sha(HERE/'subgrid-contextual-name-repeat.html')
        run(['git','apply','--reverse',str(HERE/(base+'-standalone.patch'))],tree,base+'-reverse.log')
        assert not (tree/wpt).exists()
        for n in paths:assert sha(tree/n)==sha(orig/n)
    scripts=[s for s in re.findall(r'<script[^>]*>(.*?)</script>',body,re.S) if s.strip()]
    assert len(scripts)==1
    js=scratch/'fixture.js';js.write_text(scripts[0])
    run(['node','--check',str(js)],scratch,'syntax.log')
    js.write_text('const names=[]; function test(fn,name){names.push(name);}\n'+scripts[0]+'\nprocess.stdout.write(JSON.stringify(names));')
    names=json.loads(run(['node',str(js)],scratch,'roster.log').stdout)
    assert names==json.loads((OLD/'ROSTER.json').read_text())==json.loads((HERE/'ROSTER.json').read_text())
    assert len(names)==len(set(names))==10
    lint=scratch/'lint';lint.mkdir();run(['git','init','-q'],lint,'lint-init.log')
    wptroot=ROOT/'testing/web-platform/tests'
    for n in ['.gitignore','lint.ignore']:(lint/n).write_bytes((wptroot/n).read_bytes())
    rel=wpt.removeprefix('testing/web-platform/tests/')
    p=lint/rel;p.parent.mkdir(parents=True);p.write_text(body)
    result=run([str(wptroot/'_venv3/bin/python3'),'-I','-B',str(ROOT/'artifacts/css-round-parse-negative-zero-repair-v2/check.py'),'--lint-worker',str(lint),rel],lint,'lint.log')
    assert result.stdout==result.stderr==''
(OUT/'CHECK.json').write_text(json.dumps(dict(status='NAME_REPEAT_CALIBRATION_SUCCESSOR_PASS',native_bodies_unchanged=True,native_patch_prefixes_unchanged=True,exact_WPT_delta=True,non_evaluating_availability_control=True,direct_DOM_indices=[1,2,1],case_names_unchanged=10,patch_roundtrips=2,lint_exit=0,lint_empty_output=True,scratch_removed=True,browser_run=False),indent=2)+'\n')
