import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError("Use python3 -I -S")
sys.dont_write_bytecode = True
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
HERE=Path(__file__).resolve().parent
LEAN=Path('/Users/bgrins/code/firefox/artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean')
PIN='d1d9c26a539f54fe839d2aa7760bf1ac1dd76a30b26e2c9684bebf2900038fcf'
def require(x,msg):
    if not x: raise RuntimeError(msg)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def audit(text,names):
    pattern=re.compile(r"'([A-Za-z0-9_.]+)' (?:depends on axioms: \[([^]]*)\]|(does not depend on any axioms))\n")
    pos=0; result={}
    while pos<len(text):
        m=pattern.match(text,pos); require(m is not None,'audit parse')
        n,values,empty=m.groups(); ax=[] if empty or not values else [v.strip() for v in values.split(',')]
        require(n not in result,'audit duplicate'); require(set(ax)<={'propext','Classical.choice','Quot.sound'},'forbidden axioms')
        result[n]=ax; pos=m.end()
    require(list(result)==names,'audit roster')
    return result

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    out=args.output.resolve();require(not out.exists(),'new output');out.mkdir(parents=True)
    require(sha(LEAN)==PIN,'Lean identity')
    commands=[]; controls=[]
    with tempfile.TemporaryDirectory(prefix='flex-line-proof-independent-') as tmp:
        work=Path(tmp); env={k:v for k,v in os.environ.items() if not k.startswith('LEAN_')};env['LEAN_PATH']=str(work)
        for module in ['LineSum','ObserverChallenges']:
            shutil.copyfile(HERE/(module+'.lean'),work/(module+'.lean'))
        def compile(module,positive=True):
            cmd=[str(LEAN),'-o',str(work/(module+'.olean')),str(work/(module+'.lean'))]
            run=subprocess.run(cmd,cwd=work,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
            (out/(module+'.log')).write_text(run.stdout)
            commands.append({'module':module,'command':cmd,'exit':run.returncode})
            (out/'COMMANDS.json').write_text(json.dumps(commands,indent=2)+'\n')
            require((run.returncode==0)==positive,'compile '+module)
            return run.stdout
        compile('LineSum');compile('ObserverChallenges')
        names=[]
        for module,namespace in [('LineSum','FlexLineSum'),('ObserverChallenges','IndependentLineSum')]:
            names += [namespace+'.'+n for n in re.findall(r'^theorem (\w+)',(work/(module+'.lean')).read_text(),re.M)]
        (work/'Audit.lean').write_text('import ObserverChallenges\n'+'\n'.join('#print axioms '+n for n in names)+'\n')
        audited=audit(compile('Audit'),names)
        for module,claim in {'FalseUnboundedIdentity':'applyBounds none none (accumulate 0 [720000000, 720000000]) = 1440000000','FalseNegativeSuffix':'min (1073741823 : Int) (min 1073741823 (1073741823 + 10) - 10) = min (1073741823 : Int) ((1073741823 + 10) - 10)'}.items():
            source='import ObserverChallenges\nopen FlexLineSum IndependentLineSum\ntheorem wrong : '+claim+' := by decide +kernel\n'
            (work/(module+'.lean')).write_text(source);(out/(module+'.lean')).write_text(source)
            log=compile(module,False)
            require('is false' in log or '(kernel) application type mismatch' in log,'false claim reached kernel')
            controls.append({'name':module,'result':'kernel rejected false claim'})
        source='axiom injected : False\ntheorem wrong : False := injected\n#print axioms wrong\n'
        (work/'CustomAxiom.lean').write_text(source);(out/'CustomAxiom.lean').write_text(source)
        log=compile('CustomAxiom')
        try: audit(log,['wrong'])
        except RuntimeError as exc:
            require(str(exc)=='forbidden axioms','axiom rejection reason')
        else: raise RuntimeError('axiom accepted')
        controls.append({'name':'CustomAxiom','result':'compiled then rejected forbidden axiom'})
    result={'status':'PASS','audits':audited,'controls':controls,'input_sha256':{n:sha(HERE/n) for n in ['LineSum.lean','ObserverChallenges.lean']},'lean_sha256':PIN,'temporary_compiler_products_removed':True,'scope':'Primitive mathematical proofs and conditional observer composition. Not a full source translation or proof of provider construction.'}
    (out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':'PASS','audits':len(audited),'controls':len(controls)}))
if __name__=='__main__': main()
