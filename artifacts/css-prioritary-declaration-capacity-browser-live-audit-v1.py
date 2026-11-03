import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
ROOT = Path(__file__).resolve().parent.parent
OWNER = ROOT / 'artifacts/css-prioritary-declaration-capacity-browser-v1'
RUNTIME = ROOT / 'artifacts/css-prioritary-declaration-capacity-browser-runtime-1'
CANONICAL = ROOT / 'artifacts/css-registered-number-native-runtime-v1'
sha = lambda body: hashlib.sha256(body).hexdigest()
read = lambda path: json.loads(path.read_bytes())


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


OUTCOME_PINS = {'APP-BEFORE-RESTORE.json': 'd1e4db233b869f664dad3a4232b71347adcee191c2abb27b464614755f994a3d', 'APP-PRE.json': '684cf6b214bd4762cb039317ad3a2f97d9367ed9414e83aecc23528e044e9a74', 'BACKUP-CLEANUP.json': '384e8b1ba4c3b4739f2b749de94bcf06a397e502938702f3fd6c0db16fa9b31e', 'BACKUPS.json': '70854b543518dbc092b430433752ecedac667dfa20b1bb14a07f75144d80857c', 'COMPARISON.json': 'ab5d4c425cf99969464c87c455ddfbfc5b50c2b102030a3d948299ba24d3a244', 'EXTRA-BEFORE-RESTORE.json': '2ee67fc7c419ac8026c5e9cdc80f03494f1c4f8e0aead997a271bf033c42ec15', 'EXTRA-PRE.json': '33960ea06f2f0d3365a9681d9e2d8fbe9f8be563b106624a9fa7ec8976d6e9cd', 'PAIR-PRE.json': 'c1854edd368ec2fb1a83f2e4127634c99bf8b2e9ad01e714aae0315c7e8f4ae3', 'POST.json': 'fdb7fe5a9ed24ca5339f6b6d956c3f37da0a30cceab4d54fb0c834276d714d02', 'RAW-INDEX-OBSERVATION.json': '7f3c2ce5c0fc983b8a6577b74d42d79d221819b457a6815650ad1f0c2b3715bc', 'RESTORATION.json': '8bbef4a1363df105fb82858a86b816804f03dc9b6f7ea9c6256a6c46f8fcddf3', 'RESULT.json': 'ed5b375ffb5f15b5c82f2a8ff3d7b468dc7afaed71135536cb308b5d0749c82a', 'ROOT-OWNER-TERMINAL.json': 'a3eef65b7ac77244310eed0d7e5c6ca5c28b5edd3b32da7173c3e14ef253f8af', 'candidate-OUTCOMES.json': '7356172d28801818c70a209b7a0371ddae52504f7a1da6d6fa076eae6825645f', 'candidate-PHASES-POST.json': 'b0dbda5d6adf16b9d14d0adc9cb711761f5d9c98c2907bfb068206267c09c4e5', 'candidate-PHASES-PRE.json': 'b0dbda5d6adf16b9d14d0adc9cb711761f5d9c98c2907bfb068206267c09c4e5', 'candidate-build/COMMAND.json': '7399a054f07afa39690ad0d1cf472e4e3842be561160c3532f12297450272ec0', 'candidate-build/PREFLIGHT.json': 'fc508b6ec2bcd230dad56b8f81268e36b6e005cf8ed84c01a50e12e4ef008c01', 'candidate-build/RESULT.json': '2d2cccf2d3da221ec3b0b07e02b80c1bf76303d6e5cc17161ba6ccce689d22a6', 'candidate-build/WAKE-PROCESS.json': 'bc988f043a9c0fd40598cf32c0642ddc8e02730aee5c5d981ef17e85fe954a34', 'candidate-build/WAKE-RESULT.json': '403f57bf29834553a98821dfc1d7a99a7bf3e3bb73e8aeba995739956b09d9a5', 'candidate-build/build-GROUP-CLEANUP.json': '93a94821a53f8f43789b71667dbafcde4f69c7dde2aa8b79c210a444d48e514b', 'candidate-build/build-PROCESS.json': '76caf80c6551aeabb360ff212959955bc267808df2adbcaa27265438f80ad64c', 'candidate-build/build-RESULT.json': '8239bb06b943380159bcb79802fd999a803b0f8d5ac5260b522ac4dabb824d8d', 'candidate-build/wake-GROUP-CLEANUP.json': '36ec2c0d09155b5c14025d58faf52817f5ec62e29c3e25375b0f7a546985ac56', 'candidate-wpt-capacity/APPLICATION-METADATA-POST.json': 'ef6c49f63738878d089931675a50a9ca233d872e60c3542cd72b9eb2da32e561', 'candidate-wpt-capacity/APPLICATION-METADATA.json': 'ef6c49f63738878d089931675a50a9ca233d872e60c3542cd72b9eb2da32e561', 'candidate-wpt-capacity/ASSESSMENT-POLICY.json': 'aa28f0dc814e3da003188c45a83cf692f3810103118cba8b9d36b714cb450a7b', 'candidate-wpt-capacity/ASSESSMENT.json': '52e2d4e750c1f24cbb1a0573882816ec0f307e93fd36475be2954fdc4180c41c', 'candidate-wpt-capacity/BEHAVIOR-COMPARISON.json': '1ad6eb12834f48e64bef4bcaf88b207f9342860d10f2b7ddcbb729c452e5958d', 'candidate-wpt-capacity/BINARY-PINS.json': '93e1ebe8f5bbbde06ae32475e96cabda9f27c6089b667bd8f54d6b3f9d82e409', 'candidate-wpt-capacity/CLEANUP.json': '9bfd5d65135f85ae50b5cd75813e3972100fb46b4c3e8457f29a4101267f0c14', 'candidate-wpt-capacity/COMMAND.json': '1e3c08f9f19c7bfd79d898c61a35add9165e104b0be80db18dab236e8c2504f7', 'candidate-wpt-capacity/POST.json': 'b0dbda5d6adf16b9d14d0adc9cb711761f5d9c98c2907bfb068206267c09c4e5', 'candidate-wpt-capacity/PRE.json': 'b0dbda5d6adf16b9d14d0adc9cb711761f5d9c98c2907bfb068206267c09c4e5', 'candidate-wpt-capacity/PROCESS.json': '0d3acbc7ccaea665aed25173e9339547a0345ebfd126ef0c29574b7f3c80d829', 'candidate-wpt-capacity/RESULT.json': '84da7f53f97a41e3708e0f5ca293565fefa50761e595ba73bad711a0c5ebb83c', 'candidate-wpt-capacity/STAGED-RESOURCES.json': 'eea800a59407a137c6f4814d5d339def1d2abf39e878f1abad5ecacd06e5d43b', 'candidate-wpt-capacity/raw.jsonl': 'a75a383bd9429ae6d4fd7228d25ab1de742bfadc5cf767289ea44a9976df1919', 'original-OUTCOMES.json': 'b862377da023d727a909335f80cc56ba103c3777e194053c5faee2984da43ac5', 'original-PHASES-POST.json': 'ac5e1e046052bff32f39fca685d8582b509b93cc51a5d0fca2c36db99305b79c', 'original-PHASES-PRE.json': 'ac5e1e046052bff32f39fca685d8582b509b93cc51a5d0fca2c36db99305b79c', 'original-build/COMMAND.json': '0bb0e47931ab57a2d9dc01dd960a3ef64a52902e021fd3cf837087428348448c', 'original-build/PREFLIGHT.json': 'a5558c9f8e4ad74f9767907b8d12a8b4046dc6525cee45fc40bdbcf05b0f3a55', 'original-build/RESULT.json': '506a7f77a2696fc44fbb5d44d467ed21529bdc8b7ab7cf560ea415f3b96cca12', 'original-build/WAKE-PROCESS.json': '924a9e6e6ef4d97b95284e1e4125eae421cf428bc854d4c7f652bdb686a39527', 'original-build/WAKE-RESULT.json': '403f57bf29834553a98821dfc1d7a99a7bf3e3bb73e8aeba995739956b09d9a5', 'original-build/build-GROUP-CLEANUP.json': '93a94821a53f8f43789b71667dbafcde4f69c7dde2aa8b79c210a444d48e514b', 'original-build/build-PROCESS.json': '943f4dbfbd1a6c1ee5d968604a8d8fb42b3932e688ecdfc30a490dd7b016bc25', 'original-build/build-RESULT.json': '9ebd397d266c00e8a4814e6f1f38a88287b31e7f7762469b65225246c3672464', 'original-build/wake-GROUP-CLEANUP.json': '36ec2c0d09155b5c14025d58faf52817f5ec62e29c3e25375b0f7a546985ac56', 'original-wpt-capacity/APPLICATION-METADATA-POST.json': '3e067b1b7be26372018963d4cb8ccc3593c727a0b8613dcebcc76b595c962d2c', 'original-wpt-capacity/APPLICATION-METADATA.json': '3e067b1b7be26372018963d4cb8ccc3593c727a0b8613dcebcc76b595c962d2c', 'original-wpt-capacity/ASSESSMENT-POLICY.json': '6bb6400cfcfa17bf0050b02cc931d7563f9dcb2a29349ff7f81a3a4db7fe9225', 'original-wpt-capacity/ASSESSMENT.json': '66fa0fbda6778ba4c90adaa0157532ebe4195b0d339d373a270a00fd16e66dc1', 'original-wpt-capacity/BEHAVIOR-COMPARISON.json': '38e0b9de817f645c4bec37c0d4a3e58baecccb040f5718dc069a72c7385a0bed', 'original-wpt-capacity/BINARY-PINS.json': 'd0f119407ec374cf46ea2a682039cf952d48d2b0c4461599fd3ec0e21b1157fb', 'original-wpt-capacity/CLEANUP.json': '9bfd5d65135f85ae50b5cd75813e3972100fb46b4c3e8457f29a4101267f0c14', 'original-wpt-capacity/COMMAND.json': '4a290208a11b3faf8122a74532f110f0f37413edf7cbd9bca58ba1e88d9a347b', 'original-wpt-capacity/POST.json': 'ac5e1e046052bff32f39fca685d8582b509b93cc51a5d0fca2c36db99305b79c', 'original-wpt-capacity/PRE.json': 'ac5e1e046052bff32f39fca685d8582b509b93cc51a5d0fca2c36db99305b79c', 'original-wpt-capacity/PROCESS.json': 'a5c4fea284a28bc419e6676416c5c2e46dec48964b520345b60e06826b3f6560', 'original-wpt-capacity/RESULT.json': '9c55fb8492d34f4863e71e27e56189571fc90ab1ffde6f9f5542c95d5cec1044', 'original-wpt-capacity/STAGED-RESOURCES.json': 'eea800a59407a137c6f4814d5d339def1d2abf39e878f1abad5ecacd06e5d43b', 'original-wpt-capacity/raw.jsonl': '3ff1d36cea5be86ad88eda0f57424a6fd003fb3b483512d0bfc340cd21d50fc3'}
assert OUTCOME_PINS, 'Actual terminal evidence is pending'
assert sha((OWNER / 'FILES.json').read_bytes()) == 'a21655a0ef950303f0d92f68a73e4dace90dc1b91c54736bcce0c36b56483425'
baseline = load('paired_live_baseline', 'artifacts/css-prioritary-declaration-capacity-browser-v1/baseline.py')
policy, ownership, roles = baseline.prepare(sha((OWNER / 'FILES.json').read_bytes()))
ENV = baseline.environment()
capture = baseline.current_capture(policy)
result = read(RUNTIME / 'RESULT.json')
for name, digest in OUTCOME_PINS.items():
    assert sha((RUNTIME / name).read_bytes()) == digest
