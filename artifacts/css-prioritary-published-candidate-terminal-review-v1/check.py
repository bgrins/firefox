import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

r=load('review_module',HERE/'review.py');observation=load('observation_module',HERE/'observations.py')
config,owner=r.authenticate()
assert not config['execution_enabled'] and config['actual_terminal'] is None
assert config['expected_session'] is None or type(config['expected_session']) is int
policy=r.read(HERE/'OWNER-PREPARED-POLICY.json')
roles=r.read(owner/'SOURCE-ROLES.json')
closure=load('saved_current_closure',HERE/'closure.py')
assert closure.external_inputs(ROOT,policy,roles)==policy['intermediate_consumed_inputs']
binder=load('saved_input_binder',HERE/'inputs.py')
consumed=binder.bind_inputs(policy['owner_directory'],(HERE/'OWNER-PREPARED-FILES.json').read_bytes(),config['prepared_owner_manifest_sha256'],policy['intermediate_consumed_inputs'])
assert all(policy[name] is not None for name in ['head','baseline_binding','baseline_capsule','controls','current_binding','execution_handoff','checkpoint_bridge'])
assert not policy['execution_enabled'] and not policy['candidate_execution_enabled']
assert len(policy['intermediate_consumed_inputs']) > 400
actual_comparison=load('actual_original77_replay',owner/'comparison.py')
actual_originals=actual_comparison.replay_all(ROOT,policy)
actual_rows=[row for lane in actual_originals.values() for row in lane['rows']]
assert observation.counts(actual_rows)=={'PASS':64,'FAIL':13}
assert sum(len(lane['ends']) for lane in actual_originals.values())==12
actual_targets=[row for lane,original in actual_originals.items() for row in original['rows'] if row['subtest'] in policy['wpt_lanes'][lane]['target_subtests'].get(row['test'],[])]
assert len(actual_targets)==24 and observation.counts(actual_targets)=={'PASS':12,'FAIL':12}
assessor_actual=load('actual_preservation_signatures',owner/'assess.py')
actual_ends=[row for lane in actual_originals.values() for row in lane['ends']]
actual_preservation=observation.preservation(actual_originals,actual_rows,actual_ends,policy,assessor_actual.signature,True)
assert actual_preservation['original_pass_count']==64 and actual_preservation['published_count']==8
assert actual_preservation['prior_pass_preserved'] and actual_preservation['endings_preserved'] and actual_preservation['published_preserved']
assert actual_preservation['targets_all_pass'] is False
improved=copy.deepcopy(actual_rows)
required={(page,name) for settings in policy['wpt_lanes'].values() for page,names in settings['target_subtests'].items() for name in names}
for row in improved:
    if (row['test'],row['subtest']) in required and row['status']!='PASS':
        row['status']='PASS';row.pop('message',None)
improved_check=observation.preservation(actual_originals,improved,actual_ends,policy,assessor_actual.signature,True)
assert all(improved_check[key] for key in ['targets_all_pass','prior_pass_preserved','endings_preserved','published_preserved'])
for label in ['PASS','published','ending']:
    changed_rows=copy.deepcopy(actual_rows);changed_ends=copy.deepcopy(actual_ends)
    if label=='ending':target=changed_ends[0]
    elif label=='published':
        names={(page,name) for settings in policy['wpt_lanes'].values() for page,subtests in settings['published_subtests'].items() for name in subtests}
        target=next(row for row in changed_rows if (row['test'],row['subtest']) in names)
    else:target=next(row for row in changed_rows if row['status']=='PASS')
    target['message']='changed full signature'
    checked=observation.preservation(actual_originals,changed_rows,changed_ends,policy,assessor_actual.signature,True)
    assert not checked[{'PASS':'prior_pass_preserved','published':'published_preserved','ending':'endings_preserved'}[label]]
partial=observation.preservation(actual_originals,[actual_rows[0],actual_rows[0]],[],policy,assessor_actual.signature,False)
assert partial['prior_pass_preserved'] is None and partial['targets_all_pass'] is None and len(partial['ambiguous_keys'])==1
policy['head']='e'*40
for settings in [policy['wpt'],*policy['wpt_lanes'].values()]:
    settings['harness_revision']=policy['head'];settings['phase_revisions']={'original':policy['head'],'candidate':policy['head']}
