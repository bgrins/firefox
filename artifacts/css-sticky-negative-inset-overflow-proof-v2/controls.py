import sys
if not sys.flags.isolated or not sys.flags.no_site:raise RuntimeError('require -I -S')
sys.dont_write_bytecode=True
import hashlib,importlib.util,json,shutil,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('seal',ROOT/'seal.py');sealer=importlib.util.module_from_spec(spec);spec.loader.exec_module(sealer)

def main():
    out=Path(sys.argv[1]).resolve();out.mkdir();records=[]
    original=ROOT/'capsule';original_pin=hashlib.sha256((original/'FILES.json').read_bytes()).hexdigest()
    def case(name,change,reason,reseal=False,full=False,optimize=False):
        clone=out/'disposable';shutil.copytree(original,clone)
        change(clone)
        pin=sealer.seal(clone) if reseal else hashlib.sha256((clone/'FILES.json').read_bytes()).hexdigest()
        command=[sys.executable,'-I','-S',*(['-O'] if optimize else []),str(clone/'check.py'),'--manifest-sha',pin]
        command += ['--out',str(out/(name+'-unexpected-run'))] if full else ['--verify-only']
        p=subprocess.run(command,capture_output=True,text=True)
        (out/(name+'.log')).write_text(p.stdout+p.stderr)
        record={'name':name,'command':command,'exit':p.returncode,'reason':reason,'resealed':reseal,'manifest':pin,'original_manifest':original_pin}
        records.append(record);(out/'RESULT.json').write_text(json.dumps(records,indent=2)+'\n')
        if p.returncode==0 or reason not in p.stdout+p.stderr:raise RuntimeError('wrong rejection '+name)
        shutil.rmtree(clone)
    def json_change(root,name,fn):
        p=root/name;v=json.loads(p.read_text());fn(v);p.write_text(json.dumps(v,indent=2)+'\n')
    case('unlisted-file',lambda r:(r/'unexpected').write_text('x'),'unexpected file')
    case('empty-directory',lambda r:(r/'unexpected-dir').mkdir(),'unexpected directory')
    case('symlink',lambda r:(r/'unexpected-link').symlink_to('TOOLCHAIN.json'),'nonregular entry')
    case('stale-cache',lambda r:(r/'__pycache__').mkdir(),'unexpected directory')
    case('resealed-cache',lambda r:(r/'cache.pyc').write_bytes(b'x'),'forbidden capsule cache',True)
    case('resealed-olean',lambda r:(r/'lean/Injected.olean').write_bytes(b'x'),'forbidden capsule cache',True)
    case('changed-source',lambda r:(r/'inputs/combined-after.cpp').write_text('changed'),'file hash')
    case('role-substitution',lambda r:(r/'inputs/combined-after.cpp').write_bytes((r/'inputs/standalone-after.cpp').read_bytes()),'source role: combined-after bytes',True)
    case('old-role-substitution',lambda r:(r/'inputs/standalone-before.cpp').write_bytes((r/'inputs/combined-before.cpp').read_bytes()),'source role: standalone-before bytes',True)
    case('header-role',lambda r:(r/'inputs/combined-final-StickyScrollContainer.h').write_bytes((r/'inputs/before-StickyScrollContainer.h').read_bytes()),'source role: combined-final-StickyScrollContainer.h',True)
    case('receipt-role',lambda r:json_change(r,'inputs/candidate-wpt-v1-RUN.json',lambda v:v['before'].__setitem__('layout/generic/StickyScrollContainer.cpp','0'*64)),'source role: candidate before native identity',True)
    case('patch-role',lambda r:(r/'inputs/fix.patch').write_text('wrong'),'source role: standalone patch identity',True)
    case('duplicate-path',lambda r:json_change(r,'FILES.json',lambda v:v['files'].append(v['files'][0])),'duplicate manifest path')
    case('parent-path',lambda r:json_change(r,'FILES.json',lambda v:v['files'][0].__setitem__('path','../outside')),'manifest path')
    case('absolute-path',lambda r:json_change(r,'FILES.json',lambda v:v['files'][0].__setitem__('path','/tmp/outside')),'manifest path')
    case('compiler-pin',lambda r:json_change(r,'TOOLCHAIN.json',lambda v:v.__setitem__('compiler_sha256','0'*64)),'tool identity compiler',True)
    case('lean-library-pin',lambda r:json_change(r,'LEAN-TOOLCHAIN.json',lambda v:v['entries'][0].__setitem__('sha256','0'*64)),'transitive toolchain manifest',True)
    case('header-pin',lambda r:json_change(r,'CPP-HEADERS.json',lambda v:v['entries'][0].__setitem__('sha256','0'*64)),'C++ header identity',True)
    case('case-roster',lambda r:json_change(r,'CASES.json',lambda v:v.pop()),'case roster',True,True)
    case('extraction-binding',lambda r:json_change(r,'bindings/combined-after.json',lambda v:v[0].__setitem__('sha256','0'*64)),'source extraction combined-after',True,True)
    case('axiom-policy',lambda r:json_change(r,'AUDITS.json',lambda v:v['allowed_axioms'].append('sorryAx')),'axiom roster/policy',True,True)
    case('optimized-python',lambda r:None,'Require python3 -I -S without optimization',optimize=True)
    print(json.dumps({'controls':len(records),'all_rejected':True}))
if __name__=='__main__':main()
