import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--output',type=Path,required=True)
    out=ap.parse_args().output.resolve(); assert not out.exists() and not out.is_symlink()
    inputs=json.loads((HERE/'INPUTS.json').read_text())
    for n,d in json.loads((HERE/'REFERENCES.json').read_text()).items(): assert sha(ROOT/n)==d,n
    for n,d in inputs['models'].items():
        assert sha(HERE/n)==d
        assert not re.search(r'\b(sorry|axiom|native_decide)\b',(HERE/n).read_text())
    compiler=ROOT/inputs['compiler']; assert sha(compiler)==inputs['compiler_sha256']
    out.mkdir(); records=[]
    false={
      'dummy-provider-suffices':'evaluate (fun _ => (none : Option Nat)) cache parser plain fallback = ⟨12, true⟩',
      'real-provider-needs-no-cache':'evaluate provider (fun _ => none) parser plain fallback = ⟨12, true⟩',
      'namespace-erasure-safe':'evaluate provider aliasCache parser qualified fallback = ⟨17, true⟩',
      'old-frame-cache-safe':'[stale] = runFrame resolver (frame 20)',
      'attribute-result-untainted':'evaluate provider cache parser plain fallback = ⟨12, false⟩',
    }
    with tempfile.TemporaryDirectory(prefix='attr-prep-',dir='/private/tmp') as tmp:
        scratch=Path(tmp); env=dict(os.environ,LEAN_NUM_THREADS='2',LEAN_PATH=tmp)
        def run(name,args,success=True):
            r=subprocess.run([str(compiler),*args],cwd=scratch,env=env,text=True,capture_output=True,timeout=55)
            log=r.stdout+r.stderr; q=out/(name+'.log');q.write_text(log)
            records.append(dict(name=name,exit=r.returncode,sha256=sha(q)))
            if success: assert r.returncode==0 and 'warning:' not in log and 'sorryAx' not in log,log
            else:
                assert r.returncode!=0 and 'false' in log and 'decide' in log,log
                assert not any(s in log for s in ['Unknown identifier','unknown identifier','unexpected token','failed to synthesize']),log
            return log
        version=run('version',['--version'])
        for name in ['Preparation','Examples']:
            shutil.copyfile(HERE/(name+'.lean'),scratch/(name+'.lean'))
            run(name,['-o',name+'.olean',name+'.lean'])
        shutil.copyfile(HERE/'Audit.lean',scratch/'Audit.lean')
        audit=run('Audit',['Audit.lean']); axioms={}
        for line in audit.splitlines():
            m=re.fullmatch(r"'([^']+)' (?:depends on axioms: \[([^]]*)\]|does not depend on any axioms)",line)
            assert m,line
            axioms[m[1]]=m[2].split(', ') if m[2] else []
            assert set(axioms[m[1]]) <= {'propext','Quot.sound','Classical.choice'}
        assert list(axioms)==inputs['audits']
        for name,claim in false.items():
            source='import Examples\nopen KeyframeAttributePreparation PreparationExamples\nexample : '+claim+' := by decide +kernel\n'
            (scratch/'FalseClaim.lean').write_text(source);(out/(name+'.lean.txt')).write_text(source)
            run(name,['FalseClaim.lean'],False)
    assert not scratch.exists()
    check=dict(status='KEYFRAME_ATTRIBUTE_PREPARATION_MODEL_PASS',compiler=version.strip(),audits=axioms,records=records,
        audited_declarations=5,closed_examples=9,rejected_false_claims=5,new_semantic_or_native_theorem_credit=0,
        resolver_and_context_mapping_external=True,canonical_changes=False,scratch_products_removed=True)
    (out/'CHECK.json').write_text(json.dumps(check,indent=2)+'\n'); print(json.dumps(check,indent=2))
if __name__=='__main__': main()
