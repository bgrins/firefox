import hashlib
import json
from pathlib import Path
import re

HERE=Path(__file__).resolve().parent
LAB=HERE.parent/'css-keyframe-source-position-lean-20261110-v1'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    manifest=json.loads((LAB/'SOURCE-ONLY.json').read_text())
    assert set(manifest)=={'PositionModel.lean','PositionLaws.lean','check.py','README.md'}
    assert all(sha(LAB/n)==h for n,h in manifest.items())
    imports={n:re.findall(r'(?m)^import (.+)$',(LAB/n).read_text()) for n in ['PositionModel.lean','PositionLaws.lean']}
    assert imports=={'PositionModel.lean':['Std'],'PositionLaws.lean':['PositionModel']}
    report=json.loads((LAB/'verification/report.json').read_text())
    assert report['status']=='pass' and report['temporary_builds_removed']
    assert not report['native_sort_or_memory_correctness_proved']
    for n,h in report['sources'].items():
        assert h==manifest[n]
    names=re.findall(r'(?m)^theorem ([A-Za-z_][A-Za-z0-9_]*)',(LAB/'PositionLaws.lean').read_text())
    assert len(names)==11 and len(set(names))==11
    assert set(report['audits'])=={'KeyframeSourcePosition.'+n for n in names}
    assert all(set(a)<= {'propext','Classical.choice','Quot.sound'} for a in report['audits'].values())
    for label,receipt in report['commands'].items():
        assert sha(LAB/'verification'/(label+'.log'))==receipt['sha256']
    mutants=['forward-source-scan','retain-latest-position','wrong-source-coordinate']
    assert report['compiling_semantic_mutants']==mutants
    assert all(report['commands'][n]['exit']==0 for n in ['model','laws','axioms','positive-witness'])
    for m in mutants:
        assert report['commands'][m+'-compile']['exit']==0
        assert report['commands'][m+'-unchanged-laws']['exit']!=0
        assert report['commands'][m+'-false-witness']['exit']!=0
        failure=(LAB/'verification'/(m+'-false-witness.log')).read_text()
        assert failure.count('error:')==1 and 'Tactic `decide` proved that the proposition' in failure
        assert 'recordPositions [0, 1, 2, 1].zipIdx 1 = some 1' in failure and failure.endswith('is false\n')
    assert not any(p.is_dir() for p in (LAB/'verification').iterdir())
    assert not list(LAB.rglob('*.olean')) and not list(LAB.rglob('*.ilean'))
    evidence={str(p.relative_to(HERE.parent)):sha(p) for p in LAB.rglob('*') if p.is_file()}
    (HERE/'INPUTS.json').write_text(json.dumps(evidence,indent=2)+'\n')
    print(json.dumps({'status':'PASS','source_manifest_files':4,'closed_local_imports':True,'kernel_audits_authenticated':11,'compiled_semantic_mutants_authenticated':3,'all_command_logs_authenticated':len(report['commands']),'owned_compiled_outputs_absent':True,'fresh_Lean_replay':False},indent=2))


if __name__=='__main__':
    main()
