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
assert config['expected_session']==99665 and config['expected_launch']=='31e9ed'
policy=r.read(owner/'POLICY.json')
wpt=load('actual_staging',owner/'wpt.py')
synthetic=load('saved_synthetic',ROOT/'artifacts/css-prioritary-selection-original-v1/check.py')
assessor=load('original_assessor',owner/'assess.py')
checks=load('saved_stream_checks',ROOT/policy['wpt']['checks_helper'])
results=[]
with tempfile.TemporaryDirectory(prefix='css-original74-review-',dir='/private/tmp') as scratch:
    scratch_path=Path(scratch);root=scratch_path/'root';root.mkdir();pair=scratch_path/'runtime';pair.mkdir()
    (root/'testing/web-platform/tests/tools').mkdir(parents=True)
    for relative in [policy['owner_directory']+'/assess.py','artifacts/css-minmax-relative-infinity-broader-browser-v5/assess.py',policy['wpt']['checks_helper']]:
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
    binaries={name:'built' for name in policy['rebuilt_binaries']}
    sources={name:role['candidate_sha256'] for name,role in r.read(owner/'SOURCE-ROLES.json').items()}
    built={'command_success':True,'preservation_verified':True,'error':None,'native_sources':sources,'binaries':binaries,'snapshot':snapshot,'browser_build_performed':True}
    (pair/'original-build').mkdir();wpt.save(pair/'original-build/RESULT.json',built);wpt.save(pair/'original-build/COMMAND.json',{'source_sha256':sources})
    wpt.save(pair/'PHASES-PRE.json',snapshot);wpt.save(pair/'PHASES-POST.json',snapshot)
    all_rows=[];all_ends=[];phase_receipts={}
    for index,lane in enumerate(policy['lane_order']):
        phase=pair/('original-wpt-'+lane);phase.mkdir();settings=policy['wpt_lanes'][lane]
        config_path,capture=wpt.prepare_inputs(root,phase,settings,'original')
        events,code,_,app=synthetic.synthetic(policy,lane,'FAIL',policy['head'])
        assessment=assessor.assess(events,code,observation.phase_policy(settings),checks,run_binding=app);assert assessment['complete']
        all_rows.extend(assessment['rows']);all_ends.extend(assessment['ends'])
        (phase/'raw.jsonl').write_text(''.join(json.dumps(event)+'\n' for event in events))
        command=['/Users/bgrins/venvs/firefox/bin/python','./mach','wpt','--headless','--processes=1','--no-manifest-update','--no-manifest-download','--binary='+str(root/settings['binary']),'--config='+str(config_path),'--run-info='+str(root/'objdir-full.noindex'),'--prefs-root='+str(root/'testing/profiles'),'--log-raw='+str(phase/'raw.jsonl')]
        command.extend('--include='+page for page in settings['expected_subtests'])
        temporary=Path('/private/tmp')/('css-easing-paired-'+scratch_path.name+'-'+lane);assert not temporary.exists()
        bodies={'ASSESSMENT.json':assessment,'ASSESSMENT-POLICY.json':observation.phase_policy(settings),'PRE.json':snapshot,'POST.json':snapshot,'APPLICATION-METADATA.json':app,'APPLICATION-METADATA-POST.json':app,'BINARY-PINS.json':binaries,'CLEANUP.json':{'owned_group_absent':True,'temporary_root_removed':True},'PROCESS.json':{'pid':900000+index,'pgid':900000+index},'COMMAND.json':{'command':command,'temporary_root':str(temporary),'timeout_seconds':settings['timeout_seconds']}}
        for name,body in bodies.items():wpt.save(phase/name,body)
        zoom=None
        if capture:
            binding=r.read(phase/'ZOOM-BINDING.json')
            row={'kind':'zoom-observation','initial':'0px','diagnosticOnly':True,'phases':[]}
            for i,size in enumerate([20,30]):row['phases'].append({'phase':i,'value':'1em','samples':['0px']*4,'expected':None,'expectedFont':None,'font':str(size)+'px','line':'19px','family':'monospace','writingMode':'horizontal-tb','zoom':'1','referenceFont':str(size)+'px','referenceWidth':str(size*2)+'px','size':size,'keywordSupported':True,'zoomSyntaxSupported':True})
            payload={k:binding[k] for k in ['version','nonce','role','page']};payload['row']=row
            wpt.save(phase/'tests/__research__/zoom/REQUEST.json',payload)
            capture.review(phase,events);zoom=r.sha(phase/'ZOOM-OBSERVATION.json')
        phase_result={'success':True,'exit':code,'execution_error':None,'preservation_verified':True,'comparison_gate_passed':False,'required_zoom_capture_complete':capture is not None}
        wpt.save(phase/'RESULT.json',phase_result)
        phase_receipts[lane]={'lane':lane,'zoom_observation_sha256':zoom,'assessment_sha256':r.sha(phase/'ASSESSMENT.json'),'raw_sha256':r.sha(phase/'raw.jsonl'),'result_sha256':r.sha(phase/'RESULT.json')}
    outcomes={'rows':all_rows,'endings':all_ends,'callbacks_passed':0,'callbacks_failed':74,'provider_source_role':'clean-original','native_acceptance':False,'zoom_target_correctness':None,'lanes':phase_receipts}
    wpt.save(pair/'OUTCOMES.json',outcomes)
    result={'success':True,'phase':phase_receipts,'error':None};pre={'snapshot':snapshot};build={'exit':0,'error':None,'stop_reason':None}
    inputs={}
    def record(name):inputs[name]=r.sha(pair/name);return r.read(pair/name)
    ownership=SimpleNamespace(group_absent=lambda pgid:None)
    def run(result):return observation.review(root,HERE,pair,policy,pre,result,build,record,inputs,ownership,r.validate_build_phase)
    value=run(result);assert value['observation_complete'] and value['raw_counts']=={'FAIL':74};results.append('complete all74FAIL/11OK and genuine metadata/Zoom replay')
    ordinary=pair/'original-wpt-ordinary'
    raw_request=ordinary/'tests/__research__/zoom/REQUEST.json';saved_bytes=raw_request.read_bytes();raw_request.unlink()
    value=run(result);assert not value['observation_complete'] and value['raw_counts']=={'FAIL':74};results.append('missing Zoom preserves raw but rejects completeness');raw_request.write_bytes(saved_bytes)
    phase_result=ordinary/'RESULT.json';saved_result=phase_result.read_bytes();phase_result.unlink()
    failed={'success':False,'phase':None,'error':'AssertionError()'};wpt.save(pair/'FAILURE-TRACEBACK.json',{'error':'AssertionError()'})
    value=run(failed);assert not value['observation_complete'] and value['lanes']['ordinary']['browser_exit'] is None and len(value['raw_rows'])==74;results.append('partial lane RESULT absent retains74rows with exitnull');phase_result.write_bytes(saved_result)
    metadata=ordinary/'metadata/forced-colors-mode/forced-colors-mode-51.html.ini';saved_meta=metadata.read_bytes();metadata.write_text('rewritten')
    value=run(failed);assert not value['observation_complete'] and not value['lanes']['ordinary']['resources_and_metadata_verified'];results.append('rewritten expectedFAIL metadata rejected');metadata.write_bytes(saved_meta)
    config_file=ordinary/'wptrunner.ini';saved_config=config_file.read_bytes()
    config_file.write_text(config_file.read_text().replace('url_base = /_mozilla/','url_base = /wrong/'))
    value=run(failed);assert not value['observation_complete'] and not value['lanes']['ordinary']['resources_and_metadata_verified'];results.append('wrong manifest URL root rejected independently');config_file.write_bytes(saved_config)
    assert r.summary_counts(value)=={'callbacks_passed':None,'callbacks_failed':None}
    results.append('incomplete final summary preserves null counts')
    for path in HERE.glob('*.py'):compile(path.read_text(),str(path),'exec')
assert not scratch_path.exists()
print(json.dumps({'saved_owner_authenticated':True,'terminal_null':True,'cases':results,'owned_scratch_removed':True,'live_process_checks_mocked':True,'current_state_verifier_not_run':True}))
