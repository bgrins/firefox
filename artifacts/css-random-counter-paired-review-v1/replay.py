import copy
import hashlib
import importlib.util
import json
from collections import Counter
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
CAPSULE=ROOT/'artifacts/css-random-counter-paired-wpt-runner-v2'
OWNER=ROOT/'artifacts/css-random-counter-reversible-pair-v2'
RUNTIME=ROOT/'artifacts/css-random-counter-reversible-pair-runtime-1'
CAPSULE_SHA='b658dcad3916f77dfae980b2e66479d12b461d71d0f1c9dd469f366dadecaec6'
OWNER_SHA='793ebc740d97789fbdb57d3ab161012a9ebdc933a14195d4243f1bae20cc26da'
RUNTIME_SHA='53553a9253f123bc91282e6a2a3809337c47075c247e947c8413a89e62d648f2'
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
r=load('paired_review_runner',CAPSULE/'run.py');b=load('paired_review_bindings',CAPSULE/'bindings.py');a=load('paired_review_assessor',CAPSULE/'assess.py')
for path,digest in ((CAPSULE,CAPSULE_SHA),(OWNER,OWNER_SHA),(RUNTIME,RUNTIME_SHA)):r.authenticate(path,digest)
files,links=b.inventory(RUNTIME,r)
manifest=read(RUNTIME/'FILES.json');expected_files={n:(v['sha256'] if isinstance(v,dict) else v) for n,v in manifest.items()}
assert files=={**expected_files,'FILES.json':RUNTIME_SHA} and links==read(RUNTIME/'SYMLINKS.json')['links']
fixed=read(CAPSULE/'POLICY.json');checks=load('paired_review_checks',ROOT/fixed['helpers']['checks'])
expected={(url,name) for group in ('target_subtests','regression_subtests') for url,names in fixed[group].items() for name in names}
reg={(url,name) for url,names in fixed['regression_subtests'].items() for name in names};targets=expected-reg
assert len(expected)==553 and len(reg)==507 and len(targets)==46
assessments={};phase_reports={}
for role in ('original','candidate'):
    directory=RUNTIME/(role+'-wpt');p=read(directory/'POLICY.json');epoch=read(directory/'EPOCH.json');result=read(directory/'RESULT.json');saved=read(directory/'ASSESSMENT.json');metadata=read(directory/'APPLICATION-METADATA.json')
    assert b.bind_policy(ROOT,CAPSULE,fixed,epoch,sha(directory/'EPOCH.json'),role+'-1',r)==p
    b.validate_phase(ROOT,CAPSULE,p,epoch,r)
    original=b.validate_original(ROOT,CAPSULE,p,r)
    events=[json.loads(line) for line in (directory/'raw.jsonl').read_text().splitlines()]
    assessed=a.assess(events,result['exit'],p,checks,original=original,run_binding=metadata)
    publication=r.augment_assessment(assessed,phase=role+'-1',capsule_sha=CAPSULE_SHA,epoch_sha=sha(directory/'EPOCH.json'),policy=p,capsule_directory=str(CAPSULE.relative_to(ROOT)),experiment_sha=sha(CAPSULE/'EXPERIMENT.json'),execution_preserved=True)
    assert json.loads(json.dumps(publication))==saved
    rows=[x for x in events if x.get('action')=='test_status'];starts=[x for x in events if x.get('action')=='test_start'];ends=[x for x in events if x.get('action')=='test_end']
    assert len(rows)==553 and Counter((x['test'],x['subtest']) for x in rows)==Counter(expected)
    assert len(starts)==len(ends)==7 and Counter(x['test'] for x in starts)==Counter(fixed['tests'].keys())==Counter(x['test'] for x in ends)
    assert all(x['status'] in ('PASS','FAIL') for x in rows) and all(x['status']=='OK' for x in ends)
    assert saved['complete'] and saved['execution_preserved'] and not saved['errors'] and not saved['infrastructure_faults']
    assert result['observation_gate_passed'] and result['execution_error'] is None and result['preservation_error'] is None and not result['native_fix_acceptance']
    assert result['comparison_gate_passed']==(role=='candidate')
    assert read(directory/'PRE.json')==read(directory/'POST.json')
    assert metadata==read(directory/'APPLICATION-METADATA-POST.json')
    assert saved['run_info']['browser_build_id']==metadata['browser_build_id'] and saved['run_info']['revision']==metadata['revision']==fixed['frozen_head']
    assert read(directory/'NORMAL-BINARIES.json')==p['phase_binaries'] and all(epoch['pins'][n]==v for n,v in p['phase_binaries'].items())
    assert all(epoch['pins'][n]==v for n,v in fixed['source_roles'][role].items())
    cleanup=read(directory/'CLEANUP.json');assert cleanup['owned_group_absent'] and cleanup['temporary_root_removed']
    assert read(RUNTIME/(role+'-WRAPPER-CLEANUP.json'))['restoration_safe']
    process=read(directory/'PROCESS.json');assert process['pid']==process['pgid'] and process['pid']>0
    command=read(directory/'COMMAND.json');assert command['wrapper_manifest_sha256']==CAPSULE_SHA and command['epoch_sha256']==sha(directory/'EPOCH.json')
    assert set(x.removeprefix('--include=') for x in command['command'] if x.startswith('--include='))==set(fixed['tests'])
    build=RUNTIME/(role+'-build');assert (directory/'EPOCH.json').read_bytes()==(build/'EPOCH.json').read_bytes()
    for name in ('build-GROUP-CLEANUP.json','wake-GROUP-CLEANUP.json'):assert read(build/name)['owned_group_absent']
    for name,item in read(CAPSULE/'SOURCE-PINS.json').items():
        relative=Path(name.removeprefix('testing/web-platform/'));dest=(directory/('tests' if relative.parts[0]=='tests' else 'metadata')).joinpath(*relative.parts[1:])
        if item['exists']:assert sha(dest)==item['sha256']
        else:assert not dest.exists()
    phase_reports[role]={'subtests':len(rows),'statuses':dict(Counter(x['status'] for x in rows)),'build_id':metadata['browser_build_id'],'assessment_sha256':sha(directory/'ASSESSMENT.json'),'full_publication_replay':True,'preservation_cleanup_and_build_joins':True}
    assessments[role]=saved