wpt=load('actual_staging',owner/'wpt.py')
synthetic=load('saved_synthetic',ROOT/'artifacts/css-prioritary-selection-original-v1/check.py')
assessor=load('original_assessor',owner/'assess.py')
checks=load('saved_stream_checks',ROOT/policy['wpt']['checks_helper'])
results=['actual baseline64PASS/13FAIL and24targets12PASS/12FAIL replayed','all24 target improvements accepted with64priorPASS/endings/eightpublished preserved','independent full-signature PASS/published/ending mutations rejected','partial duplicate callback evidence remains ambiguous and gates null']
bad_policy=copy.deepcopy(policy)
bad_policy['intermediate_consumed_inputs'].pop(next(iter(bad_policy['intermediate_consumed_inputs'])))
try:r.consumed_map(owner,bad_policy,roles,config['prepared_owner_manifest_sha256'])
except AssertionError:results.append('omitted consumed input rejected by independent reconstruction')
else:raise AssertionError('omitted consumed input accepted')
with tempfile.TemporaryDirectory(prefix='css-published-candidate77-review-',dir='/private/tmp') as scratch:
    scratch_path=Path(scratch);root=scratch_path/'root';root.mkdir();pair=scratch_path/'runtime';pair.mkdir()
    (root/'testing/web-platform/tests/tools').mkdir(parents=True)
    for relative in [policy['owner_directory']+'/assess.py',policy['owner_directory']+'/comparison.py','artifacts/css-minmax-relative-infinity-broader-browser-v5/assess.py',policy['wpt']['checks_helper']]:
        target=root/relative;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((ROOT/relative).read_bytes())
    for settings in policy['wpt_lanes'].values():
        pins=list(settings['resources'].values())+list(settings['manifests'].values())+list(settings['install_managed_resources'].values())
        pins += [entry for group in settings['metadata'].values() for entry in group.values() if entry['sha256'] is not None]
        for pin in pins:
            source=ROOT/pin['path'];target=root/pin['path'];target.parent.mkdir(parents=True,exist_ok=True);assert r.sha(source)==pin['sha256'];target.write_bytes(source.read_bytes())
        server=root/settings['server_config']['path'];server.parent.mkdir(parents=True,exist_ok=True);server.write_text(json.dumps({'ports':{}}));settings['server_config']['sha256']=r.sha(server)
        base_config=root/settings['wpt_config'];base_config.parent.mkdir(parents=True,exist_ok=True);base_config.write_text('[paths]\n[web-platform-tests]\n')
    capture_dir=Path(policy['capture_binding']['directory'])
    for name in ['capture.py','candidate.html','record.js','receive.py']:
        target=root/capture_dir/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((ROOT/capture_dir/name).read_bytes())
    snapshot={'index':{'head':policy['head'],'entries':'e','cached_diff':hashlib.sha256(b'').hexdigest(),'working_diff':hashlib.sha256(b'').hexdigest()},'nested_index':{'same':True},'working_sources_binaries_research_preserved':True,'current_raw_stable_during_check':True}
    full_snapshot=copy.deepcopy(snapshot)
    snapshot.pop('working_sources_binaries_research_preserved')
    snapshot.update(working_sources_binaries_preserved=True,archival_research_not_rechecked=True,verification_scope='intermediate-consumed-inputs-v1',consumed_inputs_sha256=hashlib.sha256(json.dumps(consumed,sort_keys=True,separators=(',',':')).encode()).hexdigest())
    binaries={name:'built' for name in policy['rebuilt_binaries']}
    sources={name:role['candidate_sha256'] for name,role in r.read(owner/'SOURCE-ROLES.json').items()}
    built={'command_success':True,'preservation_verified':True,'error':None,'native_sources':sources,'binaries':binaries,'snapshot':snapshot,'browser_build_performed':True}
    (pair/'candidate-build').mkdir();wpt.save(pair/'candidate-build/RESULT.json',built);wpt.save(pair/'candidate-build/COMMAND.json',{'source_sha256':sources})
    wpt.save(pair/'PHASES-PRE.json',snapshot);wpt.save(pair/'PHASES-POST.json',snapshot)
    all_rows=[];all_ends=[];phase_receipts={};originals={};behaviors={}
    comparison=load('saved_behavior',owner/'comparison.py')
    real_load=observation.load
    def reviewed_load(name,path):
        if name=='candidate74_comparison':return SimpleNamespace(replay_all=lambda root,policy:originals,behavior=comparison.behavior)
        return real_load(name,path)
    observation.load=reviewed_load
    policy['baseline_binding']={'directory':'saved-original'}
    for index,lane in enumerate(policy['lane_order']):
        phase=pair/('candidate-wpt-'+lane);phase.mkdir();settings=policy['wpt_lanes'][lane]
        config_path,capture=wpt.prepare_inputs(root,phase,settings,'candidate')
        events,code,_,app=synthetic.synthetic(policy,lane,'FAIL',policy['head'])
        app['source_role']='candidate'
        original_events=copy.deepcopy(events)
        for event in original_events:
            if event.get('action')=='test_status':event['message']='different original assertion'
        before=assessor.assess(original_events,code,observation.phase_policy(settings),checks,run_binding=app)
        originals[lane]=before
        assessment=assessor.assess(events,code,observation.phase_policy(settings),checks,original=before,run_binding=app);assert assessment['complete']
        behavior=comparison.behavior(before,assessment,settings,assessor.signature);behaviors[lane]=behavior
        all_rows.extend(assessment['rows']);all_ends.extend(assessment['ends'])
        (phase/'raw.jsonl').write_text(''.join(json.dumps(event)+'\n' for event in events))
        command=['/Users/bgrins/venvs/firefox/bin/python','./mach','wpt','--headless','--processes=1','--no-manifest-update','--no-manifest-download','--binary='+str(root/settings['binary']),'--config='+str(config_path),'--run-info='+str(root/'objdir-full.noindex'),'--prefs-root='+str(root/'testing/profiles'),'--log-raw='+str(phase/'raw.jsonl')]
        command.extend('--include='+page for page in settings['expected_subtests'])
        temporary=Path('/private/tmp')/('css-easing-paired-'+scratch_path.name+'-'+lane);assert not temporary.exists()
        bodies={'BEHAVIOR-COMPARISON.json':behavior,'ASSESSMENT.json':assessment,'ASSESSMENT-POLICY.json':observation.phase_policy(settings),'PRE.json':snapshot,'POST.json':snapshot,'APPLICATION-METADATA.json':app,'APPLICATION-METADATA-POST.json':app,'BINARY-PINS.json':binaries,'CLEANUP.json':{'owned_group_absent':True,'temporary_root_removed':True},'PROCESS.json':{'pid':900000+index,'pgid':900000+index},'COMMAND.json':{'command':command,'temporary_root':str(temporary),'timeout_seconds':settings['timeout_seconds']}}
        for name,body in bodies.items():wpt.save(phase/name,body)
        zoom=None;zoom_comparison=None
        if capture:
            binding=r.read(phase/'ZOOM-BINDING.json')
            row={'kind':'zoom-observation','initial':'0px','diagnosticOnly':True,'phases':[]}
            for i,size in enumerate([20,30]):row['phases'].append({'phase':i,'value':'1em','samples':['0px']*4,'expected':None,'expectedFont':None,'font':str(size)+'px','line':'19px','family':'monospace','writingMode':'horizontal-tb','zoom':'1','referenceFont':str(size)+'px','referenceWidth':str(size*2)+'px','size':size,'keywordSupported':True,'zoomSyntaxSupported':True})
            payload={k:binding[k] for k in ['version','nonce','role','page']};payload['row']=row
            wpt.save(phase/'tests/__research__/zoom/REQUEST.json',payload)
            capture.review(phase,events);zoom=r.sha(phase/'ZOOM-OBSERVATION.json')
            original_phase=root/'saved-original'/('original-wpt-'+lane);original_phase.parent.mkdir(parents=True,exist_ok=True)
            import shutil
            shutil.copytree(phase,original_phase)
            for relative in ['ZOOM-BINDING.json','tests/__research__/zoom/CONFIG.json','tests/__research__/zoom/REQUEST.json']:
                path=original_phase/relative;body=r.read(path);body['role']='original';path.write_text(json.dumps(body))
            original_binding=r.read(original_phase/'ZOOM-BINDING.json');original_binding['resources']['CONFIG.json']=r.sha(original_phase/'tests/__research__/zoom/CONFIG.json');(original_phase/'ZOOM-BINDING.json').write_text(json.dumps(original_binding))
            (original_phase/'raw.jsonl').write_text(''.join(json.dumps(event)+'\n' for event in original_events))
            (original_phase/'ZOOM-OBSERVATION.json').unlink();original_zoom=capture.review(original_phase,original_events)
            wpt.save(phase/'ZOOM-COMPARISON.json',capture.compare(original_zoom,r.read(phase/'ZOOM-OBSERVATION.json')));zoom_comparison=r.sha(phase/'ZOOM-COMPARISON.json')
        phase_result={'success':True,'exit':code,'execution_error':None,'preservation_verified':True,'comparison_gate_passed':assessment['comparison_gate_passed'],'repair_observation_gate':behavior['repair_observation_gate'],'all_signatures_equal':behavior['all_signatures_equal'],'required_zoom_capture_complete':capture is not None}
        wpt.save(phase/'RESULT.json',phase_result)
        phase_receipts[lane]={'lane':lane,'behavior_sha256':r.sha(phase/'BEHAVIOR-COMPARISON.json'),'zoom_comparison_sha256':zoom_comparison,'zoom_observation_sha256':zoom,'assessment_sha256':r.sha(phase/'ASSESSMENT.json'),'raw_sha256':r.sha(phase/'raw.jsonl'),'result_sha256':r.sha(phase/'RESULT.json')}
    outcomes={'rows':all_rows,'endings':all_ends,'callbacks_passed':0,'callbacks_failed':77,'provider_source_role':'provider-cascade-value-candidate','native_acceptance':False,'zoom_target_correctness':None,'lanes':phase_receipts}
    wpt.save(pair/'OUTCOMES.json',outcomes)
    wpt.save(pair/'COMPARISON.json',{'lanes':behaviors,'repair_observation_gate':False,'all89_signatures_equal':False,'zoom_comparison_sha256':phase_receipts['ordinary']['zoom_comparison_sha256'],'native_acceptance':False})
    result={'success':True,'phase':phase_receipts,'error':None};pre={'snapshot':full_snapshot};build={'exit':0,'error':None,'stop_reason':None}
    inputs={}
    def record(name):inputs[name]=r.sha(pair/name);return r.read(pair/name)
    ownership=SimpleNamespace(group_absent=lambda pgid:None)
    def run(result):return observation.review(root,HERE,pair,policy,pre,result,build,record,inputs,ownership,lambda *args:r.validate_build_phase(*args,consumed_inputs=consumed))
    value=run(result);assert value['observation_complete'] and value['raw_counts']=={'FAIL':77} and value['repair_observation_gate'] is False and value['all89_signatures_equal'] is False;results.append('complete all77FAIL/12OK with nonempty differences and genuine metadata/Zoom replay')
    assert value['target_callbacks']==24 and value['original_endings']==12 and sum(len(b['candidate_signatures']) for b in value['behaviors'].values())==89
    assert all(b['differences'] for b in value['behaviors'].values())
    original_digest=consumed[next(iter(consumed))];consumed[next(iter(consumed))]='wrong-pin'
    value=run(result);assert not value['observation_complete'] and value['raw_counts']=={'FAIL':77};results.append('wrong consumed digest retains raw but rejects completeness')
    consumed[next(iter(consumed))]=original_digest
    scope=load('review_scope_check',HERE/'review_scope.py');scope.require_full(full_snapshot);scope.require_intermediate(snapshot,consumed)
    for wrong,scope_check in [(snapshot,scope.require_full),(full_snapshot,lambda value:scope.require_intermediate(value,consumed))]:
        try:scope_check(wrong)
        except AssertionError:pass
        else:raise AssertionError('wrong scope accepted')
    results.append('full and limited scope substitutions rejected')
    ordinary=pair/'candidate-wpt-ordinary'
    behavior_path=ordinary/'BEHAVIOR-COMPARISON.json';saved_behavior=behavior_path.read_bytes()
    altered=r.read(behavior_path);altered['differences'][0]['identity'][2]+=' changed';behavior_path.write_text(json.dumps(altered))
    value=run(result);assert not value['observation_complete'] and value['raw_counts']=={'FAIL':77};results.append('changed nonempty difference identity rejected retaining rows');behavior_path.write_bytes(saved_behavior)
    altered=r.read(behavior_path);altered['repair_observation_gate']=True;behavior_path.write_text(json.dumps(altered))
    value=run(result);assert not value['observation_complete'] and value['raw_counts']=={'FAIL':77};results.append('invented repair gate rejected with all rows retained');behavior_path.write_bytes(saved_behavior)
    raw_request=ordinary/'tests/__research__/zoom/REQUEST.json';saved_bytes=raw_request.read_bytes()
    altered=r.read(raw_request);altered['role']='original';raw_request.write_text(json.dumps(altered))
    value=run(result);assert not value['observation_complete'] and value['raw_counts']=={'FAIL':77};results.append('candidate Zoom role substitution rejected');raw_request.write_bytes(saved_bytes)
    raw_request.unlink()
    value=run(result);assert not value['observation_complete'] and value['raw_counts']=={'FAIL':77};results.append('missing Zoom preserves raw but rejects completeness');raw_request.write_bytes(saved_bytes)
    phase_result=ordinary/'RESULT.json';saved_result=phase_result.read_bytes();phase_result.unlink()
    failed={'success':False,'phase':None,'error':'AssertionError()'};wpt.save(pair/'FAILURE-TRACEBACK.json',{'error':'AssertionError()'})
    value=run(failed);assert not value['observation_complete'] and value['lanes']['ordinary']['browser_exit'] is None and len(value['raw_rows'])==77;results.append('partial lane RESULT absent retains77rows with exitnull');phase_result.write_bytes(saved_result)
    metadata=ordinary/'metadata/forced-colors-mode/forced-colors-mode-51.html.ini';saved_meta=metadata.read_bytes();metadata.write_text('rewritten')
    value=run(failed);assert not value['observation_complete'] and not value['lanes']['ordinary']['resources_and_metadata_verified'];results.append('rewritten expectedFAIL metadata rejected');metadata.write_bytes(saved_meta)
    config_file=ordinary/'wptrunner.ini';saved_config=config_file.read_bytes()
    config_file.write_text(config_file.read_text().replace('url_base = /_mozilla/','url_base = /wrong/'))
    value=run(failed);assert not value['observation_complete'] and not value['lanes']['ordinary']['resources_and_metadata_verified'];results.append('wrong manifest URL root rejected independently');config_file.write_bytes(saved_config)
    assert r.summary_counts(value)=={'callbacks_passed':None,'callbacks_failed':None}
    results.append('incomplete final summary preserves null counts')
    mismatch={'repository':'root','before':{'raw_index':'a'},'after':{'raw_index':'b'},'changed_fields':['raw_index'],'verification_call':3}
    r.validate_mismatch(mismatch,failed)
    for changed,rv in [(dict(mismatch,changed_fields=[]),failed),(mismatch,result)]:
        try:r.validate_mismatch(changed,rv)
        except AssertionError:pass
        else:raise AssertionError('false mismatch accepted')
    results.append('mismatch pair retained, invented difference and successful-owner mismatch rejected')
    for path in HERE.glob('*.py'):compile(path.read_text(),str(path),'exec')
assert not scratch_path.exists()
print(json.dumps({'saved_owner_authenticated':True,'terminal_null':True,'cases':results,'owned_scratch_removed':True,'live_process_checks_mocked':True,'current_state_verifier_not_run':True}))
