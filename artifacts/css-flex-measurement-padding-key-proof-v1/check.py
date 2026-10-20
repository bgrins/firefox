import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit("require isolated nonoptimized Python without site")
sys.dont_write_bytecode = True
from pathlib import Path
import argparse, hashlib, json, os, re, stat, subprocess

ROOT=Path(__file__).resolve().parent
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def unique_pairs(pairs):
    value={}
    for key,item in pairs:
        if key in value: raise RuntimeError('duplicate JSON key')
        value[key]=item
    return value
def read(path): return json.loads(path.read_text(),object_pairs_hook=unique_pairs)
def authenticate():
    for name in ['FILES.json','FREEZE.json']:
        if not stat.S_ISREG((ROOT/name).lstat().st_mode): raise RuntimeError('nonregular seal')
    manifest=read(ROOT/'FILES.json');seal=read(ROOT/'FREEZE.json')
    if digest(ROOT/'FILES.json')!=seal['files_sha256'] or digest(ROOT/'check.py')!=seal['checker_sha256']:
        raise RuntimeError('seal mismatch')
    directories=set();expected=set(manifest)|{'FILES.json','FREEZE.json'}
    for name,value in manifest.items():
        path=Path(name)
        if path.is_absolute() or str(path)!=name or any(x in ['.','..'] for x in path.parts) or not re.fullmatch('[0-9a-f]{64}',value):
            raise RuntimeError('invalid manifest path/hash')
        directories.update(str(x) for x in path.parents if str(x)!='.')
    actual=set()
    def walk(directory):
        for item in os.scandir(directory):
            path=Path(item.path);relative=str(path.relative_to(ROOT));mode=item.stat(follow_symlinks=False).st_mode
            if stat.S_ISDIR(mode):
                if relative not in directories: raise RuntimeError('unexpected directory')
                walk(path)
            elif stat.S_ISREG(mode): actual.add(relative)
            else: raise RuntimeError('nonregular source')
    walk(ROOT)
    if actual!=expected: raise RuntimeError('source roster mismatch')
    for name,value in manifest.items():
        if digest(ROOT/name)!=value: raise RuntimeError('source hash mismatch: '+name)
    for row in read(ROOT/'SOURCE-BINDINGS.json'):
        source=ROOT/row['source'];body=row['body']
        if digest(source)!=row['source_sha256'] or source.read_text().count(body)!=1 or hashlib.sha256(body.encode()).hexdigest()!=row['body_sha256']:
            raise RuntimeError('source binding mismatch')
    return manifest

def invoke(command,env):
    p=subprocess.run(command,capture_output=True,text=True,env=env)
    return dict(command=command,exit=p.returncode,stdout=p.stdout,stderr=p.stderr)

def main():
    authenticate()
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    out=args.output.resolve()
    if not args.output.is_absolute() or out.exists() or out.is_relative_to(ROOT):
        raise SystemExit('fresh absolute external output required')
    config=read(ROOT/'TOOLCHAIN.json')
    for tool in ['lean','clang']:
        if digest(Path(config[tool]))!=config[tool+'_sha256']: raise RuntimeError(tool+' executable mismatch')
    out.mkdir(parents=True)
    env={k:v for k,v in os.environ.items() if not k.startswith(('LEAN_','PYTHON'))}
    compiled=invoke([sys.executable,'-I','-S',str(ROOT/'compile.py'),'--output',str(out/'proof')],env)
    (out/'COMPILE.json').write_text(json.dumps(compiled,indent=2)+'\n')
    if compiled['exit'] or compiled['stderr']: raise RuntimeError('Lean compilation failed')
    env['LEAN_PATH']=str(out/'proof')
    audit=invoke([config['lean'],str(ROOT/'lean/Audit.lean')],env)
    (out/'AUDIT.json').write_text(json.dumps(audit,indent=2)+'\n')
    if audit['exit'] or audit['stderr']: raise RuntimeError('Lean audit failed')
    names=re.findall(r"'MeasurementPadding\.([^']+)'",audit['stdout'])
    if names!=read(ROOT/'AUDIT-NAMES.json'): raise RuntimeError('audit roster mismatch')
    axioms=re.findall(r'depends on axioms: \[([^]]*)\]',audit['stdout'])
    if any(a.strip() not in ['propext','Quot.sound','Classical.choice'] for row in axioms for a in row.split(',')):
        raise RuntimeError('unexpected axiom')
    if re.search(r'\b(sorry|admit|axiom)\b','\n'.join((ROOT/'lean'/f'{m}.lean').read_text() for m in read(ROOT/'MODULES.json'))):
        raise RuntimeError('proof hole/axiom token')
    negatives=[]
    for name in read(ROOT/'MUTANTS.json'):
        record=invoke([config['lean'],str(ROOT/'mutants'/name)],env);negatives.append(record)
        if record['exit']==0 or record['stderr'] or 'is false' not in record['stdout']:
            raise RuntimeError('mutant did not fail semantically')
    (out/'MODEL-MUTANTS.json').write_text(json.dumps(negatives,indent=2)+'\n')
    native=invoke([sys.executable,'-I','-S',str(ROOT/'native/check.py'),str(out/'native')],env)
    (out/'NATIVE.json').write_text(json.dumps(native,indent=2)+'\n')
    if native['exit'] or native['stderr']: raise RuntimeError('native replay failed')
    authenticate()
    result=dict(status='PASS',audits=len(names),model_mutants=len(negatives),native=json.loads(native['stdout']))
    (out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))

if __name__=='__main__': main()
