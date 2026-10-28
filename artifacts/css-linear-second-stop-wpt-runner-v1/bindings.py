import json
from pathlib import Path


def inventory(runtime, h):
    files = {str(p.relative_to(runtime)): h.sha(p) for p in runtime.rglob('*')
             if p.is_file() and not p.is_symlink() and 'tools' not in p.relative_to(runtime).parts}
    links = {str(p.relative_to(runtime)): str(p.readlink()) for p in runtime.rglob('*') if p.is_symlink()}
    return files, links


def bind_policy(root, here, fixed, epoch, epoch_sha, phase, h):
    marker = epoch['reversible_linear_guard_phase']
    role = phase.split('-', 1)[0]
    h.need(set(marker) == {'role', 'build_directory', 'source_package_manifest', 'owner_runtime'}, 'phase marker fields')
    h.need(marker['role'] == role and marker['source_package_manifest'] == fixed['source_package_manifest'], 'phase source role')
    owner = Path(marker['owner_runtime'])
    h.need(str(owner) == fixed['owner_runtime'], 'owned runtime path')
    h.need(not (root / owner).is_symlink() and (root / owner).resolve() == root / owner, 'owned runtime regular directory')
    build = owner / (role + '-build')
    h.need(marker['build_directory'] == str(build), 'exact role build directory')
    q = dict(fixed, phase=phase, epoch_sha256=epoch_sha, owner_runtime=str(owner),
             build_epoch=str(build / 'EPOCH.json'), build_result=str(build / 'RESULT.json'),
             inner_build_result=str(build / 'build-RESULT.json'), original_binding=None)
    q['tests'] = fixed['phase_tests'][phase]
    q['build_epoch_sha256'] = epoch_sha
    q['build_result_sha256'] = h.sha(root / q['build_result'])
    q['build_evidence'] = {str(build / name): h.sha(root / build / name)
                           for name in ('EPOCH.json', 'RESULT.json', 'build-RESULT.json', 'COMMAND.json')}
    q['phase_binaries'] = {name: epoch['pins'][name] for name in q['normal_binaries']}
    if role == 'candidate':
        captures = {}
        for label in ('original-baseline', 'original-crash'):
            runtime = root / owner / (label + '-wpt')
            files, links = inventory(runtime, h)
            captures[label] = {'runtime': str(runtime.relative_to(root)), 'files': files, 'symlinks': links}
        q['original_binding'] = {'capsule': str(here.relative_to(root)),
                                 'capsule_sha256': h.sha(here / 'FILES.json'), 'captures': captures}
    return q


def validate_phase(root, here, policy, epoch, h):
    h.need(h.sha(root / policy['build_epoch']) == policy['epoch_sha256'], 'saved phase-local build epoch')
    h.need(h.read(root / policy['build_epoch']) == epoch, 'build/observation epoch equality')
    h.need(epoch['semantic_index']['head'] == policy['frozen_head'], 'frozen HEAD')
    role = policy['phase'].split('-', 1)[0]
    baseline = h.read(here / 'SIGNING-BASELINE-EPOCH.json')
    h.need(baseline['semantic_index']['head'] == policy['frozen_head'], 'signed baseline HEAD')
    h.need(epoch['staged_working'] == baseline['staged_working'] == {}, 'clean signing state')
    sources = set(policy['source_roles'][role])
    allowed = sources | set(policy['rebuilt_binaries'])
    normalized = json.loads(json.dumps(epoch))
    normalized.pop('reversible_linear_guard_phase')
    h.need(set(epoch['pins']) == set(baseline['pins']) | sources, 'exact phase source pin roster')
    h.need(set(epoch['installed_identities']) == set(baseline['installed_identities']) | sources, 'exact phase identity roster')
    for name in allowed:
        if name in baseline['pins']:
            normalized['pins'][name] = baseline['pins'][name]
        else:
            del normalized['pins'][name]
    for name in sources:
        if name in baseline['installed_identities']:
            h.need(normalized['installed_identities'][name] == baseline['installed_identities'][name], 'existing source identity')
        else:
            del normalized['installed_identities'][name]
    expected_native = set(baseline['modified_native_paths']) | (sources if role == 'candidate' else set())
    h.need(set(epoch['modified_native_paths']) == expected_native, 'one-source phase scope')
    h.need(epoch['counts'] == dict(baseline['counts'], roles=len(epoch['pins']), installed_identities=len(epoch['installed_identities']), native_modified_paths=len(expected_native)), 'exact local phase counts')
    normalized['modified_native_paths'] = baseline['modified_native_paths']
    normalized['counts'] = baseline['counts']
    normalized['raw_index_observation']['current'] = baseline['raw_index_observation']['current']
    if role == 'original':
        h.need(epoch['semantic_index']['working_diff'] == baseline['semantic_index']['working_diff'], 'original working diff')
    normalized['semantic_index']['working_diff'] = baseline['semantic_index']['working_diff']
    h.need(normalized == baseline, 'unrelated signed context or accepted source changed')
    marker = epoch['reversible_linear_guard_phase']
    h.need(marker['role'] == role and marker['source_package_manifest'] == policy['source_package_manifest'], 'phase marker')
    for name, digest in policy['build_evidence'].items():
        h.need(h.sha(root / name) == digest, 'build evidence: ' + name)
    result = h.read(root / policy['build_result'])
    h.need(result['command_success'] is True and result['preservation_verified'] is True and
           result['source_role'] == role and result['browser_build_performed'] is True and result['error'] is None and not result['owned_processes'], 'successful preserved build')
    h.need(not result.get('publication_errors', []), 'build publication errors')
    inner = h.read(root / policy['inner_build_result'])
    h.need(inner['exit'] == 0 and inner['error'] is None and inner['stop_reason'] is None and
           not inner['cleanup_errors'] and inner['owned_group_absent'] is True, 'inner build exit/cleanup')
    for name, digest in dict(policy['source_roles'][role], **policy['phase_binaries']).items():
        h.need(epoch['pins'].get(name) == digest, 'compiled source/binary: ' + name)
    h.need(set(policy['normal_binaries']) == set(policy['phase_binaries']), 'binary roster')
    h.need(role == 'original' or bool(policy['original_binding']), 'candidate original binding')
    return {'role': role, 'build_evidence': policy['build_evidence'], 'marker': marker,
            'native_sources': policy['source_roles'][role], 'binaries': policy['phase_binaries']}


