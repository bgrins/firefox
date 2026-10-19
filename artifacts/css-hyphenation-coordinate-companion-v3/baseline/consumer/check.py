import argparse,hashlib,json,os,re,shutil,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--manifest-sha',required=True);parser.add_argument('--lean',required=True);args=parser.parse_args()
raw=(ROOT/'MANIFEST.json').read_bytes();assert hashlib.sha256(raw).hexdigest()==args.manifest_sha
manifest=json.loads(raw)
for name,digest in manifest['files'].items():
    rel=Path(name);assert not rel.is_absolute()and '..'not in rel.parts
    path=ROOT/rel;assert not path.is_symlink()and path.resolve().is_relative_to(ROOT)
    assert hashlib.sha256(path.read_bytes()).hexdigest()==digest,name
for path in ROOT.rglob('*'):
    if path.is_file():
        name=str(path.relative_to(ROOT));assert name in manifest['files']or name in ['MANIFEST.json','FREEZE.json']or name.startswith('development-build/')or name.startswith('provider-bridge-v1/development-build/'),name
print('authenticated',len(manifest['files']),'files',flush=True)
tool=json.loads((ROOT/'TOOL.json').read_text());clang=Path(tool['clang']);assert hashlib.sha256(clang.read_bytes()).hexdigest()==tool['sha256'];assert subprocess.check_output([clang,'--version'],text=True)==tool['version']
lean=Path(args.lean).resolve();leanTool=json.loads((ROOT/'LEAN-TOOL.json').read_text());assert hashlib.sha256(lean.read_bytes()).hexdigest()==leanTool['lean_sha256'];assert leanTool['lean_version_contains']in subprocess.check_output([lean,'--version'],text=True)
out=ROOT/'development-build/full';out.mkdir(parents=True,exist_ok=True)
sdk=Path('/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk')
flags=[str(clang),'-std=c++20','-isysroot',str(sdk),'-isystem',str(clang.parent.parent/'include/c++/v1'),'-O1','-g','-fsanitize=undefined','-I',str(ROOT/'provider-bridge-v1/source/providers/intl/icu/source/common')]
receipts=[]
def run(name,args,input=None,env=None):
    cmd=list(map(str,args));r=subprocess.run(cmd,input=input,capture_output=True,text=True,env=env,timeout=180)
    (out/(name+'.log')).write_text(r.stdout+r.stderr);receipts.append({'name':name,'args':cmd,'exit':r.returncode});(out/'CONSUMER-REPLAY.json').write_text(json.dumps(receipts,indent=2)+'\n')
    print(name,r.returncode,flush=True);assert r.returncode==0,(name,r.stdout,r.stderr);return r.stdout
commands=[[sys.executable,ROOT/'native/build-transform.py'],[sys.executable,ROOT/'native/extract-measurement.py'],[sys.executable,ROOT/'native/extract-hyphen-consumer.py'],flags+[out/'measurement.cpp','-o',out/'measurement'],flags+[out/'hyphen-consumer.cpp','-licucore','-o',out/'hyphen-consumer'],[sys.executable,ROOT/'check-hyphen-consumer-development.py']]
for i,command in enumerate(commands):run('baseline-stage-'+str(i),command)
for name in ['measurement-coordinate-input.txt','measurement-coordinate-output.txt']:shutil.copy2(ROOT/'seeds'/name,out/name)
coordinate=run('baseline-coordinate',[out/'measurement'],input=(out/'measurement-coordinate-input.txt').read_text());assert coordinate==(ROOT/'seeds/measurement-coordinate-output.txt').read_text()
(out/'commands.json').write_text(json.dumps([{'name':'compile-provider','args':flags+['-c'],'role':'fresh shared compiler flags, not a claimed compilation'}],indent=2)+'\n')
run('metric-build',[sys.executable,ROOT/'native/build-metric-providers.py'])
run('metric-replay',[sys.executable,ROOT/'native/check-metric-providers.py'])
run('spacing-rebuild-and-replay',[sys.executable,ROOT/'native/build-spacing-consumer.py'])
leanOut=ROOT/'development-build/lean';leanOut.mkdir(parents=True,exist_ok=True)
for p in leanOut.glob('*.olean'):p.unlink()
env=dict(os.environ,LEAN_PATH=str(leanOut));reports=0
for module in ['GlyphBreakBits','SpacingEligibility']:
    path=ROOT/'lean-stream'/(module+'.lean');source=path.read_text();assert not re.search(r'\b(sorry|admit|axiom|native_decide|bv_decide)\b',source)
    run(module,[lean,'-o',leanOut/(module+'.olean'),path],env=env)
    namespace=re.search(r'^namespace ([\w.]+)',source,re.M)[1]
    theorems=re.findall(r'^(?:@\[[^\n]*\]\s*)?theorem ([\w.]+)',source,re.M)
    audit=leanOut/(module+'Axioms.lean');audit.write_text('import '+module+'\n'+'\n'.join('#print axioms '+namespace+'.'+name for name in theorems)+'\n')
    result=run(module+'-axioms',[lean,audit],env=env);assert 'sorryAx'not in result
    for group in re.findall(r'depends on axioms: \[([^]]*)\]',result):assert set(map(str.strip,group.split(',')))<={'propext','Classical.choice','Quot.sound',''}
    reports+=len(theorems)
replay=json.loads((out/'metric-providers/REPLAY.json').read_text())
result={'manifest_sha256':args.manifest_sha,'files':len(manifest['files']),'lean_modules':2,'theorem_reports':reports,'fixed_cases':[{k:v for k,v in r.items()if k!='differences'}|{'differences':len(r['differences'])}for r in replay['records']],'spacing':json.loads((out/'spacing-consumer/REPLAY.json').read_text()),'status':'Fresh source-only native and Lean development replay passed; complete provider/ownership scope remains open.'}
(ROOT/'development-build/RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
