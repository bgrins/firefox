import hashlib
import importlib.util
import json
from pathlib import Path
import stat
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PLAN = ROOT / 'artifacts/css-finite-mod-rem-comparison-data-v1'
DATA = PLAN
BASELINE = ROOT / 'artifacts/css-finite-mod-rem-comparison-runtime-v1'
PRIOR = ROOT / 'artifacts/css-counter-additive-install-runtime-v1'
read = lambda p: json.loads(p.read_text())


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()

def need(ok, message):
    if not ok:
        raise RuntimeError(message)

def save(name, value):
    with (HERE / name).open('x') as stream:
        stream.write(json.dumps(value, indent=2) + '\n')

def authenticate(directory, digest):
    need(sha(directory / 'FILES.json') == digest, 'manifest ' + str(directory))
    for name, value in read(directory / 'FILES.json').items():
        need(not Path(name).is_absolute() and '..' not in Path(name).parts, 'relative member')
        path = directory / name
        need(stat.S_ISREG(path.lstat().st_mode) and sha(path) == value, 'payload ' + name)

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def verify_roles(pins):
    for name, digest in pins.items():
        path = ROOT / name
        need((not path.exists() and not path.is_symlink()) if digest is None else
             stat.S_ISREG(path.lstat().st_mode) and sha(path) == digest, 'role ' + name)

def verify(phase, binaries, active=True):
    pins = {**restoration, **maps[phase], **binaries}
    if active:
        pins.update({name: item['sha256'] for name, item in owned.items()})
    verify_roles(pins)
    snapshot = wpt.snapshot()
    need(snapshot['sources'] == maps[phase], 'source phase')
    for key in ('head', 'index_diff_sha256', 'index_entries_sha256'):
        need(snapshot[key] == before['snapshot'][key], 'preserved ' + key)
    need(snapshot == snapshots[phase], 'exact source/index/native phase snapshot')
    native = {n for n in wpt.git('diff', '--name-only').decode().splitlines() if not n.startswith('artifacts/')}
    need(native == set(config['modified_native_paths']) and len(native) == 43, 'exact native inventory')
    need(not wpt.git('ls-files', '--others', '--exclude-standard', '--', 'layout', 'dom', 'servo', 'mfbt'), 'no untracked native')
    identities = {**before['installed_tests'], **(owned if active else {})}
    for name, item in identities.items():
        path = ROOT / name
        info = path.lstat()
        need(stat.S_ISREG(info.st_mode) and [info.st_dev, info.st_ino] == item['identity']
             and sha(path) == item['sha256'], 'test identity ' + name)
    need(not wpt.git('ls-files', '--', *identities, *owned_plan['temporary_fixtures'], *owned_plan['permanent_absences']),
         'installed/temporary tests and permanent absences untracked')
    need(wpt.pins(config['existing_tests']) == config['existing_test_pins']
         and wpt.git('ls-files', '--', *config['existing_tests']).decode().splitlines()
         == config['tracked_existing_tests'], 'existing test ownership')
    prior.index.index_state(wpt)
    for name, digest in config['index_expectations']['staged_payload_sha256'].items():
        path = ROOT / name
        need(stat.S_ISREG(path.lstat().st_mode) and sha(path) == digest, 'working staged payload ' + name)
    return {'snapshot': snapshot, 'pins': pins, 'installed_tests': identities}

def write_source(name, phase, recovery=False):
    global mutation_started
    path = ROOT / name
    info = path.lstat()
    need(stat.S_ISREG(info.st_mode) and [info.st_dev, info.st_ino] == source_identities[name], 'source inode ' + name)
    actual = sha(path)
    allowed = {maps['baseline'][name], maps['candidate'][name]} if recovery else {current_sources[name]}
    need(actual in allowed, 'unknown source body preserved: ' + name)
    target_hash = maps[phase][name]
    if actual == target_hash:
        current_sources[name] = target_hash
        return
    source = ROOT / bodies[name]['candidate' if phase == 'candidate' else 'original']
    need(sha(source) == target_hash, 'reviewed source body ' + name)
    mutation_started = True
    path.write_bytes(source.read_bytes())
    current_sources[name] = target_hash
    transitions.append({'path': name, 'from': actual, 'to': target_hash, 'recovery': recovery})
    save('source-write-' + str(len(transitions)) + '.json', transitions[-1])
    need(sha(path) == target_hash, 'source write result ' + name)

