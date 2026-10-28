import copy
import hashlib
import json
import os
from pathlib import Path

SOURCE = 'servo/components/style/values/specified/easing.rs'

def old_bindings_inventory(runtime, h):
    files = {str(p.relative_to(runtime)): h.sha(p) for p in runtime.rglob('*') if p.is_file() and not p.is_symlink()}
    links = {str(p.relative_to(runtime)): str(p.readlink()) for p in runtime.rglob('*') if p.is_symlink()}
    return files, links



def bind_policy(root, here, fixed, epoch, epoch_sha, phase, h):
    h.need(phase == 'candidate-1' and epoch_sha == fixed['epoch_sha256'], 'fixed final candidate epoch')
    build = fixed['build_directory']
    h.need(build == fixed['owner_runtime'] + '/candidate-build-1', 'promotion build directory')
    h.need((root / fixed['owner_runtime']).resolve() == root / fixed['owner_runtime'], 'regular promotion runtime')
    q = dict(fixed, phase=phase, build_epoch=build + '/EPOCH.json',
             build_result=build + '/RESULT.json', inner_build_result=build + '/build-RESULT.json')
    q['phase_binaries'] = {name: epoch['pins'][name] for name in q['normal_binaries']}
    q['original_binding'] = {'capsule': q['pair_capsule'], 'capsule_sha256': q['pair_capsule_sha256'],
                             'runtime': q['paired_runtime'],
                             'runtime_manifest_sha256': q['paired_manifest_sha256'],
                             'provenance': 'authenticated separate original baseline and target CRASH; not a fresh final-capsule run'}
    return q


def project_promotion(epoch, baseline, policy, ownership, h):
    tests = policy['installed_tests']
    h.need(set(ownership) == {SOURCE} | set(tests), 'exact installed ownership roster')
    h.need(ownership[SOURCE]['identity'] == policy['original_source_identity'], 'original easing inode retained')
    marker = epoch['linear_guard_transition']
    h.need(marker == {'role': 'candidate', 'compiled': True, 'accepted': False,
                     'manifest_sha256': policy['promotion_manifest_sha256'],
                     'source_sha256': policy['source_roles']['candidate'][SOURCE],
                     'last_phase': 'candidate-build-1', 'variant': 'linear-both-position-guard'}, 'compiled promotion marker')
    h.need(epoch['staged_working'] == baseline['staged_working'] == {}, 'empty staging')
    h.need(epoch['modified_native_paths'] == sorted(baseline['modified_native_paths'] + [SOURCE]), 'only easing source added')
    allowed_pins = {SOURCE} | set(tests) | set(policy['rebuilt_binaries'])
    h.need(set(epoch['pins']) == set(baseline['pins']) | {SOURCE} | set(tests), 'exact new pin roster')
    h.need(set(epoch['installed_identities']) == set(baseline['installed_identities']) | {SOURCE} | set(tests), 'exact new identity roster')
    for name, digest in {SOURCE: policy['source_roles']['candidate'][SOURCE], **tests}.items():
        claim = ownership[name]
        h.need(claim['path'] == name and claim['owned_sha256'] == digest and
               epoch['pins'][name] == digest and epoch['installed_identities'][name] == claim['identity'], 'installed source/test ownership: ' + name)
    h.need(epoch['counts'] == dict(baseline['counts'], roles=len(epoch['pins']),
           installed_identities=len(epoch['installed_identities']), native_modified_paths=len(epoch['modified_native_paths'])), 'exact promotion counts')
    normalized = copy.deepcopy(epoch)
    del normalized['linear_guard_transition']
    for name in allowed_pins:
        if name in baseline['pins']:
            normalized['pins'][name] = baseline['pins'][name]
        else:
            del normalized['pins'][name]
    for name in {SOURCE} | set(tests):
        if name in baseline['installed_identities']:
            h.need(normalized['installed_identities'][name] == baseline['installed_identities'][name], 'existing source identity')
        else:
            del normalized['installed_identities'][name]
    normalized['counts'] = baseline['counts']
    normalized['modified_native_paths'] = baseline['modified_native_paths']
    normalized['semantic_index']['working_diff'] = baseline['semantic_index']['working_diff']
    normalized['raw_index_observation']['current'] = baseline['raw_index_observation']['current']
    h.need(normalized == baseline, 'unrelated promotion context changed')


