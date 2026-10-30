import copy
import hashlib
import importlib.util
import json
from pathlib import Path

read = lambda path: json.loads(path.read_bytes())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def expected_wpt(root, policy):
    settings = copy.deepcopy(read(root / policy['baseline_capsule']['directory'] / 'POLICY.json')['wpt'])
    assert settings['phase_revisions'] == {'original':policy['head']}
    settings['phase_revisions']['candidate'] = policy['head']
    return settings


def phase_policy(settings):
    result = dict(settings, tests=settings['test_types'], held_subtests={})
    result['regression_subtests'] = {page:[name for name in names if name not in settings['target_subtests'].get(page, [])] for page,names in settings['expected_subtests'].items()}
    result['cardinality_description'] = 'Exact sealed target and control names; existing control failures retain full signatures.'
    return result


def original_directory(root, policy):
    binding = policy['baseline_binding']
    assert binding is not None
    assert binding['directory'] == 'artifacts/css-contextual-duration-feedback-trace-original-runtime-1'
    return root / binding['directory'] / 'feedback-wpt'


def require_restored_snapshots(before, after, current):
    expected = copy.deepcopy(before)
    expected['index']['raw_index'] = after['index']['raw_index']
    assert expected == after
    projected = copy.deepcopy(after)
    projected['index']['raw_index'] = current['index']['raw_index']
    assert projected == current


def admit_restored_snapshot(root, policy, current):
    directory = original_directory(root, policy).parent
    require_restored_snapshots(read(directory / 'PRE.json'),read(directory / 'POST.json'),current)


