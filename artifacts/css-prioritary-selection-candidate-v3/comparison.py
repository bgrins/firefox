import copy
import hashlib
import importlib.util
import json

read = lambda path: json.loads(path.read_bytes())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def phase_policy(settings):
    result = dict(settings, tests={page:'testharness' for page in settings['expected_subtests']}, held_subtests={})
    result['regression_subtests'] = {page:[name for name in names if name not in settings['target_subtests'].get(page,[])] for page,names in settings['expected_subtests'].items()}
    result['cardinality_description'] = 'Exact sealed target and control names; existing control failures retain full signatures.'
    return result


def admit_snapshot(historical, current):
    expected = copy.deepcopy(historical)
    expected['index']['raw_index'] = current['index']['raw_index']
    assert expected == current


def replay_original(root, policy, assessor, checks, lane):
    binding, capsule = policy['baseline_binding'], policy['baseline_capsule']
    assert binding is not None and capsule is not None
    ownership = load('original74_ownership',root/policy['ownership_helper'])
    directory, source_owner = root/binding['directory'], root/capsule['directory']
    ownership.authenticate(directory,binding['manifest_sha256'])
    ownership.authenticate(source_owner,capsule['sha256'])
    assert sha(directory/'RESULT.json') == binding['result_sha256']
    baseline=load('original74_terminal_schema',root/policy['owner_directory']/'baseline.py')
    baseline.owner_terminal(directory,binding,capsule)
    source=read(source_owner/'POLICY.json')
    assert source['owner_directory']==capsule['directory']
    assert source['suite_binding']==policy['suite_binding'] and source['capture_binding']==policy['capture_binding']
    assert source['head']==policy['head'] and source['lane_order']==policy['lane_order']
    result=read(directory/'RESULT.json')
    assert result['success'] and result['restoration_verified'] and result['runtime_controls_unchanged']
    assert result['provider_source_role']=='clean-original' and result['build_revision']==source['head']
    assert result['native_fix_acceptance'] is False
    assert set(result['phase']) == set(policy['lane_order']) and result['phase'][lane]['lane'] == lane
    phase=directory/('original-wpt-'+lane)
    settings=source['wpt_lanes'][lane]
    current=policy['wpt_lanes'][lane]
    for key in ['resources','metadata','manifests','capture','install_managed_resources','expected_subtests']:
        assert settings[key]==current[key]
    for url,record in settings['resources'].items():
        path=phase/'mozilla-tests'/url[len('/_mozilla/'):] if url.startswith('/_mozilla/') else phase/'tests'/url[1:]
        assert sha(path)==record['sha256']
    for kind,folder in [('portable','metadata'),('mozilla','mozilla-metadata')]:
        assert sha(phase/folder/'MANIFEST.json')==settings['manifests'][kind]['sha256']
        for name,pin in settings['metadata'][kind].items():
            path=phase/folder/name
            if pin['sha256'] is None:assert not path.exists() and not path.is_symlink()
            else:assert sha(path)==pin['sha256']
    staged=read(phase/'STAGED-RESOURCES.json')
    assert all(sha(phase/name)==digest for name,digest in staged.items())
    for name,key in [('ASSESSMENT.json','assessment_sha256'),('raw.jsonl','raw_sha256'),('RESULT.json','result_sha256')]:
        assert sha(phase/name)==result['phase'][lane][key]
    build=read(directory/'original-build/RESULT.json')
    assert build['command_success'] and build['preservation_verified'] and build['error'] is None
    assert read(directory/'original-build/build-RESULT.json')['exit']==0
    assert build['native_sources']=={'servo/components/style/custom_properties.rs':policy['semantic_original_sources']['servo/components/style/custom_properties.rs']}
    assert read(phase/'BINARY-PINS.json')==build['binaries'] and set(build['binaries'])==set(policy['rebuilt_binaries'])
    assert read(phase/'PRE.json')==read(phase/'POST.json')==read(directory/'PHASES-PRE.json')==read(directory/'PHASES-POST.json')==build['snapshot']
    scope=load('original77_review_scope',root/policy['owner_directory']/'review_scope.py')
    inputs=load('original77_input_binding',root/policy['owner_directory']/'inputs.py')
    closure=load('original77_closure',source_owner/'closure.py')
    expected_inputs=closure.external_inputs(root,source,read(source_owner/'SOURCE-ROLES.json'))
    assert source['intermediate_consumed_inputs']==expected_inputs
    effective=inputs.bind_inputs(capsule['directory'],(source_owner/'FILES.json').read_bytes(),capsule['sha256'],expected_inputs)
    scope.require_intermediate(build['snapshot'],effective)
    assert build['snapshot']['index']['working_diff']==hashlib.sha256(b'').hexdigest()
    metadata=read(phase/'APPLICATION-METADATA.json')
    assert metadata==read(phase/'APPLICATION-METADATA-POST.json')
    assert metadata['revision']==metadata['build_revision']==metadata['harness_revision']==source['head']
    assert metadata['source_role']=='original'
    assert read(phase/'ASSESSMENT-POLICY.json')==phase_policy(settings)
    phase_result=read(phase/'RESULT.json')
    assert phase_result['success'] and phase_result['preservation_verified'] and phase_result['execution_error'] is None
    cleanup=read(phase/'CLEANUP.json')
    assert cleanup['owned_group_absent'] and cleanup['temporary_root_removed']
    events=[json.loads(line) for line in (phase/'raw.jsonl').read_text().splitlines()]
    source_assessor=load('original74_assessor',source_owner/'assess.py')
    replay=source_assessor.assess(events,phase_result['exit'],phase_policy(settings),checks,run_binding=metadata)
    assert replay==read(phase/'ASSESSMENT.json') and replay['complete']
    if lane=='ordinary':
        capture=load('original74_zoom',root/settings['capture']['path'])
        zoom=capture.replay(phase,events)
        assert zoom==read(phase/'ZOOM-OBSERVATION.json') and zoom['role']=='original'
        assert sha(phase/'ZOOM-OBSERVATION.json')==result['phase'][lane]['zoom_observation_sha256']
        assert phase_result['required_zoom_capture_complete'] is True
    projected=assessor.assess(events,phase_result['exit'],phase_policy(current),checks,run_binding=metadata)
    assert projected['complete'] and projected['rows']==replay['rows'] and projected['ends']==replay['ends']
    return projected


