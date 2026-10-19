import sys
assert sys.flags.isolated and sys.flags.no_site, 'Use python3 -I -S -B'
import argparse,hashlib,json,re
from pathlib import Path,PurePosixPath
R=Path(__file__).resolve().parent
H=lambda b:hashlib.sha256(b).hexdigest()
def pairs(xs):
 d={}
 for k,v in xs:assert k not in d,k;d[k]=v
 return d
def read(p):return json.loads(p.read_text(),object_pairs_hook=pairs)
p=argparse.ArgumentParser();p.add_argument('--manifest',required=True);a=p.parse_args()
assert H((R/'MANIFEST.json').read_bytes())==a.manifest
m=read(R/'MANIFEST.json');seen=set()
for n,h in m.items():
 q=PurePosixPath(n);assert str(q)==n and not q.is_absolute() and '..' not in q.parts
 assert n.casefold() not in seen;seen.add(n.casefold());s=R/n
 for x in [s,*s.parents]:assert not x.is_symlink(),str(x)
 assert H(s.read_bytes())==h,n
E=R/'evidence';B=E/'browser'
assert H((E/'producer-MANIFEST.json').read_bytes())=='ea51379cff0787a77d8ac1cdf6113132384c3870c7c94e65db7b93e312a72842'
assert H((E/'producer-FREEZE.json').read_bytes())=='a5864dee05dab3792318f2e98455e2b485a76eaaf71ba0315d4558f467699655'
assert H((E/'producer-both-candidate.rs').read_bytes())==read(E/'producer-MANIFEST.json')['integration/both-candidate.rs']
assert H((E/'prior-review-MANIFEST.json').read_bytes())=='6fd0b95c3a4ffcbd7f6558685606aeb5a00772207894ebe485cb809b3e587649'
assert H((E/'prior-review-FREEZE.json').read_bytes())=='26e381f99577b75d8bfb1e6695b40a37fb6288edab88d489d95afaa963ea979c'
assert H((E/'prior-review-REPORT.md').read_bytes())==read(E/'prior-review-MANIFEST.json')['REPORT.md']
c=read(E/'COMPOSITION.json');both=(E/'producer-both-candidate.rs').read_text();composed=(E/'composed-proposal.rs').read_text();original=(B/'custom_properties.original.rs').read_text();candidate=(B/'custom_properties.candidate.rs').read_text();d=c['parity_format_delta']
assert H(both.encode())==c['both_source_sha256']
assert both.count(d['old'])==1 and both.replace(d['old'],d['new'])==composed
assert original.count(c['old'])==1 and original.replace(c['old'],c['new'])==composed
assert H(original.encode())==c['original_sha256']
assert candidate==composed and H(candidate.encode())==c['composed_sha256']==read(E/'FORMAT-BINDING.json')['sha256']=='9f7dfa8368c3b3e99855d168ff24b695938a20afb08e693922a87d888b7c1355'
# Independent front-consuming decoder for the fixture's ordinary-character/escape grammar.
def decode(raw):
 quote=raw[0];out='';i=1
 while i<len(raw):
  c=raw[i];i+=1
  if c==quote:return out
  if c=='\\':
   if i==len(raw):return out
   out+=raw[i];i+=1
  else:out+=c
 return out
