import sys
assert sys.flags.isolated and sys.flags.no_site, 'Run with python3 -I -S -B'
import argparse,hashlib,json,re,subprocess
from pathlib import Path,PurePosixPath
R=Path(__file__).resolve().parent
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def pairs(xs):
 d={}
 for k,v in xs:assert k not in d,k;d[k]=v
 return d
def read(p):return json.loads(p.read_text(),object_pairs_hook=pairs)
p=argparse.ArgumentParser();p.add_argument('--manifest',required=True);p.add_argument('--native-output',type=Path);a=p.parse_args()
assert H(R/'MANIFEST.json')==a.manifest
m=read(R/'MANIFEST.json');seen=set()
for n,d in m.items():
 q=PurePosixPath(n);assert str(q)==n and not q.is_absolute() and '..' not in q.parts and n.casefold() not in seen;seen.add(n.casefold());f=R/n
 for item in [f,*f.parents]:assert not item.is_symlink()
 assert H(f)==d,n
S=R/'evidence/scout';assert H(S/'FREEZE.json')=='6cfabf732d74b25e1277663515aa99e3add2cf7691265e8215607fb62aafcab2';assert H(S/'MANIFEST.json')=='aed04dfdf039b19efce5e6c8a815acb9ea56de05b8455233073c0157a092aee5'
for n,d in read(S/'MANIFEST.json').items():assert H(S/n)==d,n
old=(S/'source/third_party/rust/cssparser/src/parser.rs').read_bytes();assert old==(S/'vendor/cssparser/src/parser.rs').read_bytes()==(R/'evidence/searchfox-parser.rs').read_bytes()
needle=b'    if parser.current_block_depth >= parser.nested_block_limit && parser.nested_block_limit != 0 {\n';assert old.count(needle)==1
assert old.replace(needle,needle+b'        parser.consume_until_end_of_block(block_type);\n')==(R/'evidence/candidate-parser.rs').read_bytes()
rows={}
for mode in ['original','candidate']:
 rr=[json.loads(x) for x in (R/'receipts'/(mode+'.jsonl')).read_text().splitlines()];rows[mode]=rr;assert len(rr)==126
 for row in rr:
  if row['family']=='unwind':
   assert row['leaked']==(mode=='original' and not row['retry'] and row['limit']>0 and row['depth']>row['limit'])
   assert row['suffix']==('color:blue;);color:green;' if row['leaked'] else 'color:green;')
  elif row['family']=='catch':
   assert not row['callback_invoked'] and row['after_callback']
   assert row['marker']==(mode=='candidate')
  elif row['family']=='eof':assert row['at_eof_after_rejection']==(mode=='candidate')
  else:raise AssertionError(row)
assert sum(x.get('leaked',False) for x in rows['original'])==24
assert read(R/'receipts/RESULT.json')=={'original':126,'candidate':126}
B=R/'evidence/browser';before=read(B/'baseline-before.json');after=read(B/'baseline-after.json');assert before==after
result=read(B/'baseline-result.json');assert result['raw_sha256']==H(B/'baseline-raw.jsonl') and result['console_sha256']==H(B/'baseline-console.log')
rr=[r for r in [json.loads(x) for x in (B/'baseline-raw.jsonl').read_text().splitlines()] if r.get('action') in ['test_status','test_end']]
key=lambda r:(r['action'],r['test'],r.get('subtest'));assert len({key(r) for r in rr})==len(rr)==22
assert {key(r):r['status'] for r in rr}=={key(r):r['status'] for r in result['rows']}
expected={}
for prop in ['padding','width']:
 test='/css/css-syntax/declaration-recovery-nesting-limit-'+prop+'.html'
 path='testing/web-platform/tests'+test;assert before['fixed'][path]==H(B/Path(test).name)
 for mode in ['inline','stylesheet']:
  for depth in [1,74,75,76]:
   name=f'{mode}: semicolon inside {depth} nested functions stays in the value';expected[('test_status',test,name)]='FAIL' if prop=='padding' and mode=='inline' and depth==76 else 'PASS'
   css='color:red;'+('padding-left' if prop=='padding' else 'width')+':'+'calc('*depth+'1px'+')'*(depth-1)+';color:blue;)'
   level=0;decls=[];start=0
   for i,c in enumerate(css):
    if c=='(':level+=1
    elif c==')':level-=1;assert level>=0
    elif c==';' and level==0:decls.append(css[start:i]);start=i+1
   decls.append(css[start:]);assert level==0 and len(decls)==2 and decls[0]=='color:red' and not any(x.startswith('color:blue') for x in decls)
  expected[('test_status',test,f'{mode}: a declaration outside the function applies')]='PASS'
 expected[('test_end',test,None)]='OK'
assert {key(r):r['status'] for r in rr}==expected
assert before['fixed']['third_party/rust/cssparser/src/parser.rs']==H(S/'vendor/cssparser/src/parser.rs')
if a.native_output:
 cmd=[sys.executable,'-I','-S','-B',str(R/'replay.py'),'--output',str(a.native_output.resolve())]
 p=subprocess.run(cmd,text=True,capture_output=True);assert p.returncode==0,p.stdout+p.stderr;print(p.stdout,end='')
print(json.dumps({'status':'PASS','inputs':len(m),'baseline_browser':'1 failure / 19 passes','native_cases_per_variant':126,'original_leaks':24,'candidate_leaks':0,'direct_catch_cases':30,'direct_eof_cases':6,'acceptance':'confirmed defect and narrow candidate source; formal and candidate-browser gates separate'}))
