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
DATA = HERE
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
    global candidate_snapshot
    pins = {**restoration, **maps[phase], **binaries}
    if active:
        pins.update({name: item['sha256'] for name, item in owned.items()})
    verify_roles(pins)
    snapshot = wpt.snapshot()
    need(snapshot['sources'] == maps[phase], 'source phase')
    for key in ('head', 'index_diff_sha256', 'index_entries_sha256'):
        need(snapshot[key] == before['snapshot'][key], 'preserved ' + key)
    if phase != 'candidate':
        need(snapshot == before['snapshot'], 'exact restored source/index/native snapshot')
    native = {n for n in wpt.git('diff', '--name-only').decode().splitlines() if not n.startswith('artifacts/')}
    need(native == set(inventories[phase]), 'exact native inventory for phase')
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
    if phase == 'candidate':
        if candidate_snapshot is None:
            save('CANDIDATE-SNAPSHOT.json', snapshot)
            candidate_snapshot = snapshot
        else:
            need(snapshot == candidate_snapshot, 'frozen candidate source/index/native snapshot')
    return {'snapshot': snapshot, 'pins': pins, 'installed_tests': before['installed_tests']}


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


def build(label, phase):
    global current_binaries
    pre = verify(phase, current_binaries)
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
    verify(phase, current_binaries)


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
    reference = observed if phase == 'baseline' else baseline_outcomes
    need(reference is not None, 'actual baseline required')
    return policy.assess(actual, reference, phase)


def capture(label, phase):
    global baseline_outcomes
    need(set(owned) == set(owned_plan['temporary_fixtures']), 'all owned fixtures created')
    verified = verify(phase, current_binaries)
    need(set(wpt.resource_paths(config['tests'])) <= set(verified['pins']), 'complete resource closure')
    save(label + '-PRE-CAPTURE.json', verified)
    result = prior.tests.run(wpt, label, verified['pins'])
    need(result['before'] == result['after'] == verified['pins'], 'phase role joins')
    need(verify(phase, current_binaries) == verified, 'full phase preservation')
    need(len(result['rows']) == 182 and len(result['ends']) == 13, 'full selected roster counts')
    need(all(e['status'] == e.get('expected', 'OK') == 'OK' and not e.get('known_intermittent', [])
             for e in result['ends']), 'strict OK harness metadata')
    need(all(r.get('expected', r['status']) in ('PASS', 'FAIL')
             and type(r.get('known_intermittent', [])) is list
             and all(v in ('PASS', 'FAIL') for v in r.get('known_intermittent', []))
             for r in result['rows']), 'complete row metadata')
    classified = classifier.classify([row for row in result['rows'] if row['test'] in diagnostic_tests])
    save(label + '-CLASSIFICATION.json', classified)
    actual = outcomes(result)
    differences, improvements, errors = assess(actual, phase)
    errors.extend('landing classification: ' + str(item) for item in classified['errors'])
    save(label + '-OUTCOMES.json', list(actual.values()))
    save(label + '-DIFFERENCES.json', differences)
    save(label + '-IMPROVEMENTS.json', improvements)
    save(label + '-SUMMARY.json', {'status': 'PHASE_EXACT_POLICY_PASS' if not errors else 'PHASE_SEMANTIC_REJECTION',
         'subtests': len(result['rows']), 'harnesses_ok': len(result['ends']), 'reference_passes': 0,
         'counts': {status: sum(row['status'] == status for row in result['rows']) for status in ('PASS', 'FAIL')},
         'required_repairs': len(repair_keys) if phase == 'candidate' else 0,
         'observational_only_cases': len(policy.OBSERVATIONAL),
         'manual_observational_review_required': any(item['observational_only'] for item in differences),
         'all_restored_outcomes_exact': actual == baseline_outcomes if phase == 'restored' else None,
         'upstream_unexpected_passes': sum(row['status'] == 'PASS' and row.get('expected') == 'FAIL' for row in result['rows']), 'errors': errors, 'wpt_exit': result['exit'], 'native_acceptance': False})
    captured.append(label)
    need(not errors, label + ' semantic comparison rejected; inspect SUMMARY and DIFFERENCES')
    if phase == 'baseline':
        baseline_outcomes = actual
    completed.append(phase)

