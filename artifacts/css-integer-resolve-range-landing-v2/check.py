from pathlib import Path
import argparse,hashlib,json,re,subprocess,sys,tempfile
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
WPT=ROOT/'testing/web-platform/tests'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
if len(sys.argv)>1 and sys.argv[1]=='--lint-worker':
    sys.path.insert(0,str(WPT))
    from tools.lint import lint
    raise SystemExit(1 if lint.lint(sys.argv[2],sys.argv[3:],'json',jobs=1) else 0)
ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
assert not args.output.exists()
for manifest,h in json.loads((HERE/'REFERENCES.json').read_text()).items():
    p=ROOT/manifest;assert sha(p)==h
    for n,s in json.loads(p.read_text()).items():assert sha(p.parent/n)==s,n
old=ROOT/'artifacts/css-integer-resolve-range-repair-v1'
meta=ROOT/'artifacts/css-subgrid-zero-repeat-help-link-v1'
paths=json.loads((HERE/'PATHS.json').read_text()); native=paths['native'];fixtures=paths['fixtures']
zero='subgrid-repeat-calculated-zero.html';timing='timing-functions-calculated-step-range.html'
assert (HERE/timing).read_bytes()==(old/timing).read_bytes()
a=(meta/'subgrid-calculated-zero-repeat-diagnostic.html').read_text();b=(HERE/zero).read_text()
assert a.replace('<title>Bounded subgrid calculated repeat zero diagnostic</title>','<title>Calculated zero subgrid repeat counts are clamped to one</title>')==b
assert re.findall(r'<script>(.*?)</script>',a,re.S)==re.findall(r'<script>(.*?)</script>',b,re.S)
assert re.findall(r'<style>(.*?)</style>',a,re.S)==re.findall(r'<style>(.*?)</style>',b,re.S)
receipt={'status':'UNACCEPTED_PACKAGING_VERIFIED','variants':{},'fixtures':{},'title_only_change':True}
def run(cmd,cwd):
    p=subprocess.run(cmd,cwd=cwd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    assert p.returncode==0,(cmd,p.returncode,p.stdout,p.stderr)
    return p.stdout
lint_sources=['tools/lint/wpt/wpt.py','testing/web-platform/tests/tools/lint/lint.py','testing/web-platform/tests/tools/lint/rules.py','testing/web-platform/tests/tools/manifest/sourcefile.py','testing/web-platform/tests/lint.ignore','testing/web-platform/tests/.gitignore']
source_pins={n:sha(ROOT/n) for n in lint_sources}
with tempfile.TemporaryDirectory(prefix='landing-check-',dir=HERE) as temp:
    temp=Path(temp)
    for variant,source in [('head90','number-head90.rs'),('installed118','number-118.rs')]:
        scratch=temp/variant;scratch.mkdir();run(['git','init','-q'],scratch)
        target=scratch/native;target.parent.mkdir(parents=True);target.write_bytes((old/'sources'/source).read_bytes())
        pre=target.read_bytes();post=(old/(variant+'-candidate-number.rs')).read_bytes()
        assert pre.replace(b'let value = calc.as_number()?.get();',b'let value = calc.clamping_mode.clamp(calc.as_number()?.get());',1)==post
        patch=HERE/(variant+'-standalone.patch')
        changed=re.findall(r'^diff --git a/(.*?) b/.*$',patch.read_text(),re.M)
        assert changed==[native,*fixtures.values()]
        run(['git','apply','--check',str(patch)],scratch);run(['git','apply',str(patch)],scratch)
        assert target.read_bytes()==post
        for local,path in fixtures.items():assert (scratch/path).read_bytes()==(HERE/local).read_bytes()
        run(['git','diff','--check'],scratch)
        run(['git','apply','--reverse','--check',str(patch)],scratch);run(['git','apply','--reverse',str(patch)],scratch)
        assert target.read_bytes()==pre and all(not (scratch/p).exists() for p in fixtures.values())
        receipt['variants'][variant]={'git_check_apply_reverse':'PASS','exact_three_paths':changed,'native_preimage':hashlib.sha256(pre).hexdigest(),'native_postimage':hashlib.sha256(post).hexdigest(),'patch':sha(patch)}
    for local,count in [(timing,24),(zero,1)]:
        js='\n'.join(re.findall(r'<script>(.*?)</script>',(HERE/local).read_text(),re.S))
        p=temp/'fixture.js';p.write_text(js);run(['/opt/homebrew/bin/node','--check',str(p)],temp)
        p.write_text('const names=[];global.test=(f,n)=>names.push(n);\n'+js+'\nconsole.log(JSON.stringify(names));')
        names=json.loads(run(['/opt/homebrew/bin/node',str(p)],temp));assert len(names)==count==len(set(names))
        receipt['fixtures'][local]={'sha256':sha(HERE/local),'names':names,'count':count,'callbacks_executed':False,'javascript_syntax':'PASS'}
    scratch=temp/'lint';scratch.mkdir();run(['git','init','-q'],scratch)
    for name in ('lint.ignore','.gitignore'):(scratch/name).write_bytes((WPT/name).read_bytes())
    relative=[]
    for local,path in fixtures.items():
        path=path.removeprefix('testing/web-platform/tests/');relative.append(path)
        p=scratch/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((HERE/local).read_bytes())
    stdout=run([str(WPT/'_venv3/bin/python3'),'-B','-I',str(HERE/'check.py'),'--lint-worker',str(scratch),*relative],scratch)
    assert stdout==''
    receipt['wpt_lint']={'exit':0,'errors':[],'api':'tools.lint.lint.lint','paths':relative,'existing_ignore_files_unchanged':True,'source_pins':source_pins}
assert source_pins=={n:sha(ROOT/n) for n in lint_sources}
receipt['temporary_products_removed']=True
args.output.write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'status':receipt['status'],'cases':25,'variants':2,'lint_exit':0}))
