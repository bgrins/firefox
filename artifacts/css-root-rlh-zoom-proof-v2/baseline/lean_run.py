import json
import os
from pathlib import Path
import subprocess
import re
from fractions import Fraction
import cases
import domain
import mutants
BASE=Path(__file__).resolve().parent
DEFAULT_LEAN=BASE.parent/'stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean'
MODULES=['Model','Trace','Grid','Mutants','Nonvacuity','Admission','Runner']

def run(out,events,lean=None):
    out.mkdir(parents=True,exist_ok=True)
    lean=Path(lean or os.environ.get('RLH_LEAN',DEFAULT_LEAN)).resolve()
    env=dict(os.environ,LEAN_PATH=str(out.resolve()))
    commands=[]
    for name in MODULES:
        cmd=[str(lean),'-o',str(out/(name+'.olean')),str(BASE/(name+'.lean'))]
        p=subprocess.run(cmd,cwd=BASE,env=env,text=True,capture_output=True)
        commands.append(dict(command=cmd,cwd=str(BASE),exit=p.returncode,stdout=p.stdout,stderr=p.stderr))
        assert p.returncode==0,(name,p.stdout,p.stderr)
    theorems=[]
    for module in MODULES:
        source=(BASE/(module+'.lean')).read_text()
        assert not re.search(r'\b(sorry|axiom|native_decide)\b',source),module
        theorems.extend(re.findall(r'^theorem ([A-Za-z_][A-Za-z_0-9]*)',source,re.M))
    axiom_source='import Nonvacuity\nimport Mutants\n'+''.join('#print axioms Rlh.'+n+'\n' for n in theorems)
    (out/'Axioms.lean').write_text(axiom_source)
    cmd=[str(lean),str(out/'Axioms.lean')]
    p=subprocess.run(cmd,cwd=BASE,env=env,text=True,capture_output=True)
    commands.append(dict(command=cmd,cwd=str(BASE),exit=p.returncode,stdout=p.stdout,stderr=p.stderr))
    assert p.returncode==0 and 'sorryAx' not in p.stdout and 'Lean.ofReduceBool' not in p.stdout,(p.stdout,p.stderr)
    (out/'axioms.txt').write_text(p.stdout)
    (out/'theorems.json').write_text(json.dumps(theorems,indent=2)+'\n')
    cmd=[str(lean),'--run',str(BASE/'Admission.lean')]
    p=subprocess.run(cmd,cwd=BASE,env=env,text=True,capture_output=True)
    commands.append(dict(command=cmd,cwd=str(BASE),exit=p.returncode,stdout=p.stdout,stderr=p.stderr))
    assert p.returncode==0,(p.stdout,p.stderr)
    (out/'admission-lean.json').write_text(json.dumps(dict(zip(['nonvacuity','negativeAdmissions','prepublicationRoles'],map(int,p.stdout.split()))),indent=2)+'\n')
    admitted=domain.admit(events);ids={x['id'] for x in admitted}
    selected=[e for e in events if e['event']!='READ' or e['id'] in ids]
    # Diagnostic root commits have no admitted reads and need no model execution.
    epochs={x['rootEpoch'] for x in admitted};current=None;filtered=[]
    for e in selected:
        if e['event']=='ROOT':current=e['epoch']
        if current in epochs:filtered.append(e)
    protocol=[]
    for line in cases.protocol(filtered).splitlines():
        protocol.append(' '.join([line.split()[0]]+[str(Fraction(x)) for x in line.split()[1:]]))
    text='\n'.join(protocol)+'\n';(out/'input.txt').write_text(text)
    (out/'admission.json').write_text(json.dumps(dict(cases=admitted,rejected=domain.rejected_domains()),indent=2)+'\n')
    for name,m in [('original',1),('candidate',0)]+[(n,i) for i,n in mutants.NAMES.items()]:
        cmd=[str(lean),'--run',str(BASE/'Runner.lean'),str(m)]
        p=subprocess.run(cmd,cwd=BASE,env=env,text=True,input=text,capture_output=True)
        commands.append(dict(command=cmd,cwd=str(BASE),exit=p.returncode,stderr=p.stderr))
        (out/(name+'.txt')).write_text(p.stdout)
        assert p.returncode==0,(name,p.stdout,p.stderr)
        assert len(p.stdout.splitlines())==len(ids)
    (out/'commands.json').write_text(json.dumps(commands,indent=2)+'\n')
    return admitted
if __name__=='__main__':run(Path(__import__('sys').argv[1]),cases.generate())
