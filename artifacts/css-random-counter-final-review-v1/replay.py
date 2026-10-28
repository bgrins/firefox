import hashlib
import importlib.util
import json
from collections import Counter
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
CAPSULE=ROOT/'artifacts/css-random-counter-final-wpt-v1'
RUNTIME=ROOT/'artifacts/css-random-counter-promotion-runtime-v1/candidate-wpt'
CAPSULE_SHA='58d1b9d4266b329a3fdb9f8f7c4c80e2500b1c9818b45a6e305092e709e5cfe9'
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
r=load('review_runner',CAPSULE/'run.py');b=load('review_bindings',CAPSULE/'bindings.py')
r.authenticate(CAPSULE,CAPSULE_SHA)
fixed=read(CAPSULE/'POLICY.json');p=read(RUNTIME/'POLICY.json');epoch=read(RUNTIME/'EPOCH.json')
bound=b.bind_policy(ROOT,CAPSULE,fixed,epoch,sha(RUNTIME/'EPOCH.json'),'candidate-1',r)
original=b.validate_original(ROOT,CAPSULE,bound,r)
assert bound==p
result=read(RUNTIME/'RESULT.json');saved=read(RUNTIME/'ASSESSMENT.json');metadata=read(RUNTIME/'APPLICATION-METADATA.json')
assert result=={'comparison_gate_passed':True,'execution_error':None,'exit':0,'native_fix_acceptance':False,'observation_gate_passed':True,'observation_only':False,'phase':'candidate-1','preservation_error':None}
checks=load('review_checks',ROOT/p['helpers']['checks']);assessor=load('review_assessor',CAPSULE/'assess.py')
events=[json.loads(line) for line in (RUNTIME/'raw.jsonl').read_text().splitlines()]
replayed=assessor.assess(events,result['exit'],p,checks,original=original,run_binding=metadata)
published=r.augment_assessment(replayed,phase='candidate-1',capsule_sha=CAPSULE_SHA,epoch_sha=sha(RUNTIME/'EPOCH.json'),policy=p,capsule_directory=str(CAPSULE.relative_to(ROOT)),experiment_sha=sha(CAPSULE/'EXPERIMENT.json'),execution_preserved=True)
assert json.loads(json.dumps(published))==saved
rows=[e for e in events if e.get('action')=='test_status'];starts=[e for e in events if e.get('action')=='test_start'];ends=[e for e in events if e.get('action')=='test_end']
expected={(url,name) for group in ('target_subtests','regression_subtests') for url,names in p[group].items() for name in names}
assert len(rows)==553 and Counter((x['test'],x['subtest']) for x in rows)==Counter(expected)
assert len(starts)==len(ends)==7 and Counter(x['test'] for x in starts)==Counter(p['tests'].keys())==Counter(x['test'] for x in ends)
targets={(url,name) for url,names in p['target_subtests'].items() for name in names}
assert len(targets)==46 and all(x['status']=='PASS' for x in rows if (x['test'],x['subtest']) in targets)
assert Counter(x['status'] for x in rows)=={'PASS':544,'FAIL':9} and all(x['status']=='OK' for x in ends)
def signature(x):
    return tuple((k,k in x,json.dumps(x.get(k),sort_keys=True)) for k in ('status','message','expected','known_intermittent'))
