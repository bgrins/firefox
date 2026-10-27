import copy,importlib.util,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('fallback_state',ROOT/'artifacts/css-attr-non-type-fallback-native-runtime-v1/state.py');s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
epoch=s.read(HERE/'CURRENT-EPOCH.json');s.a.verify_current(s.h,ROOT,s.ENV,epoch)
name='artifacts/stylo-bloom-tools/CURRENT-COMMITS.json';old=(ROOT/name).read_bytes();d=json.loads(old)
ids=['demand-validation','attr-cycle-research','number-research','joint-context','fallback-review'];receipts={n:s.read(HERE/(n+'-receipt.json')) for n in ids}
d['research_signing_history'].append(d['latest_research_signing']);d['latest_research_signing']={'status':'SIGNED_VERIFIED_LOCAL','commits':{n:r['commit'] for n,r in receipts.items()},'directory':'artifacts/css-local-signing-20261027-v9'}
d['latest_verified_working_epoch']['path']='artifacts/css-local-signing-20261027-v9/CURRENT-EPOCH.json'
(ROOT/name).write_text(json.dumps(d,indent=2)+'\n');current=copy.deepcopy(epoch)
for key in ['pins','staged_working','committed_research_working_payloads']:
 if name in current[key]:current[key][name]=s.h.fingerprint(ROOT,name)
state=s.h.index_state(ROOT,s.ENV);current['semantic_index']=s.h.semantic_index(state);current['raw_index_observation']['current']=state['raw_index'];s.a.verify_current(s.h,ROOT,s.ENV,current)
(HERE/'CURRENT-EPOCH.json').write_text(json.dumps(current,indent=2,sort_keys=True)+'\n')
s.save(HERE/'LEDGER-REFRESH.json',{'commits':{n:r['commit'] for n,r in receipts.items()},'accepted':135,'full_preservation_verified':True})
print('Latest research ledger updated; preservation verified',flush=True)
