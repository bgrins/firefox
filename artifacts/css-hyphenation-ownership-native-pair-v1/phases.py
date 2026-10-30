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
        results[lane]=wpt.run(root,here,phase,role,policy,env,verify,owned,cancelled,original=output/('original-wpt-'+lane) if role=='candidate' else None,lane=lane)
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
    assert len(rows)==len({(row['test'],row['subtest']) for row in rows})==897
    assert len(endings)==len({row['test'] for row in endings})==23
    assert all(value['zoom_observation_sha256'] is None for value in results.values())
    if role=='candidate':
        assert sum(len(value['candidate_signatures']) for value in behaviors.values())==920
        wpt.save(output/'COMPARISON.json',{'lanes':behaviors,'publication_observation_gate':all(value['publication_observation_gate'] for value in behaviors.values()),'all920_signatures_equal':all(value['all_signatures_equal'] for value in behaviors.values()),'native_acceptance':False})
        spec = importlib.util.spec_from_file_location('language_port_comparison', here/'port_comparison.py')
        ports = importlib.util.module_from_spec(spec);spec.loader.exec_module(ports)
        spec = importlib.util.spec_from_file_location('language_signature', here/'assess.py')
        assessor = importlib.util.module_from_spec(spec);spec.loader.exec_module(assessor)
        try:
            derived = ports.compare(root, output, policy,
                read(output/'original-wpt-regression/ASSESSMENT.json'),
                read(output/'candidate-wpt-regression/ASSESSMENT.json'), assessor.signature)
        except (AssertionError, KeyError, TypeError, ValueError) as error:
            derived = {'derived_ownership_gate': False, 'error': repr(error), 'raw_assessments_unchanged': True}
        derived['publication_observation_gate'] = derived['derived_ownership_gate'] and behaviors['target']['publication_observation_gate'] and behaviors['context']['publication_observation_gate']
        derived['native_acceptance'] = False
        wpt.save(output/'DERIVED-COMPARISON.json', derived)
    wpt.save(output/(role+'-OUTCOMES.json'),{'callbacks_passed':sum(row['status']=='PASS' for row in rows),'callbacks_failed':sum(row['status']=='FAIL' for row in rows),'rows':rows,'endings':endings,'lanes':results,'diagnostics':diagnostics,'provider_source_role':role,'native_acceptance':False})
    wpt.save(output/(role+'-PHASES-POST.json'),initial)
    return results
