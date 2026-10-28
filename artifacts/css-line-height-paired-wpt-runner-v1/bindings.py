import json
from pathlib import Path


def inventory(runtime, h):
    files = {str(p.relative_to(runtime)): h.sha(p) for p in runtime.rglob('*')
             if p.is_file() and not p.is_symlink() and 'tools' not in p.relative_to(runtime).parts}
    links = {str(p.relative_to(runtime)): str(p.readlink()) for p in runtime.rglob('*') if p.is_symlink()}
    return files, links


def bind_policy(root, here, fixed, epoch, epoch_sha, phase, h):
    marker = epoch['reversible_line_height_phase']
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
    q['build_epoch_sha256'] = epoch_sha
    q['build_result_sha256'] = h.sha(root / q['build_result'])
    q['build_evidence'] = {str(build / name): h.sha(root / build / name)
                           for name in ('EPOCH.json', 'RESULT.json', 'build-RESULT.json', 'COMMAND.json')}
    q['phase_binaries'] = {name: epoch['pins'][name] for name in q['normal_binaries']}
    if role == 'candidate':
        runtime = root / owner / 'original-wpt'
        files, links = inventory(runtime, h)
        q['original_binding'] = {'capsule': str(here.relative_to(root)),
                                 'capsule_sha256': h.sha(here / 'FILES.json'),
                                 'runtime': str(runtime.relative_to(root)), 'files': files, 'symlinks': links}
    return q


def validate_phase(root, here, policy, epoch, h):
    h.need(h.sha(root / policy['build_epoch']) == policy['epoch_sha256'], 'saved phase-local build epoch')
    h.need(h.read(root / policy['build_epoch']) == epoch, 'build/observation epoch equality')
    h.need(epoch['semantic_index']['head'] == policy['frozen_head'], 'frozen HEAD')
    role = policy['phase'].split('-', 1)[0]
    marker = epoch['reversible_line_height_phase']
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
        h.need(policy['phase'] == 'original-1', 'original phase')
        return None
    h.need(policy['phase'] == 'candidate-1', 'paired candidate phase')
    h.need(binding['capsule'] == str(here.relative_to(root)) and
           binding['capsule_sha256'] == h.sha(here / 'FILES.json'), 'same immutable capsule')
    runtime = root / binding['runtime']
    files, links = inventory(runtime, h)
    h.need(files == binding['files'] and links == binding['symlinks'], 'original runtime inventory')
    original_policy = h.read(runtime / 'POLICY.json')
    fixed = h.read(here / 'POLICY.json')
    h.need(all(original_policy.get(k) == v for k, v in fixed.items()), 'original fixed experiment')
    h.need(original_policy['phase'] == 'original-1' and original_policy['original_binding'] is None and
           original_policy['owner_runtime'] == policy['owner_runtime'], 'original owner/role')
    original_epoch = h.read(runtime / 'EPOCH.json')
    h.need(h.sha(runtime / 'EPOCH.json') == original_policy['epoch_sha256'], 'original epoch digest')
    validate_phase(root, here, original_policy, original_epoch, h)
    result, saved = h.read(runtime / 'RESULT.json'), h.read(runtime / 'ASSESSMENT.json')
    h.need(result['observation_gate_passed'] is True and result['execution_error'] is None and
           result['preservation_error'] is None and saved['complete'] is True and saved['execution_preserved'] is True,
           'completed preserved original')
    h.need(saved['capsule_manifest_sha256'] == binding['capsule_sha256'] and
           saved['epoch_sha256'] == original_policy['epoch_sha256'] and
           saved['native_sources'] == policy['source_roles']['original'], 'original provenance')
    h.need(h.read(runtime / 'PRE.json') == h.read(runtime / 'POST.json'), 'original preservation')
    metadata = h.read(runtime / 'APPLICATION-METADATA.json')
    h.need(metadata == h.read(runtime / 'APPLICATION-METADATA-POST.json'), 'original metadata')
    cleanup = h.read(runtime / 'CLEANUP.json')
    h.need(cleanup['owned_group_absent'] and cleanup['temporary_root_removed'], 'original cleanup')
    current = h.read(root / policy['build_epoch'])
    allowed = {'servo/components/style/values/specified/font.rs'} | set(policy['rebuilt_binaries'])
    stable = lambda e: {n: v for n, v in e['pins'].items() if n not in allowed}
    h.need(stable(current) == stable(original_epoch), 'unrelated phase inputs changed')
    for name in ('staged_working', 'nested_semantic_index', 'untracked_native', 'installed_identities',
                 'committed_research_working_payloads'):
        h.need(current[name] == original_epoch[name], 'paired preserved ' + name)
    for name in ('head', 'entries', 'cached_diff'):
        h.need(current['semantic_index'][name] == original_epoch['semantic_index'][name], 'paired index ' + name)
    h.need(set(current['modified_native_paths']) == set(original_epoch['modified_native_paths']) | {'servo/components/style/values/specified/font.rs'}, 'font-only changed native scope')
    parser = h.load('line_height_original_assessor', here / 'assess.py')
    checks = h.load('line_height_original_checks', root / policy['helpers']['checks'])
    events = [json.loads(line) for line in (runtime / 'raw.jsonl').read_text().splitlines()]
    replay = parser.assess(events, result['exit'], original_policy, checks, run_binding=metadata)
    replay = json.loads(json.dumps(replay))
    h.need(all(saved.get(k) == v for k, v in replay.items()), 'original raw replay')
    h.need(saved['run_binding']['revision'] == policy['frozen_head'], 'original frozen revision')
    return saved
