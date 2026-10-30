import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    owner = ROOT / 'artifacts/css-contextual-duration-finite-depth-candidate-v1'
    runtime = ROOT / 'artifacts/css-contextual-duration-finite-depth-candidate-runtime-1'
    policy = read(owner / 'POLICY.json')
    assert sha(runtime / 'FILES.json') == '7439b1de3c87ad0d0a100b558ca4c09a02ea5553f5a8d519b047a630737b1125'
    for name, pin in read(runtime / 'FILES.json').items():
        assert sha(runtime / name) == (pin if isinstance(pin, str) else pin['sha256'])
    terminal = read(runtime / 'ROOT-TERMINAL.json')
    assert (terminal['session_id'], terminal['terminal_chunk'], terminal['exit']) == (34257, 'ffd55f', 1)
    assert terminal['owner_sha256'] == sha(owner / 'FILES.json')
    assert terminal['result_sha256'] == sha(runtime / 'CANDIDATE-RESULT.json')
    assert terminal['state_and_application_restoration_independently_verified']
    assert terminal['backup_removed_bytes'] == 1008605176 and not terminal['native_acceptance']
    refresh_path = ROOT / 'artifacts/css-contextual-duration-finite-depth-root-refresh.json'
    assert sha(refresh_path) == '7366b6e3ab35a8bb33041fe8af8c6ed72c5b7b33e3174e418220f3780cc02f8a'
    refresh = read(refresh_path)
    assert refresh['runtime_manifest_sha256'] == sha(runtime / 'FILES.json')
    assert refresh['observation'] == terminal['raw_index_observation']
    assert refresh['full_restored_state_verified'] and refresh['accepted_fix_increment'] == 0
    assert refresh['only_changed_field'] == 'raw_index_observation.current'
    for name, pin in read(owner / 'FILES.json').items():
        assert sha(owner / name) == (pin if isinstance(pin, str) else pin['sha256'])
    original_dir = ROOT / policy['baseline_binding']['directory']
    assert sha(original_dir / 'FILES.json') == '495d2c0299a77f537fd18426afb6e0aab13065ccebb50564c4edeaab1b40901c'
    for name, pin in read(original_dir / 'FILES.json').items():
        assert sha(original_dir / name) == (pin if isinstance(pin, str) else pin['sha256'])
    comparison = load('pair_comparison', owner / 'comparison.py')
    assessor = load('pair_assessor', owner / 'assess.py')
    checks = load('pair_stream_checks', ROOT / policy['wpt']['checks_helper'])
    original = comparison.replay_original(ROOT, policy, assessor, checks)
    phase = runtime / 'candidate-wpt'
    phase_result = read(phase / 'RESULT.json')
    metadata = read(phase / 'APPLICATION-METADATA.json')
    settings = read(phase / 'ASSESSMENT-POLICY.json')
    assert settings == comparison.phase_policy(policy['wpt'])
    events = [json.loads(line) for line in (phase / 'raw.jsonl').read_text().splitlines()]
    actual = assessor.assess(events, phase_result['exit'], settings, checks, original=original, run_binding=metadata)
    assert actual == read(phase / 'ASSESSMENT.json')
    assert actual['complete'] and not actual['errors'] and not actual['infrastructure_faults']
    assert not actual['comparison_gate_passed']
    assert [r['status'] for r in actual['rows']] == ['FAIL'] * 4
    assert [r['status'] for r in actual['ends']] == ['OK']
    assert all('first-leaf-read expected' in r['message'] for r in actual['rows'])
    assert read(phase / 'PRE.json') == read(phase / 'POST.json')
    assert metadata == read(phase / 'APPLICATION-METADATA-POST.json')
    build = read(runtime / 'candidate-build/RESULT.json')
    assert build['command_success'] and build['preservation_verified']
    assert read(phase / 'BINARY-PINS.json') == build['binaries']
    roles = read(owner / 'SOURCE-ROLES.json')
    assert build['native_sources'] == {name: role['candidate_sha256'] for name, role in roles.items()}
    assert phase_result['exit'] == 1 and phase_result['execution_error'] is None and phase_result['preservation_verified']
    cleanup = read(phase / 'CLEANUP.json')
    assert cleanup['owned_group_absent'] and cleanup['temporary_root_removed']
    collection = load('pair_record_collection', owner / 'records.py').collect(ROOT, runtime / 'progress-records', read(runtime / 'PROGRESS-BINDING.json'), policy, actual)
    assert collection == read(runtime / 'PROGRESS-RECORDS.json')
    assert collection['complete'] and len(collection['records']) == 4
    record_pairs = load('pair_phase_helpers', owner / 'phases.py').record_comparison(ROOT, runtime, policy, collection)
    assert record_pairs == read(runtime / 'RECORD-COMPARISON.json')
    projection = load('pair_projection', ROOT / 'artifacts/css-contextual-duration-finite-depth-original-projection-v1/project.py')
    result = {'original_statuses': [r['status'] for r in original['rows']], 'candidate_statuses': [r['status'] for r in actual['rows']], 'candidate_ending': 'OK', 'candidate_comparison_passed': False, 'native_pass_count_inferred': False, 'depths': {}}
    for depth in (1, 2, 4, 8):
        modes = {}
        for label, directory in [('original', original_dir), ('candidate', runtime)]:
            record = read(directory / 'progress-records' / f'depth-{depth}.json')
            comparison.require_original_calibration(record['observations'])
            item = record['observations']['contextual']
            modes[label] = {'samples': item['samples'], 'before_membership': projection.project(depth, item['beforeMembership']), 'after_membership': projection.project(depth, item['afterMembership']), 'membership': item['membership'], 'later_snapshots_equal': item['beforeMembership'] == item['afterMembership']}
        result['depths'][str(depth)] = {'expected_leaf': comparison.expected_snapshot(depth, True)['opacity'], 'literal_and_initial_calibrations_verified': True, **modes}
    outer = read(runtime / 'CANDIDATE-RESULT.json')
    assert not outer['success'] and not outer['native_fix_acceptance'] and outer['restoration_verified'] and not outer['publication_errors']
    assert read(runtime / 'RESTORATION.json')['errors'] == []
    paths = [owner / 'FILES.json', owner / 'POLICY.json', owner / 'comparison.py', owner / 'phases.py', owner / 'records.py', owner / 'assess.py', original_dir / 'FILES.json']
    paths += [phase / n for n in ('raw.jsonl', 'ASSESSMENT.json', 'ASSESSMENT-POLICY.json', 'RESULT.json', 'APPLICATION-METADATA.json', 'APPLICATION-METADATA-POST.json', 'BINARY-PINS.json', 'CLEANUP.json')]
    paths += [runtime / n for n in ('CANDIDATE-RESULT.json', 'RESTORATION.json', 'PROGRESS-BINDING.json', 'PROGRESS-RECORDS.json', 'RECORD-COMPARISON.json', 'candidate-build/RESULT.json')]
    paths += list((runtime / 'progress-records').glob('depth-*.json'))
    paths += [runtime / 'FILES.json', runtime / 'ROOT-TERMINAL.json', refresh_path]
    paths += [owner / 'SOURCE-ROLES.json', ROOT / 'artifacts/css-contextual-duration-finite-depth-original-projection-v1/project.py', ROOT / 'artifacts/css-contextual-duration-finite-depth-oracle-model-v1/FILES.json']
    result['root_terminal'] = terminal
    result['root_refresh'] = refresh
    result['references'] = {str(p.relative_to(ROOT)): sha(p) for p in paths}
    result['stale_comparison_wording'] = actual['comparison_errors']
    (HERE / 'REPLAY.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({depth: value['candidate']['samples'] for depth, value in result['depths'].items()}))


if __name__ == '__main__':
    main()
