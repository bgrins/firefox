import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import time

read = lambda path: json.loads(path.read_bytes())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
SELECTOR = 'dom/animation/test/mozilla/test_restyles.html'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def signature(event):
    result = {key:value for key,value in event.items() if key not in ('time','thread','pid')}
    result['expected_effective'] = event.get('expected', event['status'])
    result['expected_field_present'] = 'expected' in event
    if event['action']=='test_end':
        assert re.fullmatch(r'Finished in [0-9]+ms',event['message'])
        elapsed=ast.literal_eval(event['stack'])
        assert isinstance(elapsed,dict) and set(elapsed)=={'runtime'} and type(elapsed['runtime']) is int and elapsed['runtime']>=0
        assert event['message']==f"Finished in {elapsed['runtime']}ms"
        result['message']='Finished in <elapsed>ms'
        result['stack']={'runtime':'<elapsed>'}
    return result


def assess(events, code, checks):
    assert checks.lifecycle(events,{'expected_subtests':{SELECTOR:[]},'reftests':[]})
    assert not checks.infrastructure_faults(events)
    rows=[e for e in events if e.get('action')=='test_status']
    ends=[e for e in events if e.get('action')=='test_end']
    starts=[e for e in events if e.get('action')=='test_start']
    assert len(rows)==170 and len(ends)==len(starts)==1
    assert all(e['test']==SELECTOR and e['status'] in ('PASS','FAIL') for e in rows)
    assert sum(e['status']=='PASS' for e in rows)==162 and sum(e['status']=='FAIL' for e in rows)==8
    assert ends[0]['test']==SELECTOR and ends[0]['status']=='PASS'
    assert code==0 and checks.exit_matches_results(code,rows+ends)
    suites=[e for e in events if e.get('action')=='suite_start']
    assert len(suites)==1 and suites[0]['name']=='mochitest-plain'
    assert suites[0]['tests']=={'dom/animation/test/mochitest.toml':[SELECTOR]}
    return {'assertions':[signature(e) for e in rows], 'ending':signature(ends[0]),
            'assertion_count':170,'pass':162,'expected_failures':8,'child_exit':code,
            'test_end_elapsed_time_normalized_only':True,
            'missing_expected_uses_observed_status':True}


def original(root, policy):
    path=root/policy['restyle_baseline']['directory']
    assert sha(path/'ROOT-TERMINAL.json')==policy['restyle_baseline']['terminal_sha256']
    assert sha(path/'raw.jsonl')==policy['restyle_baseline']['raw_sha256']
    terminal=read(path/'ROOT-TERMINAL.json')
    assert terminal['session_id']==79082 and terminal['terminal_chunk']=='ecbdc0' and terminal['exit']==terminal['child_exit']==0
    result=read(path/'RESULT.json')
    assert result['exit']==0 and result['execution_error'] is None and result['preservation_verified'] and result['owned_group_absent']
    assert read(path/'PRE.json')==read(path/'POST.json')
    assert read(path/'APPLICATION-METADATA.json')==read(path/'APPLICATION-METADATA-POST.json')
    assert read(path/'CLEANUP.json')['owned_group_absent']
    checks=load('restyle_checks',root/policy['wpt']['checks_helper'])
    events=[json.loads(line) for line in (path/'raw.jsonl').read_text().splitlines()]
    return assess(events,0,checks)


def run(root, output, policy, env, verify, owned, cancelled, wpt_app):
    expected=original(root,policy)
    source=read(root/policy['restyle_baseline']['directory']/'POLICY.json')
    for name,pin in source['source_pins'].items():
        if name.startswith('dom/animation/test/'):
            assert sha(root/name)==pin
    control=load('restyle_process_control',root/policy['wpt']['control_helper'])
    metadata=load('restyle_application_metadata',root/policy['wpt']['metadata_helper'])
    checks=load('restyle_runtime_checks',root/policy['wpt']['checks_helper'])
    output.mkdir()
    def save(name,value):
        with (output/name).open('x') as stream:
            json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
    before=verify()
    app=metadata.application_metadata(root/source['app_ini'],policy['head'])
    assert app=={k:v for k,v in wpt_app.items() if k not in ('build_revision','harness_revision','source_role')}
    save('PRE.json',before);save('APPLICATION-METADATA.json',app)
    command=['/Users/bgrins/venvs/firefox/bin/python','./mach','mochitest','--headless','--flavor=plain','--timeout=180','--appname='+str(root/policy['wpt']['binary']),'--log-raw='+str(output/'raw.jsonl'),SELECTOR]
    old_command=read(root/policy['restyle_baseline']['directory']/'COMMAND.json')['command']
    assert [c for c in command if not c.startswith('--log-raw=')]==[c for c in old_command if not c.startswith('--log-raw=')]
    save('COMMAND.json',{'command':command,'external_timeout_seconds':600})
    process,code,error=None,None,None
    try:
        with (output/'mochitest.log').open('x') as stream:
            process=subprocess.Popen(command,cwd=root,env=env,stdout=stream,stderr=subprocess.STDOUT,start_new_session=True)
            owned['restyles']=process.pid
            save('PROCESS.json',{'pid':process.pid,'pgid':process.pid})
            deadline=time.monotonic()+600
            while process.poll() is None:
                assert not cancelled() and time.monotonic()<deadline,'Mochitest cancelled or timed out'
                time.sleep(0.2)
            code=process.wait()
    except BaseException as caught:
        error=repr(caught)
    finally:
        cleanup=control.terminate(process)
        save('CLEANUP.json',cleanup)
        assert cleanup['owned_group_absent']
        owned.pop('restyles',None)
    after=verify()
    app_after=metadata.application_metadata(root/source['app_ini'],policy['head'])
    save('POST.json',after);save('APPLICATION-METADATA-POST.json',app_after)
    assert before==after and app==app_after
    comparison_error=None
    try:
        events=[json.loads(line) for line in (output/'raw.jsonl').read_text().splitlines()]
        actual=assess(events,code,checks)
        save('ASSESSMENT.json',actual)
        assert actual==expected,'Mochitest assertion or ending signature differs'
    except BaseException as caught:
        comparison_error=repr(caught)
    save('RESULT.json',{'exit':code,'execution_error':error,'preservation_verified':True,'owned_group_absent':True,'comparison_error':comparison_error,'comparison_passed':error is None and comparison_error is None,'native_acceptance':False})
    assert error is None and comparison_error is None,(error,comparison_error)
    return {'result_sha256':sha(output/'RESULT.json'),'assessment_sha256':sha(output/'ASSESSMENT.json'),'raw_sha256':sha(output/'raw.jsonl')}