terminal = read(RUNTIME / 'ROOT-OWNER-TERMINAL.json')
assert terminal['session'] == 68207 and terminal['launch'] == 'b1490c'
assert terminal['terminal'] and terminal['exit'] == (0 if result['success'] else 1)
assert terminal['result_sha256'] == OUTCOME_PINS['RESULT.json']
assert result['restoration_verified'] and result['runtime_controls_unchanged']
assert result['empty_staging_preserved'] and not result['native_fix_acceptance']
assert policy['lane_order'] == ['capacity'] and policy['diagnostic_lane_order'] == []
if result['success']:
    assert result['error'] is None and result['publication_errors'] == []
    assert set(result['phase']) == {'original','candidate'}
else:
    assert result['error'] or result['publication_errors']
    if result['error']:
        trace = read(RUNTIME / 'FAILURE-TRACEBACK.json')
        assert trace['error'] == result['error'] and trace['traceback']
assert not (CANONICAL / 'SOURCE-TRANSITION.lock').exists()
ownership.quiescent(CANONICAL)
ownership.quiescent(ROOT / 'artifacts/css-page-selector-native-runtime-v1')
absent_groups, process_records = [], []
for role in ('original', 'candidate'):
    build = RUNTIME / (role + '-build')
    for process_file, cleanup_file in [('build-PROCESS.json', 'build-GROUP-CLEANUP.json'),
                                       ('WAKE-PROCESS.json', 'wake-GROUP-CLEANUP.json')]:
        record = build / process_file
        if not record.exists():
            continue
        group = read(record)['pgid']
        assert read(build / cleanup_file)['owned_group_absent']
        ownership.group_absent(group)
        absent_groups.append(group)
        process_records.append(str(record.relative_to(RUNTIME)))
    phase = RUNTIME / (role + '-wpt-capacity')
    if phase.exists():
        cleanup = read(phase / 'CLEANUP.json')
        assert cleanup['owned_group_absent'] and cleanup['temporary_root_removed']
        if (phase / 'PROCESS.json').exists():
            group = read(phase / 'PROCESS.json')['pgid']
            ownership.group_absent(group)
            absent_groups.append(group)
            process_records.append(str((phase / 'PROCESS.json').relative_to(RUNTIME)))
        temporary = Path(read(phase / 'COMMAND.json')['temporary_root'])
        assert not temporary.exists() and not temporary.is_symlink()
