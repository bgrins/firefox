import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit("require Python -I -S without optimization")
sys.dont_write_bytecode=True
import argparse,hashlib,importlib.util,json,os,re,stat,subprocess
from pathlib import Path, PurePosixPath
ROOT=Path(__file__).resolve().parent
PINS={'FILES.json':'1ee421e14ca92e166927ce78f6be14a02fc8308cd61cef5fb20a18b588430a39','FREEZE.json':'330ca76a08b3f48fe4c101737e8300cb17ca34969f9fd019fa7fcde95a4aacea','check.py':'ba3a03b0f7b45cf0173a7a107231c40eeb42e305f428f49d28b4b358d8e9c7b6'}
def require(ok,message):
    if not ok:raise ValueError(message)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def decode(text):
    def pairs(xs):
        out={}
        for k,v in xs:
            require(k not in out,'duplicate JSON key');out[k]=v
        return out
    return json.loads(text,object_pairs_hook=pairs)
def closure(root):
    for n in ['FILES.json','FREEZE.json']:require(stat.S_ISREG((root/n).lstat().st_mode),'nonregular seal')
    seal=decode((root/'FREEZE.json').read_text())
    require(seal.get('manifest_sha256',seal.get('files_sha256'))==sha(root/'FILES.json'),'manifest binding')
    data=decode((root/'FILES.json').read_text())['files']
    if isinstance(data,list):
        require(len({x['path'] for x in data})==len(data),'duplicate path')
        data={x['path']:x['sha256'] for x in data}
    require(type(data) is dict and data,'roster')
    dirs=set()
    for n,h in data.items():
        q=PurePosixPath(n)
        require(not q.is_absolute() and q.as_posix()==n and all(x not in ['.','..',''] for x in q.parts),'path grammar')
        require(type(h) is str and re.fullmatch('[0-9a-f]{64}',h),'hash grammar')
        dirs.update(str(x) for x in q.parents if str(x)!='.')
    actual=set();actualdirs=set()
    for base,ds,fs in os.walk(root,followlinks=False):
        for n in ds+fs:
            p=Path(base)/n;r=p.relative_to(root).as_posix();m=p.lstat().st_mode
            if stat.S_ISREG(m):actual.add(r)
            elif stat.S_ISDIR(m):actualdirs.add(r)
            else:raise ValueError('nonregular entry')
    require(actual==set(data)|{'FILES.json','FREEZE.json'},'closed file roster')
    require(actualdirs==dirs,'closed directory roster')
    for n,h in data.items():require(sha(root/n)==h,'source hash: '+n)
    return data

def authenticate():
    outer=closure(ROOT)
    for n,h in PINS.items():require(sha(ROOT/'capsule'/n)==h,'nested pin '+n)
    inner=closure(ROOT/'capsule')
    return {'outer_files':len(outer),'inner_files':len(inner)}

def load_native():
    spec=importlib.util.spec_from_file_location('review_native',ROOT/'native_audit.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    result=m.audit(ROOT)
    require(result==decode((ROOT/'NATIVE-AUDIT.json').read_text()),'native audit mismatch')
    expected=decode((ROOT/'SOURCE-IDENTITY-FINDING.json').read_text())
    for folder,rows in expected['observed'].items():
        for n,h in rows.items():require(sha(ROOT/folder/n)==h,'source role finding identity')
    require(sha(ROOT/'capsule/inputs/candidate.cpp')!=expected['producer_claimed_tested'],'expected source-role defect changed')
    return result

def replay(output):
    output.mkdir(parents=True)
    commands=[]
    def run(cmd,name,env=None,success=True):
        r=subprocess.run(cmd,capture_output=True,text=True,cwd=output,env=env)
        text=r.stdout+r.stderr;(output/(name+'.log')).write_text(text)
        commands.append({'command':cmd,'exit':r.returncode});(output/'COMMANDS.json').write_text(json.dumps(commands,indent=2)+'\n')
        require((r.returncode==0)==success,'command '+name)
        return text
    run([sys.executable,'-I','-S',str(ROOT/'capsule/check.py'),'--manifest-sha',PINS['FILES.json'],'--out',str(output/'producer')],'producer')
    actual=decode((output/'producer/RESULT.json').read_text())
    expected=decode((ROOT/'replay/RESULT.json').read_text())
    require(actual==expected,'producer replay observations')
    lean=decode((ROOT/'capsule/TOOLCHAIN.json').read_text())['lean']
    work=output/'independent';work.mkdir()
    env={'PATH':'/usr/bin:/bin','LEAN_PATH':str(work)}
    sources=[(n,ROOT/'capsule/lean'/(n+'.lean')) for n in ['OffsetEncoding','OffsetSource','ModelMutants']]
    sources += [('Independent',ROOT/'Independent.lean'),('Audit',ROOT/'Audit.lean')]
    for name,src in sources:
        log=run([lean,'--root='+str(src.parent),'-o',str(work/(name+'.olean')),str(src)],name,env)
        require('warning:' not in log,'Lean warning')
    log=(output/'Audit.log').read_text();names=decode((ROOT/'AUDITS.json').read_text())
    found=re.findall(r"^'([^']+)' (?:depends on axioms:|does not depend on any axioms)",log,re.M)
    require(found==names,'independent audit roster')
    for body in re.findall(r'depends on axioms:\s*\[([^]]*)\]',log):
        require(set(x.strip() for x in body.split(',') if x.strip())<={'propext','Quot.sound','Classical.choice'},'independent axioms')
    negatives=['OffsetEncoding.reserve OffsetEncoding.autoCode = OffsetEncoding.autoCode',
      'OffsetEncoding.reserve (-1) = 0',
      '(OffsetSource.observe ⟨0,true,0,0⟩).resolves = 1',
      '(OffsetEncoding.autoCode+1)-OffsetEncoding.reserve (OffsetEncoding.autoCode+1) = 1']
    for i,claim in enumerate(negatives):
        f=work/('Negative'+str(i)+'.lean');f.write_text('import OffsetSource\nexample : '+claim+' := by decide +kernel\n')
        log=run([lean,str(f)],'negative-'+str(i),env,False)
        require('is false' in log and 'unknown' not in log,'semantic negative')
    return {'status':'pass','verdict':'HOLD-tested-source-identity','independent_results':len(names),'semantic_negatives':len(negatives)}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out');parser.add_argument('--authenticate-only',action='store_true');args=parser.parse_args()
    before=authenticate()
    if args.authenticate_only:print(json.dumps(before));return
    load_native()
    require(args.out is not None,'output required');output=Path(args.out).resolve()
    require(not output.exists() and output!=ROOT and ROOT not in output.parents,'new external output required')
    require(not any(c.isspace() or c==':' for c in str(output)),'producer dependency path profile')
    result=replay(output);require(authenticate()==before,'inputs changed')
    (output/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