def owned_group_errors():
    errors = []
    for label in ('baseline_capture', 'candidate', 'restored'):
        directory = HERE / ('wpt-' + label)
        if directory.exists():
            try:
                receipt = read(directory / 'CLEANUP.json')
                if receipt.get('owned_group_absent') is not True or receipt.get('errors') != []:
                    errors.append('owned WPT process group absence not established: ' + label)
            except BaseException as error:
                errors.append('owned WPT cleanup receipt ' + label + ': ' + repr(error))
    return errors

def cleanup_fixtures():
    removed, errors = [], owned_group_errors()
    if errors:
        return removed, errors
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
need(sha(HERE / 'compare.py') == inputs['compare_sha256'], 'bound controller')
for name, digest in inputs['manifests'].items():
    authenticate(ROOT / name, digest)
review = inputs['controller_review']
need(review is not None, 'required controller review')
authenticate(ROOT / review['path'], review['manifest_sha256'])
need(read(HERE / 'ROOT-REVIEW-BINDING.json') == {'status': 'KEYFRAME_CSS_DURATION_COMPARISON_ROOT_BINDING_GO',
     'inputs_sha256': sha(HERE / 'INPUTS.json'), 'compare_sha256': inputs['compare_sha256'],
     'controller_review_manifest_sha256': review['manifest_sha256']}, 'exact root activation binding')
for name, digest in inputs['helper_pins'].items():
    need(sha(ROOT / name) == digest, 'bound helper ' + name)
for name, digest in inputs['local_pins'].items():
    need(sha(HERE / name) == digest, 'local input ' + name)
need(read(ROOT / review['path'] / 'CHECK.json')['status'] == 'KEYFRAME_CSS_DURATION_COMPARISON_REVIEW_GO',
     'successful controller review')
epoch = read(DATA / 'BASELINE-BINDING.json')
need(epoch is not None, 'actual post-context epoch remains unbound')
BASELINE = ROOT / epoch['runtime']
authenticate(BASELINE, epoch['manifest_sha256'])
authenticate(ROOT / epoch['peer'], epoch['peer_manifest_sha256'])
need(read(ROOT / epoch['peer'] / 'CHECK.json')['status'] == 'KEYFRAME_CUSTOM_CONTEXT_DIAGNOSTIC_TERMINAL_REVIEW_GO', 'context terminal peer GO')
peer_refs = read(ROOT / epoch['peer'] / 'REFERENCES.json')
need(peer_refs[epoch['runtime'] + '/FILES.json'] == epoch['manifest_sha256']
     and peer_refs[epoch['runtime'] + '/ROOT-COMPLETION.json'] == epoch['root_receipt_sha256'], 'peer runtime/root joins')
need(sha(BASELINE / 'ROOT-COMPLETION.json') == epoch['root_receipt_sha256'], 'actual root receipt')
completion = read(BASELINE / 'ROOT-COMPLETION.json')
need(completion['status'] == 'KEYFRAME_CUSTOM_CONTEXT_DIAGNOSTIC_ROOT_PRESERVATION_PASS'
     and completion['session'] == epoch['session'] and completion['actual_exit'] == epoch['exit'] == 0,
     'verified context capture prerequisite')
need(read(BASELINE / 'ACTUAL-TERMINAL.json') == {'session': epoch['session'], 'exit': 0, 'terminal_chunk': epoch['terminal_chunk']}, 'actual observed context terminal')
verification = read(BASELINE / 'ROOT-VERIFY-TERMINAL.json')
need(verification['session'] == epoch['root_session'] and verification['exit'] == 0
     and verification['capture_session'] == epoch['session'], 'successful actual root verifier')
