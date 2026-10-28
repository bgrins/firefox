import hashlib
import importlib.util
import json
from collections import Counter
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
CAPSULE=ROOT/'artifacts/css-line-height-final-wpt-v1'
RUNTIME=ROOT/'artifacts/css-line-height-promotion-runtime-v1/candidate-wpt'
CAPSULE_SHA='fd5ddcff03b0e861f59788da712d4c511e0fcc8a61aeabc523257cddf9ba2729'
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
r=load('review_runner',CAPSULE/'run.py');b=load('review_bindings',CAPSULE/'bindings.py')
r.authenticate(CAPSULE,CAPSULE_SHA)
fixed=read(CAPSULE/'POLICY.json');p=read(RUNTIME/'POLICY.json');epoch=read(RUNTIME/'EPOCH.json')
assert b.bind_policy(ROOT,CAPSULE,fixed,epoch,sha(RUNTIME/'EPOCH.json'),'candidate-1',r)==p
original=b.validate_original(ROOT,CAPSULE,p,r)
result=read(RUNTIME/'RESULT.json');saved=read(RUNTIME/'ASSESSMENT.json');metadata=read(RUNTIME/'APPLICATION-METADATA.json')
assert result=={'comparison_gate_passed':True,'execution_error':None,'exit':0,'native_fix_acceptance':False,'observation_gate_passed':True,'observation_only':False,'phase':'candidate-1','preservation_error':None}
checks=load('review_checks',ROOT/p['helpers']['checks']);assessor=load('review_assessor',CAPSULE/'assess.py')
events=[json.loads(line) for line in (RUNTIME/'raw.jsonl').read_text().splitlines()]
replayed=assessor.assess(events,result['exit'],p,checks,original=original,run_binding=metadata)
published=r.augment_assessment(replayed,phase='candidate-1',capsule_sha=CAPSULE_SHA,epoch_sha=sha(RUNTIME/'EPOCH.json'),policy=p,capsule_directory=str(CAPSULE.relative_to(ROOT)),experiment_sha=sha(CAPSULE/'EXPERIMENT.json'),execution_preserved=True)
assert json.loads(json.dumps(published))==saved
rows=[e for e in events if e.get('action')=='test_status'];starts=[e for e in events if e.get('action')=='test_start'];ends=[e for e in events if e.get('action')=='test_end']
expected={(url,name) for group in ('target_subtests','regression_subtests') for url,names in p[group].items() for name in names}
assert len(rows)==34 and Counter((x['test'],x['subtest']) for x in rows)==Counter(expected)
assert len(starts)==len(ends)==6 and Counter(x['test'] for x in starts)==Counter(p['tests'].keys())==Counter(x['test'] for x in ends)
assert all(x['status']=='PASS' for x in rows) and all(x['status']=='OK' for x in ends)
def signature(x):
    return tuple((k,k in x,json.dumps(x.get(k),sort_keys=True)) for k in ('status','message','expected','known_intermittent'))