def validate_saved_phase(root, here, policy, epoch, h):
    h.authenticate(root / policy['promotion_capsule'], policy['promotion_manifest_sha256'])
    controls = policy['runtime_control_pins']
    h.need(set(controls) == {'artifacts/css-registered-number-native-runtime-v1/' + n for n in ('CURRENT-EPOCH.json', 'ROLE.json', 'OWNED.json')}, 'exact runtime control roster')
    for name, digest in controls.items():
        h.need(h.sha(root / name) == digest, 'runtime control: ' + name)
    h.need(controls['artifacts/css-registered-number-native-runtime-v1/CURRENT-EPOCH.json'] == policy['epoch_sha256'], 'canonical compiled epoch')
    for name, digest in policy['build_evidence'].items():
        h.need(h.sha(root / name) == digest, 'promotion evidence: ' + name)
    mandatory = {policy['build_directory'] + '/' + n for n in
                 ('EPOCH.json', 'RESULT.json', 'build-RESULT.json', 'COMMAND.json', 'APPLICATION-METADATA.json')}
    mandatory |= {policy['owner_runtime'] + '/' + n for n in ('OWNERSHIP.json', 'INSTALL-RESULT.json', 'INSTALLED-EPOCH.json')}
    h.need(mandatory <= set(policy['build_evidence']), 'complete saved promotion evidence')
    h.need(h.sha(root / policy['build_epoch']) == policy['build_epoch_sha256'], 'exact historical build epoch')
    built = h.read(root / policy['build_epoch'])
    h.need(h.sha(here / 'PROMOTION-BASELINE-EPOCH.json') == policy['promotion_baseline_sha256'], 'promotion baseline digest')
    baseline = h.read(here / 'PROMOTION-BASELINE-EPOCH.json')
    h.need(epoch['semantic_index']['head'] == baseline['semantic_index']['head'] == policy['frozen_head'], 'frozen HEAD')
    ownership = h.read(root / policy['owner_runtime'] / 'OWNERSHIP.json')
    build_policy = dict(policy, installed_tests={'testing/web-platform/tests' + policy['target_rename']['old']: policy['target_rename']['sha256']})
    project_promotion(built, baseline, build_policy, ownership, h)
    relocated_ownership = validate_rename(root, here, policy, epoch, built, ownership, h)
    project_promotion(epoch, baseline, policy, relocated_ownership, h)
    installed = h.read(root / policy['owner_runtime'] / 'INSTALLED-EPOCH.json')
    normalized = copy.deepcopy(built)
    for name in policy['rebuilt_binaries']:
        normalized['pins'][name] = installed['pins'][name]
    normalized['raw_index_observation']['current'] = installed['raw_index_observation']['current']
    normalized['linear_guard_transition'] = installed['linear_guard_transition']
    expected_install = dict(built['linear_guard_transition'], compiled=False, last_phase='install')
    del expected_install['variant']
    h.need(installed['linear_guard_transition'] == expected_install and normalized == installed, 'only build binaries/raw/compiled marker changed')
    result = h.read(root / policy['build_result'])
    h.need(result['command_success'] is True and result['preservation_verified'] is True and
           result['source_role'] == 'candidate' and result['browser_build_performed'] is True and
           result['accepted'] is False and result['error'] is None and not result['owned_processes'] and
           not result['publication_errors'], 'successful preserved promotion build')
    inner = h.read(root / policy['inner_build_result'])
    h.need(inner['exit'] == 0 and inner['error'] is None and inner['stop_reason'] is None and
           not inner['cleanup_errors'] and inner['owned_group_absent'] is True, 'inner build exit/cleanup')
    install = h.read(root / policy['owner_runtime'] / 'INSTALL-RESULT.json')
    h.need(install['installed'] and install['preservation_verified'] and install['held_provider_preserved'] and
           not install['accepted'] and not install['compiled'] and
           set(install['files']) == {SOURCE} | set(build_policy['installed_tests']), 'preserved exact installation')
    h.need(install['epoch_sha256'] == h.sha(root / policy['owner_runtime'] / 'INSTALLED-EPOCH.json'), 'installed epoch join')
    return {'role': 'candidate', 'build_evidence': policy['build_evidence'], 'marker': epoch['linear_guard_transition'],
            'native_sources': policy['source_roles']['candidate'], 'binaries': policy['phase_binaries']}


