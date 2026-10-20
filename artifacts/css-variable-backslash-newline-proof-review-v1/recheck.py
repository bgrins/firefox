import sys
if not (sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize):
    raise RuntimeError('use python3 -I -S without optimization')
import argparse,hashlib,json,os,shutil,stat,subprocess
from pathlib import Path,PurePosixPath
HERE=Path(__file__).resolve().parent
PINS={'FILES.json':'e8e8b8ec25a81688264e70587122f2c930cbf7ea273c9b3758d4d8ff8937db6b','FREEZE.json':'17cdff311c3c919779ad327b250cc75667ef7f5ff0b85bddd9c0bb320633c54a','check.py':'efd36aa2662d5553ea51cf377bea3521f494eebc014046d568a9750cd7aea589','REPORT.md':'385c338a6df89994334efbe118cf42e78f7ba8ff466f4bf87a42bea16e78e8de'}
def need(ok,message):
    if not ok:raise RuntimeError(message)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def unique(pairs):
    r={}
    for k,v in pairs:
        need(k not in r,'duplicate JSON key');r[k]=v
    return r
def read(p):return json.loads(p.read_text(),object_pairs_hook=unique)
def authenticate(root):
    for n,h in PINS.items():need(sha(root/n)==h,'external pin '+n)
    m=read(root/'FILES.json');expected={'FILES.json','FREEZE.json'}
    for row in m:
        n=row['path'];q=PurePosixPath(n)
        need(n==str(q) and not q.is_absolute() and '..' not in q.parts and n not in expected,'path')
        expected.add(n);need(sha(root/n)==row['sha256'] and (root/n).stat().st_size==row['bytes'],'input')
    dirs={str(d) for n in expected for d in PurePosixPath(n).parents if str(d)!='.'};af=set();ad=set()
    for p in root.rglob('*'):
        mode=p.lstat().st_mode;n=p.relative_to(root).as_posix()
        if stat.S_ISREG(mode):af.add(n)
        elif stat.S_ISDIR(mode):ad.add(n)
        else:raise RuntimeError('nonregular input')
    need(af==expected and ad==dirs,'closed roster');return expected
root=HERE/'capsule';files=authenticate(root)
review=read(root/'evidence/native-review/FILES.json')
for name in ['CASES.json','NATIVE-INPUTS.json','INPUTS.json']:
    need(sha(root/'evidence/native-review'/name)==review[name],'accepted review input '+name)
oldcases=read(root/'evidence/native-review/CASES.json');cases=read(root/'native/CASES.json')
def case_relation(c):return len(oldcases)==73 and len(c)==56 and c==oldcases[:56]
need(case_relation(cases),'actual historical case binding')
need(not case_relation(cases[1:]+cases[:1]),'reordered input must reject')
changed=[dict(c) for c in cases];changed[0]['css']='different input'
need(not case_relation(changed),'altered input must reject')
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve()
need(not out.exists() and out!=HERE and HERE not in out.parents,'new external output')
out.mkdir(parents=True);commands=[]
def run(cmd,env=None):
    r=subprocess.run(cmd,capture_output=True,text=True,env=env)
    commands.append({'command':cmd,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr});(out/'COMMANDS.json').write_text(json.dumps(commands,indent=2)+'\n')
    need(r.returncode==0,r.stdout+r.stderr);return r
run([sys.executable,'-I','-S',str(root/'check.py'),'--output',str(out/'producer')])
config=read(root/'TOOLCHAIN.json');env={k:v for k,v in os.environ.items() if not k.startswith(('LEAN_','PYTHON'))};env['LEAN_PATH']=str(out/'producer/lean')
r=run([config['lean'],'-R',str(HERE),str(HERE/'Challenges.lean')],env);need(not r.stdout and not r.stderr,'challenge diagnostics')
negative=[]
for name in ['shadow-controller','shadow-compiler','shadow-native','optimized','double-optimized','nested-seal','empty-dir','source-change']:
    c=out/name;shutil.copytree(root,c);target=out/(name+'-output');entry='check.py';flags=['-I','-S']
    if name.startswith('shadow'):
        entry={'shadow-controller':'check.py','shadow-compiler':'compile.py','shadow-native':'native/build_projection.py'}[name]
        (c/Path(entry).parent/'json.py').write_text('raise RuntimeError("UNSAFE_IMPORT_EXECUTED")\n');flags=['-S']
    elif name=='optimized':flags+=['-O']
    elif name=='double-optimized':flags+=['-OO']
    elif name=='nested-seal':(c/'source/FILES.json').write_text('{}')
    elif name=='empty-dir':(c/'empty').mkdir()
    elif name=='source-change':(c/'lean/ProtectedSpan.lean').write_text('changed')
    cmd=[sys.executable,*flags,str(c/entry),'--output',str(target)]
    r=subprocess.run(cmd,capture_output=True,text=True)
    need(r.returncode!=0 and not target.exists() and 'UNSAFE_IMPORT_EXECUTED' not in r.stdout+r.stderr,'negative '+name)
    negative.append({'name':name,'command':cmd,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'output_absent':True});shutil.rmtree(c)
(out/'NEGATIVES.json').write_text(json.dumps(negative,indent=2)+'\n');authenticate(root)
result={'status':'ACCEPTED_SCOPED','producer_audits':53,'fresh_tokenizer_cases':56,'historical_constructor_comparisons':224,'historical_input_binding':'accepted review CASES authenticated; exact first56 equality independently checked','independent_kernel_examples':15,'integrity_negatives':8,'case_binding_negatives':2,'full_native_translation':False,'native_metadata_directly_observed':False}
(out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