def signature(x):
    return tuple((k,k in x,json.dumps(x.get(k),sort_keys=True)) for k in ('status','message','expected','known_intermittent'))
old={(x['test'],x['subtest']):x for x in assessments['original']['rows']};new={(x['test'],x['subtest']):x for x in assessments['candidate']['rows']}
assert all(signature(old[k])==signature(new[k]) for k in reg)
assert all(new[k]['status']=='PASS' for k in targets)
repaired=[k for k in targets if old[k]['status']=='FAIL'];assert len(repaired)==18
oldends={x['test']:x for x in assessments['original']['ends']};assert all(signature(oldends[x['test']])==signature(x) for x in assessments['candidate']['ends'])
assert phase_reports['original']['statuses']=={'PASS':526,'FAIL':27}
assert phase_reports['candidate']['statuses']=={'PASS':544,'FAIL':9}
run_changes=[k for k in assessments['original']['run_info'] if assessments['original']['run_info'][k]!=assessments['candidate']['run_info'].get(k)]
assert set(assessments['original']['run_info'])==set(assessments['candidate']['run_info']) and set(run_changes)<= {'browser_build_id'}
result=read(RUNTIME/'RESULT.json');assert result['success'] and result['restoration_verified'] and result['runtime_controls_unchanged'] and result['empty_staging_preserved'] and result['backups_removed_after_verification']
assert result['error'] is None and not result['publication_errors'] and not result['native_fix_acceptance']
for role in ('original','candidate'):assert result['phase_results'][role]=={'assessment_sha256':phase_reports[role]['assessment_sha256'],'wrapper_exit':0}
restore=read(RUNTIME/'RESTORATION.json');assert not restore['errors'] and not restore['owned_processes'] and restore['source_sha256']==fixed['source_roles']['original']
cleanup=read(RUNTIME/'BACKUP-CLEANUP.json');assert cleanup['removed'] and cleanup['verified_original_restoration'] and not cleanup['retained_after_experiment_failure'] and cleanup['inventory_sha256']==sha(RUNTIME/'BACKUPS.json')
raw=read(RUNTIME/'RAW-INDEX-OBSERVATION.json');pre=read(RUNTIME/'PRE-OBSERVATION-EPOCH.json');post=read(RUNTIME/'POST-OBSERVATION-EPOCH.json');normalized=copy.deepcopy(post);normalized['raw_index_observation']['current']=pre['raw_index_observation']['current'];assert normalized==pre
assert raw['before']==pre['raw_index_observation']['current'] and raw['after']==post['raw_index_observation']['current'] and raw['semantic_index_unchanged'] and raw['cause']=='unknown' and not raw['runtime_epoch_updated']
before=read(RUNTIME/'PRE.json');after=read(RUNTIME/'POST.json');normalized=copy.deepcopy(after);normalized['index']['raw_index']=before['index']['raw_index'];assert normalized==before
assert after['index']['raw_index']==raw['after']
assert pre['accepted_line_height']==post['accepted_line_height'] and pre['accepted_line_height']['fix']==141
assert all(pre['pins'][n]==v==post['pins'][n] for n,v in pre['accepted_line_height']['files'].items())
assert post['modified_native_paths']==['servo/components/style/custom_properties.rs'] and post['staged_working']=={}
terminal=read(RUNTIME/'ROOT-TERMINAL.json');assert terminal['exit_code']==0 and terminal['source_application_restored'] and terminal['exact_landing_wpt_execution_pending']
report={'complete':True,'phase_reports':phase_reports,'targets':46,'target_repairs':18,'regression_signatures_preserved':507,'harness_end_signatures_preserved':7,'remaining_failures_preserved':9,'run_info_changes':run_changes,'saved_source_application_restoration_verified':True,'raw_index_drift':raw,'accepted_line_height_preserved':True,'native_fix_acceptance':False,'supports_candidate_promotion':True,'exact_standalone_landing_fixture_execution_pending':True,'new_browser_or_live_guard_executed':False,'remaining_failures':[{'test':k[0],'subtest':k[1],'message':v.get('message')} for k,v in sorted(new.items()) if v['status']=='FAIL']}
for name,value in [('REVIEW.json',report),('EVIDENCE.json',{'capsule_manifest':CAPSULE_SHA,'owner_manifest':OWNER_SHA,'runtime_manifest':RUNTIME_SHA,'runtime_payloads':len(manifest),'symlinks':links})]:
    path=HERE/name
    if path.exists():assert read(path)==value
    else:path.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='remaining_failures'}))
