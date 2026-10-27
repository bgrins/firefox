import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
WPT=ROOT/'testing/web-platform/tests'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())

parser=argparse.ArgumentParser();parser.add_argument('--output',required=True,type=Path)
out=parser.parse_args().output;out.mkdir(exist_ok=False)
for name,h in read(HERE/'REFERENCES.json').items():
    assert sha(ROOT/name)==h,name
cases=read(HERE/'FIXTURES.json')
prior=HERE.parent/'css-round-numerical-baseline-plan-v1'
assert (HERE/'BINDING.json').read_bytes()==(prior/'BINDING.json').read_bytes()
assert (HERE/'ROSTER.json').read_bytes()==(prior/'ROSTER.json').read_bytes()
for case in cases:
    if 'predecessor_source' not in case:
        assert (HERE/case['local']).read_bytes()==(prior/case['local']).read_bytes()
    else:
        body=(HERE/case['local']).read_text()
        recovered=body.replace('  assert_not_equals(element.style.opacity, "", "opacity setter retention");\n','')
        start=recovered.index('  const first = Number(getComputedStyle(element).opacity);')
        end=recovered.index('  return first;', start)
        recovered=recovered[:start]+'  const first = Number(getComputedStyle(element).opacity);\n  assert_equals(Number(getComputedStyle(element).opacity), first, "stable computed value");\n'+recovered[end:]
        assert recovered==(prior/case['local']).read_text()
        assert body.count('getComputedStyle(element).opacity')==2
        assert 'Number.isFinite(first) && first >= 0 && first <= 1' in body
        assert 'Number.isFinite(repeated) && repeated >= 0 && repeated <= 1' in body
        assert body.index('opacity setter retention') < body.index('document.body.append(element)')
        assert body.index('finite in-range repeated opacity') < body.index('stable computed value')
roster={}
with tempfile.TemporaryDirectory(prefix='round-numerical-plan-') as t:
    scratch=Path(t)
    result=subprocess.run(['git','init','-q'],cwd=scratch,capture_output=True,text=True);assert result.returncode==0
    for name in ['.gitignore','lint.ignore']:(scratch/name).write_bytes((WPT/name).read_bytes())
    paths=[]
    for i,case in enumerate(cases):
        source=ROOT/case['source'];assert sha(source)==case['sha256']
        body=(HERE/case['local']).read_bytes();assert body==source.read_bytes()
        path=scratch/case['wpt_relative'];path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(body);paths.append(case['wpt_relative'])
        scripts=[s for s in re.findall(r'<script[^>]*>(.*?)</script>',body.decode(),re.S) if s.strip()]
        assert len(scripts)==1
        js=scratch/'fixture.js';js.write_text(scripts[0])
        r=subprocess.run(['node','--check',str(js)],capture_output=True,text=True);assert r.returncode==0,(r.stdout,r.stderr)
        js.write_text('const names=[];function test(fn,name){names.push(name); }\n'+scripts[0]+'\nprocess.stdout.write(JSON.stringify(names));')
        r=subprocess.run(['node',str(js)],capture_output=True,text=True);assert r.returncode==0,(r.stdout,r.stderr)
        names=json.loads(r.stdout);assert names==case['names'] and len(names)==len(set(names))
        roster['/'+case['wpt_relative']]=names
    command=[str(WPT/'_venv3/bin/python3'),'-B','-I',str(ROOT/'artifacts/css-round-parse-negative-zero-repair-v2/check.py'),'--lint-worker',str(scratch),*paths]
    r=subprocess.run(command,cwd=scratch,capture_output=True,text=True,timeout=60)
    (out/'lint.log').write_text(r.stdout+r.stderr)
    assert r.returncode==0 and r.stdout==r.stderr==''
assert roster==read(HERE/'ROSTER.json')
(out/'CHECK.json').write_text(json.dumps({'status':'PLAN_FIXTURES_PASS','cases':sum(map(len,roster.values())),'harnesses':len(roster),'family_counts':{c['family']:len(c['names']) for c in cases},'fixture_bytes_exact':True,'javascript_syntax':True,'inert_registration':True,'wpt_lint_exit':0,'lint_stdout_stderr_empty':True,'scratch_removed':True,'native_build':False,'browser_executed':False},indent=2)+'\n')
