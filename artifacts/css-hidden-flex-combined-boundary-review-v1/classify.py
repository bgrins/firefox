import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('Use python3 -I -S')
import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--run', required=True, type=Path)
parser.add_argument('--output', required=True, type=Path)
args = parser.parse_args()
if args.output.exists():
    raise SystemExit('output already exists')
expected = json.loads((HERE/'INPUTS.json').read_text())['expected_subtests']
run = json.loads(args.run.read_text())
if not run['complete'] or run['before'] != run['after']:
    raise SystemExit('incomplete or unstable WPT phase')
rows = []
for test, names in expected.items():
    actual = [r for r in run['rows'] if r['test'] == test]
    if [r['subtest'] for r in actual] != names:
        raise SystemExit('boundary roster mismatch')
    for row in actual:
        message = row.get('message') or ''
        if row['status'] == 'PASS':
            category = 'all_fixture_assertions_pass'
        elif any(s in message for s in ['visible calibration', 'independent visible calibration', 'actual visible fragmentation', 'visible containing block fragmented', 'visible OOF fragmented', 'visible count', 'visible fragment']):
            category = 'visible_calibration_failure_target_verdict_unavailable'
        elif 'offset parent' in message:
            category = 'ownership_identity_assertion_failure'
        elif 'warm' in message or 'external owner before hidden' in message:
            category = 'initial_target_geometry_failure'
        elif 'shown' in message or 'external owner restored' in message:
            category = 'restored_target_geometry_failure'
        elif 'hidden' in message or 'insertion' in message or 'resize' in message:
            category = 'post_hide_target_geometry_failure'
        else:
            category = 'unclassified_failure_requires_manual_read'
        rows.append({'test':test,'name':row['subtest'],'status':row['status'],'category':category,'message':message,'stack':row.get('stack')})
result = {'run_path':str(args.run.resolve()),'run_sha256':hashlib.sha256(args.run.read_bytes()).hexdigest(),'rows':rows,'counts':{c:sum(r['category']==c for r in rows) for c in sorted({r['category'] for r in rows})},'qualification':'Classification of first failing assertions only; hidden-target observations are not inferred when reference calibration failed.'}
args.output.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result['counts'],sort_keys=True))
