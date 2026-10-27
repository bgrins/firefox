import sys
assert sys.flags.isolated and sys.flags.no_site
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
i=json.loads((HERE/'INPUTS.json').read_text())
for n,h in i['pins'].items():assert sha(ROOT/n)==h,n
assert sha(HERE/'ProviderState.lean')==i['source_sha256']
env={**os.environ,'LEAN_NUM_THREADS':'2','LEAN_PATH':str(ROOT/i['library_objects'])}
command=[str(ROOT/i['compiler']),str(HERE/'ProviderState.lean')]
r=subprocess.run(command,cwd=ROOT,env=env,capture_output=True,text=True,timeout=60)
log=r.stdout+r.stderr
(HERE/'release.log').write_text(log)
assert r.returncode==0 and 'error:' not in log and 'sorryAx' not in log
matches=re.findall(r"'([^']+)' (?:does not depend on any axioms|depends on axioms:\s*\[([^\]]*)\])",log)
assert len(matches)==9
assert all(set(x.strip() for x in axioms.split(',') if x.strip()) <= {'propext','Classical.choice','Quot.sound'} for _,axioms in matches)
negatives={
 'request-implies-current':'example : 10 * factor (readExtent hiddenOnly) .vw = 24 := by obtain ⟨_, _, _, _, _, h, _⟩ := request_alone_counterexample; rw [h]; decide +kernel',
 'same-dimension-old-generation':'example : publish { reconstruct ⟨240,120⟩ initial with completed := initial.completed } ≠ none := by\n  have h : publish { reconstruct ⟨240,120⟩ initial with completed := initial.completed } = none := by\n    simp [publish, reconstruct, initial]\n  rw [h]\n  decide +kernel',
}
rejected={}
for name,claim in negatives.items():
    p=HERE/('.'+name+'.lean')
    try:
        with p.open('x') as stream:
            stream.write((HERE/'ProviderState.lean').read_text()+'\nopen CrossDocumentViewport\n'+claim+'\n')
        r=subprocess.run([str(ROOT/i['compiler']),str(p)],cwd=ROOT,env=env,capture_output=True,text=True,timeout=60)
        output=r.stdout+r.stderr
        (HERE/(name+'.log')).write_text(output)
        assert r.returncode!=0 and 'is false' in output and 'unknown identifier' not in output and 'unknown module' not in output
        rejected[name]={'exit':r.returncode,'false_claim_rejected':True}
    finally:
        p.unlink(missing_ok=True)
for n,h in i['pins'].items():assert sha(ROOT/n)==h,n
assert sha(HERE/'ProviderState.lean')==i['source_sha256']
assert not list(HERE.glob('*.olean')) and not list(HERE.glob('.*.lean'))
receipt={'status':'PASS','command':command,'environment':{'LEAN_NUM_THREADS':'2','LEAN_PATH':env['LEAN_PATH']},
         'exit':0,'audits':{n:[a.strip() for a in ax.split(',') if a.strip()] for n,ax in matches},
         'negative_controls':rejected,'canonical_files_changed':False,'new_target_directory':False,
         'owned_compiler_products_present':False,'native_refinement_proved':False,'source_sha256':i['source_sha256']}
(HERE/'CHECK.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({k:v for k,v in receipt.items() if k!='audits'},indent=2))