def validate_phase(root, here, policy, epoch, h):
    result = validate_saved_phase(root, here, policy, epoch, h)
    baseline = h.read(here / 'PROMOTION-BASELINE-EPOCH.json')
    h.need(not os.path.lexists(root / ('testing/web-platform/tests' + policy['target_rename']['old'])), 'old target path remains absent')
    helper = h.load('promotion_working_diff', root / policy['helpers']['preservation'])
    env = dict(os.environ, GIT_OPTIONAL_LOCKS='0')
    h.need(hashlib.sha256(helper.git(root, env, 'diff', '--binary', '--', '.', ':(exclude)' + SOURCE)).hexdigest() ==
           baseline['semantic_index']['working_diff'], 'easing-only live working delta')
    h.need(sorted(helper.git(root, env, 'diff', '--name-only').decode().splitlines()) == epoch['modified_native_paths'], 'exact live native paths')
    metadata = h.application_metadata(root / policy['application_ini'], policy['frozen_head'])
    h.need(metadata == h.read(root / policy['build_directory'] / 'APPLICATION-METADATA.json'), 'actual compiled application metadata')
    return result


def validate_original(root, here, policy, h):
    old = root / policy['pair_capsule']
    pair = root / policy['paired_runtime']
    h.authenticate(old, policy['pair_capsule_sha256'])
    h.authenticate(pair, policy['paired_manifest_sha256'])
    manifest = h.read(pair / 'FILES.json')
    files, links = old_bindings_inventory(pair, h)
    h.need(files == {**{n: v['sha256'] for n, v in manifest.items()},
                     'FILES.json': policy['paired_manifest_sha256']}, 'exact paired regular inventory')
    expected_links = {label + '/tests/tools': str(root / 'testing/web-platform/tests/tools')
                      for label in ('original-baseline-wpt', 'original-crash-wpt', 'candidate-wpt')}
    h.need(links == h.read(pair / 'SYMLINKS.json') == expected_links, 'exact three paired tools links')
    result = h.read(pair / 'RESULT.json')
    h.need(result['success'] and result['restoration_verified'] and result['runtime_controls_unchanged'] and
           result['empty_staging_preserved'] and result['backups_removed_after_verification'] and
           result['error'] is None and result['publication_errors'] == [], 'successful restored pair')
    h.need(h.read(pair / 'ROOT-TERMINAL.json')['exit'] == 0, 'paired outer terminal')
    validate_renamed_inputs(root, here, policy, h)
    old_run = h.load('linear_historical_runner', old / 'run.py')
    old_bindings = h.load('linear_historical_bindings', old / 'bindings.py')
    candidate = pair / 'candidate-wpt'
    candidate_policy = h.read(candidate / 'POLICY.json')
    original = old_bindings.validate_original(root, old, candidate_policy, old_run)
    old_bindings.validate_phase(root, old, candidate_policy, h.read(candidate / 'EPOCH.json'), old_run)
    baseline = h.read(here / 'PROMOTION-BASELINE-EPOCH.json')
    canonical = h.read(pair / 'PRE-CURRENT-EPOCH.json')
    normalized = copy.deepcopy(baseline)
    normalized['raw_index_observation']['current'] = canonical['raw_index_observation']['current']
    h.need(normalized == canonical, 'promotion baseline differs only by authenticated raw observation')
    original_epoch = h.read(pair / 'original-baseline-wpt/EPOCH.json')
    h.need(original_epoch['installed_identities'][SOURCE] == policy['original_source_identity'], 'original source identity')
    normalized = copy.deepcopy(original_epoch)
    marker = normalized.pop('reversible_linear_guard_phase')
    h.need(marker['role'] == 'original' and marker['source_package_manifest'] == policy['source_package_manifest'] and
           marker['owner_runtime'] == policy['paired_runtime'], 'historical original marker')
    h.need(normalized['pins'][SOURCE] == policy['source_roles']['original'][SOURCE], 'historical original source')
    for name in policy['rebuilt_binaries']:
        normalized['pins'][name] = canonical['pins'][name]
    normalized['raw_index_observation']['current'] = canonical['raw_index_observation']['current']
    for field in ('pins', 'installed_identities'):
        if SOURCE in canonical[field]:
            h.need(normalized[field][SOURCE] == canonical[field][SOURCE], 'existing source field: ' + field)
        else:
            del normalized[field][SOURCE]
    normalized['counts']['roles'] = len(normalized['pins'])
    normalized['counts']['installed_identities'] = len(normalized['installed_identities'])
    h.need(normalized == canonical, 'historical original context/source projection')
    parser = h.load('linear_historical_assessor', old / 'assess.py')
    checks = h.load('linear_historical_checks', root / policy['helpers']['checks'])
    events = [json.loads(line) for line in (candidate / 'raw.jsonl').read_text().splitlines()]
    saved = h.read(candidate / 'ASSESSMENT.json')
    child_result = h.read(candidate / 'RESULT.json')
    h.need(child_result['phase_gate_passed'] and child_result['comparison_gate_passed'] and
           child_result['execution_error'] is None and child_result['preservation_error'] is None and
           saved['execution_preserved'], 'paired candidate preservation/gate')
    h.need(h.read(candidate / 'PRE.json') == h.read(candidate / 'POST.json'), 'paired candidate state')
    metadata = h.read(candidate / 'APPLICATION-METADATA.json')
    h.need(metadata == h.read(candidate / 'APPLICATION-METADATA-POST.json'), 'paired candidate metadata')
    cleanup = h.read(candidate / 'CLEANUP.json')
    h.need(cleanup['owned_group_absent'] and cleanup['temporary_root_removed'], 'paired candidate cleanup')
    replay = parser.assess(events, child_result['exit'], candidate_policy, checks, original=original, run_binding=metadata)
    replay = old_run.augment_assessment(replay, phase='candidate-1', capsule_sha=policy['pair_capsule_sha256'],
        epoch_sha=candidate_policy['epoch_sha256'], policy=candidate_policy, capsule_directory=policy['pair_capsule'],
        experiment_sha=h.sha(old / 'EXPERIMENT.json'), execution_preserved=True)
    h.need(json.loads(json.dumps(replay)) == saved, 'complete paired candidate publication replay')
    h.need(saved['complete'] and saved['comparison_gate_passed'], 'complete passing paired candidate comparison')
    return original