oracle={}
for quote in ['"',"'"]:
 for count in range(5):
  for terminal in ([True] if count>0 and count%2==0 else [False,True]):
   raw=quote+'example'+'\\'*count+(quote if terminal else '')
   expected='example'+'\\'*(count//2)+(quote if terminal and count%2 else '')
   assert decode(raw)==expected
   name=f'{quote} with {count} backslashes and '+('a final quote' if terminal else 'EOF')
   oracle[name]={'raw':raw,'decoded':expected,'baseline':'FAIL' if terminal and count%2 else 'PASS','candidate':'PASS'}
for name in ['closed fallback','missing quote and parenthesis']:
 oracle[name]={'decoded':'example','baseline':'PASS','candidate':'PASS'}
assert len(oracle)==18 and sum(x['baseline']=='FAIL' for x in oracle.values())==4
assert oracle==read(R/'ORACLE.json')
new='/css/css-variables/quoted-eof-escaped-terminal-quote.html';semantics='/css/css-variables/quoted-eof-string-semantics.html'
key=lambda r:(r['action'],r['test'],r.get('subtest'))
rows={};pins={}
for mode in ['baseline','candidate']:
 before=read(B/(mode+'-before.json'));after=read(B/(mode+'-after.json'));assert before==after; pins[mode]=before
 rr=[r for r in [json.loads(l) for l in (B/(mode+'-raw.jsonl')).read_text().splitlines()] if r.get('action') in ['test_status','test_end']]
 rows[mode]={key(r):r for r in rr};assert len(rr)==len(rows[mode])
 result=read(B/(mode+'-result.json'))
 assert result['raw_sha256']==H((B/(mode+'-raw.jsonl')).read_bytes())
 assert result['console_sha256']==H((B/(mode+'-console.log')).read_bytes())
 assert {key(r):r['status'] for r in result['rows']}=={key(r):r['status'] for r in rr}
 nr={r['subtest']:r['status'] for r in rr if r['action']=='test_status' and r['test']==new}
 assert nr=={name:o[mode] for name,o in oracle.items()}
 assert rows[mode][('test_end',new,None)]['status']=='OK'
source='servo/components/style/custom_properties.rs';wpt='testing/web-platform/tests'+new
assert pins['baseline']['fixed'][source]==H((B/'custom_properties.original.rs').read_bytes())=='fe09e9ee8e7eb4efadad9f93974770b3adcaa97c95ebfee123149a50c4c19665'
assert pins['candidate']['fixed'][source]==H(candidate.encode())
assert pins['baseline']['fixed'][wpt]==pins['candidate']['fixed'][wpt]==H((B/'quoted-eof-escaped-terminal-quote.html').read_bytes())
assert {k:v for k,v in pins['baseline']['fixed'].items() if k!=source}=={k:v for k,v in pins['candidate']['fixed'].items() if k!=source}
build=read(B/'build-after.json');assert build['exit_code']==0 and build['build_log_sha256']==H((B/'build.log').read_bytes())
actual=[]
for group in ['fixed','binaries']:
 for path,old in pins['baseline'][group].items():
  now=pins['candidate'][group][path]
  if old!=now:actual.append({'group':group,'path':path,'before':old,'after':now})
assert actual==build['changes'] and len(actual)==3
assert read(B/'candidate-exit.json')['exit_code']==0
assert rows['baseline'].keys()==rows['candidate'].keys()
changes=[]
for k,old in rows['baseline'].items():
 now=rows['candidate'][k]
 if old['status']!=now['status']:
  assert k[1] in [new,semantics] and k[2] in oracle and oracle[k[2]]['baseline']=='FAIL'
  assert (old['status'],now['status'])==('FAIL','PASS');changes.append(k)
 else:assert old.get('expected')==now.get('expected')
assert len(changes)==8
remaining=[r for r in rows['candidate'].values() if r['test']==semantics and r['status']=='FAIL']
assert len(remaining)==0
broad=[r for r in rows['candidate'].values() if r['test']==semantics and r['action']=='test_status'];assert len(broad)==22 and all(r['status']=='PASS' for r in broad)
endpoint=[r for r in rows['candidate'].values() if r['test']=='/css/css-variables/quoted-eof-fallback-endpoints.html' and r['action']=='test_status'];assert len(endpoint)==38 and all(r['status']=='PASS' for r in endpoint)
parity=[r for r in rows['candidate'].values() if r['test']=='/css/css-variables/quoted-eof-backslash-parity.html' and r['action']=='test_status'];assert len(parity)==18 and all(r['status']=='PASS' for r in parity)
print(json.dumps({'status':'PASS','files':len(m),'closure_original':'4 FAIL / 14 PASS','closure_candidate':'18 PASS','endpoint_controls':38,'other_semantic_same_repair_transitions':4,'broad_semantic_pass':22,'parity_controls':18,'raw_result_keys':len(rows['candidate']),'changed_keys':len(changes)}))