def replay_all(root, policy):
    assert policy['baseline_binding'] is not None
    here=root/policy['owner_directory']
    assessor=load('candidate74_assessor',here/'assess.py')
    checks=load('candidate74_checks',root/policy['wpt']['checks_helper'])
    lanes={lane:replay_original(root,policy,assessor,checks,lane) for lane in policy['lane_order']}
    rows=[row for lane in policy['lane_order'] for row in lanes[lane]['rows']]
    ends=[row for lane in policy['lane_order'] for row in lanes[lane]['ends']]
    outcomes=read(root/policy['baseline_binding']['directory']/'OUTCOMES.json')
    assert outcomes['rows']==rows and outcomes['endings']==ends
    result=read(root/policy['baseline_binding']['directory']/'RESULT.json')
    assert outcomes['lanes']==result['phase']
    assert outcomes['provider_source_role']=='clean-original' and outcomes['native_acceptance'] is False
    assert outcomes['zoom_target_correctness'] is None
    assert len(rows)==77 and len(ends)==12
    assert outcomes['callbacks_passed']==sum(row['status']=='PASS' for row in rows)
    assert outcomes['callbacks_failed']==sum(row['status']=='FAIL' for row in rows)
    return lanes


def behavior(original, candidate, settings, signature):
    key=lambda row:(row['test'],row['kind'],row.get('subtest') or '')
    before=sorted([signature(row) for row in original['rows']+original['ends']],key=key)
    after=sorted([signature(row) for row in candidate['rows']+candidate['ends']],key=key)
    old={key(row):row for row in before};new={key(row):row for row in after}
    errors=[]
    if not original['complete'] or not candidate['complete']:errors.append('incomplete observation')
    if set(old)!=set(new):errors.append('callback/page identities changed')
    for identity,row in old.items():
        if (row['kind']=='test_end' or row['status']=='PASS') and new.get(identity)!=row:
            errors.append('original PASS or page ending signature changed: '+str(identity))
    targets={(page,name) for page,names in settings['target_subtests'].items() for name in names}
    target_rows=[row for row in candidate['rows'] if (row['test'],row['subtest']) in targets]
    if len(target_rows)!=len(targets) or any(row['status']!='PASS' for row in target_rows):errors.append('target callback remains non-PASS')
    errors.extend(error for error in candidate['comparison_errors'] if error!='regression identities/status/expectations/intermittents changed')
    result = {'repair_observation_gate':not errors,'errors':errors,'all_signatures_equal':before==after,
            'original_signatures':before,'candidate_signatures':after,
            'differences':[{'identity':identity,'original':old.get(identity),'candidate':new.get(identity)} for identity in sorted(set(old)|set(new)) if old.get(identity)!=new.get(identity)],
            'target_rows':target_rows,'native_acceptance':False}
    return json.loads(json.dumps(result))