def validate_final_assessment(root, here, policy, assessment, h):
    h.need(assessment['complete'] and assessment['comparison_gate_passed'], 'final complete comparison')
    parser = h.load('linear_final_signature', here / 'assess.py')
    prior = h.read(root / policy['paired_runtime'] / 'candidate-wpt/ASSESSMENT.json')
    signature = lambda a: sorted([parser.signature(e) for e in a['rows'] + a['ends']],
                                key=lambda e: (e['test'], e['kind'], e['subtest'] or ''))
    expected = signature(prior)
    rename = policy['target_rename']
    mapped = 0
    for event in expected:
        if event['test'] == rename['old']:
            event['test'] = rename['new']
            mapped += 1
    h.need(mapped == 7, 'exact six paired target rows plus one ending renamed')
    expected.sort(key=lambda e: (e['test'], e['kind'], e['subtest'] or ''))
    h.need(signature(assessment) == expected, 'final signatures equal paired candidate after exact target identity rename')


def validate_renamed_inputs(root, here, policy, h):
    old = root / policy['pair_capsule']
    rename = policy['target_rename']
    h.need(rename == {'old': '/css/css-easing/linear-contextual-second-position-crash.html',
                      'new': '/css/css-easing/linear-contextual-second-position.html',
                      'sha256': 'efd06917742f977112c20ace787c0fa02f3701e00639760d77ded4fe35f034b8'}, 'exact rename scope')
    before, after = rename['old'], rename['new']
    def renamed_keys(value):
        if isinstance(value, dict):
            return {(after if k == before else k): renamed_keys(v) for k, v in value.items()}
        if isinstance(value, list):
            return [renamed_keys(v) for v in value]
        return value
    fixed = h.read(old / 'POLICY.json')
    current = h.read(here / 'POLICY.json')
    for key in ('tests', 'phase_tests', 'target_subtests', 'calibration_subtests', 'regression_subtests',
                'source_roles', 'rebuilt_binaries', 'source_package_manifest', 'frozen_head'):
        h.need(current[key] == renamed_keys(fixed[key]), 'exact historical roster/source rename: ' + key)
    h.need((here / 'assess.py').read_bytes() == (old / 'assess.py').read_bytes(), 'unchanged assessor')
    h.need(h.read(here / 'EXPERIMENT.json') == renamed_keys(h.read(old / 'EXPERIMENT.json')), 'experiment rename only')
    pins = h.read(old / 'SOURCE-PINS.json')
    expected = {}
    for name, record in pins.items():
        updated = dict(record, capture=record['capture'].replace(before, after))
        if record['origin'] == name:
            updated['origin'] = name.replace(before, after)
        expected[name.replace(before, after)] = updated
        if record['exists']:
            h.need((old / record['capture']).read_bytes() == (here / updated['capture']).read_bytes(), 'unchanged captured body: ' + name)
    h.need(h.read(here / 'SOURCE-PINS.json') == expected, 'only target path and adjacent absent metadata renamed')
    target = expected['testing/web-platform/tests' + after]
    h.need(target['sha256'] == rename['sha256'] and h.sha(here / target['capture']) == rename['sha256'], 'exact target body')
    manifest = copy.deepcopy(h.read(old / 'SUBSET-MANIFEST.json'))
    entries = manifest['items']['testharness']['css']['css-easing']
    entries[Path(after).name] = entries.pop(Path(before).name)
    h.need(h.read(here / 'SUBSET-MANIFEST.json') == manifest, 'genuine final manifest differs by exact filename only')


