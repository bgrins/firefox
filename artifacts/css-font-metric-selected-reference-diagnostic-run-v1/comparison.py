import copy
import hashlib
import importlib.util
import json

read=lambda p:json.loads(p.read_bytes())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def build_binding(root,here,output,policy,role):
    assert role in ('original','candidate')
    assert here == root / policy['owner_directory']
    directory=output/(role+'-build')
    build=read(directory/'RESULT.json')
    assert build['command_success'] and build['preservation_verified'] and build['browser_build_performed'] and build['error'] is None
    inner=read(directory/'build-RESULT.json')
    assert inner['exit']==0 and inner['owned_group_absent'] and inner['cleanup_errors']==[] and inner['error'] is None and inner['stop_reason'] is None
    command=read(directory/'COMMAND.json')
    assert command['command'] == ['/Users/bgrins/venvs/firefox/bin/python', './mach', 'build', 'binaries', '-j2']
    assert command['owner_manifest']==sha(here/'FILES.json') and command['source_role']==role
    roles=read(here/'SOURCE-ROLES.json')
    expected={name:row['base_sha256' if role=='original' else 'candidate_sha256'] for name,row in roles.items()}
    assert command['source_sha256']==build['native_sources']==expected
    assert set(build['binaries'])==set(policy['rebuilt_binaries'])
    metadata=build['application_metadata']
    assert metadata['source_role']==role
    assert metadata['revision']==metadata['build_revision']==metadata['harness_revision']==policy['head']
    assert len(metadata['sha256'])==64 and metadata['browser_build_id']
    closure=load('pair_consumed_closure',here/'closure.py')
    inputs=load('pair_input_binding',here/'inputs.py')
    external=closure.external_inputs(root,policy,roles)
    assert external==policy['intermediate_consumed_inputs']
    effective=inputs.bind_inputs(policy['owner_directory'],(here/'FILES.json').read_bytes(),sha(here/'FILES.json'),external)
    scope=load('pair_scope',here/'review_scope.py')
    scope.require_intermediate(build['snapshot'],effective)
    assert build['snapshot']['index']['head']==policy['head']
    return build


def phase_policy(settings,builds,head):
    result=dict(settings,tests={page:'testharness' for page in settings['expected_subtests']},held_subtests={})
    result['regression_subtests']={page:[name for name in names if name not in settings['target_subtests'].get(page,[])] for page,names in settings['expected_subtests'].items()}
    result['cardinality_description']='Exact publication roster, all completed PASS and FAIL observations retained.'
    result['phase_metadata']={role:row['application_metadata'] for role,row in builds.items()}
    result['phase_lineages']={role:{'build_revision':head,'harness_revision':head} for role in builds}
    return result


def replay_original(root,here,output,policy,lane,assessor,checks):
    settings=policy['wpt_lanes'][lane]
    build=build_binding(root,here,output,policy,'original')
    phase=output/('original-wpt-'+lane)
    result=read(phase/'RESULT.json')
    assert result['success'] and result['preservation_verified'] and result['execution_error'] is None
    outcomes = read(output/'original-OUTCOMES.json')
    phases = outcomes['lanes' if lane in policy['lane_order'] else 'diagnostics']
    for name,key in [('ASSESSMENT.json','assessment_sha256'),('raw.jsonl','raw_sha256'),('RESULT.json','result_sha256')]:assert sha(phase/name)==phases[lane][key]
    assert read(phase/'APPLICATION-METADATA.json')==read(phase/'APPLICATION-METADATA-POST.json')==build['application_metadata']
    assert read(phase/'BINARY-PINS.json')==build['binaries']
    assert read(phase/'PRE.json')==read(phase/'POST.json')==build['snapshot']==read(output/'original-PHASES-PRE.json')==read(output/'original-PHASES-POST.json')
    assert read(phase/'CLEANUP.json')['owned_group_absent'] and read(phase/'CLEANUP.json')['temporary_root_removed']
    staged=read(phase/'STAGED-RESOURCES.json')
    assert all(sha(phase/name)==pin for name,pin in staged.items())
    for url,row in settings['resources'].items():
        path=phase/'mozilla-tests'/url[len('/_mozilla/'):] if url.startswith('/_mozilla/') else phase/'tests'/url[1:]
        assert sha(path)==row['sha256']
    for kind,folder in [('portable','metadata'),('mozilla','mozilla-metadata')]:
        assert sha(phase/folder/'MANIFEST.json')==settings['manifests'][kind]['sha256']
        for name,row in settings['metadata'][kind].items():
            if row['sha256'] is not None:assert sha(phase/folder/name)==row['sha256']
            else:assert not (phase/folder/name).exists()
    expected=phase_policy(settings,{'original':build},policy['head'])
    assert expected==read(phase/'ASSESSMENT-POLICY.json')
    events=[json.loads(line) for line in (phase/'raw.jsonl').read_text().splitlines()]
    replay=assessor.assess(events,result['exit'],expected,checks,run_binding=build['application_metadata'])
    assert replay==read(phase/'ASSESSMENT.json') and replay['complete']
    return replay


def behavior(original,candidate,signature):
    key=lambda row:(row['test'],row['kind'],row.get('subtest') or '')
    before=sorted([signature(row) for row in original['rows']+original['ends']],key=key)
    after=sorted([signature(row) for row in candidate['rows']+candidate['ends']],key=key)
    old={key(row):row for row in before};new={key(row):row for row in after}
    errors=list(candidate['comparison_errors'])
    if not original['complete'] or not candidate['complete']:errors.append('incomplete observation')
    if set(old)!=set(new):errors.append('callback/page identities changed')
    for identity,row in old.items():
        if (row['kind']=='test_end' or row['status']=='PASS') and new.get(identity)!=row:
            errors.append('original PASS or ending full signature changed: '+str(identity))
    if any(row['status']!='PASS' for row in candidate['rows']):errors.append('candidate publication callback remains non-PASS')
    result={'publication_observation_gate':not errors,'errors':errors,'all_signatures_equal':before==after,'original_signatures':before,'candidate_signatures':after,'differences':[{'identity':identity,'original':old.get(identity),'candidate':new.get(identity)} for identity in sorted(set(old)|set(new)) if old.get(identity)!=new.get(identity)],'native_acceptance':False}
    return json.loads(json.dumps(result))


def historical(root, policy, lane):
    binding = policy['historical_original']
    ownership = load('diagnostic_historical_ownership', root / policy['ownership_helper'])
    for key in ('owner', 'runtime'):
        item = binding[key]
        ownership.authenticate(root / item['directory'], item['manifest_sha256'])
    here, output = root / binding['owner']['directory'], root / binding['runtime']['directory']
    old_policy = read(here / 'POLICY.json')
    assert old_policy['head'] == policy['head'] and lane == 'typedattr'
    assert old_policy['wpt_lanes'][lane] == policy['wpt_lanes'][lane]
    old_comparison = load('diagnostic_historical_comparison', here / 'comparison.py')
    return here, output, old_policy, old_comparison


def historical_build(root, policy, lane):
    here, output, old_policy, old_comparison = historical(root, policy, lane)
    return old_comparison.build_binding(root, here, output, old_policy, 'original')


def historical_replay(root, policy, lane, assessor, checks):
    here, output, old_policy, old_comparison = historical(root, policy, lane)
    return old_comparison.replay_original(root, here, output, old_policy, lane, assessor, checks)