oldrows={(x['test'],x['subtest']):x for x in original['rows']};newrows={(x['test'],x['subtest']):x for x in rows}
reg={(url,name) for url,names in p['regression_subtests'].items() for name in names}
assert len(reg)==22 and all(signature(oldrows[k])==signature(newrows[k]) for k in reg)
oldends={x['test']:x for x in original['ends']};assert all(signature(oldends[x['test']])==signature(x) for x in ends)
failures=[k for k,x in oldrows.items() if x['status']=='FAIL'];assert len(failures)==7 and all(k not in reg for k in failures)
assert read(RUNTIME/'PRE.json')==read(RUNTIME/'POST.json')
assert metadata==read(RUNTIME/'APPLICATION-METADATA-POST.json')==read(ROOT/p['build_directory']/'APPLICATION-METADATA.json')
cleanup=read(RUNTIME/'CLEANUP.json');assert cleanup['owned_group_absent'] and cleanup['temporary_root_removed']
process=read(RUNTIME/'PROCESS.json');assert process['pid']==process['pgid'] and process['pid']>0
command=read(RUNTIME/'COMMAND.json');assert command['wrapper_manifest_sha256']==CAPSULE_SHA and command['epoch_sha256']==p['epoch_sha256'] and command['phase']=='candidate-1'
assert set(x.removeprefix('--include=') for x in command['command'] if x.startswith('--include='))==set(p['tests'])
assert '--headless' in command['command'] and '--processes=1' in command['command']
outer=read(RUNTIME/'OUTER.json');assert outer['exit_code']==0 and outer['result_sha256']==sha(RUNTIME/'RESULT.json')
assert read(RUNTIME/'COMPARISON.json')=={'comparison_gate_passed':True,'errors':[],'native_fix_acceptance':False}
for name,digest in p['build_evidence'].items(): assert sha(ROOT/name)==digest,name
assert (RUNTIME/'EPOCH.json').read_bytes()==(ROOT/p['build_epoch']).read_bytes()
owner=ROOT/p['owner_runtime'];ownership=read(owner/'OWNERSHIP.json');baseline=read(CAPSULE/'PROMOTION-BASELINE-EPOCH.json')
b.project_promotion(epoch,baseline,p,ownership,r)
built=read(ROOT/p['build_result']);inner=read(ROOT/p['inner_build_result'])
assert built['command_success'] and built['preservation_verified'] and built['error'] is None and not built['owned_processes'] and not built['publication_errors'] and built['browser_build_performed'] and not built['accepted']
assert inner['exit']==0 and inner['error'] is None and inner['stop_reason'] is None and inner['owned_group_absent'] and not inner['cleanup_errors']
assert read(RUNTIME/'NORMAL-BINARIES.json')==p['phase_binaries']
assert all(epoch['pins'][n]==v for n,v in p['phase_binaries'].items())
assert all(read(RUNTIME/'INPUT-PINS.json')[n]==v for n,v in p['live_oracle_sources'].items())
assert original['run_info'].keys()==saved['run_info'].keys()
run_info_changes=[k for k in original['run_info'] if original['run_info'][k]!=saved['run_info'][k]]
assert set(run_info_changes)<= {'browser_build_id'}
for name,item in read(CAPSULE/'SOURCE-PINS.json').items():
    relative=Path(name.removeprefix('testing/web-platform/'))
    destination=(RUNTIME/('tests' if relative.parts[0]=='tests' else 'metadata')).joinpath(*relative.parts[1:])
    if item['exists']: assert sha(destination)==item['sha256'],name
    else: assert not destination.exists(),name
pins={str(f.relative_to(ROOT)):sha(f) for f in RUNTIME.rglob('*') if f.is_file() and not f.is_symlink() and 'tools' not in f.relative_to(RUNTIME).parts}
pins.update(p['build_evidence']);pins[str(CAPSULE.relative_to(ROOT))+'/FILES.json']=CAPSULE_SHA
if (HERE/'EVIDENCE.json').exists():
    pins=read(HERE/'EVIDENCE.json')
    assert all(sha(ROOT/name)==digest for name,digest in pins.items())
report={'complete_raw_and_publication_replay':True,'original_subtests':34,'original_pass':27,'original_fail':7,'final_subtests':34,'final_pass':34,'target_pass':12,'regression_signatures_preserved':22,'harness_end_signatures_preserved':6,'repairs':7,'saved_preservation_and_cleanup_verified':True,'actual_installed_build_and_metadata_joined':True,'run_info_changes':run_info_changes,'independent_live_process_or_source_census':False,'browser_reexecuted':False,'native_fix_acceptance':False,'evidence_supports_acceptance':True,'original_failures':[list(k) for k in failures]}
for name,data in [('REVIEW.json',report),('EVIDENCE.json',pins)]:
    path=HERE/name
    if path.exists(): assert read(path)==data
    else: path.write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')
print(json.dumps(report))
