#!/usr/bin/env python3
import sys
assert sys.flags.isolated and sys.flags.no_site
import hashlib,json,os,subprocess
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parent
def pairs(items):
 d={}
 for k,v in items:
  assert k not in d, ('duplicate',k)
  d[k]=v
 return d
def read(p): return json.loads(p.read_text(),object_pairs_hook=pairs)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def auth(root,manifest,freeze):
 assert sha(root/'MANIFEST.json')==freeze['manifest_sha256']
 expected=set(manifest)|{'MANIFEST.json','FREEZE.json'}
 directories=set()
 for n in expected:
  q=Path(n)
  assert n==q.as_posix() and not q.is_absolute() and all(x not in ('..','.') for x in q.parts)
  directories.update(str(a) for a in q.parents if str(a)!='.')
 actual=set();dirs=set()
 for q in root.rglob('*'):
  assert not q.is_symlink(), str(q)
  n=q.relative_to(root).as_posix()
  if q.is_dir(): dirs.add(n)
  else: assert q.is_file();actual.add(n)
 assert actual==expected and dirs==directories
 for n,h in manifest.items(): assert sha(root/n)==h,n
m=read(ROOT/'MANIFEST.json');auth(ROOT,m,read(ROOT/'FREEZE.json'))
p=ROOT/'proposal'
assert sha(p/'FREEZE.json')=='15000e7ba5e31072934bd59ab124d18d0876082b5e62e578531eb0d9dfabdde5'
assert sha(p/'MANIFEST.json')=='ad253012e5c2aab47932b163508241d6103271c18d6f352b914a682d93cd0e40'
auth(p,read(p/'MANIFEST.json'),read(p/'FREEZE.json'))
r=read(ROOT/'baseline/RUN.json');raw=[json.loads(x,object_pairs_hook=pairs) for x in (ROOT/'baseline/raw.json').read_text().splitlines() if x.strip()]
rows=[x for x in raw if x.get('action')=='test_status'];ends=[x for x in raw if x.get('action')=='test_end']
assert rows==r['rows'] and r['stable_after'] and r['exit']==1
assert len({(x['test'],x['subtest']) for x in rows})==6
assert Counter(x['status'] for x in rows)=={'FAIL':2,'PASS':4}
assert len(ends)==1 and ends[0]['status']=='OK'
assert {x['subtest'] for x in rows if x['status']=='FAIL'}=={'CSS-wide initial to inherit, same payload','CSS-wide inherit to initial, same payload'}
assert all('Updated effect URL taint' in x['message'] for x in rows if x['status']=='FAIL')
test='testing/web-platform/tests/css/css-values/animation-csswide-equal-payload-taint.html'
assert r['pins'][test]==sha(p/'csswide-endpoint-taint.html')=='2e585feb0b3aef4304c07dba19b12de9a71258ada7ec3af4d64201e19e9309cf'
replay=json.loads((ROOT/'replay.stdout').read_text());assert replay['status']=='PASS' and replay['inputs']==49
if '--replay' in sys.argv:
 env={k:v for k,v in os.environ.items() if not k.startswith(('PYTHON','LEAN_'))}
 result=subprocess.run([sys.executable,'-I','-S',str(p/'check.py'),'--checks'],capture_output=True,text=True,env=env)
 assert result.returncode==0,(result.stdout,result.stderr)
 assert json.loads(result.stdout)==replay
print(json.dumps({'status':'PASS','inputs':len(m),'proposal_inputs':49,'baseline':'2 FAIL / 4 PASS / 1 OK','source_approval':'scoped','candidate_build_browser':'root separate gate'}))