context_receipt = read(BASELINE / 'ROOT-FINAL-CHECK.json')
need(context_receipt['status'] == 'KEYFRAME_CUSTOM_CONTEXT_DIAGNOSTIC_PRESERVATION_PASS'
     and context_receipt['capture_error'] is None and context_receipt['native_acceptance'] is False
     and context_receipt['roles'] == 696 and context_receipt['sources'] == 79
     and context_receipt['installed_identities'] == 25 and context_receipt['temporary_tests_removed'] == 1,
     'complete context preservation')
context_owned = read(BASELINE / 'OWNED-TESTS.json')
context_cleanup = read(BASELINE / 'CLEANUP.json')
need(len(context_owned) == 1 and context_cleanup['errors'] == [] and context_cleanup['capture_error'] is None
     and set(context_cleanup['removed']) == set(context_owned)
     and read(BASELINE / 'wpt-diagnostic/CLEANUP.json') == {'owned_group_absent': True, 'errors': []}, 'context cleanup')
archived_before = read(BASELINE / 'FINAL.json')
need(archived_before == read(BASELINE / 'BEFORE.json')
     and archived_before['pins'] == read(BASELINE / 'FINAL-PINS.json')
     and completion['final_sha256'] == sha(BASELINE / 'FINAL.json')
     and completion['final_pins_sha256'] == sha(BASELINE / 'FINAL-PINS.json'), 'actual complete final joins')
prepared = read(DATA / 'PREPARED-EPOCH.json')
need(archived_before['snapshot'] == prepared['snapshot']
     and archived_before['installed_tests'] == prepared['installed_tests']
     and all(archived_before['pins'][name] == digest for name, digest in prepared['pins'].items()),
     'unchanged native/binary/index epoch from observed52')
context_fixture = 'testing/web-platform/tests/css/css-animations/keyframe-custom-property-context.html'
context_metadata = 'testing/web-platform/meta/css/css-animations/keyframe-custom-property-context.html.ini'
need(archived_before['pins'] == prepared['pins'] | {context_fixture: None, context_metadata: None}
     and len(archived_before['pins']) == 696, 'complete696 role extension including context absences')
restoration = archived_before['pins']
need(all(restoration[name] is None for name in context_owned), 'context fixture absence retained')
source_data = read(DATA / 'SOURCE-MAPS.json')
maps = {name: source_data[name] for name in ('baseline', 'candidate', 'restored')}
promotion = read(DATA / 'SOURCE-PROMOTION.json')
need(promotion['path'] not in archived_before['snapshot']['sources']
     and restoration[promotion['path']] == promotion['sha256']
     and maps['baseline'] == maps['restored'] == archived_before['snapshot']['sources'] | {promotion['path']: promotion['sha256']}
     and len(maps['baseline']) == 80, 'explicit existing-resource promotion79to80')
before = dict(archived_before, snapshot=dict(archived_before['snapshot'], sources=maps['baseline']))
inventories = read(DATA / 'NATIVE-INVENTORIES.json')
proposal = read(DATA / 'CANDIDATE.json')
bodies = proposal['native_paths']
need(set(maps['candidate']) == set(maps['baseline']) and len(bodies) == 1
     and set(bodies) == {name for name in maps['baseline'] if maps['baseline'][name] != maps['candidate'][name]}, 'one-source candidate')
for name, item in bodies.items():
    need(sha(ROOT / item['original']) == item['original_sha256'] == maps['baseline'][name]
         and sha(ROOT / item['candidate']) == item['candidate_sha256'] == maps['candidate'][name], 'exact native body')
need(sha(ROOT / proposal['patch']) == proposal['patch_sha256'], 'proposal patch')
owned_plan = {'temporary_fixtures': proposal['fixture'], 'permanent_absences': [name for name, digest in restoration.items()
              if digest is None and name not in proposal['fixture']]}
