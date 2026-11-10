import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

P=Path(__file__).resolve().parent
OWN=['Lifetime','LifetimeDelivery','Cases']

def require(ok,why):
    if not ok:raise ValueError(why)

def sha(b):return hashlib.sha256(b).hexdigest()

def names(path):
    namespace=re.search(r'^namespace (\w+)',path.read_text(),re.M).group(1)
    return [namespace+'.'+n for n in re.findall(r'^theorem (\w+)',path.read_text(),re.M)]

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--lean',required=True,type=Path)
    parser.add_argument('--out',required=True,type=Path)
    args=parser.parse_args();lean=args.lean.resolve();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False)
    pins=json.loads((P/'TOOLCHAIN.json').read_text())
    for path,digest in pins.items():
        suffix=path.split('lean-4.35.0-rc4-darwin_aarch64/',1)[1]
        require(sha((lean.parent.parent/suffix).read_bytes())==digest,'toolchain drift:'+suffix)
    imports=json.loads((P/'IMPORTS.json').read_text())
    for n,r in imports.items():
        data=(P/(n+'.lean')).read_bytes()
        if 'namespace_transform' in r:
            original=(P/(n+'.original.lean')).read_bytes();t=r['namespace_transform']
            require(sha(original)==r['sha256'],'original accounting drift')
            require(data==original.replace(t['from'].encode(),t['to'].encode()),'namespace-only transform drift')
            require(sha(data)==t['derived_sha256'],'derived accounting drift')
        else:require(sha(data)==r['sha256'],'import drift:'+n)
    modules=list(imports)+OWN
    sources={n+'.lean':sha((P/(n+'.lean')).read_bytes()) for n in modules}
    for n in ['Accounting.original.lean','check.py','IMPORTS.json','TOOLCHAIN.json','EXPECTED.json']:
        sources[n]=sha((P/n).read_bytes())
    declarations=[]
    for n in modules:
        text=(P/(n+'.lean')).read_text()
        require(not re.search(r'\bsorry\b|\badmit\b|\bnative_decide\b|^axiom\b|^unsafe\b',text,re.M),'proof escape:'+n)
        if n!='Cases':declarations+=names(P/(n+'.lean'))
    require(len(set(declarations))==len(declarations),'duplicate theorem names')
    commands={}
    with tempfile.TemporaryDirectory(prefix='lifetime-source-',dir=out) as temp:
        work=Path(temp);env=dict(os.environ,LEAN_PATH=str(work))
        def run(label,command,reject=False):
            r=subprocess.run([str(x) for x in command],cwd=work,env=env,capture_output=True,text=True,timeout=120)
            log=r.stdout+r.stderr;(out/(label+'.log')).write_text(log)
            commands[label]={'exit_code':r.returncode,'log_sha256':sha(log.encode())}
            if reject:
                require(r.returncode==1 and log.count('error:')==1 and 'Tactic `decide` proved that the proposition' in log and 'is false' in log and 'warning:' not in log,'wrong rejection:'+label+'\n'+log)
            else:require(r.returncode==0 and not re.search(r'(?m)warning:|error:|\bsorry\b',log),'command failed:'+label+'\n'+log)
            return log
        version=run('version',[lean,'--version'])
        require('version 4.35.0-rc4,' in version,'version mismatch')
        for n in modules:
            shutil.copyfile(P/(n+'.lean'),work/(n+'.lean'))
            run('compile-'+n,[lean,'-o',n+'.olean',n+'.lean'])
        (work/'Audit.lean').write_text('import LifetimeDelivery\n'+''.join('#print axioms '+n+'\n' for n in declarations))
        audit=run('audit',[lean,'Audit.lean'])
        audits={}
        for line in re.sub(r',\n\s*',', ',audit).splitlines():
            m=re.fullmatch(r"'([^']+)' (does not depend on any axioms|depends on axioms: \[(.*)\])",line)
            require(bool(m),'unrecognized audit line:'+line)
            axioms=set(m[3].split(', ')) if m[3] else set()
            require(axioms<={'propext','Classical.choice','Quot.sound'},'unapproved axiom:'+line)
            require(m[1] not in audits,'duplicate audit');audits[m[1]]=sorted(axioms)
        require(set(audits)==set(declarations),'incomplete axiom audit')
        examples=run('examples',[lean,'--run','Cases.lean']).splitlines()
        expected=json.loads((P/'EXPECTED.json').read_text())
        require(examples==[n+': true' for n in expected],'example roster/output')
        controls={
          'SelfRenewalCause':'DrainLifetime.ValidOrigin DrainLifetime.smallTree 1 (.ancestor 1 0)',
          'RenewalDecreasesPhase':'DescendingPhases.weight (DrainLifetime.freeRenewal DrainLifetime.start).pending < DescendingPhases.weight DrainLifetime.start.pending',
          'OldCompletionSettlesNew':'LifetimeLedger.settled (completedOld 1) newKey = true',
          'CollapsedLifetimeSafe':'LifetimeLedger.settled (completeIgnoringLifetime oldKey (inFlight 1)) newKey = false',
        }
        for label,claim in controls.items():
            prefix = 'simp only [DrainLifetime.ValidOrigin, DescendingPhases.StrictDesc, DrainLifetime.smallTree, CertifiedPath.path]\n  ' if label == 'SelfRenewalCause' else ''
            (work/(label+'.lean')).write_text('import Cases\nexample : '+claim+' := by\n  '+prefix+'decide +kernel\n')
            run(label,[lean,label+'.lean'],reject=True)
    require(not work.exists(),'temporary build retained')
    require(all(sha((P/n).read_bytes())==h for n,h in sources.items()),'source changed during verification')
    own_names=names(P/'Lifetime.lean')+names(P/'LifetimeDelivery.lean')
    report={'status':'pass','toolchain':version.strip(),'sources':sources,'audits':audits,'new_declarations':own_names,'observations':expected,'negative_controls':list(controls),'commands':commands,'temporary_build_removed':True,'conditional_productive_phase_refinement':True,'native_refinement_proved':False,'fairness_or_complete_administrative_termination_proved':False,'dormant_ticket_implies_scheduled_work':False,'freshness_requires_no_future_keys':True}
    (out/'REPORT.json').write_text(json.dumps(report,indent=2)+'\n')
    print(f'PASS:{len(audits)} audits,{len(own_names)} new declarations,{len(expected)} observations,{len(controls)} negative controls')

if __name__=='__main__':main()