oldrows={(x['test'],x['subtest']):x for x in original['rows']};newrows={(x['test'],x['subtest']):x for x in rows}
reg={(url,name) for url,names in p['regression_subtests'].items() for name in names}
assert len(reg)==507 and all(signature(oldrows[k])==signature(newrows[k]) for k in reg)
oldends={x['test']:x for x in original['ends']};assert all(signature(oldends[x['test']])==signature(x) for x in ends)
failures=[k for k,x in oldrows.items() if x['status']=='FAIL']; repaired=[k for k in failures if k not in reg]
assert len(failures)==27 and len(repaired)==18 and all(newrows[k]['status']=='PASS' for k in repaired)
assert len([k for k in failures if k in reg])==9
projection=p['original_binding']['landing_projection']; assert projection['raw_events_rewritten'] is False and projection['historical_assessment_relabelled'] is False and projection['requires_fresh_landing_execution'] is True
assert (projection['page'],projection['landing_control']) in targets and (projection['page'],projection['historical_control']) not in targets
assert newrows[(projection['page'],projection['landing_control'])]['status']=='PASS'
assert read(RUNTIME/'PRE.json')==read(RUNTIME/'POST.json')
assert metadata==read(RUNTIME/'APPLICATION-METADATA-POST.json')==read(ROOT/p['build_directory']/'APPLICATION-METADATA.json')
cleanup=read(RUNTIME/'CLEANUP.json');assert cleanup['owned_group_absent'] and cleanup['temporary_root_removed']
process=read(RUNTIME/'PROCESS.json');assert process['pid']==process['pgid'] and process['pid']>0
command=read(RUNTIME/'COMMAND.json');assert command['wrapper_manifest_sha256']==CAPSULE_SHA and command['epoch_sha256']==p['epoch_sha256'] and command['phase']=='candidate-1'
assert set(x.removeprefix('--include=') for x in command['command'] if x.startswith('--include='))==set(p['tests'])
assert '--headless' in command['command'] and '--processes=1' in command['command']
outer=read(RUNTIME/'ROOT-TERMINAL.json');assert outer['exit_code']==0 and outer['session']==67000 and outer['terminal']=='02ad22'
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
PROMOTION_SHA='9a7d2871eb197eec24dba42d489ed5acd9625c92753bb6196f3f2ed7d5788312'
assert sha(owner/'FILES.json')==PROMOTION_SHA
manifest=read(owner/'FILES.json'); assert len(manifest)==77
files={str(f.relative_to(owner)):sha(f) for f in owner.rglob('*') if f.is_file() and not f.is_symlink()}
links={str(f.relative_to(owner)):str(f.readlink()) for f in owner.rglob('*') if f.is_symlink()}
assert files==dict(manifest,**{'FILES.json':PROMOTION_SHA})
assert links==read(owner/'SYMLINKS.json')['links']=={'candidate-wpt/tests/tools':str(ROOT/'testing/web-platform/tests/tools')}
recovery=read(owner/'INSTALL-RECOVERY.json'); assert recovery['installer_reexecuted'] is False and recovery['subsequent_guarded_build_exit']==0
assert recovery['observed_install_result']==read(owner/'INSTALL-RESULT.json') and recovery['observed_installed_epoch_sha256']==sha(owner/'INSTALLED-EPOCH.json')
retirement=read(owner/'RETIREMENT.json'); assert sha(ROOT/retirement['archived_path'])==retirement['claim']['owned_sha256']
installed=read(owner/'INSTALLED-EPOCH.json'); normalized=json.loads(json.dumps(epoch))
for name in p['rebuilt_binaries']: normalized['pins'][name]=installed['pins'][name]
normalized['raw_index_observation']['current']=installed['raw_index_observation']['current']
normalized['random_counter_transition']=installed['random_counter_transition']
assert normalized==installed
assert epoch['random_counter_transition']['compiled'] is True and epoch['random_counter_transition']['accepted'] is False
pins={str((owner/name).relative_to(ROOT)):digest for name,digest in files.items()}
pins.update(p['build_evidence']);pins[str(CAPSULE.relative_to(ROOT))+'/FILES.json']=CAPSULE_SHA
if (HERE/'EVIDENCE.json').exists():
    pins=read(HERE/'EVIDENCE.json')
    assert all(sha(ROOT/name)==digest for name,digest in pins.items())
report={'complete_raw_and_publication_replay':True,'original_subtests':553,'original_pass':526,'original_fail':27,'final_subtests':553,'final_pass':544,'final_fail':9,'target_pass':46,'regression_signatures_preserved':507,'unchanged_regression_failures':9,'harness_end_signatures_preserved':7,'repairs':18,'saved_preservation_and_cleanup_verified':True,'actual_installed_build_and_metadata_joined':True,'run_info_changes':run_info_changes,'landing_projection':projection,'fresh_landing_control_pass':True,'independent_live_process_or_source_census':False,'browser_reexecuted':False,'native_fix_acceptance':False,'evidence_supports_acceptance':True,'installation_terminal_limit':'Original installer exec/terminal IDs unavailable; durable installed state and subsequent guarded successful build retained without fabricating an original terminal.','repaired_original_targets':[list(k) for k in repaired]}
for name,data in [('REVIEW.json',report),('EVIDENCE.json',pins)]:
    path=HERE/name
    if path.exists(): assert read(path)==data
    else: path.write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')
print(json.dumps(report))