need(len(owned_plan['temporary_fixtures']) == 6 and len(before['installed_tests']) == 25
     and not set(owned_plan['temporary_fixtures']) & set(before['installed_tests']), 'six exclusive fixtures')
roster = read(DATA / 'ROSTER.json')
need(roster['expected_total'] == 182 and roster['files_expected_count'] == 13 and not roster['reftests'], 'selected182 roster')
config = read(BASELINE / 'CONFIG.json')
config.update(roster)
config.update(source_pins=maps['baseline'], guard_sources=sorted(maps['baseline']),
              resource_guard_paths=sorted(set(restoration) - set(maps['baseline'])), install={},
              must_be_absent=sorted(name for name, value in restoration.items() if value is None and name not in proposal['fixture']))
need(inventories['baseline'] == inventories['restored'] == sorted(config['modified_native_paths'])
     and len(inventories['baseline']) == 43 and len(inventories['candidate']) == 44
     and set(inventories['candidate']) == set(inventories['baseline']) | set(bodies)
     and set(inventories['candidate']) <= set(maps['candidate']), 'native43to44to43')
need(len(config['index_expectations']['staged_payload_sha256']) == 925, 'all925 payloads')
need(not set(config['existing_tests']) & set(owned_plan['temporary_fixtures']), 'fixture ownership')
for name, item in proposal['fixture'].items():
    need(restoration[name] is None and sha(ROOT / item['source']) == item['sha256'], 'exact observed fixture')
prior = load('duration_comparison_prior', PRIOR / 'validate.py')
wpt = load('duration_comparison_wpt', ROOT / config['helpers'] / 'run_wpt.py')
wpt.HERE, wpt.CONFIG, wpt.sha = HERE, config, sha
wpt.ENV = dict(prior.wpt.ENV)
architecture = load('duration_comparison_architecture', prior.OLD / 'architecture.py')
classifier = load('duration_diagnostic_classifier', HERE / 'diagnostic/classify.py')
policy = load('duration_comparison_policy', HERE / 'policy.py')
diagnostic_tests = set(read(HERE / 'diagnostic/ROSTER.json')['expected_subtests'])
outcome_sources = read(DATA / 'OUTCOME-SOURCES.json')
observed52 = ROOT / outcome_sources['diagnostic_runtime']
controls = ROOT / outcome_sources['controls_runtime']
need(inputs['manifests'][outcome_sources['diagnostic_runtime']] == outcome_sources['diagnostic_manifest']
     and inputs['manifests'][outcome_sources['controls_runtime']] == outcome_sources['controls_manifest'], 'observation archive binding')
need(sha(observed52 / 'wpt-diagnostic/RUN.json') == outcome_sources['diagnostic_run_sha256']
     and sha(controls / 'wpt-restored/RUN.json') == outcome_sources['controls_run_sha256'], 'raw observation joins')
old_final = read(controls / 'FINAL.json')
need(prepared['snapshot'] == old_final['snapshot'] and prepared['installed_tests'] == old_final['installed_tests']
     and all(prepared['pins'][n] == h for n, h in old_final['pins'].items()), 'same observed control source/binary epoch')
joined_rows = read(observed52 / 'wpt-diagnostic/RUN.json')['rows'] + [row for row in read(controls / 'wpt-restored/RUN.json')['rows']
               if row['test'] in outcome_sources['controls_tests']]
observed = outcomes({'rows': joined_rows, 'ends': []})
need(observed == outcomes({'rows': read(DATA / 'OBSERVED-ROWS.json'), 'ends': []}), 'exact observed182 union')
expected_keys = {(test, name) for test, names in config['expected_subtests'].items() for name in names}
repair_keys = {key for key, row in observed.items() if key in policy.MANDATORY and row['status'] == 'FAIL'}
need(set(observed) == expected_keys == policy.EXPECTED and len(expected_keys) == 182
     and len(policy.MANDATORY) == 6 and len(repair_keys) == 2, 'six landing/two observed repairs')
