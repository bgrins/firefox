import hashlib
import importlib.util
import json

read=lambda p:json.loads(p.read_bytes())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def run(root,here,output,role,policy,env,verify,owned,cancelled):
    spec=importlib.util.spec_from_file_location('paired_wpt',here/'wpt.py')
    wpt=importlib.util.module_from_spec(spec);spec.loader.exec_module(wpt)
    initial=verify()
    wpt.save(output/(role+'-PHASES-PRE.json'),initial)
    rows,endings,results,behaviors=[],[],{},{}
    diagnostics = {}
    build=read(output/(role+'-build/RESULT.json'))
    for lane in policy['lane_order']:
        phase=output/(role+'-wpt-'+lane)
        results[lane]=wpt.run(root,here,phase,role,policy,env,verify,owned,cancelled,original=None,lane=lane)
        assessment=read(phase/'ASSESSMENT.json')
        settings=policy['wpt_lanes'][lane]
        assert assessment['complete'] and len(assessment['rows'])==settings['expected_subtest_count']
        assert len(assessment['ends'])==settings['expected_page_count']
        assert all(row['status'] in ('PASS','FAIL') for row in assessment['rows'])
        behaviors[lane]=read(phase/'BEHAVIOR-COMPARISON.json')
        rows.extend(assessment['rows']);endings.extend(assessment['ends'])
        assert not owned and read(phase/'PRE.json')==read(phase/'POST.json')==initial
        metadata=read(phase/'APPLICATION-METADATA.json')
        assert metadata==read(phase/'APPLICATION-METADATA-POST.json')==build['application_metadata']
        assert metadata['revision']==metadata['build_revision']==policy['head'] and metadata['source_role']==role
        assert build['binaries']==read(phase/'BINARY-PINS.json') and verify()==initial
    assert len(rows)==len({(row['test'],row['subtest']) for row in rows})==7
    assert len(endings)==len({row['test'] for row in endings})==1
    assert all(value['zoom_observation_sha256'] is None for value in results.values())
    assert role == 'candidate' and all(value is None for value in behaviors.values())
    assert policy['diagnostic_lane_order'] == []
    wpt.save(output/'DIAGNOSTIC-OBSERVATION.json', {'complete': True, 'callbacks': len(rows), 'endings': len(endings), 'historical_comparison_performed': False, 'publication_observation_gate': False, 'native_acceptance': False})
    for lane in policy['diagnostic_lane_order']:
        phase = output / (role + '-wpt-' + lane)
        record = wpt.run(root, here, phase, role, policy, env, verify, owned, cancelled, original=output / ('original-wpt-' + lane) if role == 'candidate' else None, lane=lane)
        assessment = read(phase / 'ASSESSMENT.json')
        assert assessment['complete'] and len(assessment['rows']) == policy['wpt_lanes'][lane]['expected_subtest_count']
        assert len(assessment['ends']) == policy['wpt_lanes'][lane]['expected_page_count']
        assert read(phase / 'PRE.json') == read(phase / 'POST.json') == initial
        assert read(phase / 'APPLICATION-METADATA.json') == read(phase / 'APPLICATION-METADATA-POST.json') == build['application_metadata']
        assert read(phase / 'BINARY-PINS.json') == build['binaries'] and not owned and verify() == initial
        diagnostics[lane] = record
        wpt.save(output / (role + '-DIAGNOSTIC-' + lane + '.json'), {'rows': assessment['rows'], 'endings': assessment['ends'], 'comparison': read(phase / 'BEHAVIOR-COMPARISON.json'), 'included_in_publication28': False, 'native_acceptance': False})
    if role == 'candidate' and policy['diagnostic_lane_order']:
        diagnostic_comparisons = {lane: read(output / (role + '-wpt-' + lane) / 'BEHAVIOR-COMPARISON.json') for lane in policy['diagnostic_lane_order']}
        diagnostic_gate = all(value['publication_observation_gate'] for value in diagnostic_comparisons.values())
        publication_gate = all(value['publication_observation_gate'] for value in behaviors.values())
        wpt.save(output / 'DIAGNOSTIC-COMPARISON.json', {'lanes': diagnostic_comparisons, 'diagnostic_observation_gate': diagnostic_gate, 'publication28_observation_gate': publication_gate, 'combined_observation_gate': diagnostic_gate and publication_gate, 'native_acceptance': False})
    wpt.save(output/(role+'-OUTCOMES.json'),{'callbacks_passed':sum(row['status']=='PASS' for row in rows),'callbacks_failed':sum(row['status']=='FAIL' for row in rows),'rows':rows,'endings':endings,'lanes':results,'diagnostics':diagnostics,'provider_source_role':role,'native_acceptance':False})
    wpt.save(output/(role+'-PHASES-POST.json'),initial)
    return results
