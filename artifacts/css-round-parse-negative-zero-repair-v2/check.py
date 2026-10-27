import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WPT = ROOT / 'testing/web-platform/tests'
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path);parser.add_argument('--lint-worker',nargs='+')
    args=parser.parse_args()
    if args.lint_worker:
        sys.path.insert(0,str(WPT))
        from tools.lint import lint
        raise SystemExit(lint.lint(args.lint_worker[0],args.lint_worker[1:],'json',jobs=1))
    out=args.output.resolve();out.mkdir(exist_ok=False)
    def run(command,cwd,label):
        r=subprocess.run(command,cwd=cwd,capture_output=True,text=True,timeout=60)
        (out/(label+'.log')).write_text(r.stdout+r.stderr)
        assert r.returncode==0,(label,r.returncode,r.stdout,r.stderr)
        return r.stdout
    for name,h in read(HERE/'REFERENCES.json').items():
        f=ROOT/name;assert sha(f)==h
        for n,d in read(f).items():assert sha(f.parent/n)==d
    c=read(HERE/'INPUTS.json');native,wpt=c['native'],c['wpt']
    base=ROOT/'artifacts/css-round-parse-negative-zero-repair-v1'
    for role in ['candidate','original']:
        assert (HERE/role/native).read_bytes()==(base/role/native).read_bytes()
    assert sha(HERE/'candidate'/native)==c['candidate_sha256'] and sha(HERE/'candidate'/wpt)==c['fixture_sha256']
    assert subprocess.run(['git','show',c['revision']+':'+native],cwd=ROOT,capture_output=True,check=True).stdout==(HERE/'original'/native).read_bytes()
    summary=read(HERE/'observations/SUMMARY.json')
    events=[json.loads(line) for line in (HERE/'observations/raw.json').read_text().splitlines()]
    rows=[e for e in events if e.get('action')=='test_status']
    recorded=read(HERE/'observations/RUN.json')
    assert rows==recorded['rows']==summary['rows'] and len(rows)==15
    cases=read(HERE/'CASES.json');assert [r['subtest'] for r in rows if r['status']=='FAIL'][:4]==cases['observed_failure_names']
    assert all(r['status']=='PASS' for r in rows[:8])
    with tempfile.TemporaryDirectory(prefix='round-pow-package-') as t:
        s=Path(t);run(['git','init','-q'],s,'git-init')
        f=s/native;f.parent.mkdir(parents=True);f.write_bytes((HERE/'original'/native).read_bytes())
        run(['git','apply','--check',str(HERE/'native-and-wpt.patch')],s,'git-check')
        run(['git','apply',str(HERE/'native-and-wpt.patch')],s,'git-apply')
        for n in (native,wpt):assert (s/n).read_bytes()==(HERE/'candidate'/n).read_bytes()
        fixture=(s/wpt).read_text();scripts=[x for x in re.findall(r'<script[^>]*>(.*?)</script>',fixture,re.S) if x.strip()];assert len(scripts)==1
        js=s/'fixture.js';js.write_text(scripts[0]);run(['node','--check',str(js)],s,'syntax')
        js.write_text('const names=[];function test(fn,name){names.push(name); }\n'+scripts[0]+'\nprocess.stdout.write(JSON.stringify(names));')
        names=json.loads(run(['node',str(js)],s,'registration'));assert names==cases['names'] and len(set(names))==8
        q=ROOT/'artifacts/css-round-context-quotient-repair-v1/native-and-wpt.patch'
        run(['git','apply','--check',str(q)],s,'quotient-composes')
        run(['git','apply','--reverse','--check',str(HERE/'native-and-wpt.patch')],s,'reverse-check')
        run(['git','apply','--reverse',str(HERE/'native-and-wpt.patch')],s,'reverse')
        assert f.read_bytes()==(HERE/'original'/native).read_bytes() and not (s/wpt).exists()
    with tempfile.TemporaryDirectory(prefix='round-pow-lint-') as t:
        s=Path(t);run(['git','init','-q'],s,'lint-git')
        for n in ['.gitignore','lint.ignore']:(s/n).write_bytes((WPT/n).read_bytes())
        relative=wpt.removeprefix('testing/web-platform/tests/');f=s/relative;f.parent.mkdir(parents=True);f.write_bytes((HERE/'candidate'/wpt).read_bytes())
        command=[str(WPT/'_venv3/bin/python3'),'-B','-I',str(HERE/'check.py'),'--lint-worker',str(s),relative]
        r=subprocess.run(command,cwd=s,capture_output=True,text=True,timeout=60)
        (out/'lint.log').write_text(r.stdout+r.stderr);assert r.returncode==0 and r.stdout==r.stderr==''
    receipt={'status':'PASS','native_postimage_identical_v1':True,'patch_paths':[native,wpt],'wpt_cases':names,
             'observed_pow_failures':cases['observed_failure_names'],'archived_original_eight_pass':True,
             'scratch_git_apply_reverse':True,'javascript_syntax':True,'inert_registration':True,'wpt_lint_exit':0,
             'lint_stdout_stderr_empty':True,'helper_replayed':False,'helper_evidence_inherited_exact_native':True,
             'native_build':False,'browser_executed':False,'actual_terminal_preservation_claim':False,'scratch_removed':True}
    (out/'CHECK.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))

if __name__=='__main__':main()
