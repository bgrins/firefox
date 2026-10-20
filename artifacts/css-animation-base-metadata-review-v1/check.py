import sys
assert sys.flags.isolated and sys.flags.no_site
import hashlib,json,stat,difflib,tempfile,subprocess,shutil
from pathlib import Path
R=Path(__file__).resolve().parent
def pairs(items):
 d={}
 for k,v in items:
  assert k not in d,k
  d[k]=v
 return d
def read(p):return json.loads(p.read_text(),object_pairs_hook=pairs)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
f=read(R/'FREEZE.json');assert sha(R/'MANIFEST.json')==f['manifest_sha256']
m=read(R/'MANIFEST.json');files=set(m)|{'MANIFEST.json','FREEZE.json'};dirs=set()
for n in files:
 p=Path(n);assert n==p.as_posix() and not p.is_absolute() and '..' not in p.parts
 dirs.update(str(a) for a in p.parents if str(a)!='.')
af=set();ad=set()
for p in R.rglob('*'):
 mode=p.lstat().st_mode;assert not p.is_symlink(),str(p)
 if stat.S_ISDIR(mode):ad.add(p.relative_to(R).as_posix())
 else:assert stat.S_ISREG(mode);af.add(p.relative_to(R).as_posix())
assert af==files and ad==dirs
for n,h in m.items():assert sha(R/n)==h,n
proposal=read(R/'PROPOSAL.json')
for n,k in [('KeyframeEffect.original.cpp','original_sha256'),('KeyframeEffect.candidate.cpp','candidate_sha256'),('native.patch','patch_sha256')]:assert sha(R/n)==proposal[k]
run=read(R/'evidence/RUN.json');assert run['stable_after'] is True and run['suite_ends']==1 and run['exit']==1
assert sha(R/'evidence/probe.html')=='ad13944efa2fb29e7d38c672f3fe069165e5a181f0f5ff968d22193d63ce7f80'
rows=[json.loads(l,object_pairs_hook=pairs) for l in (R/'evidence/raw.json').read_text().splitlines()]
tests=[x for x in rows if x.get('action')=='test_status'];expected=[]
for direction in ['clean to tainted','tainted to clean']:
 expected.extend([(f'Neutral start {direction}, same payload','FAIL'),(f'Neutral start {direction}, different payload','PASS'),(f'Neutral end {direction}, same payload','FAIL'),(f'Explicit replacement ignores base {direction}','PASS')])
assert [(x['subtest'],x['status']) for x in tests]==expected
for x in tests:
 if x['status']=='FAIL':assert x['message'].startswith('assert_equals: Immediate effect URL taint expected ')
ends=[x for x in rows if x.get('action')=='test_end'];assert len(ends)==1 and ends[0]['status']=='OK'
assert sha(R/'evidence/probe-v2.html')=='3c3f231171b914e38fc60bacdc967aa34605a6b545ee5e4f2b9818131564b5d6'
v2=[json.loads(l,object_pairs_hook=pairs) for l in (R/'evidence/baseline-v2-raw.json').read_text().splitlines()]
v2tests=[x for x in v2 if x.get('action')=='test_status'];assert [(x['subtest'],x['status']) for x in v2tests]==expected
for x in v2tests:
 if x['status']=='FAIL':assert x['message'].startswith('assert_equals: Immediate effect URL taint expected ')
assert len([x for x in v2 if x.get('action')=='test_end' and x['status']=='OK'])==1

def diff(a,b,n):return ''.join(difflib.unified_diff(a.splitlines(True),b.splitlines(True),fromfile='a/'+n,tofile='b/'+n))
native='dom/animation/KeyframeEffect.cpp'
assert diff((R/'KeyframeEffect.original.cpp').read_text(),(R/'KeyframeEffect.candidate.cpp').read_text(),native)==(R/'native.patch').read_text()
paths=[native,'servo/components/style/properties_and_values/value.rs','servo/ports/geckolib/glue.rs']
assert ''.join(diff((R/'standalone/original'/n).read_text(),(R/'standalone/candidate'/n).read_text(),n) for n in paths)==(R/'standalone-native.patch').read_text()
assert 'oldSegments' not in (R/'standalone-native.patch').read_text()
assert 'custom_properties_map.rs' not in (R/'standalone-native.patch').read_text()
testpath='testing/web-platform/tests/css/css-values/animation-base-equal-payload-taint.html'
testdiff=''.join(difflib.unified_diff([],(R/'evidence/probe-v2.html').read_text().splitlines(True),fromfile='/dev/null',tofile='b/'+testpath))
for prefix in ['stack','standalone']:
 patch=R/(prefix+'-with-test.patch');basepatch=R/('native.patch' if prefix=='stack' else 'standalone-native.patch')
 assert patch.read_text()==basepatch.read_text()+testdiff
 with tempfile.TemporaryDirectory(prefix='base-metadata-review-') as td:
  d=Path(td)
  ps=[native] if prefix=='stack' else paths
  for n in ps:
   q=d/n;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/'KeyframeEffect.original.cpp' if prefix=='stack' else R/'standalone/original'/n,q)
  for reverse in [False,True]:
   p=subprocess.run(['patch','--batch','--fuzz=0','-p1']+(['-R'] if reverse else [])+['-i',str(patch)],cwd=d,capture_output=True,text=True)
   assert p.returncode==0,p.stdout+p.stderr
   assert 'fuzz' not in p.stdout.lower() and 'offset' not in p.stdout.lower()
   for n in ps:
    target=R/('KeyframeEffect.original.cpp' if reverse else 'KeyframeEffect.candidate.cpp') if prefix=='stack' else R/'standalone'/('original' if reverse else 'candidate')/n
    assert (d/n).read_bytes()==target.read_bytes()
   if not reverse:assert (d/testpath).read_bytes()==(R/'evidence/probe-v2.html').read_bytes()
   else:assert not (d/testpath).exists()
for record in read(R/'spec/INDEX.json'):assert sha(R/'spec'/record['file'])==record['sha256']
print(json.dumps({'status':'PASS','inputs':len(m),'baseline_cases':8,'failures':4,'controls':4,'patch_apply_reverse':['stack','standalone'],'candidate_runtime':'NOT_REVIEWED','formal':'SEPARATE_GATE'}))
