import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def main():
    head=sys.argv[1]
    assert len(head)==40 and all(c in '0123456789abcdef' for c in head)
    assert not (HERE/'RUN-INPUTS.json').exists(), 'Inputs already frozen'
    assert subprocess.check_output(['git','-c','core.fsmonitor=false','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==head
    plan=json.loads((HERE/'RUN-PLAN.json').read_text())
    assert plan['head'] is None
    plan['head']=head
    (HERE/'RUN-PLAN.json').write_text(json.dumps(plan,indent=2)+'\n')
    names=['run.py','analyze.py','process.py','bundle.py','RUN-PLAN.json','SOURCE-ROLES.json','EXPECTED-CALLBACKS.json','EXPECTED-BASELINE.json','EXPECTED-CHANGES.json','range-order.patch']
    for directory in ['source','candidate','runtime-inputs']:
        names += [str(p.relative_to(HERE)) for p in sorted((HERE/directory).rglob('*')) if p.is_file()]
    manifest={name:hashlib.sha256((HERE/name).read_bytes()).hexdigest() for name in names}
    (HERE/'RUN-INPUTS.json').write_text(json.dumps(manifest,indent=2)+'\n')
    result=subprocess.run([sys.executable,'-I',str(HERE/'check.py'),'--frozen'],capture_output=True,text=True)
    (HERE/'FREEZE-CHECK.log').write_text(result.stdout+result.stderr)
    assert result.returncode==0, 'Freeze verification failed; do not execute runner'
    (HERE/'CHECK.json').write_text(result.stdout)
    print(json.dumps({'head':head,'inputs':len(manifest),'manifest_sha256':hashlib.sha256((HERE/'RUN-INPUTS.json').read_bytes()).hexdigest()},indent=2))


if __name__=='__main__':
    main()