def restore_sources():
    errors = []
    for name in bodies:
        try:
            write_source(name, 'baseline', recovery=True)
        except BaseException as error:
            errors.append(name + ': ' + repr(error))
    return errors

def build(label, phase, active=True):
    global current_binaries
    pre = verify(phase, current_binaries, active=active)
    code = None
    try:
        code = wpt.command(label + '-build', ['./mach', 'build', 'binaries'])
    finally:
        current_binaries = wpt.pins(wpt.BINARIES)
        save(label + '-BINARIES.json', current_binaries)
        save(label + '-BUILD-SOURCES.json', {'before': pre['snapshot']['sources'],
             'after': wpt.pins(config['guard_sources']), 'binaries': current_binaries, 'exit': code})
    need(code == 0 and all(current_binaries.values()), 'successful build ' + label)
    save(label + '-ARCHITECTURE.json', architecture.verify(ROOT, current_binaries))
    verify(phase, current_binaries, active=active)

def outcomes(result):
    rows = [(r, r['subtest']) for r in result['rows']]
    rows += [(r, None) for r in result['ends'] if r['test'] in config['reftests']]
    normalized = {(r['test'], sub): {'test': r['test'], 'subtest': sub, 'status': r['status'],
                  'message': r.get('message'), 'expected': r.get('expected'),
                  'effective_expected': r.get('expected', r['status']),
                  'known_intermittent': r.get('known_intermittent', [])} for r, sub in rows}
    need(len(normalized) == len(rows), 'unique outcome identities')
    return normalized

def assess(actual, phase):
    need(set(actual) == expected_keys, 'exact outcome keys')
    errors, differences, improvements = [], [], []
    reference = observed if phase == 'baseline' else baseline_outcomes
    need(reference is not None, 'fresh baseline established')
    for key, expected in reference.items():
        value = actual[key]
        if phase == 'candidate' and key in repair_keys:
            wanted = dict(expected, status='PASS', message=None, expected=None,
                          effective_expected='PASS', known_intermittent=[])
            if value != wanted:
                errors.append('required repair not exact PASS: ' + str(key))
            else:
                improvements.append({'baseline': expected, 'actual': value, 'required_landing': True})
        elif value != expected:
            errors.append('unreviewed outcome change: ' + str(key))
        if value != expected:
            differences.append({'baseline': expected, 'actual': value})
    if phase == 'candidate':
        for key in landing_keys:
            value = actual[key]
            if value['status'] != 'PASS' or value['effective_expected'] != 'PASS' or value['known_intermittent']:
                errors.append('candidate landing not PASS: ' + str(key))
    return differences, improvements, errors

