import hashlib,json,os,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; HERE=Path(__file__).resolve().parent
GIT=['git','-c','core.fsmonitor=false']; PATCH=HERE/'final.patch'
FILES=['servo/components/style/custom_properties.rs','testing/web-platform/tests/css/css-properties-values-api/registered-substituted-inherit-restyle.html']
def call(args,env=None): return subprocess.check_output(GIT+args,cwd=ROOT,env=env)
head=call(['rev-parse','HEAD']).decode().strip(); rows=[]
assert not call(['diff','--cached','--name-only']).strip()
for label,base in [('branch',head),('upstream','976279105b2e78b8666a959eb3f25c9176cefaf8a')]:
 with tempfile.TemporaryDirectory(prefix='css-inherit73-index-') as tmp:
  env={**os.environ,'GIT_INDEX_FILE':str(Path(tmp)/'index')}
  call(['read-tree',base],env)
  before=call(['write-tree'],env)
  call(['apply','--cached','--check',str(PATCH)],env)
  call(['apply','--cached',str(PATCH)],env)
  assert sorted(call(['diff','--cached','--name-only',base],env).decode().splitlines())==sorted(FILES)
  pins={f:hashlib.sha256(call(['show',':'+f],env)).hexdigest() for f in FILES}
  if label=='branch':
   for f,h in pins.items():assert hashlib.sha256((ROOT/f).read_bytes()).hexdigest()==h
  call(['apply','--cached','--reverse',str(PATCH)],env)
  assert call(['write-tree'],env)==before
  rows.append({'label':label,'commit':base,'apply':'PASS','reverse':'PASS','staged_source_pins':pins})
record={'patch_sha256':hashlib.sha256(PATCH.read_bytes()).hexdigest(),'exact_files':FILES,'bases':rows,'scope':'Exact patch apply/reverse only; no isolated upstream runtime.'}
(HERE/'STANDALONE-PACKAGING.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2))