def validate_original(root, here, policy, h):
    binding = policy['original_binding']
    if binding is None:
        h.need(policy['phase'] in ('original-baseline-1', 'original-crash-1'), 'original phase')
        return None
    h.need(policy['phase'] == 'candidate-1', 'paired candidate phase')
    h.need(binding['capsule'] == str(here.relative_to(root)) and
           binding['capsule_sha256'] == h.sha(here / 'FILES.json'), 'same immutable capsule')
    h.need(set(binding['captures']) == {'original-baseline', 'original-crash'}, 'two original phases')
    parser = h.load('linear_original_assessor', here / 'assess.py')
    checks = h.load('linear_original_checks', root / policy['helpers']['checks'])
    publisher = h.load('linear_original_publisher', here / 'run.py')
    fixed = h.read(here / 'POLICY.json')
    current = h.read(root / policy['build_epoch'])
    results = {}
    for label, capture in binding['captures'].items():
        runtime = root / capture['runtime']
        h.need(runtime == root / policy['owner_runtime'] / (label + '-wpt'), 'exact original output')
        files, links = inventory(runtime, h)
        h.need(files == capture['files'] and links == capture['symlinks'], 'original runtime inventory')
        original_policy = h.read(runtime / 'POLICY.json')
        h.need(all(original_policy.get(k) == v for k, v in fixed.items() if k != 'tests'), 'original fixed experiment')
        h.need(original_policy['tests'] == fixed['phase_tests'][label + '-1'], 'original test selection')
        h.need(original_policy['phase'] == label + '-1' and original_policy['original_binding'] is None and
               original_policy['owner_runtime'] == policy['owner_runtime'], 'original owner/role')
        original_epoch = h.read(runtime / 'EPOCH.json')
        h.need(h.sha(runtime / 'EPOCH.json') == original_policy['epoch_sha256'], 'original epoch digest')
        validate_phase(root, here, original_policy, original_epoch, h)
        result, saved = h.read(runtime / 'RESULT.json'), h.read(runtime / 'ASSESSMENT.json')
        h.need(result['phase_gate_passed'] is True and result['execution_error'] is None and
               result['preservation_error'] is None and saved['phase_gate_passed'] is True and
               saved['execution_preserved'] is True, 'preserved original phase gate')
        h.need(saved['complete'] == (label == 'original-baseline'), 'original completion scope')
        h.need(saved['capsule_manifest_sha256'] == binding['capsule_sha256'] and
               saved['epoch_sha256'] == original_policy['epoch_sha256'] and
               saved['native_sources'] == policy['source_roles']['original'], 'original provenance')
        h.need(h.read(runtime / 'PRE.json') == h.read(runtime / 'POST.json'), 'original preservation')
        metadata = h.read(runtime / 'APPLICATION-METADATA.json')
        h.need(metadata == h.read(runtime / 'APPLICATION-METADATA-POST.json'), 'original metadata')
        cleanup = h.read(runtime / 'CLEANUP.json')
        h.need(cleanup['owned_group_absent'] and cleanup['temporary_root_removed'], 'original cleanup')
        allowed = set(policy['source_roles']['original']) | set(policy['rebuilt_binaries'])
        stable = lambda e: {n: v for n, v in e['pins'].items() if n not in allowed}
        h.need(stable(current) == stable(original_epoch), 'unrelated phase inputs changed')
        for name in ('staged_working', 'nested_semantic_index', 'untracked_native', 'installed_identities', 'committed_research_working_payloads'):
            h.need(current[name] == original_epoch[name], 'paired preserved ' + name)
        for name in ('head', 'entries', 'cached_diff'):
            h.need(current['semantic_index'][name] == original_epoch['semantic_index'][name], 'paired index ' + name)
        h.need(set(current['modified_native_paths']) == set(original_epoch['modified_native_paths']) | set(policy['source_roles']['candidate']), 'one-source changed scope')
        events = [json.loads(line) for line in (runtime / 'raw.jsonl').read_text().splitlines()]
        replay = parser.assess(events, result['exit'], original_policy, checks, run_binding=metadata)
        replay = publisher.augment_assessment(replay, phase=label + '-1', capsule_sha=binding['capsule_sha256'],
            epoch_sha=original_policy['epoch_sha256'], policy=original_policy,
            capsule_directory=binding['capsule'], experiment_sha=h.sha(here / 'EXPERIMENT.json'), execution_preserved=True)
        h.need(json.loads(json.dumps(replay)) == saved, 'full original raw/publication replay')
        results['baseline' if label == 'original-baseline' else 'crash'] = saved
    h.need(results['baseline']['run_binding'] == results['crash']['run_binding'], 'one original binary metadata')
    return results