def capture(label, phase):
    global baseline_outcomes
    need(set(owned) == set(owned_plan['temporary_fixtures']), 'all owned fixtures created')
    verified = verify(phase, current_binaries)
    need(set(wpt.resource_paths(config['tests'])) <= set(verified['pins']), 'complete resource closure')
    save(label + '-PRE-CAPTURE.json', verified)
    result = prior.tests.run(wpt, label, verified['pins'])
    need(result['before'] == result['after'] == verified['pins'], 'phase role joins')
    need(verify(phase, current_binaries) == verified, 'full phase preservation')
    need(len(result['rows']) == 24 and len(result['ends']) == 1, 'landing roster counts')
    need(all(e['status'] == e.get('expected', 'OK') == 'OK' and not e.get('known_intermittent', [])
             for e in result['ends']), 'strict OK harness metadata')
    need(all(r.get('expected', r['status']) in ('PASS', 'FAIL')
             and type(r.get('known_intermittent', [])) is list
             and all(v in ('PASS', 'FAIL') for v in r.get('known_intermittent', []))
             for r in result['rows']), 'complete row metadata')
    landing_rows = [dict(row, test=classifier.TARGET) for row in result['rows'] if row['test'] == landing_url]
    classified = classifier.classify(landing_rows)
    save(label + '-LANDING-CLASSIFICATION.json', {'comparison_test': landing_url,
         'classifier_test': classifier.TARGET, 'classification': classified})
    actual = outcomes(result)
    differences, improvements, errors = assess(actual, phase)
    errors.extend('landing classification: ' + str(item) for item in classified['errors'])
    save(label + '-OUTCOMES.json', list(actual.values()))
    save(label + '-DIFFERENCES.json', differences)
    save(label + '-IMPROVEMENTS.json', improvements)
    save(label + '-SUMMARY.json', {'status': 'PHASE_EXACT_POLICY_PASS' if not errors else 'PHASE_SEMANTIC_REJECTION',
         'subtests': len(result['rows']), 'harnesses_ok': len(result['ends']), 'reference_passes': 0,
         'counts': {status: sum(row['status'] == status for row in result['rows']) for status in ('PASS', 'FAIL')},
         'required_repairs': 16 if phase == 'candidate' else 0,
         'additional_improvements': 0, 'errors': errors, 'wpt_exit': result['exit'], 'native_acceptance': False})
    captured.append(label)
    need(not errors, label + ' semantic comparison rejected; inspect SUMMARY and DIFFERENCES')
    if phase == 'baseline':
        baseline_outcomes = actual
    completed.append(phase)

def cleanup_fixtures():
    removed, errors = [], []
    for name, item in owned.items():
        try:
            path = ROOT / name
            info = path.lstat()
            need(stat.S_ISREG(info.st_mode) and [info.st_dev, info.st_ino] == item['identity']
                 and sha(path) == item['sha256'], 'cleanup ownership ' + name)
            path.unlink()
            removed.append(name)
        except BaseException as error:
            errors.append(name + ': ' + repr(error))
    return removed, errors


inputs = read(HERE / 'INPUTS.json')
need(inputs['ready_for_execution'] is True and inputs['actual_session'] is None and inputs['actual_exit'] is None,
     'disabled or invalid activation')
need(sha(HERE / 'install.py') == inputs['install_sha256'], 'bound controller')
for name, digest in inputs['manifests'].items():
    authenticate(ROOT / name, digest)
for field in ('controller_review', 'terminal_review', 'acceptance'):
    binding = inputs[field]
    need(binding is not None and set(binding) == {'path', 'manifest_sha256'}, 'required binding ' + field)
    authenticate(ROOT / binding['path'], binding['manifest_sha256'])
review = inputs['controller_review']
need(read(HERE / 'ROOT-REVIEW-BINDING.json') == {'status': 'FINITE_MOD_REM_INSTALL_ROOT_BINDING_GO',
     'inputs_sha256': sha(HERE / 'INPUTS.json'), 'install_sha256': inputs['install_sha256'],
     'controller_review_manifest_sha256': review['manifest_sha256']}, 'exact root activation binding')
for name, digest in inputs['helper_pins'].items():
    need(sha(ROOT / name) == digest, 'bound helper ' + name)
terminal_directory = ROOT / inputs['terminal_review']['path']
peer = read(terminal_directory / 'CHECK.json')
need(peer['status'] == 'MOD_REM_COMPARISON_TERMINAL_REVIEW_GO'
     and peer['runtime_manifest'] == sha(BASELINE / 'FILES.json')
     and peer['root_receipt'] == sha(BASELINE / 'ROOT-FINAL-CHECK.json')
     and peer['restored_exact'] is True and peer['repairs'] == 16 and peer['other_changes'] == 0, 'actual terminal review')