save('ARCHIVED-EPOCH.json', archived_before)

owned, transitions, captured, completed = {}, [], [], []
baseline_outcomes = None
candidate_snapshot = None
current_sources = dict(maps['baseline'])
current_binaries = {name: restoration[name] for name in wpt.BINARIES}
source_identities = {name: [(ROOT / name).lstat().st_dev, (ROOT / name).lstat().st_ino] for name in bodies}
mutation_started = False
failure, recovery_errors = None, []
initial = verify('baseline', current_binaries, active=False)
need(initial == {'snapshot': before['snapshot'], 'pins': restoration,
                 'installed_tests': before['installed_tests']}, 'actual epoch with complete extension')
save('BEFORE.json', before)
save('BASELINE-PINS.json', restoration)
save('CONFIG.json', config)
save('PRE-FLIGHT.json', initial)
save('baseline-ARCHITECTURE.json', architecture.verify(ROOT, current_binaries))
try:
    for name, item in owned_plan['temporary_fixtures'].items():
        path, source = ROOT / name, ROOT / item['source']
        need(restoration[name] is None and not path.exists() and not path.is_symlink(), 'temporary absence ' + name)
        need(sha(source) == item['sha256'], 'temporary body ' + name)
        with path.open('xb') as stream:
            info = path.lstat()
            owned[name] = {'identity': [info.st_dev, info.st_ino], 'sha256': item['sha256']}
            body = source.read_bytes()
            need(stream.write(body) == len(body), 'complete fixture write')
    save('OWNED-TESTS.json', owned)
    capture('baseline_capture', 'baseline')
    for name in bodies:
        write_source(name, 'candidate')
    build('candidate', 'candidate')
    capture('candidate', 'candidate')
except BaseException as error:
    failure = repr(error)
finally:
    try:
        recovery_errors.extend(owned_group_errors())
    except BaseException as error:
        recovery_errors.append('owned process cleanup receipt: ' + repr(error))
    if not recovery_errors:
        recovery_errors.extend(restore_sources())
    if mutation_started and not recovery_errors:
        try:
            build('restored', 'restored')
            capture('restored', 'restored')
        except BaseException as error:
            recovery_errors.append('restoration build/capture: ' + repr(error))
    removed, errors = cleanup_fixtures()
    recovery_errors.extend(errors)
    try:
        final = verify('restored', current_binaries, active=False)
        save('FINAL.json', final)
        save('FINAL-PINS.json', final['pins'])
        if not recovery_errors and (not mutation_started or 'restored' in completed):
            save('ROOT-FINAL-CHECK.json', {'status': 'ORIGINAL_STACK_RESTORED_VERIFIED' if mutation_started
                 else 'ORIGINAL_STACK_PRESERVED_NO_NATIVE_MUTATION',
                 'full_roles': 696, 'source_count': 80, 'installed_identities': 25, 'staged_paths': 925, 'native_paths': 43,
                 'completed_phases': completed, 'captured_phases': captured, 'comparison_error': failure,
                 'recovery_errors': [], 'final_pins_sha256': sha(HERE / 'FINAL-PINS.json'), 'native_acceptance': False})
    except BaseException as error:
        recovery_errors.append('final preservation/publication: ' + repr(error))
    try:
        save('CLEANUP.json', {'removed': removed, 'errors': list(recovery_errors), 'comparison_error': failure})
    except BaseException as error:
        recovery_errors.append('cleanup publication: ' + repr(error))
    save('RESULT.json', {'completed_phases': completed, 'captured_phases': captured, 'comparison_error': failure,
         'recovery_errors': recovery_errors, 'source_transitions': transitions, 'mutation_started': mutation_started,
         'fresh_baseline_established': baseline_outcomes is not None,
         'restoration_capture_required': mutation_started, 'native_acceptance': False})
need(failure is None and not recovery_errors and completed == ['baseline', 'candidate', 'restored'],
     'comparison or restoration failed; inspect retained evidence')
