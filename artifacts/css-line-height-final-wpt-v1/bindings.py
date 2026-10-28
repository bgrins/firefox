import copy
import hashlib
import json
import os
from pathlib import Path

FONT = 'servo/components/style/values/specified/font.rs'

def old_bindings_inventory(runtime, h):
    files = {str(p.relative_to(runtime)): h.sha(p) for p in runtime.rglob('*') if p.is_file() and not p.is_symlink() and 'tools' not in p.relative_to(runtime).parts}
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
                             'runtime': q['paired_runtime'] + '/original-wpt',
                             'runtime_manifest_sha256': q['paired_manifest_sha256'],
                             'provenance': 'authenticated original reversible experiment; not a fresh final-capsule run'}
    return q


def project_promotion(epoch, baseline, policy, ownership, h):
    tests = policy['live_oracle_sources']
    h.need(set(ownership) == {FONT} | set(tests), 'exact installed ownership roster')
    h.need(ownership[FONT]['identity'] == policy['original_font_identity'], 'original font inode retained')
    marker = epoch['line_height_transition']
    h.need(marker == {'role': 'candidate', 'compiled': True, 'accepted': False,
                     'manifest_sha256': policy['promotion_manifest_sha256'],
                     'source_sha256': policy['source_roles']['candidate'][FONT],
                     'last_phase': 'candidate-build-1', 'variant': 'line-height-contextual-leaves'}, 'compiled promotion marker')
    h.need(epoch['staged_working'] == baseline['staged_working'] == {}, 'empty staging')
    h.need(epoch['modified_native_paths'] == sorted(baseline['modified_native_paths'] + [FONT]), 'only font source added')
    allowed_pins = {FONT} | set(tests) | set(policy['rebuilt_binaries'])
    h.need(set(epoch['pins']) == set(baseline['pins']) | {FONT} | set(tests), 'exact new pin roster')
    h.need(set(epoch['installed_identities']) == set(baseline['installed_identities']) | {FONT} | set(tests), 'exact new identity roster')
    for name, digest in {FONT: policy['source_roles']['candidate'][FONT], **tests}.items():
        claim = ownership[name]
        h.need(claim['path'] == name and claim['owned_sha256'] == digest and
               epoch['pins'][name] == digest and epoch['installed_identities'][name] == claim['identity'], 'installed source/test ownership: ' + name)
    h.need(epoch['counts'] == dict(baseline['counts'], roles=len(epoch['pins']),
           installed_identities=len(epoch['installed_identities']), native_modified_paths=len(epoch['modified_native_paths'])), 'exact promotion counts')
    normalized = copy.deepcopy(epoch)
    del normalized['line_height_transition']
    for name in allowed_pins:
        if name in baseline['pins']:
            normalized['pins'][name] = baseline['pins'][name]
        else:
            del normalized['pins'][name]
    for name in {FONT} | set(tests):
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
    h.need(h.sha(root / policy['build_epoch']) == policy['epoch_sha256'] and
           h.read(root / policy['build_epoch']) == epoch, 'exact build epoch')
    h.need(h.sha(here / 'PROMOTION-BASELINE-EPOCH.json') == policy['promotion_baseline_sha256'], 'promotion baseline digest')
    baseline = h.read(here / 'PROMOTION-BASELINE-EPOCH.json')
    h.need(epoch['semantic_index']['head'] == baseline['semantic_index']['head'] == policy['frozen_head'], 'frozen HEAD')
    ownership = h.read(root / policy['owner_runtime'] / 'OWNERSHIP.json')
    project_promotion(epoch, baseline, policy, ownership, h)
    installed = h.read(root / policy['owner_runtime'] / 'INSTALLED-EPOCH.json')
    normalized = copy.deepcopy(epoch)
    for name in policy['rebuilt_binaries']:
        normalized['pins'][name] = installed['pins'][name]
    normalized['raw_index_observation']['current'] = installed['raw_index_observation']['current']
    normalized['line_height_transition'] = installed['line_height_transition']
    expected_install = dict(epoch['line_height_transition'], compiled=False, last_phase='install')
    del expected_install['variant']
    h.need(installed['line_height_transition'] == expected_install and normalized == installed, 'only build binaries/raw/compiled marker changed')
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
           set(install['files']) == {FONT} | set(policy['live_oracle_sources']), 'preserved exact installation')
    h.need(install['epoch_sha256'] == h.sha(root / policy['owner_runtime'] / 'INSTALLED-EPOCH.json'), 'installed epoch join')
    return {'role': 'candidate', 'build_evidence': policy['build_evidence'], 'marker': epoch['line_height_transition'],
            'native_sources': policy['source_roles']['candidate'], 'binaries': policy['phase_binaries']}