terminal_refs = read(terminal_directory / 'REFERENCES.json')
for name in ('FILES.json', 'ROOT-FINAL-CHECK.json', 'ROOT-COMPLETION.json'):
    need(terminal_refs[str((BASELINE / name).relative_to(ROOT))] == sha(BASELINE / name), 'terminal review receipt join')
completion = read(BASELINE / 'ROOT-COMPLETION.json')
need(completion['status'] == 'MOD_REM_COMPARISON_ROOT_TERMINAL_AND_LIVE_ROLES_PASS'
     and completion['session'] == 59511 and completion['actual_exit'] == 0
     and completion['source_snapshot_restored'] is True, 'actual comparison completion')
acceptance_directory = ROOT / inputs['acceptance']['path']
acceptance = read(acceptance_directory / 'ACCEPTANCE.json')
need(acceptance['status'] == 'ACCEPTED_PENDING_SIGNATURE' and type(acceptance['fix']) is int
     and acceptance['comparison_session'] == 59511 and acceptance['comparison_exit'] == 0
     and acceptance['restoration_verified'] is True and acceptance['all_other_outcomes_exact'] is True,
     'accepted completed comparison')
acceptance_refs = read(acceptance_directory / 'REFERENCES.json')
need(acceptance_refs[str((BASELINE / 'FILES.json').relative_to(ROOT))] == sha(BASELINE / 'FILES.json')
     and acceptance_refs[inputs['terminal_review']['path'] + '/FILES.json'] == inputs['terminal_review']['manifest_sha256'],
     'acceptance comparison and peer joins')
terminal = read(BASELINE / 'ROOT-FINAL-CHECK.json')
need(terminal['status'] == 'ORIGINAL_STACK_RESTORED_VERIFIED' and terminal['comparison_error'] is None
     and not terminal['recovery_errors'] and terminal['completed_phases'] == ['baseline', 'candidate', 'restored'],
     'successful reviewed comparison')
before = read(BASELINE / 'FINAL.json')
restoration = read(BASELINE / 'FINAL-PINS.json')
need(before['pins'] == restoration and len(restoration) == 628
     and terminal['final_pins_sha256'] == sha(BASELINE / 'FINAL-PINS.json'), 'complete restored epoch role join')
source_data = read(DATA / 'SOURCE-MAPS.json')
maps = {name: source_data[name] for name in ('baseline', 'candidate', 'restored')}
proposal = read(DATA / 'CANDIDATE.json')
bodies = proposal['native_paths']
need(before['snapshot']['sources'] == maps['baseline'] == maps['restored'] and len(maps['baseline']) == 72, 'all original sources')
need(set(bodies) == {name for name in maps['baseline'] if maps['baseline'][name] != maps['candidate'][name]}
     == {'servo/components/style/values/generics/calc.rs'}, 'exact one-source candidate')
for name, item in bodies.items():
    need(sha(ROOT / item['original']) == item['original_sha256'] == maps['baseline'][name]
         and sha(ROOT / item['candidate']) == item['candidate_sha256'] == maps['candidate'][name], 'source body binding')
need(sha(ROOT / proposal['patch']) == proposal['patch_sha256'] == acceptance['patch_sha256'], 'accepted exact installed patch')
owned_plan = {'temporary_fixtures': proposal['fixture'],
              'permanent_absences': [name for name, digest in restoration.items() if digest is None]}
need(len(owned_plan['temporary_fixtures']) == 1 and len(before['installed_tests']) == 24
     and not set(owned_plan['temporary_fixtures']) & set(before['installed_tests']), 'exclusive landing fixture')
landing_path, = owned_plan['temporary_fixtures']
landing_url = '/' + landing_path.removeprefix('testing/web-platform/tests/')
need(set(acceptance['native_paths']) == set(bodies) | {landing_path}, 'exact accepted two-path scope')
roster = read(DATA / 'ROSTER.json')
config = read(BASELINE / 'CONFIG.json')
config.update(tests=[landing_path], expected_subtests={landing_url: roster['expected_subtests'][landing_url]}, reftests=[])
config.update(expected_total=24, files_expected_count=1, source_pins=maps['baseline'], guard_sources=sorted(maps['baseline']),
              resource_guard_paths=sorted(set(restoration) - set(maps['baseline'])), install={})
