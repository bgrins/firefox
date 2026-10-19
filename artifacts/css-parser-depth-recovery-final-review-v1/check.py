import sys
assert sys.flags.isolated and sys.flags.no_site, 'Use python3 -I -S -B'
import argparse,hashlib,json
from pathlib import Path,PurePosixPath
R=Path(__file__).resolve().parent
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def pairs(xs):
 d={}
 for k,v in xs:assert k not in d,k;d[k]=v
 return d
def read(p):return json.loads(p.read_text(),object_pairs_hook=pairs)
p=argparse.ArgumentParser();p.add_argument('--manifest',required=True);a=p.parse_args();assert H(R/'MANIFEST.json')==a.manifest
m=read(R/'MANIFEST.json');seen=set()
for n,h in m.items():
 q=PurePosixPath(n);assert str(q)==n and not q.is_absolute() and '..' not in q.parts and n.casefold() not in seen;seen.add(n.casefold());f=R/n
 for x in [f,*f.parents]:assert not x.is_symlink()
 assert H(f)==h,n
E=R/'evidence';B=E/'browser'
assert H(E/'prior-FREEZE.json')=='32d5f214ffa57db308c7c9521d9c63676ca2c786cba450935380d0c000732038'
assert H(E/'prior-MANIFEST.json')=='86e592c867f5f9e72a50fcb328cf65d465b332a733c8cac9522dbc3fee5844d0'
assert H(E/'prior-REPORT.md')==read(E/'prior-MANIFEST.json')['REPORT.md']
old=(B/'parser.original.rs').read_bytes();new=(B/'parser.candidate.rs').read_bytes();needle=b'    if parser.current_block_depth >= parser.nested_block_limit && parser.nested_block_limit != 0 {\n'
assert old.count(needle)==1 and old.replace(needle,needle+b'        parser.consume_until_end_of_block(block_type);\n')==new
assert H(B/'parser.candidate.rs')==read(E/'prior-FREEZE.json')['candidate_parser_sha256']=='2ac2c7f820ff5095c705446ff8a0f31507affe08e68bf6cc3735d5fb5bc38788'
co=read(B/'checksum.original.json');cn=read(B/'checksum.candidate.json');assert co.keys()==cn.keys() and co['package']==cn['package'] and co['files'].keys()==cn['files'].keys()
assert co['files']['src/parser.rs']==H(B/'parser.original.rs') and cn['files']['src/parser.rs']==H(B/'parser.candidate.rs')
assert [k for k in co['files'] if co['files'][k]!=cn['files'][k]]==['src/parser.rs']
newtest='/css/css-syntax/declaration-recovery-nesting-limit.html';oracle={}
for mode in ['inline','stylesheet']:
 for prop in ['padding-left','width']:
  for depth in [1,74,75,76]:
   name=f'{mode} {prop}: semicolon inside {depth} nested functions stays in the value'
   oracle[name]={'color':'rgb(255, 0, 0)','baseline':'FAIL' if mode=='inline' and prop=='padding-left' and depth==76 else 'PASS','candidate':'PASS'}
  oracle[f'{mode} {prop}: a declaration outside the function applies']={'color':'rgb(0, 0, 255)','baseline':'PASS','candidate':'PASS'}
 oracle[f'{mode}: recovery preserves declarations after the deep function']={'color':'rgb(0, 128, 0)','baseline':'PASS','candidate':'PASS'}
assert len(oracle)==22 and oracle==read(R/'ORACLE.json')
key=lambda r:(r['action'],r['test'],r.get('subtest'))
rows={};pins={}
for mode in ['baseline','candidate']:
 pins[mode]=read(B/(mode+'-before.json'));assert pins[mode]==read(B/(mode+'-after.json'))
 rr=[r for r in [json.loads(l) for l in (B/(mode+'-raw.jsonl')).read_text().splitlines()] if r.get('action') in ['test_status','test_end']];rows[mode]={key(r):r for r in rr};assert len(rows[mode])==len(rr)==69
 result=read(B/(mode+'-result.json'));assert result['raw_sha256']==H(B/(mode+'-raw.jsonl')) and result['console_sha256']==H(B/(mode+'-console.log'))
 assert {key(r):r['status'] for r in result['rows']}=={key(r):r['status'] for r in rr}
 assert {r['subtest']:r['status'] for r in rr if r['test']==newtest and r['action']=='test_status'}=={k:v[mode] for k,v in oracle.items()}
 assert rows[mode][('test_end',newtest,None)]['status']=='OK'
 assert pins[mode]['fixed']['third_party/rust/cssparser/src/parser.rs']==H(B/('parser.original.rs' if mode=='baseline' else 'parser.candidate.rs'))
 assert pins[mode]['fixed']['third_party/rust/cssparser/.cargo-checksum.json']==H(B/('checksum.original.json' if mode=='baseline' else 'checksum.candidate.json'))
 assert pins[mode]['fixed']['testing/web-platform/tests'+newtest]==H(B/'declaration-recovery-nesting-limit.html')
assert rows['baseline'].keys()==rows['candidate'].keys()
changes=[]
for k,before in rows['baseline'].items():
 after=rows['candidate'][k]
 if before['status']!=after['status']:
  assert k==('test_status',newtest,'inline padding-left: semicolon inside 76 nested functions stays in the value') and (before['status'],after['status'])==('FAIL','PASS');changes.append(k)
 else:assert before.get('expected')==after.get('expected')
assert len(changes)==1
assert sum(k[1]!=newtest for k in rows['candidate'])==46
fixed_changes=[k for k in pins['baseline']['fixed'] if pins['baseline']['fixed'][k]!=pins['candidate']['fixed'][k]]
assert set(fixed_changes)=={'third_party/rust/cssparser/src/parser.rs','third_party/rust/cssparser/.cargo-checksum.json'}
assert pins['baseline']['fixed'].keys()==pins['candidate']['fixed'].keys()
assert read(B/'baseline-exit.json')['exit_code']==1 and read(B/'candidate-exit.json')['exit_code']==0
build_before=read(B/'candidate-build-before.json');build_after=read(B/'candidate-build-after.json')
assert build_before['fixed']==build_after['fixed']==pins['candidate']['fixed']
assert build_before['binaries']==pins['baseline']['binaries'] and build_after['binaries']==pins['candidate']['binaries']
assert all(build_before['binaries'][k]!=v for k,v in build_after['binaries'].items())
phases=read(B/'candidate-build-result.json');assert [x['phase'] for x in phases]==['clean-parser','force-rust','link']
for phase in phases:assert phase['exit_code']==0 and phase['log_sha256']==H(B/('candidate-'+phase['phase']+'.log'))
assert 'Compiling cssparser v0.38.0' in (B/'candidate-force-rust.log').read_text() and 'Compiling style v0.0.1' in (B/'candidate-force-rust.log').read_text()
assert 'toolkit/library/build/XUL' in (B/'candidate-link.log').read_text()
print(json.dumps({'status':'PASS','files':len(m),'new_wpt':'1 FAIL / 21 PASS -> 22 PASS','unchanged_other_outcomes':46,'total_outcomes':69,'exact_source_and_checksum':True,'build_phases_passed':3,'formal_acceptance':'separate pending gate'}))