def validate_rename(root, here, policy, epoch, built, ownership, h):
    h.authenticate(root / policy['rename_capsule'], policy['rename_manifest_sha256'])
    directory = root / policy['rename_runtime']
    mandatory = {str((directory / n).relative_to(root)) for n in ('EPOCH.json', 'OWNERSHIP.json', 'RESULT.json', 'POST.json', 'PRE-CURRENT-EPOCH.json', 'PRE-OWNED.json', 'PRE-ROLE.json')}
    h.need(mandatory <= set(policy['rename_evidence']), 'complete rename evidence')
    for name, digest in policy['rename_evidence'].items():
        h.need(h.sha(root / name) == digest, 'rename evidence: ' + name)
    h.need(h.read(directory / 'EPOCH.json') == epoch and h.sha(directory / 'EPOCH.json') == policy['epoch_sha256'], 'actual post-rename epoch')
    h.need(h.read(directory / 'PRE-CURRENT-EPOCH.json') == built and
           h.sha(directory / 'PRE-CURRENT-EPOCH.json') == policy['build_epoch_sha256'], 'rename starts from actual build epoch')
    old = 'testing/web-platform/tests' + policy['target_rename']['old']
    new = 'testing/web-platform/tests' + policy['target_rename']['new']
    expected = copy.deepcopy(built)
    for field in ('pins', 'installed_identities'):
        h.need(old in expected[field] and new not in expected[field], 'rename original field: ' + field)
        expected[field][new] = expected[field].pop(old)
    expected['raw_index_observation']['current'] = epoch['raw_index_observation']['current']
    h.need(epoch == expected, 'only target pin/identity keys and raw observation changed after build')
    claim = dict(ownership[old], path=new)
    h.need(h.read(directory / 'OWNERSHIP.json') == {new: claim}, 'same test bytes/inode relocated')
    owners = h.read(directory / 'PRE-OWNED.json')
    h.need(owners[old] == ownership[old] and new not in owners, 'original owned test claim')
    owners[new] = dict(owners.pop(old), path=new)
    runtime = root / 'artifacts/css-registered-number-native-runtime-v1'
    h.need(h.read(runtime / 'OWNED.json') == owners, 'only owned test path changed')
    h.need((directory / 'PRE-ROLE.json').read_bytes() == (runtime / 'ROLE.json').read_bytes(), 'role unchanged by rename')
    result = h.read(directory / 'RESULT.json')
    h.need(result['renamed'] and result['body_and_inode_preserved'] and result['native_and_binaries_unchanged'] and
           result['preservation_verified'] and result['accepted'] is False and result['old_path'] == old and result['new_path'] == new and
           result['build_epoch_sha256'] == policy['build_epoch_sha256'] and result['epoch_sha256'] == policy['epoch_sha256'], 'preserved rename result')
    h.need(result['raw_observation_changed'] == (built['raw_index_observation']['current'] != epoch['raw_index_observation']['current']), 'exact raw rename observation')
    return {SOURCE: ownership[SOURCE], new: claim}