assert len(absent_groups) == len(set(absent_groups))
assert set(process_records) == {str(path.relative_to(RUNTIME)) for path in RUNTIME.rglob('*PROCESS.json')}
assert all(name in OUTCOME_PINS for name in process_records)
for name, digest in policy['controls'].items():
    assert sha((CANONICAL / name).read_bytes()) == digest
baseline.metadata_guard(policy)
for name in policy['preserved_absent_metadata'] + policy['preserved_absent_resources']:
    assert not (ROOT / name).exists() and not (ROOT / name).is_symlink()
state = load('paired_live_state', 'artifacts/css-registered-number-native-runtime-v1/state.py')
epoch = read(CANONICAL / 'CURRENT-EPOCH.json')
index = state.h.index_state(ROOT, ENV)
assert state.h.semantic_index(index) == epoch['semantic_index']
adjusted = copy.deepcopy(epoch)
adjusted['raw_index_observation']['current'] = index['raw_index']
observed = state.a.verify_current(state.h, ROOT, ENV, adjusted)
expected = copy.deepcopy(capture['snapshot'])
expected['index']['raw_index'] = index['raw_index']
assert observed == expected == read(RUNTIME / 'POST.json')
for label, path in [('root', ROOT), ('nested', ROOT / 'artifacts/css-spec-lean')]:
    assert sha(state.h.git(path, ENV, 'ls-files', '-v', '-z')) == capture['flag_hashes'][label]
