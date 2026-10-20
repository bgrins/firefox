import hashlib
import json
from pathlib import Path
from collections import Counter
import sys

repo=Path(sys.argv[1]).resolve()
out=Path(sys.argv[2]).resolve()
root=repo/'artifacts/css-attr-leading-whitespace-root-v1'
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
raw=lambda p:[json.loads(line) for line in p.read_text().splitlines()]
key=lambda row:(row['test'],row['subtest'])
status=lambda row:(row['status'],row.get('message'))
run=read(root/'candidate-wpt-v1/RUN.json')
assert run['phase']=='done' and run['complete'] and run['stable'] and run['exit']==run['build_exit']==0
assert run['before']==run['after']
records=raw(root/'candidate-wpt-v1/raw.json')
assert run['rows']==[r for r in records if r.get('action')=='test_status']
assert run['harness']==[r for r in records if r.get('action')=='test_end']
assert Counter(r['status'] for r in run['rows'])=={'PASS':373,'FAIL':2}
assert len(run['harness'])==21 and all(r['status']=='OK' for r in run['harness'])
previous=read(repo/'artifacts/css-animation-invalid-publication-fix-v1/RUN.json')['rows']
controls=read(repo/'artifacts/css-animation-invalid-publication-controls-v1/RUN.json')['rows']
before={key(r):status(r) for r in previous+controls}
after={key(r):status(r) for r in run['rows']}
assert len(before)==349 and len(after)==375 and before.keys()<=after.keys()
assert all(after[k]==v for k,v in before.items())
new=[r for r in run['rows'] if key(r) not in before]
assert len(new)==26 and all(r['test']=='/css/css-values/attr-substitution-leading-whitespace.html' and r['status']=='PASS' for r in new)
candidate=read(root/'CANDIDATE.json')
assert sha(root/'candidate-custom-properties.rs')==candidate['candidate_sha256']==run['before'][candidate['native_path']]
assert sha(repo/candidate['wpt']['path'])==candidate['wpt']['sha256']==run['before'][candidate['wpt']['path']]
release=read(root/'release-v1/RUN.json');baseline=read(root/'baseline-v1/RUN.json')
for receipt in [release,baseline]:assert receipt['stable'] and receipt['before']==receipt['after']
for receipt in [release,baseline]:
 plain=next(row for row in receipt['rows'] if row['case']=='plain')
 assert plain['result_received'] and any(e.get('data',{}).get('actual')=='37px' for e in plain['events'])
crashes=[]
for case in ['space','minimal']:
 files=list((root/'release-v1'/case/'minidumps').glob('*.extra'));assert len(files)==1
 data=read(files[0]);assert data['ProcessType']=='content'
 assert data['MozCrashReason']=='start byte index 9 is out of bounds of `var(--v)`'
 crashes.append({'case':case,'extra_sha256':sha(files[0]),'product':data['ProductName'],'version':data['Version'],'channel':data['ReleaseChannel'],'process':data['ProcessType'],'reason':data['MozCrashReason']})
minimal=(root/'release-v1/minimal/served.html').read_text();assert '<script' not in minimal and 'data-x=" var(--v)"' in minimal
result={'status':'PASS','candidate_rows':{'PASS':373,'unchanged_expected_FAIL':2},'harness_OK':21,'new_WPT_PASS':26,'unchanged_prior_status_message_pairs':349,'new_WPT_baseline_execution':False,'baseline_controls':'plain 37px on local and installed release; local literal 37px recorded separately','release_crash_evidence':crashes,'script_free_minimal_sha256':sha(root/'release-v1/minimal/served.html'),'candidate_receipt_sha256':sha(root/'candidate-wpt-v1/RUN.json'),'candidate_raw_sha256':sha(root/'candidate-wpt-v1/raw.json'),'release_receipt_sha256':sha(root/'release-v1/RUN.json'),'native_sha256':candidate['candidate_sha256'],'wpt_sha256':candidate['wpt']['sha256'],'scope':'Independent retained-receipt reconciliation, not reviewer browser execution; no isolated upstream build/run.'}
out.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['release_crash_evidence']}))
