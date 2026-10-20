#!/usr/bin/env python3
import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError('Require python3 -I -S without optimization')
sys.dont_write_bytecode=True
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def closed(root,expected):
    raw=(root/'FILES.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest()==expected,'external manifest pin mismatch'
    manifest=json.loads(raw)
    paths=list(root.rglob('*'))
    assert not any(p.is_symlink() for p in paths),'symlink in capsule'
    actual=sorted(str(p.relative_to(root)) for p in paths if p.is_file() and str(p.relative_to(root)) not in {'FILES.json','FREEZE.json'})
    assert actual==sorted(manifest),'closed roster mismatch'
    for name,pin in manifest.items():assert hashlib.sha256((root/name).read_bytes()).hexdigest()==pin,name
    freeze=json.loads((root/'FREEZE.json').read_text())
    assert freeze['files_sha256']==expected and freeze['payload_count']==len(manifest)
    return len(manifest)

if len(sys.argv)!=3 or sys.argv[1]!='--files-sha256':raise SystemExit('Usage: verify.py --files-sha256 OUTER_PIN')
count=closed(ROOT,sys.argv[2])
closed(ROOT/'capsule','ccfc2946ea8a71b25f1c14edf3eb2022be3984f6b1019a79b8a145cbd0909da1')
# Imported bounds use their producer's independently checked manifest convention.
bounds=ROOT/'numeric-bounds-v2'
assert hashlib.sha256((bounds/'FILES.json').read_bytes()).hexdigest()=='ba7e47fdf9896fb713de22d5975772157209b94dec6033e3126f84235ec1b25f'
manifest=json.loads((bounds/'FILES.json').read_text())
assert sorted(manifest)==sorted(str(f.relative_to(bounds)) for f in bounds.rglob('*') if f.is_file() and str(f.relative_to(bounds)) not in {'FILES.json','FREEZE.json'})
for name,pin in manifest.items():assert hashlib.sha256((bounds/name).read_bytes()).hexdigest()==pin,name
for directory in ['original','candidate','include']:
    for f in (ROOT/directory).rglob('*'):
        if f.is_file():assert f.read_bytes()==(ROOT/'capsule'/directory/f.relative_to(ROOT/directory)).read_bytes()
for name in ['replay.py','facade.cpp','harness.cpp','v1-helper.cpp','SOURCE-PINS.json','CANDIDATE-PINS.json']:
    assert (ROOT/name).read_bytes()==(ROOT/'capsule'/name).read_bytes()
a=json.loads((ROOT/'calibration/RESULT.json').read_text())
b=json.loads((ROOT/'relocated-calibration/RESULT.json').read_text())
assert a==b and len(a['runs'])==14
for row in a['runs']:
    assert (row['exit']==0)==(row['variant'] in ['original','candidate'])
    if row['variant'] in ['original','candidate']:assert row['rows']==168
for opt in ['-O0','-O2']:
    old=(ROOT/'calibration'/('original'+opt+'-run.log')).read_text().splitlines()
    new=(ROOT/'calibration'/('candidate'+opt+'-run.log')).read_text().splitlines()
    assert [r for r in old if r.startswith('ROW ')]==[r for r in new if r.startswith('ROW ')]
    assert 'V1_DOMAIN_PASS 2048' in new and 'EXACT_CHECKS_PASS' in new
    for role in ['original','candidate']:
        for witness in ['grouping','rect-origin','crossdoc-restart']:
            text=(ROOT/'calibration'/(role+opt+'-'+witness+'.log')).read_text()
            if role=='original' or witness=='crossdoc-restart':assert 'runtime error: signed integer overflow' in text
            else:assert 'WIDE_WITNESS_PASS' in text
            if role=='candidate' and witness=='crossdoc-restart':assert 'NUMERIC_RESTART' in text
controls=json.loads((ROOT/'GUARD-CONTROLS.json').read_text())
assert len(controls)==6 and all(c['exit']!=0 and not c['output_created'] for c in controls)
print(json.dumps({'verified_payloads':count,'native_replays':2,'paired_rows_per_optimization':168,'v1_domain_rows_per_optimization':2048,'semantic_mutants':5,'status':'PROPOSAL_PENDING_INDEPENDENT_REVIEW_AND_FULL_BUILD'}))
