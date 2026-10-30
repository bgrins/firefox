import copy
import difflib
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda path: json.loads(path.read_bytes())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

refs = read(HERE / 'REFERENCES.json')
for path, pin in refs.items():
    assert sha(ROOT/path) == pin['sha256'] and (ROOT/path).stat().st_size == pin['bytes']
base = ROOT/'artifacts/css-minmax-relative-infinity-broader-browser-v5/assess.py'
assert (HERE/'ASSESSOR-DELTA.patch').read_text() == ''.join(difflib.unified_diff(
    base.read_text().splitlines(True), (HERE/'assess.py').read_text().splitlines(True),
    fromfile=str(base.relative_to(ROOT)), tofile=str((HERE/'assess.py').relative_to(ROOT))))
owner = ROOT/'artifacts/css-prioritary-published-candidate-v1'
runtime = ROOT/'artifacts/css-prioritary-published-candidate-runtime-1'
policy = read(owner/'POLICY.json')
ownership = load('saved_ownership', ROOT/policy['ownership_helper'])
for path in [owner, runtime]:
    ownership.authenticate(path, refs[str((path/'FILES.json').relative_to(ROOT))]['sha256'])
admission = load('saved_bridge', owner/'admission.py')
capture = admission.validate_current(ROOT, policy, read(owner/'SOURCE-ROLES.json'))
comparison = load('saved_comparison', owner/'comparison.py')
legacy = load('saved_assessor', owner/'assess.py')
fixed = load('corrected_assessor', HERE/'assess.py')
checks = load('saved_checks', ROOT/policy['wpt']['checks_helper'])
originals = comparison.replay_all(ROOT, policy)
terminal = read(runtime/'ROOT-OWNER-TERMINAL.json')
assert terminal == {'session':70364,'launch_chunk':'ee9196','terminal_chunk':'d8ef1a','exit':0,'result_sha256':sha(runtime/'CANDIDATE-RESULT.json')}
result = read(runtime/'CANDIDATE-RESULT.json')
assert result['success'] and result['build_revision'] == policy['head'] == capture['checkpoint']['head']
build = read(runtime/'candidate-build/RESULT.json')
assert build['command_success'] and build['preservation_verified'] and build['error'] is None
assert read(runtime/'candidate-build/build-RESULT.json')['exit'] == 0
roles = read(owner/'SOURCE-ROLES.json')
assert build['native_sources'] == {path:row['candidate_sha256'] for path,row in roles.items()}
command = read(runtime/'candidate-build/COMMAND.json')
assert command['source_sha256'] == build['native_sources']
assert command['owner_manifest'] == sha(owner/'FILES.json')
assert build['snapshot']['index']['head'] == policy['head']
lanes = {}
negative_results = []
policies = {}
for lane in policy['lane_order']:
    phase = runtime/('candidate-wpt-'+lane)
    settings = read(phase/'ASSESSMENT-POLICY.json')
    assert settings == comparison.phase_policy(policy['wpt_lanes'][lane])
    for name,key in [('ASSESSMENT.json','assessment_sha256'),('raw.jsonl','raw_sha256'),('RESULT.json','result_sha256'),('BEHAVIOR-COMPARISON.json','behavior_sha256')]:
        assert sha(phase/name) == result['phase'][lane][key]
    staged = read(phase/'STAGED-RESOURCES.json')
    assert all(sha(phase/name)==digest for name,digest in staged.items())
    for url,pin in settings['resources'].items():
        path = phase/'mozilla-tests'/url[len('/_mozilla/'):] if url.startswith('/_mozilla/') else phase/'tests'/url[1:]
        assert sha(path) == pin['sha256']
    for kind,folder in [('portable','metadata'),('mozilla','mozilla-metadata')]:
        assert sha(phase/folder/'MANIFEST.json') == settings['manifests'][kind]['sha256']
        for name,pin in settings['metadata'][kind].items():
            path=phase/folder/name
            if pin['sha256'] is None: assert not path.exists() and not path.is_symlink()
            else: assert sha(path)==pin['sha256']
    metadata = read(phase/'APPLICATION-METADATA.json')
    assert metadata == read(phase/'APPLICATION-METADATA-POST.json')
    assert metadata['revision'] == metadata['build_revision'] == metadata['harness_revision'] == policy['head']
    assert metadata['source_role']=='candidate'
    assert read(phase/'BINARY-PINS.json') == build['binaries']
    phase_result = read(phase/'RESULT.json')
    assert phase_result['success'] and phase_result['preservation_verified'] and phase_result['execution_error'] is None
    events = [json.loads(line) for line in (phase/'raw.jsonl').read_text().splitlines()]
    original = originals[lane]
    old = legacy.assess(events,phase_result['exit'],settings,checks,original=original,run_binding=metadata)
    assert old == read(phase/'ASSESSMENT.json') and old['complete']
    old_behavior = comparison.behavior(original,old,policy['wpt_lanes'][lane],legacy.signature)
    assert old_behavior == read(phase/'BEHAVIOR-COMPARISON.json') and not old_behavior['repair_observation_gate']
    assert old['comparison_errors'] == ['phase revision differs from authenticated build lineage','run_info changed outside the independently bound BuildID']
    revised = copy.deepcopy(settings)
    revised['phase_revisions'] = {'original':policy['baseline_head'],'candidate':policy['head']}
    revised['phase_lineages'] = {role:{'build_revision':revision,'harness_revision':revision}
        for role,revision in revised['phase_revisions'].items()}
    revised['phase_metadata'] = {'original':original['run_binding'],'candidate':metadata}
    policies[lane] = {key:revised[key] for key in ['phase_revisions','phase_lineages','phase_metadata']}
    def evaluate(stream=events, before=original, binding=metadata, config=revised):
        assessed=fixed.assess(stream,phase_result['exit'],config,checks,original=before,run_binding=binding)
        assessed['oracle_caveat']=old['oracle_caveat']
        return assessed,comparison.behavior(before,assessed,policy['wpt_lanes'][lane],fixed.signature)
    corrected, behavior = evaluate()
    assert corrected['complete'] and corrected['comparison_gate_passed'] and behavior['repair_observation_gate']
    unchanged = set(old)-{'comparison_errors','comparison_gate_passed'}
    assert all(corrected[key]==old[key] for key in unchanged)
    assert all(behavior[key]==old_behavior[key] for key in set(behavior)-{'errors','repair_observation_gate'})
    if lane=='ordinary':
        zoom = load('saved_zoom',ROOT/settings['capture']['path'])
        observed=zoom.replay(phase,events)
        assert observed==read(phase/'ZOOM-OBSERVATION.json') and observed['role']=='candidate'
        assert sha(phase/'ZOOM-OBSERVATION.json')==result['phase'][lane]['zoom_observation_sha256']
        for label in ['wrong_role','original_role','wrong_build','wrong_harness','wrong_build_id','unrelated_run_info','missing_lineage','original_PASS_signature','published_signature']:
            stream,before,binding,config=[copy.deepcopy(value) for value in (events,original,metadata,revised)]
            info=next(row['run_info'] for row in stream if row.get('action')=='suite_start')
            if label=='wrong_role': binding['source_role']='original'
            elif label=='original_role': before['run_binding']['source_role']='candidate'
            elif label=='wrong_build': binding['revision']=binding['build_revision']='0'*40
            elif label=='wrong_harness': binding['harness_revision']=info['revision']='0'*40
            elif label=='wrong_build_id': binding['browser_build_id']=info['browser_build_id']='wrong'
            elif label=='unrelated_run_info': info['debug']=not info['debug']
            elif label=='missing_lineage': del config['phase_lineages']
            else:
                published={(page,name) for page,names in settings['published_subtests'].items() for name in names}
                chosen=next(row for row in original['rows'] if row['status']=='PASS' and
                    (((row['test'],row['subtest']) in published)==(label=='published_signature')))
                target=next(row for row in stream if row.get('action')=='test_status' and (row['test'],row['subtest'])==(chosen['test'],chosen['subtest']))
                target['message']='mutated full signature'
            bad,bad_behavior=evaluate(stream,before,binding,config)
            assert not bad['comparison_gate_passed'] and not bad_behavior['repair_observation_gate'],label
            if label=='published_signature': assert 'published callback full signatures changed or missing' in bad_behavior['errors']
            if label=='original_PASS_signature': assert any('original PASS or page ending' in e for e in bad_behavior['errors'])
            negative_results.append({'case':label,'assessment_errors':bad['errors'],'comparison_errors':bad['comparison_errors'],'behavior_errors':bad_behavior['errors']})
    lanes[lane] = {'callbacks':{'PASS':sum(r['status']=='PASS' for r in corrected['rows']),'FAIL':sum(r['status']=='FAIL' for r in corrected['rows'])},
        'endings_OK':len(corrected['ends']),'preserved_original_PASS':sum(r['status']=='PASS' for r in original['rows']),
        'targets_PASS':len(behavior['target_rows']),'published_signatures_preserved':len(behavior['published_original_signatures']),
        'differences':len(behavior['differences']),'stored_gate':old_behavior['repair_observation_gate'],'stored_errors':old_behavior['errors'],
        'corrected_assessment_gate':corrected['comparison_gate_passed'],'corrected_behavior_gate':behavior['repair_observation_gate'],
        'corrected_errors':behavior['errors'],'run_info_changed_keys':sorted(k for k in original['run_info'].keys()|corrected['run_info'].keys() if original['run_info'].get(k)!=corrected['run_info'].get(k))}
assert sum(x['preserved_original_PASS'] for x in lanes.values())==64
assert sum(x['targets_PASS'] for x in lanes.values())==24
assert sum(x['endings_OK'] for x in lanes.values())==12
for path,pin in refs.items(): assert sha(ROOT/path)==pin['sha256']
print(json.dumps({'lanes':lanes,'policy_additions':policies,'negative_checks':negative_results,'artifact_only_V89_bridge_authenticated':True,
    'live_records_modified':False,'restoration_reverified':False,'native_acceptance':False,'zoom_numeric_oracle':None},indent=2,sort_keys=True))