def validate_phase(root, here, policy, epoch, h):
    result = validate_saved_phase(root, here, policy, epoch, h)
    baseline = h.read(here / 'PROMOTION-BASELINE-EPOCH.json')
    helper = h.load('promotion_working_diff', root / policy['helpers']['preservation'])
    env = dict(os.environ, GIT_OPTIONAL_LOCKS='0')
    h.need(hashlib.sha256(helper.git(root, env, 'diff', '--binary', '--', '.', ':(exclude)' + FONT)).hexdigest() ==
           baseline['semantic_index']['working_diff'], 'font-only live working delta')
    h.need(sorted(helper.git(root, env, 'diff', '--name-only').decode().splitlines()) == epoch['modified_native_paths'], 'exact live native paths')
    metadata = h.application_metadata(root / policy['application_ini'], policy['frozen_head'])
    h.need(metadata == h.read(root / policy['build_directory'] / 'APPLICATION-METADATA.json'), 'actual compiled application metadata')
    return result


def validate_original(root, here, policy, h):
    old = root / policy['pair_capsule']
    pair = root / policy['paired_runtime']
    h.authenticate(old, policy['pair_capsule_sha256'])
    h.need(h.sha(pair / 'FILES.json') == policy['paired_manifest_sha256'], 'paired runtime manifest')
    manifest = h.read(pair / 'FILES.json')
    h.need(set(manifest) == {'files', 'status', 'symlink_inventory', 'excluded_owned_backup_directory'}, 'runtime manifest schema')
    for name, item in manifest['files'].items():
        path = pair / name
        h.need(not path.is_symlink() and path.is_file() and h.sha(path) == item['sha256'] and path.stat().st_size == item['size'], 'paired runtime payload: ' + name)
    actual_files, actual_links = old_bindings_inventory(pair, h)
    h.need(actual_files == {**{n: v['sha256'] for n,v in manifest['files'].items()}, 'FILES.json': policy['paired_manifest_sha256']}, 'exact paired runtime file inventory')
    h.need(actual_links == h.read(pair / 'SYMLINKS.json'), 'paired runtime symlinks')
    old_run = h.load('final_original_runner', old / 'run.py')
    old_bindings = h.load('final_original_bindings', old / 'bindings.py')
    old_policy = h.read(pair / 'candidate-wpt/POLICY.json')
    saved = old_bindings.validate_original(root, old, old_policy, old_run)
    for name in ('assess.py', 'SOURCE-PINS.json', 'EXPERIMENT.json', 'SUBSET-MANIFEST.json', 'ENUMERATED-SUBTESTS.json'):
        h.need((here / name).read_bytes() == (old / name).read_bytes(), 'unchanged original experiment: ' + name)
    original = pair / 'original-wpt'
    original_policy = h.read(original / 'POLICY.json')
    original_epoch = h.read(original / 'EPOCH.json')
    baseline = h.read(here / 'PROMOTION-BASELINE-EPOCH.json')
    normalized = copy.deepcopy(original_epoch)
    marker = normalized.pop('reversible_line_height_phase')
    h.need(marker['role'] == 'original' and marker['source_package_manifest'] == policy['source_package_manifest'] and
           marker['owner_runtime'] == policy['paired_runtime'], 'historical original phase retained')
    h.need(original_epoch['installed_identities'][FONT] == policy['original_font_identity'], 'authenticated original font identity')
    h.need(normalized['pins'][FONT] == policy['source_roles']['original'][FONT], 'original font base')
    del normalized['pins'][FONT]
    del normalized['installed_identities'][FONT]
    normalized['counts']['roles'] -= 1
    normalized['counts']['installed_identities'] -= 1
    normalized['raw_index_observation']['current'] = baseline['raw_index_observation']['current']
    for name in policy['rebuilt_binaries']:
        normalized['pins'][name] = baseline['pins'][name]
    h.need(normalized == baseline, 'same original source/context apart from explicit local font pin and rebuilt binaries')
    parser = h.load('final_original_assessor', here / 'assess.py')
    checks = h.load('final_original_checks', root / policy['helpers']['checks'])
    events = [json.loads(line) for line in (original / 'raw.jsonl').read_text().splitlines()]
    replay = parser.assess(events, h.read(original / 'RESULT.json')['exit'], original_policy, checks,
                           run_binding=h.read(original / 'APPLICATION-METADATA.json'))
    replay = old_run.augment_assessment(replay, phase='original-1', capsule_sha=policy['pair_capsule_sha256'],
                epoch_sha=original_policy['epoch_sha256'], policy=original_policy,
                capsule_directory=policy['pair_capsule'], experiment_sha=h.sha(old / 'EXPERIMENT.json'), execution_preserved=True)
    h.need(json.loads(json.dumps(replay)) == saved, 'complete original publication replay')
    return saved