need(len(config['modified_native_paths']) == 43 and set(bodies) <= set(config['modified_native_paths']) <= set(maps['baseline']), 'native source inventory')
need(len(config['index_expectations']['staged_payload_sha256']) == 925, 'all staged payloads')
need(not set(config['existing_tests']) & set(owned_plan['temporary_fixtures']), 'fixture not read-only')
prior = load('finite_mod_rem_install_prior', PRIOR / 'validate.py')
wpt = load('finite_mod_rem_install_wpt', ROOT / config['helpers'] / 'run_wpt.py')
wpt.HERE, wpt.CONFIG, wpt.sha = HERE, config, sha
wpt.ENV = dict(prior.wpt.ENV)
architecture = load('finite_mod_rem_install_architecture', prior.OLD / 'architecture.py')
diagnostic = ROOT / read(DATA / 'BASELINE-EPOCH.json')['runtime']
classifier = load('finite_mod_rem_install_classifier', diagnostic / 'classify.py')
observed_data = read(DATA / 'OBSERVED-LANDING-BASELINE.json')
need(classifier.TARGET == observed_data['original_test'] and observed_data['comparison_test'] == landing_url
     and observed_data['body_sha256'] == owned_plan['temporary_fixtures'][landing_path]['sha256'], 'reviewed classifier and fixture')
policy = read(DATA / 'POLICY.json')
landing_keys = {(test, subtest) for test, names in policy['mandatory_candidate_pass'].items() for subtest in names}
expected_keys = {(test, name) for test, names in config['expected_subtests'].items() for name in names}
observed = outcomes({'rows': observed_data['rows'], 'ends': []})
baseline_outcomes = {(row['test'], row['subtest']): row for row in read(BASELINE / 'baseline_capture-OUTCOMES.json') if row['test'] == landing_url}
repair_keys = {(row['test'], row['subtest']) for row in policy['observed_repair_identities']}
need(len(expected_keys) == 24 and expected_keys == landing_keys == set(observed) == set(baseline_outcomes)
     and baseline_outcomes == observed and len(repair_keys) == 16
     and repair_keys == {key for key, row in observed.items() if row['status'] == 'FAIL'}, 'exact actual landing baseline and repair whitelist')
for phase in ('candidate', 'restored'):
    actual_rows = read(BASELINE / (phase + '-OUTCOMES.json'))
    selected = {(row['test'], row['subtest']): row for row in actual_rows if row['test'] == landing_url}
    need(len(actual_rows) == 700 and len(selected) == 24 and not assess(selected, phase)[2], 'actual full comparison landing ' + phase)
snapshots = {'baseline': before['snapshot'], 'restored': before['snapshot'],
             'candidate': read(BASELINE / 'candidate-PRE-CAPTURE.json')['snapshot']}
need(snapshots['candidate']['sources'] == maps['candidate'], 'tested candidate snapshot')
for field in ('head', 'index_diff_sha256', 'index_entries_sha256'):
    need(snapshots['candidate'][field] == before['snapshot'][field], 'candidate epoch ' + field)
data_pins = read(DATA / 'RESOURCES.json')
need(set(restoration) == set(data_pins)
     and all(value == data_pins[name] for name, value in restoration.items() if name not in wpt.BINARIES),
     'all inherited nonbinary roles unchanged')
owned, transitions, captured, completed = {}, [], [], []
current_sources = dict(maps['baseline'])
current_binaries = {name: restoration[name] for name in wpt.BINARIES}
source_identities = {name: [(ROOT / name).lstat().st_dev, (ROOT / name).lstat().st_ino] for name in bodies}
mutation_started, candidate_ready, installed = False, False, False
failure, recovery_errors, final = None, [], None
need(verify('baseline', current_binaries, active=False) == before, 'actual restored comparison epoch')
save('BEFORE.json', before)
save('CONFIG.json', config)
save('PRE-FLIGHT.json', before)
save('baseline-ARCHITECTURE.json', architecture.verify(ROOT, current_binaries))