def replay_original(root, policy, assessor, checks):
    binding = policy['baseline_binding']
    phase = original_directory(root, policy)
    directory = phase.parent
    source_dir = root / policy['baseline_capsule']['directory']
    source = read(source_dir / 'POLICY.json')
    assert policy['wpt'] == expected_wpt(root, policy)
    assert source['head'] == policy['head'] and source['trace_source_role'] == 'instrumented-original'
    for key in ('logger','feedback_transport','trace_parser','source_context_pins','accepted_current_payloads','accepted_epoch_records','original_build'):
        assert source[key] == policy[key], key
    roles = read(source_dir / 'SOURCE-ROLES.json')
    candidate_roles = read(Path(__file__).resolve().parent / 'SOURCE-ROLES.json')
    assert set(roles) == {'dom/animation/EffectCompositor.cpp'}
    assert roles['dom/animation/EffectCompositor.cpp'] == candidate_roles['dom/animation/EffectCompositor.cpp']
    assert source['source_context_pins']['servo/components/style/matching.rs'] == candidate_roles['servo/components/style/matching.rs']['base_sha256']
    assert read(directory / binding['terminal_path']) == binding['terminal']
    assert binding['terminal']['exit'] == 0
    assert sha(directory / 'RESULT.json') == binding['result_sha256']
    assert sha(directory / 'POST.json') == binding['restored_snapshot_sha256']
    outer = read(directory / 'RESULT.json')
    assert outer['success'] and outer['error'] is None and outer['publication_errors'] == []
    assert outer['restoration_verified'] and outer['runtime_controls_unchanged'] and outer['empty_staging_preserved']
    assert outer['trace_source_role'] == 'instrumented-original' and outer['native_fix_acceptance'] is False
    restoration = read(directory / 'RESTORATION.json')
    assert restoration['errors'] == [] and restoration['owned_processes'] == {}
    assert set(restoration['sources']) == set(roles)
    for name, role in roles.items():
        assert restoration['sources'][name]['sha256'] == role['base_sha256']
    backup = read(directory / 'BACKUP-CLEANUP.json')
    assert backup['removed'] and backup['verified_original_restoration'] and not backup['retained_after_failure']
    observation = read(directory / 'RAW-INDEX-OBSERVATION.json')
    assert observation['semantic_index_unchanged'] and observation['canonical_updated'] is False
    assert observation['before'] == read(directory / 'PRE.json')['index']['raw_index']
    assert observation['after'] == read(directory / 'POST.json')['index']['raw_index']
    require_restored_snapshots(read(directory / 'PRE.json'),read(directory / 'POST.json'),read(directory / 'POST.json'))
    saved_policy = read(phase / 'ASSESSMENT-POLICY.json')
    assert saved_policy == phase_policy(source['wpt'])
    events = [json.loads(line) for line in (phase / 'raw.jsonl').read_text().splitlines()]
    metadata = read(phase / 'APPLICATION-METADATA.json')
    result = read(phase / 'RESULT.json')
    observed = assessor.assess(events,result['exit'],saved_policy,checks,run_binding=metadata)
    assert json.loads(json.dumps(observed)) == read(phase / 'ASSESSMENT.json')
    assert observed['complete'] and not observed['errors']
    assert len(observed['rows']) == 2 and all(row['status'] == 'PASS' for row in observed['rows'])
    assert len(observed['ends']) == 1 and observed['ends'][0]['status'] == 'OK'
    assert result['success'] and result['exit'] == 0 and result['preservation_verified'] and result['execution_error'] is None
    assert metadata == read(phase / 'APPLICATION-METADATA-POST.json')
    assert metadata['revision'] == metadata['build_revision'] == policy['head']
    assert metadata['trace_source_role'] == 'instrumented-original' and metadata['source_role'] == 'original'
    cleanup = read(phase / 'CLEANUP.json')
    assert cleanup['owned_group_absent'] and cleanup['temporary_root_removed']
    build = read(directory / 'trace-build/RESULT.json')
    inner = read(directory / 'trace-build/build-RESULT.json')
    assert build['command_success'] and build['preservation_verified'] and build['error'] is None
    assert inner['exit'] == 0 and inner['owned_group_absent'] and inner['cleanup_errors'] == [] and inner['error'] is None and inner['stop_reason'] is None
    assert build['binaries'] == read(phase / 'BINARY-PINS.json')
    assert build['native_sources'] == {name:role['candidate_sha256'] for name,role in roles.items()}
    assert read(directory / 'trace-build/TRACE-SOURCE-ROLE.json') == {'source_role':'instrumented-original','build_revision':policy['head'],'overlay':build['native_sources'],'context_sources':policy['source_context_pins']}
    assert read(phase / 'PRE.json') == read(phase / 'POST.json') == build['snapshot']
    assert read(directory / 'PHASES-PRE.json') == read(directory / 'PHASES-POST.json') == build['snapshot']
    assert outer['phases']['feedback'] == {'assessment_sha256':sha(phase / 'ASSESSMENT.json'),'raw_sha256':sha(phase / 'raw.jsonl'),'result_sha256':sha(phase / 'RESULT.json')}
    assert outer['phases']['calibrated_acquisition'] is True
    assert outer['phases']['trace_index_sha256'] == sha(directory / 'TRACE-INDEX.json')
    assert outer['phases']['record_index_sha256'] == sha(directory / 'FEEDBACK-RECORDS.json')
    records = load('trace_original_records',source_dir / 'phases.py').feedback_records(root,directory,source)
    assert records == read(directory / 'FEEDBACK-RECORDS.json') and records['calibrated_acquisition'] is True
    trace = load('trace_original_parser_adapter',source_dir / 'trace.py').capture(phase)
    assert trace == read(directory / 'TRACE-INDEX.json') and trace['trace_syntax_and_sequence_valid']
    diagnostics = read(directory / 'DIAGNOSTICS.json')
    assert diagnostics['phase_error'] is None and diagnostics['collection_errors'] == []
    return observed


def replay_all(root, policy):
    ownership = load('trace_ownership',root / policy['ownership_helper'])
    capsule = policy['baseline_capsule']
    ownership.authenticate(root / capsule['directory'],capsule['sha256'])
    binding = policy['baseline_binding']
    assert binding is not None
    ownership.authenticate(root / binding['directory'],binding['manifest_sha256'])
    here = Path(__file__).resolve().parent
    assessor = load('trace_strict_assessor',here / 'assess.py')
    checks = load('trace_lifecycle_checks',root / policy['wpt']['checks_helper'])
    return replay_original(root,policy,assessor,checks)
