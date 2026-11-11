import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parent

def sha(data):return hashlib.sha256(data).hexdigest()
def require(ok,why):
    if not ok:raise ValueError(why)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--lean',required=True,type=Path)
    parser.add_argument('--out',required=True,type=Path)
    args=parser.parse_args();lean=args.lean.resolve();out=args.out.resolve()
    out.mkdir(parents=True,exist_ok=False)
    pins=json.loads((ROOT/'TOOLCHAIN.json').read_text())
    for name,digest in pins.items():require(sha((lean.parent.parent/name).read_bytes())==digest,'toolchain drift:'+name)
    source=(ROOT/'Guard.lean').read_text()
    require(not re.search(r'\bsorry\b|\badmit\b|\bnative_decide\b|^axiom\b|^unsafe\b|^partial\b',source,re.M),'proof escape')
    names=['ClipGuardReview.'+n for n in re.findall(r'^theorem ([\w.]+)',source,re.M)]
    require(len(names)==len(set(names)),'duplicate declarations')
    hashes={n:sha((ROOT/n).read_bytes()) for n in ['Guard.lean','check.py','TOOLCHAIN.json']}
    commands={}
    with tempfile.TemporaryDirectory(prefix='clip-guard-proof-') as directory:
        work=Path(directory);env=dict(os.environ,LEAN_PATH=str(work))
        shutil.copyfile(ROOT/'Guard.lean',work/'Guard.lean')
        def run(label,argv,reject=False):
            p=subprocess.run([str(a) for a in argv],cwd=work,env=env,capture_output=True,text=True,timeout=120)
            output=p.stdout+p.stderr;(out/(label+'.log')).write_text(output)
            commands[label]={'exit_code':p.returncode,'log_sha256':sha(output.encode())}
            if reject:
                require(p.returncode==1 and bool(re.fullmatch(r"[^\n]+:\d+:\d+: error: Tactic `decide` proved that the proposition\n(?:  [^\n]*\n)+is false\n",output)),'unexpected negative result:'+label+'\n'+output)
            else:require(p.returncode==0 and not re.search(r'warning:|error:|\bsorry\b',output),'unexpected diagnostic:'+label+'\n'+output)
            return output
        version=run('version',[lean,'--version']);require('version 4.35.0-rc4,' in version,'version mismatch')
        run('compile',[lean,'-o','Guard.olean','Guard.lean'])
        (work/'Audit.lean').write_text('import Guard\n'+''.join('#print axioms '+n+'\n' for n in names))
        output=run('audit',[lean,'Audit.lean']);audits={}
        for line in re.sub(r',\n\s*',', ',output).splitlines():
            m=re.fullmatch(r"'([^']+)' (does not depend on any axioms|depends on axioms: \[(.*)\])",line)
            require(bool(m),'unknown audit:'+line)
            axioms=set(m[3].split(', ')) if m[3] else set()
            require(axioms<={'propext','Classical.choice','Quot.sound'},'unapproved axiom:'+line)
            require(m[1] not in audits,'duplicate audit');audits[m[1]]=sorted(axioms)
        require(set(audits)==set(names),'incomplete audit')
        controls={
          'OmittedGuard':'rawRect mixed = oldRect mixed',
          'RejectedOuterAuto':'newValue .add (.outerAuto : Input Nat Nat) = none',
          'CountZeroShortcut':'wrongCountZero (.accumulate 0) (.rect (fun _ => mixed)) = newValue (.accumulate 0) (.rect (fun _ => mixed))',
          'RejectedNumericRect':'newRect numeric = none',
        }
        for label,claim in controls.items():
            (work/(label+'.lean')).write_text('import Guard\nopen ClipGuardReview\nexample : '+claim+' := by decide +kernel\n')
            run(label,[lean,label+'.lean'],reject=True)
    require(not work.exists(),'temporary build retained')
    require(all(sha((ROOT/n).read_bytes())==h for n,h in hashes.items()),'source changed during run')
    report={'status':'pass','sources':hashes,'toolchain_pins':pins,'toolchain_version':version.strip(),'audits':audits,'false_claim_controls':controls,'commands':commands,'temporary_build_removed':True,'universal_pure_total_result_equivalence':True,'arithmetic_only':True,'native_refinement_or_ieee_proof':False,'runtime_or_debug_validation':False}
    (out/'REPORT.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS',len(audits),'audits;',len(controls),'exact false-claim rejections')

if __name__=='__main__':main()
