import argparse,hashlib,json,os,runpy,shutil,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parent
parser=argparse.ArgumentParser()
parser.add_argument('--manifest-sha',required=True)
parser.add_argument('--lean',type=Path)
parser.add_argument('--output',type=Path)
parser.add_argument('--authenticate-only',action='store_true')
a=parser.parse_args()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def authenticate():
 assert sha(R/'MANIFEST.json')==a.manifest_sha
 files=json.loads((R/'MANIFEST.json').read_text())['files']
 actual={str(p.relative_to(R))for p in R.rglob('*')if p.is_file()}
 assert actual==set(files)|{'MANIFEST.json','FREEZE.json'}
 for name,digest in files.items():
  rel=Path(name);assert not rel.is_absolute()and '..'not in rel.parts
  p=R/rel;assert not p.is_symlink()and p.resolve().is_relative_to(R)and sha(p)==digest,name
 return len(files)
count=authenticate()
provenance=json.loads((R/'PROVENANCE.json').read_text())
old='prevMostRecentWordBoundary < oldHyphenBufferLength'
new='prevMostRecentWordBoundary < bufferRange.start'
original=(R/'guard/source/original-gfxTextRun.cpp').read_text()
candidate=(R/'guard/source/candidate-gfxTextRun.cpp').read_text()
assert original.count(old)==1 and candidate==original.replace(old,new)
assert sha(R/'browser/fix-coordinate-v1.patch')==provenance['browser_patch_sha256']
if a.authenticate_only:print('authenticated',count,'inputs and exact source delta');raise SystemExit
assert a.output and a.lean
out=a.output.resolve();assert R!=out and R not in out.parents
out.mkdir(parents=True,exist_ok=False)
receipts=[]
def run(name,args,data=None,timeout=900):
 result=subprocess.run(list(map(str,args)),input=data,capture_output=True,timeout=timeout)
 (out/(name+'.stdout')).write_bytes(result.stdout);(out/(name+'.stderr')).write_bytes(result.stderr)
 receipts.append({'name':name,'args':list(map(str,args)),'exit':result.returncode})
 (out/'COMMANDS.json').write_text(json.dumps(receipts,indent=2)+'\n')
 print(name,result.returncode,flush=True)
 assert result.returncode==0,(name,result.stderr.decode(errors='replace'))
 return result.stdout
baseline=out/'baseline';shutil.copytree(R/'baseline',baseline)
run('baseline-source-replay',[sys.executable,'-I','-S','-B',baseline/'check.py','--manifest-sha',provenance['baseline_manifest_sha256'],'--lean',a.lean])
run('guard-kernel',[sys.executable,'-I','-S','-B',R/'guard/check.py','--manifest-sha',provenance['guard_manifest_sha256'],'--lean',a.lean,'--output',out/'guard-result'])
consumer=baseline/'consumer';full=consumer/'development-build/full'
helper=runpy.run_path(str(consumer/'native/extract-full.py'))
marker='uint32_t gfxTextRun::BreakAndMeasureText('
baselineBody=helper['full'](consumer/'source/providers/gfx/thebes/gfxTextRun.cpp',marker)
rootOriginal=helper['full'](R/'guard/source/original-gfxTextRun.cpp',marker)
rootCandidate=helper['full'](R/'guard/source/candidate-gfxTextRun.cpp',marker)
assert baselineBody==rootOriginal and rootCandidate==baselineBody.replace(old,new)
flags=next(x['args']for x in json.loads((full/'commands.json').read_text())if x['name']=='compile-provider')
flags=flags[:flags.index('-c')]
executables={}
for family,header,driver,exe in [
 ('initial',full/'hyphen-consumer.hpp',full/'hyphen-consumer.cpp',full/'hyphen-consumer'),
 ('full-spacing',full/'spacing-consumer/spacing.hpp',full/'spacing-consumer/spacing.cpp',full/'spacing-consumer/spacing')]:
 text=header.read_text();assert text.count(baselineBody)==1
 target=out/family;target.mkdir()
 (target/header.name).write_text(text.replace(baselineBody,rootCandidate))
 (target/driver.name).write_bytes(driver.read_bytes())
 args=flags+['-I'+str(full),'-I'+str(header.parent),target/driver.name,'-licucore','-o',target/'candidate']
 run(family+'-compile-candidate',args)
 executables[family]={'original':exe,'candidate':target/'candidate'}
fixture=json.loads((R/'fixtures/PROVENANCE.json').read_text())
assert sha(full/'hyphen-consumer-matrix-input.txt')==fixture['matrix_input_sha256']
records=[]
for family,variants in executables.items():
 for name,path in [('admitted',R/'fixtures/admitted-coordinate-consumer-input.txt'),('controls',full/'hyphen-consumer-matrix-input.txt')]:
  data=path.read_bytes();outputs={}
  for variant,exe in variants.items():
   actual=run(family+'-'+name+'-'+variant,[exe],data)
   assert not (out/(family+'-'+name+'-'+variant+'.stderr')).read_bytes()
   outputs[variant]=actual.splitlines()
   assert len(outputs[variant])==len(data.splitlines())
   key=('matrix_original_output_sha256'if name=='controls'else'admitted_'+variant+'_output_sha256')
   assert hashlib.sha256(actual).hexdigest()==fixture[key],(family,name,variant)
  changes=[i for i,(x,y)in enumerate(zip(outputs['original'],outputs['candidate']))if x!=y]
  assert changes==([1,9]if name=='admitted'else[])
  if name=='admitted':
   for i in range(0,16,2):assert outputs['candidate'][i].split()[5:]==outputs['candidate'][i+1].split()[5:]
   for i in [0,1,8,9]:assert int(outputs['candidate'][i].split()[5])==21
  records.append({'family':family,'fixture':name,'rows':len(outputs['candidate']),'changed_indices':changes})
assert authenticate()==count
result={'files':count,'source_bindings':helper['records'],'native':records,'guard':json.loads((out/'guard-result/RESULT.json').read_text()),'scope':'Narrow guard candidate replay; retained dictionary masks are explicit fixtures. No full ownership/native memory/font/IEEE refinement.'}
(out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'files':count,'native':records,'guard_modules':result['guard']['modules'],'guard_reports':result['guard']['theorem_reports']}))