try:
    for name, item in owned_plan['temporary_fixtures'].items():
        path, source = ROOT / name, ROOT / item['source']
        need(restoration[name] is None and not path.exists() and not path.is_symlink(), 'landing absence ' + name)
        need(sha(source) == item['sha256'], 'landing body ' + name)
        with path.open('xb') as stream:
            info = path.lstat()
            owned[name] = {'identity': [info.st_dev, info.st_ino], 'sha256': item['sha256']}
            stream.write(source.read_bytes())
    save('OWNED-TESTS.json', owned)
    verify('baseline', current_binaries)
    for name in bodies:
        write_source(name, 'candidate')
    build('candidate', 'candidate')
    capture('candidate', 'candidate')
    final = verify('candidate', current_binaries)
    need(len(final['installed_tests']) == 25 and len(final['pins']) == 628, 'installed identity and role counts')
    candidate_ready = True
except BaseException as error:
    failure = repr(error)
finally:
    removed = []
    if candidate_ready and failure is None:
        try:
            save('FINAL.json', final)
            save('FINAL-PINS.json', final['pins'])
            save('CLEANUP.json', {'removed': [], 'retained': sorted(owned),
                                 'errors': [], 'installation_error': None})
            save('RESULT.json', {'status': 'ACCEPTED_FIX_INSTALLED', 'fix': acceptance['fix'],
                 'installed': True, 'restored': False, 'candidate_ready': True,
                 'completed_phases': completed, 'captured_phases': captured,
                 'installation_error': None, 'recovery_errors': [],
                 'source_transitions': transitions, 'mutation_started': mutation_started,
                 'new_native_acceptance': False})
            installed = True
        except BaseException as error:
            failure = 'success publication: ' + repr(error)
    if not installed:
        final = None
        recovery_errors.extend(restore_sources())
        if not recovery_errors:
            try:
                build('restored', 'restored', active=bool(owned))
            except BaseException as error:
                recovery_errors.append('restoration build: ' + repr(error))
            else:
                if set(owned) == set(owned_plan['temporary_fixtures']):
                    try:
                        capture('restored', 'restored')
                    except BaseException as error:
                        recovery_errors.append('restoration capture: ' + repr(error))
                else:
                    recovery_errors.append('restoration capture unavailable: landing fixture creation incomplete')
        removed, errors = cleanup_fixtures()
        recovery_errors.extend(errors)
        try:
            final = verify('restored', current_binaries, active=False)
        except BaseException as error:
            recovery_errors.append('final preservation: ' + repr(error))
        records = []
        if final is not None:
            records.extend([('RECOVERY-FINAL.json', final), ('RECOVERY-FINAL-PINS.json', final['pins'])])
        records.append(('RECOVERY-CLEANUP.json', {'removed': removed, 'retained': [],
                        'errors': recovery_errors, 'installation_error': failure}))
        for name, value in records:
            try:
                save(name, value)
            except BaseException as error:
                recovery_errors.append('recovery publication ' + name + ': ' + repr(error))
        save('RECOVERY-RESULT.json', {'status': 'INSTALLATION_FAILED', 'fix': acceptance['fix'],
             'installed': False, 'restored': not recovery_errors and 'restored' in completed,
             'candidate_ready': candidate_ready,
             'completed_phases': completed, 'captured_phases': captured,
             'installation_error': failure, 'recovery_errors': recovery_errors,
             'source_transitions': transitions, 'mutation_started': mutation_started,
             'supersedes_partial_success_records': [name for name in
                 ('FINAL.json', 'FINAL-PINS.json', 'CLEANUP.json', 'RESULT.json') if (HERE / name).exists()],
             'new_native_acceptance': False})
need(installed and failure is None and not recovery_errors and completed == ['candidate'],
     'installation failed; inspect retained recovery evidence')
