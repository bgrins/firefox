import copy
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OWNER = ROOT / 'artifacts/css-contextual-duration-feedback-trace-original-v1'
RUN = ROOT / 'artifacts/css-contextual-duration-feedback-trace-original-runtime-1'
PHASE = RUN / 'feedback-wpt'
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def authenticate(directory, expected):
    assert sha(directory / 'FILES.json') == expected
    for name, entry in read(directory / 'FILES.json').items():
        assert sha(directory / name) == (entry['sha256'] if isinstance(entry, dict) else entry)

def main():
    authenticate(OWNER, 'eaa11eba71b4c6163618df4be3f58d039a8b756e3f7c318c070dc3715085967b')
    policy = read(OWNER / 'POLICY.json')
    for name, pin in policy['references'].items():
        if name.startswith('artifacts/'):
            assert sha(ROOT / name) == pin, name
    for key in ('logger', 'feedback_transport', 'trace_parser'):
        item = policy[key]
        authenticate(ROOT / item['directory'], item['manifest_sha256'])
    assessor = load('saved_assessor', OWNER / 'assess.py')
    checks = load('saved_checks', ROOT / policy['wpt']['checks_helper'])
    phases = load('saved_phases', OWNER / 'phases.py')
    adapter = load('saved_trace_adapter', OWNER / 'trace.py')
    outer = read(RUN / 'RESULT.json')
    result = read(PHASE / 'RESULT.json')
    metadata = read(PHASE / 'APPLICATION-METADATA.json')
    saved_policy = read(PHASE / 'ASSESSMENT-POLICY.json')
    expected_policy = dict(policy['wpt'], tests=policy['wpt']['test_types'], held_subtests={})
    expected_policy['regression_subtests'] = policy['wpt']['expected_subtests']
    expected_policy['cardinality_description'] = 'Exact sealed target and control names; existing control failures retain full signatures.'
    assert saved_policy == expected_policy
    events = [json.loads(line) for line in (PHASE / 'raw.jsonl').read_text().splitlines()]
    assessment = assessor.assess(events, result['exit'], saved_policy, checks, run_binding=metadata)
    assert json.loads(json.dumps(assessment)) == read(PHASE / 'ASSESSMENT.json')
    records = phases.feedback_records(ROOT, RUN, policy)
    assert records == read(RUN / 'FEEDBACK-RECORDS.json')
    phases.require_calibration(assessment, records)
    phases.require_metadata(policy, metadata)
    trace = adapter.capture(PHASE)
    assert trace == read(RUN / 'TRACE-INDEX.json')
    assert trace['trace_syntax_and_sequence_valid'] and not trace['errors']
    assert len(trace['events_in_input_order']) == 385
    assert len(trace['observed_ids']) == 10 and not trace['missing_ids']
    assert not trace['truncated'] and not trace['cap_markers']
    assert not trace['bounded_candidate_witnesses']
    assert metadata == read(PHASE / 'APPLICATION-METADATA-POST.json')
    assert result['success'] and result['exit'] == 0 and result['execution_error'] is None and result['preservation_verified']
    assert outer['success'] and outer['error'] is None and not outer['publication_errors']
    assert outer['phases']['feedback'] == {'assessment_sha256':sha(PHASE/'ASSESSMENT.json'), 'raw_sha256':sha(PHASE/'raw.jsonl'), 'result_sha256':sha(PHASE/'RESULT.json')}
    assert outer['phases']['trace_index_sha256'] == sha(RUN/'TRACE-INDEX.json')
    assert outer['phases']['record_index_sha256'] == sha(RUN/'FEEDBACK-RECORDS.json')
    assert outer['phases']['calibrated_acquisition'] is True
    build = read(RUN/'trace-build/RESULT.json')
    inner = read(RUN/'trace-build/build-RESULT.json')
    assert build['command_success'] and build['preservation_verified'] and build['error'] is None
    assert inner['exit'] == 0 and inner['owned_group_absent'] and not inner['cleanup_errors'] and inner['error'] is None and inner['stop_reason'] is None
    assert build['binaries'] == read(PHASE/'BINARY-PINS.json')
    assert read(PHASE/'PRE.json') == read(PHASE/'POST.json') == read(RUN/'PHASES-PRE.json') == read(RUN/'PHASES-POST.json') == build['snapshot']
    roles = read(OWNER/'SOURCE-ROLES.json')
    assert build['native_sources'] == {name:role['candidate_sha256'] for name,role in roles.items()}
    assert read(RUN/'trace-build/TRACE-SOURCE-ROLE.json') == {'build_revision':policy['head'], 'context_sources':policy['source_context_pins'], 'overlay':build['native_sources'], 'source_role':'instrumented-original'}
    before, after = read(RUN/'PRE.json'), read(RUN/'POST.json')
    projected = copy.deepcopy(before); projected['index']['raw_index'] = after['index']['raw_index']
    assert projected == after
    restored = read(RUN/'RESTORATION.json'); backup = read(RUN/'BACKUP-CLEANUP.json')
    assert not restored['errors'] and not restored['owned_processes']
    for name, role in roles.items():
        assert restored['sources'][name]['sha256'] == role['base_sha256']
        assert restored['sources'][name]['identity'] == read(RUN/'TRACE-PRE.json')['sources'][name]['identity']
    assert backup['removed'] and backup['verified_original_restoration'] and not backup['retained_after_failure']
    assert read(PHASE/'CLEANUP.json')['owned_group_absent'] and read(PHASE/'CLEANUP.json')['temporary_root_removed']
    summaries = {}
    for kind in ('coupled','zero-start'):
        record = read(RUN/f'feedback-records/{kind}.json')
        summaries[kind] = {}
        for trajectory in record['trajectories']:
            role = trajectory['role']; observations = []
            for phase in trajectory['phases']:
                for observation in phase['reads']:
                    if role == 'literal' or (role == 'override' and phase['name'] != 'initial-750'):
                        assert all(e['duration'] == 2000 and e['time'] == 750 and e['progress'] == .375 for e in observation['effects'])
                        assert observation['style']['font'] == ('22px' if kind == 'coupled' else '12px')
                        assert observation['style']['opacity'] == ('0.375' if kind == 'coupled' else '1')
                        assert all(observation['sameAnimations']) and all(observation['sameEffects'])
                    observations.append({'phase':phase['name'], 'order':observation['order'], 'style':observation['style'], 'effects':observation['effects']})
            summaries[kind][role] = observations
    paths = ['RESULT.json','RESTORATION.json','BACKUP-CLEANUP.json','RAW-INDEX-OBSERVATION.json','DIAGNOSTICS.json','FEEDBACK-RECORDS.json','FEEDBACK-BINDING.json','TRACE-INDEX.json','PRE.json','POST.json','TRACE-PRE.json','PHASES-PRE.json','PHASES-POST.json','trace-build/RESULT.json','trace-build/build-RESULT.json','trace-build/TRACE-SOURCE-ROLE.json']
    paths += ['feedback-wpt/'+name for name in ['raw.jsonl','wpt.log','ASSESSMENT.json','ASSESSMENT-POLICY.json','RESULT.json','APPLICATION-METADATA.json','APPLICATION-METADATA-POST.json','BINARY-PINS.json','PRE.json','POST.json','CLEANUP.json']]
    paths += ['feedback-records/coupled.json','feedback-records/zero-start.json']
    references = {str((RUN/name).relative_to(ROOT)):{'sha256':sha(RUN/name),'bytes':(RUN/name).stat().st_size} for name in paths}
    return {'ok':True,'callbacks':{'PASS':2,'FAIL':0},'page_OK':1,'raw_assessment_replay_exact':True,'trace_replay_exact':True,'record_replay_exact':True,'trace_events':385,'trace_ids':10,'caps':0,'bounded_witnesses':0,'actual_build_id':metadata['browser_build_id'],'build_and_harness_revision':metadata['revision'],'fixed_2s_controls_independently_checked':True,'saved_restoration_receipts_consistent':True,'live_state_verified':False,'root_terminal_manifest_pending':True,'references':references,'observations':summaries}

if __name__ == '__main__':
    print(json.dumps(main(),indent=2,sort_keys=True))
