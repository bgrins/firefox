import configparser
import hashlib
import importlib.util
import json
import os
from pathlib import Path

sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
read=lambda path:json.loads(path.read_bytes())


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


def phase_policy(settings):
    result=dict(settings,tests={page:'testharness' for page in settings['expected_subtests']},held_subtests={})
    result['regression_subtests']={page:[name for name in names if name not in settings['target_subtests'].get(page,[])] for page,names in settings['expected_subtests'].items()}
    result['cardinality_description']='Exact sealed target and control names; existing control failures retain full signatures.'
    return result


def counts(rows):
    return {status:sum(row.get('status')==status for row in rows) for status in sorted({row.get('status') for row in rows if isinstance(row.get('status'),str)})}


def review(root,here,pair,policy,pre,result,build,record,inputs,ownership,validate_build_phase):
    owner=root/policy['owner_directory']
    assessor=load('terminal74_assessor',owner/'assess.py')
    checks=load('terminal74_streams',root/policy['wpt']['checks_helper'])
    comparison=load('candidate74_comparison',owner/'comparison.py')
    originals=comparison.replay_all(root,policy)
    lanes={};all_rows=[];all_ends=[];errors=[];behaviors={}
    for lane in policy['lane_order']:
        relative='candidate-wpt-'+lane;directory=pair/relative;settings=policy['wpt_lanes'][lane]
        evidence={'directory_exists':directory.exists(),'browser_executed':False,'wpt_process_started':False,'observation_complete':False,'browser_exit':None,'raw_rows':[],'raw_endings':[],'errors':[],'regular_file_hashes':{},'borrowed_symlinks':{}}
        lanes[lane]=evidence
        if not directory.exists():
            evidence['errors'].append('lane not started');continue
        for path in sorted(directory.rglob('*')):
            if path.is_symlink():
                assert path==directory/'tests/tools' and os.readlink(path)==str(root/'testing/web-platform/tests/tools')
                evidence['borrowed_symlinks'][str(path.relative_to(directory))]=os.readlink(path)
            elif path.is_file():
                name=str(path.relative_to(pair));inputs[name]=sha(path);evidence['regular_file_hashes'][str(path.relative_to(directory))]=inputs[name]
        def optional(name):
            path=directory/name
            return record(relative+'/'+name) if path.is_file() and not path.is_symlink() else None
        raw=directory/'raw.jsonl';events=None
        if raw.is_file():
            try:
                events=[json.loads(line) for line in raw.read_text().splitlines()]
                assert all(isinstance(event,dict) for event in events)
                evidence['raw_rows']=[e for e in events if e.get('action')=='test_status']
                evidence['raw_endings']=[e for e in events if e.get('action')=='test_end']
                evidence['raw_counts']=counts(evidence['raw_rows'])
                all_rows.extend(evidence['raw_rows']);all_ends.extend(evidence['raw_endings'])
            except (ValueError,TypeError,AssertionError) as error:
                events=None
                evidence['errors'].append('raw parse: '+repr(error))
        else:
            evidence['errors'].append('raw log absent')
        process=optional('PROCESS.json');command=optional('COMMAND.json');cleanup=optional('CLEANUP.json')
        if process is not None:
            assert process['pid']==process['pgid'] and process['pgid']>1
            ownership.group_absent(process['pgid'])
            evidence['wpt_process_started']=True
            evidence['browser_executed']=True if evidence['raw_rows'] else None
            assert cleanup and cleanup['owned_group_absent'] and cleanup['temporary_root_removed']
        if command is not None:
            expected=['/Users/bgrins/venvs/firefox/bin/python','./mach','wpt','--headless','--processes=1','--no-manifest-update','--no-manifest-download','--binary='+str(root/settings['binary']),'--config='+str(directory/'wptrunner.ini'),'--run-info='+str(root/'objdir-full.noindex'),'--prefs-root='+str(root/'testing/profiles'),'--log-raw='+str(directory/'raw.jsonl')]
            expected.extend('--include='+page for page in settings['expected_subtests'])
            assert command['command']==expected and command['timeout_seconds']==settings['timeout_seconds']
            temporary=Path(command['temporary_root'])
            assert temporary.parent==Path('/private/tmp') and temporary.name.startswith('css-easing-paired-')
            assert not temporary.exists() and not temporary.is_symlink()
        elif process is not None:
            raise AssertionError('process exists without owned command/profile receipt')
        phase=optional('RESULT.json');saved=optional('ASSESSMENT.json')
        if phase is None:
            evidence['errors'].append('lane RESULT absent: browser exit is not inferred')
        else:
            evidence['browser_exit']=phase['exit']
        try:
            for url,pin in settings['resources'].items():
                path=directory/'mozilla-tests'/url[len('/_mozilla/'):] if url.startswith('/_mozilla/') else directory/'tests'/url[1:]
                assert sha(path)==pin['sha256']
            for kind,folder in [('portable','metadata'),('mozilla','mozilla-metadata')]:
                assert sha(directory/folder/'MANIFEST.json')==settings['manifests'][kind]['sha256']
                for name,pin in settings['metadata'][kind].items():
                    path=directory/folder/name
                    if pin['sha256'] is None:assert not path.exists() and not path.is_symlink()
                    else:assert sha(path)==pin['sha256']
            config=configparser.ConfigParser(interpolation=None)
            assert config.read(directory/'wptrunner.ini')
            assert {name for name in config.sections() if name.startswith('manifest:')}=={'manifest:upstream','manifest:mozilla'}
            for name,tests,metadata,url in [('upstream','tests','metadata','/'),('mozilla','mozilla-tests','mozilla-metadata','/_mozilla/')]:
                assert dict(config['manifest:'+name])=={'tests':str(directory/tests),'metadata':str(directory/metadata),'url_base':url,'manifest':str(directory/metadata/'MANIFEST.json')}
            assert config['paths']['run_info']==str(root/'objdir-full.noindex') and config['paths']['prefs']==str(root/'testing/profiles')
            assert config['web-platform-tests']['sync_path']==str(directory/'unused-sync')
            staged=optional('STAGED-RESOURCES.json');assert staged is not None
            assert all(sha(directory/name)==digest for name,digest in staged.items())
            assert evidence['borrowed_symlinks']=={'tests/tools':str(root/'testing/web-platform/tests/tools')}
            evidence['resources_and_metadata_verified']=True
        except (AssertionError,OSError,TypeError,KeyError,configparser.Error) as error:
            evidence['resources_and_metadata_verified']=False;evidence['errors'].append('staged resources: '+repr(error))
        if settings['capture'] is not None:
            try:
                assert cleanup and cleanup['owned_group_absent'] and cleanup['temporary_root_removed']
                assert events is not None
                helper=root/settings['capture']['path'];assert sha(helper)==settings['capture']['sha256']
                capture=load('terminal74_zoom',helper)
                replay=capture.replay(directory,events)
                evidence['zoom_replay']=replay
                assert replay['role']=='candidate' and replay==optional('ZOOM-OBSERVATION.json')
                assert phase is not None and phase['required_zoom_capture_complete'] is True
                original_directory=root/policy['baseline_binding']['directory']/('original-wpt-'+lane)
                original_events=[json.loads(line) for line in (original_directory/'raw.jsonl').read_text().splitlines()]
                original_zoom=capture.replay(original_directory,original_events)
                assert original_zoom['role']=='original' and original_zoom==read(original_directory/'ZOOM-OBSERVATION.json')
                zoom_comparison=capture.compare(original_zoom,replay)
                assert zoom_comparison==optional('ZOOM-COMPARISON.json') and zoom_comparison['target_correctness'] is None
                evidence['zoom_comparison']=zoom_comparison
                evidence['zoom_capture_complete']=True
            except (AssertionError,OSError,ValueError,TypeError,KeyError) as error:
                evidence['zoom_capture_complete']=False;evidence['errors'].append('Zoom capture: '+repr(error))
        if phase is not None and events is not None:
            try:
                metadata=optional('APPLICATION-METADATA.json')
                actual_settings=optional('ASSESSMENT-POLICY.json');assert actual_settings==phase_policy(settings)
                replay=assessor.assess(events,phase['exit'],actual_settings,checks,original=originals[lane],run_binding=metadata)
                evidence['assessment_replay']=replay;evidence['saved_assessment_matches']=replay==saved
                assert replay==saved and replay['complete']
                assert len(replay['rows'])==settings['expected_subtest_count'] and len(replay['ends'])==settings['expected_page_count']
                assert phase['comparison_gate_passed']==replay['comparison_gate_passed']
                behavior=comparison.behavior(originals[lane],replay,settings,assessor.signature)
                assert behavior==optional('BEHAVIOR-COMPARISON.json')
                assert phase['repair_observation_gate']==behavior['repair_observation_gate']
                assert phase['all_signatures_equal']==behavior['all_signatures_equal']
                behaviors[lane]=behavior
                evidence['behavior']=behavior
                assert phase['success'] and phase['preservation_verified'] and phase['execution_error'] is None
                built=record('candidate-build/RESULT.json')
                assert build['exit']==0 and build['error'] is None and build['stop_reason'] is None
                assert built['command_success'] and built['preservation_verified'] and built['error'] is None
                assert built['native_sources']==record('candidate-build/COMMAND.json')['source_sha256']
                validate_build_phase(policy,pre,built,metadata,optional('APPLICATION-METADATA-POST.json'),[optional('PRE.json'),optional('POST.json'),record('PHASES-PRE.json')],optional('BINARY-PINS.json'))
                assert process is not None and cleanup and command
            except (AssertionError,OSError,ValueError,TypeError,KeyError) as error:
                evidence['errors'].append('lane assessment/build join: '+repr(error))
        evidence['observation_complete']=not evidence['errors']
    complete=all(lane['observation_complete'] for lane in lanes.values())
    outcome=None
    if complete:
        try:
            assert len(all_rows)==74 and len(all_ends)==11
            assert len({(r['test'],r['subtest']) for r in all_rows})==74 and len({r['test'] for r in all_ends})==11
            outcome=record('OUTCOMES.json')
            assert outcome['rows']==all_rows and outcome['endings']==all_ends
            assert outcome['callbacks_passed']==sum(r['status']=='PASS' for r in all_rows)
            assert outcome['callbacks_failed']==sum(r['status']=='FAIL' for r in all_rows)
            assert outcome['provider_source_role']=='clean-provider-cascade-candidate' and outcome['native_acceptance'] is False and outcome['zoom_target_correctness'] is None
            assert outcome['lanes']==result['candidate_phase'] and set(result['candidate_phase'])==set(policy['lane_order'])
            for lane,entry in result['candidate_phase'].items():
                assert entry['lane']==lane
                prefix='candidate-wpt-'+lane+'/'
                for name,key in [('ASSESSMENT.json','assessment_sha256'),('raw.jsonl','raw_sha256'),('RESULT.json','result_sha256')]:assert inputs[prefix+name]==entry[key]
                assert inputs[prefix+'BEHAVIOR-COMPARISON.json']==entry['behavior_sha256']
                if lane=='ordinary':
                    assert inputs[prefix+'ZOOM-OBSERVATION.json']==entry['zoom_observation_sha256']
                    assert inputs[prefix+'ZOOM-COMPARISON.json']==entry['zoom_comparison_sha256']
                else:assert entry['zoom_observation_sha256'] is None
            assert record('PHASES-POST.json')==record('PHASES-PRE.json')==record('candidate-build/RESULT.json')['snapshot']
            aggregate={'lanes':behaviors,'repair_observation_gate':all(v['repair_observation_gate'] for v in behaviors.values()),'all85_signatures_equal':all(v['all_signatures_equal'] for v in behaviors.values()),'zoom_comparison_sha256':result['candidate_phase']['ordinary']['zoom_comparison_sha256'],'native_acceptance':False}
            assert sum(len(v['candidate_signatures']) for v in behaviors.values())==85
            assert record('COMPARISON.json')==aggregate
            assert result['success']
        except (AssertionError,OSError,ValueError,TypeError,KeyError) as error:
            complete=False;errors.append('aggregate observation: '+repr(error))
    if not result['success']:
        assert result['candidate_phase'] is None
        assert record('FAILURE-TRACEBACK.json')['error']==result['error']
    return {'lanes':lanes,'browser_executed':True if any(lane['browser_executed'] is True for lane in lanes.values()) else None if any(lane['wpt_process_started'] for lane in lanes.values()) else False,'observation_complete':complete,'build_exit':build['exit'],'raw_rows':all_rows,'raw_endings':all_ends,'raw_counts':counts(all_rows),'outcomes':outcome,'errors':errors,'native_acceptance':False,'zoom_target_correctness':None,'original_counts':counts([row for original in originals.values() for row in original['rows']]),'original_endings':sum(len(original['ends']) for original in originals.values()),'target_callbacks':sum(settings['expected_target_count'] for settings in policy['wpt_lanes'].values()),'behaviors':behaviors,'repair_observation_gate':all(v['repair_observation_gate'] for v in behaviors.values()) if complete else None,'all85_signatures_equal':all(v['all_signatures_equal'] for v in behaviors.values()) if complete else None}
