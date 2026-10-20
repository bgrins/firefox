import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError("Require python3 -I -S without optimization")
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def closed(root,pin):
    raw=(root/'FILES.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest()==pin,'external pin'
    files=json.loads(raw)
    paths=list(root.rglob('*'))
    assert not any(p.is_symlink() for p in paths),'symlink'
    actual=sorted(str(p.relative_to(root)) for p in paths if p.is_file() and str(p.relative_to(root)) not in {'FILES.json','FREEZE.json'})
    assert actual==sorted(files),'closed roster'
    for name,value in files.items():
        assert hashlib.sha256((root/name).read_bytes()).hexdigest()==value,name
    freeze=json.loads((root/'FREEZE.json').read_text())
    assert freeze['files_sha256']==pin and freeze['payload_count']==len(files)
    return len(files)

if len(sys.argv)!=3 or sys.argv[1]!='--files-sha256':
    raise SystemExit('verify.py --files-sha256 OUTER_PIN')
count=closed(ROOT,sys.argv[2])
closed(ROOT/'capsule','993dde69e30ebadf821bafb8587baba61f010bfc537600fad61a0839652db5eb')
for d in ['original','v2','candidate','include']:
    for f in (ROOT/d).rglob('*'):
        if f.is_file():assert f.read_bytes()==(ROOT/'capsule'/d/f.relative_to(ROOT/d)).read_bytes()
for name in ['replay.py','facade.cpp','harness.cpp','v1-helper.cpp','SOURCE-PINS.json','CANDIDATE-PINS.json','TOOLCHAIN.json']:
    assert (ROOT/name).read_bytes()==(ROOT/'capsule'/name).read_bytes()
for role,pins in json.loads((ROOT/'CANDIDATE-PINS.json').read_text()).items():
    for name,pin in pins.items():assert hashlib.sha256((ROOT/role/name).read_bytes()).hexdigest()==pin
for name in ['nsIFrame.h','nsLayoutUtils.cpp','nsLayoutUtils.h','DOMRect.cpp']:
    assert (ROOT/'v2'/name).read_bytes()==(ROOT/'candidate'/name).read_bytes()
a=json.loads((ROOT/'calibration/RESULT.json').read_text())
b=json.loads((ROOT/'relocated-calibration/RESULT.json').read_text())
assert a==b and len(a['runs'])==20
for row in a['runs']:
    success=row['variant'] in ['original','v2','candidate','mutant-overflow']
    assert (row['exit']==0)==success
    if success:assert row['rows']==168
for opt in ['-O0','-O2']:
    old=(ROOT/'calibration'/('original'+opt+'-run.log')).read_text().splitlines()
    previous=(ROOT/'calibration'/('v2'+opt+'-run.log')).read_text()
    candidate=(ROOT/'calibration'/('candidate'+opt+'-run.log')).read_text()
    assert previous==candidate
    assert [s for s in old if s.startswith('ROW ')]==[s for s in candidate.splitlines() if s.startswith('ROW ')]
    assert 'V1_DOMAIN_PASS 2048' in candidate and 'EXACT_CHECKS_PASS' in candidate
    for role in ['original','v2','candidate']:
        for witness in ['grouping','rect-origin','crossdoc-restart']:
            text=(ROOT/'calibration'/(role+opt+'-'+witness+'.log')).read_text()
            if role=='original' or witness=='crossdoc-restart':assert 'runtime error: signed integer overflow' in text
            else:assert 'WIDE_WITNESS_PASS' in text
            if role!='original' and witness=='crossdoc-restart':assert 'NUMERIC_RESTART' in text
    for role in ['v2','candidate','mutant-overflow']:
        for number in range(1,9):
            text=(ROOT/'calibration'/(role+opt+'-injected-'+str(number)+'.log')).read_text()
            if role=='mutant-overflow' and number in [1,5]:assert 'FAIL 451' in text
            else:assert 'INJECTED_GUARD_PASS' in text and 'NUMERIC_RESTART' in text
controls=json.loads((ROOT/'GUARD-CONTROLS.json').read_text())
assert len(controls)==7 and all(c['exit']!=0 and not c['output_created'] for c in controls)
assert all(x['exit']==0 and x['all_files_match'] for x in json.loads((ROOT/'PATCH-ROUNDTRIP.json').read_text()))
print(json.dumps({'payloads':count,'replays':2,'configurations_per_replay':20,'matrix_rows_per_optimization':168,'v1_domain_per_optimization':2048,'mutants':7,'guards':7,'status':'PROPOSAL_PENDING_REVIEW_FULL_BUILD_AND_PERFORMANCE'}))