for name, role in roles.items():
    assert sha((ROOT / name).read_bytes()) == role['base_sha256']
    claim = read(RUNTIME / 'PAIR-PRE.json')['sources'][name]
    assert [(ROOT / name).stat().st_dev, (ROOT / name).stat().st_ino] == claim['identity']
bundle = load('paired_live_bundle', policy['bundle_helper'])
assert bundle.semantic(bundle.scan(ROOT / policy['bundle_path'])) == bundle.semantic(read(RUNTIME / 'APP-PRE.json'))
extras = {name: bundle.entry(ROOT / name) for name in policy['extra_backup_paths']}
assert bundle.semantic(extras) == bundle.semantic(read(RUNTIME / 'EXTRA-PRE.json'))
assert all(sha((ROOT / name).read_bytes()) == digest for name, digest in capture['binaries'].items())
metadata = load('paired_live_metadata', policy['wpt']['metadata_helper'])
application = metadata.application_metadata(ROOT / policy['wpt']['application_ini'], policy['restored_application_revision'])
semantic_metadata = lambda row: {key: value for key, value in row.items() if key not in ('entry_identity', 'identity')}
assert semantic_metadata(application) == semantic_metadata(capture['application_metadata'])
cleanup = read(RUNTIME / 'BACKUP-CLEANUP.json')
assert cleanup['verified_original_restoration'] is True
backups = read(RUNTIME / 'BACKUPS.json')
assert cleanup['owned_backup_bytes'] == backups['bytes'] == read(RUNTIME / 'PAIR-PRE.json')['owned_backup_bytes']
assert cleanup['removed'] is result['success'] and cleanup['retained_after_failure'] is (not result['success'])
if cleanup['removed']:
    assert not (RUNTIME / 'backups').exists() and not (RUNTIME / 'backups').is_symlink()
else:
    assert not (RUNTIME / 'backups').is_symlink()
    assert bundle.scan(RUNTIME / 'backups') == backups['owned_inventory']
assert not read(RUNTIME / 'RESTORATION.json')['errors']
assert not read(RUNTIME / 'RESTORATION.json')['owned_processes']
assert not (CANONICAL / 'SOURCE-TRANSITION.lock').exists()
output = RUNTIME / 'ROOT-LIVE-RESTORATION.json'
with output.open('x') as stream:
    json.dump({'independent_live_restoration_verified': True, 'snapshot': observed,
               'application_and_extras_semantically_restored': True,
               'source_and_binary_hashes_restored': True, 'flags_restored': True,
               'controls_unchanged': True, 'backup_removed': cleanup['removed'], 'retained_backup_inventory_verified': not cleanup['removed'],
               'backup_inventory_sha256': OUTCOME_PINS['BACKUPS.json'],
               'owner_terminal': terminal, 'outcome_pins': OUTCOME_PINS,
               'independently_absent_process_groups': absent_groups,
               'restored_application_metadata': application,
               'owner_result_sha256': sha((RUNTIME / 'RESULT.json').read_bytes()),
               'audit_script_sha256': sha(Path(__file__).read_bytes()),
               'native_acceptance': False}, stream, indent=2)
    stream.write('\n')
print('Independent live source, application, controls, index and flags audit passed')
