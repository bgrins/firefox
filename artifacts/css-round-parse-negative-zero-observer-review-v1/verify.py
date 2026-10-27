import hashlib,importlib.util,json,re,subprocess,sys,tempfile
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
P=ROOT/'artifacts/css-round-parse-negative-zero-repair-v2';V1=ROOT/'artifacts/css-round-parse-negative-zero-repair-v1';T=ROOT/'artifacts/css-round-baseline-surprises-terminal-review-v1';R=ROOT/'artifacts/css-round-baseline-surprises-browser-runtime-v1'
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def auth(p,digest):
 assert sha(p)==digest
 for n,h in read(p).items():assert not Path(n).is_absolute() and '..' not in Path(n).parts and sha(p.parent/n)==h,n
auth(P/'FILES.json','89466aa12536371fe6b553803c23130b0c730bb433ff72c07b330025724d64ac')
auth(T/'FILES.json','bfd06c17349f21b2cfe40a4a8994eb0f3ca5efdf5eadc97ca8414096c4514ad7')
for n,h in read(T/'REFERENCES.json').items():assert sha(ROOT/n)==h,n
rrefs=read(T/'REFERENCES.json');auth(R/'FILES.json',rrefs[str((R/'FILES.json').relative_to(ROOT))])
for n,h in read(P/'REFERENCES.json').items():auth(ROOT/n,h)
c=read(P/'INPUTS.json');native,wpt=c['native'],c['wpt']
for role in ['candidate','original']:assert (P/role/native).read_bytes()==(V1/role/native).read_bytes()
assert sha(P/'candidate'/native)=='ef99276d935fbc9c74fb51c213605d095f1c64442b2fd51da88ff4ff93e06e67'
for relative,local in [('SUMMARY.json','SUMMARY.json'),('wpt-round-parse-routes/raw.json','raw.json'),('wpt-round-parse-routes/RUN.json','RUN.json')]:
 assert (R/relative).read_bytes()==(P/'observations'/local).read_bytes()
events=[json.loads(line) for line in (R/'wpt-round-parse-routes/raw.json').read_text().splitlines()]
rows=[e for e in events if e.get('action')=='test_status'];assert len(rows)==15
assert rows==read(P/'observations/RUN.json')['rows']==read(P/'observations/SUMMARY.json')['rows']
failures=[e for e in rows if e['status']=='FAIL'];assert len(failures)==5 and sum(e['status']=='PASS' for e in rows)==10
assert all(e['status']=='PASS' for e in rows[:8]);cases=read(P/'CASES.json')
assert [e['subtest'] for e in failures[:4]]==cases['observed_failure_names']
assert failures[-1]['subtest']=='both-infinite route: deferred value, literal step'
for row in failures[:4]:
 assert row['message'].endswith('expected 0 but got 1')
 snap=json.loads(row['message'].split('snapshot=',1)[1].rsplit(' expected 0 but got 1',1)[0])
 assert snap['observed']['first']==snap['observed']['repeat']==1
 assert snap['positive']['first']==1 and snap['negative']['first']==0 and snap['division']['first']==0
 assert all(s['font']==32 for s in snap.values())
with tempfile.TemporaryDirectory(prefix='round-observer-review-') as tmp:
 s=Path(tmp);f=s/native;f.parent.mkdir(parents=True);f.write_bytes((P/'original'/native).read_bytes())
 def run(args):
  r=subprocess.run(args,cwd=s,capture_output=True,text=True,timeout=30);assert r.returncode==0,r.stderr;return r.stdout
 run(['git','apply',str(P/'native-and-wpt.patch')]);assert f.read_bytes()==(P/'candidate'/native).read_bytes()
 assert (s/wpt).read_bytes()==(P/'candidate'/wpt).read_bytes()
 source=re.findall(r'<script>(.*?)</script>',(s/wpt).read_text(),re.S)[0]
 js=s/'fixture.js';js.write_text(source);run(['node','--check',str(js)])
 js.write_text('const names=[];function test(fn,name){names.push(name);}\n'+source+'\nconsole.log(JSON.stringify({names,cases}));')
 result=json.loads(run(['node',str(js)]));assert result['names']==cases['names'] and len(set(result['names']))==8
 for i,row in enumerate(failures[:4]):
  snap=json.loads(row['message'].split('snapshot=',1)[1].rsplit(' expected 0 but got 1',1)[0]);assert snap['observed']['expression']==f"clamp(0, pow({result['cases'][i][1]}, -1), 1)"
 run(['git','apply','--check',str(ROOT/'artifacts/css-round-context-quotient-repair-v1/native-and-wpt.patch')])
 run(['git','apply','--reverse',str(P/'native-and-wpt.patch')]);assert f.read_bytes()==(P/'original'/native).read_bytes() and not (s/wpt).exists()
assert (P/'check-results/lint.log').read_bytes()==b'' and read(P/'check-results/CHECK.json')['wpt_lint_exit']==0
receipt={'status':'FINITE_PARSE_ZERO_OBSERVER_REVIEW_GO','proposal_sha256':sha(P/'FILES.json'),'actual_terminal_review_sha256':sha(T/'FILES.json'),'native_identical_v1':True,'candidate_sha256':sha(P/'candidate'/native),'landing_cases':8,'observed_same_pow_witnesses':4,'prospective_pow_controls':4,'original_division_controls_pass':8,'separate_infinity_failure_excluded':True,'archived_15_raw_recount':{'PASS':10,'FAIL':5},'scratch_patch_apply_reverse':True,'JS_syntax_inert_roster':True,'quotient_patch_applies_after':True,'producer_clean_lint_receipt_authenticated':True,'lint_rerun':False,'owned_scratch_removed':True,'native_build_or_browser':False,'native_acceptance':False,'independence':'Reviewer authored native v1; independent successor fixture/packaging and actual archived observation joins.'}
(HERE/'CHECK.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
