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
PLAN = ROOT / 'artifacts/css-name-repeat-context-comparison-data-v1'
DATA = PLAN / 'data'
BASELINE = ROOT / 'artifacts/css-name-repeat-context-baseline-runtime-v1'
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
    if phase != 'candidate':
        need(snapshot == before['snapshot'], 'exact restored source/index/native snapshot')
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
    need(set(actual) == set(archived), 'exact outcome keys')
    differences = [{'baseline': archived[k], 'actual': v} for k, v in actual.items() if v != archived[k]]
    errors, improvements = [], []
    for key, expected in archived.items():
        value = actual[key]
        if phase == 'restored':
            if value != expected:
                errors.append('restored outcome changed: ' + str(key))
        elif expected['status'] == 'PASS':
            if value['status'] != 'PASS' or value['effective_expected'] != expected['effective_expected'] or value['known_intermittent'] != expected['known_intermittent']:
                errors.append('baseline PASS/metadata lost: ' + str(key))
        elif value['status'] == 'PASS':
            if value['effective_expected'] != expected['effective_expected'] or value['known_intermittent'] != expected['known_intermittent']:
                errors.append('improvement metadata changed: ' + str(key))
            improvements.append({'baseline': expected, 'actual': value, 'required_landing': key in repair_keys})
        elif value != expected:
            errors.append('retained FAIL changed: ' + str(key))
    if phase == 'candidate':
        for key in landing_keys:
            value = actual[key]
            if value['status'] != 'PASS' or value['effective_expected'] != 'PASS' or value['known_intermittent']:
                errors.append('candidate landing not PASS: ' + str(key))
        for key in repair_keys:
            if archived[key]['status'] != 'FAIL' or actual[key]['status'] != 'PASS':
                errors.append('required repair missing: ' + str(key))
    return differences, improvements, errors


def capture(label, phase):
    need(set(owned) == set(owned_plan['temporary_fixtures']), 'all seven fixtures created')
    verified = verify(phase, current_binaries)
    need(set(wpt.resource_paths(config['tests'])) <= set(verified['pins']), 'complete resource closure')
    save(label + '-PRE-CAPTURE.json', verified)
    result = prior.tests.run(wpt, label, verified['pins'])
    need(result['before'] == result['after'] == verified['pins'], 'phase role joins')
    need(verify(phase, current_binaries) == verified, 'full phase preservation')
    need(len(result['rows']) == 1532 and len(result['ends']) == 46, 'full capture counts')
    actual = outcomes(result)
    differences, improvements, errors = assess(actual, phase)
    save(label + '-DIFFERENCES.json', differences)
    save(label + '-IMPROVEMENTS.json', improvements)
    save(label + '-SUMMARY.json', {'status': 'PHASE_PRESERVATION_PASS_PENDING_REVIEW' if not errors else 'PHASE_SEMANTIC_REJECTION',
         'subtests': len(result['rows']), 'harnesses_ok': sum(e['status'] == 'OK' for e in result['ends']),
         'reference_passes': sum(e['status'] == 'PASS' for e in result['ends'] if e['test'] in config['reftests']),
         'counts': {s: sum(r['status'] == s for r in result['rows']) for s in ('PASS', 'FAIL')},
         'required_repairs': len(repair_keys) if phase == 'candidate' else 0,
         'additional_improvements': sum(not x['required_landing'] for x in improvements),
         'errors': errors, 'wpt_exit': result['exit'], 'native_acceptance': False})
    captured.append(label)
    need(not errors, label + ' semantic comparison rejected; inspect SUMMARY and DIFFERENCES')
    completed.append(label)


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
need(sha(HERE / 'compare.py') == inputs['compare_sha256'], 'bound controller')
for name, digest in inputs['manifests'].items():
    authenticate(ROOT / name, digest)
need(inputs['controller_review'] is not None, 'required controller review')
review = inputs['controller_review']
authenticate(ROOT / review['path'], review['manifest_sha256'])
need(read(HERE / 'ROOT-REVIEW-BINDING.json') == {'status': 'NAME_REPEAT_COMPARISON_ROOT_BINDING_GO',
     'inputs_sha256': sha(HERE / 'INPUTS.json'), 'compare_sha256': inputs['compare_sha256'],
     'controller_review_manifest_sha256': review['manifest_sha256']}, 'exact root activation binding')
for name, digest in inputs['helper_pins'].items():
    need(sha(ROOT / name) == digest, 'bound helper ' + name)
prior = load('name_repeat_comparison_prior', PRIOR / 'validate.py')
before = read(BASELINE / 'FINAL.json')
restoration = read(DATA / 'RESTORATION-PINS.json')
need(before['pins'] == restoration == read(BASELINE / 'FINAL-PINS.json') and len(restoration) == 611, 'complete baseline role join')
source_data = read(DATA / 'SOURCE-MAPS.json')
maps = {name: source_data[name] for name in ('baseline', 'candidate', 'restored')}
bodies = source_data['bodies']
need(before['snapshot']['sources'] == maps['baseline'] == maps['restored'] and len(maps['baseline']) == 72, 'all original sources')
need(set(bodies) == {k for k in maps['baseline'] if maps['baseline'][k] != maps['candidate'][k]} and len(bodies) == 2, 'exact two-source candidate')
owned_plan = read(DATA / 'OWNERSHIP.json')
need(owned_plan['installed_identities'] == before['installed_tests'] and len(before['installed_tests']) == 23, 'installed identities')
need(len(owned_plan['temporary_fixtures']) == 7 and not set(owned_plan['temporary_fixtures']) & set(before['installed_tests']), 'exclusive fixtures')
roster = read(DATA / 'ROSTER.json')
config = read(BASELINE / 'CONFIG.json')
config.update({key: roster[key] for key in ('tests', 'expected_subtests', 'reftests')})
config['tests'] = ['testing/web-platform/tests' + name for name in roster['tests']]
config.update(expected_total=1532, files_expected_count=46, source_pins=maps['baseline'], guard_sources=sorted(maps['baseline']),
              resource_guard_paths=sorted(read(DATA / 'RESOURCES.json')), install={})
config['modified_native_paths'] = sorted(set(config['modified_native_paths']) | {'servo/components/style/values/generics/calc.rs'})
need(len(config['modified_native_paths']) == 43 and set(bodies) <= set(config['modified_native_paths']) <= set(maps['baseline']), 'native source inventory')
need(len(config['index_expectations']['staged_payload_sha256']) == 925, 'all staged payloads')
need(not set(config['existing_tests']) & set(owned_plan['temporary_fixtures']), 'temporary fixtures not read-only tests')
wpt = load('name_repeat_comparison_wpt', ROOT / config['helpers'] / 'run_wpt.py')
wpt.HERE, wpt.CONFIG, wpt.sha = HERE, config, sha
wpt.ENV = dict(prior.wpt.ENV)
architecture = load('name_repeat_comparison_architecture', prior.OLD / 'architecture.py')
policy = read(DATA / 'EXPERIMENT-POLICY.json')
landing_keys = {(x['test'], x['subtest']) for x in policy['candidate_required_PASS']}
repair_keys = {(x['test'], x['subtest']) for x in policy['observed_repair_witnesses']}
archived = {(x['test'], x['subtest']): x for x in read(DATA / 'ARCHIVED-OUTCOMES.json')}
need(len(archived) == 1540 and len(landing_keys) == 10 and len(repair_keys) == 8 and repair_keys <= landing_keys, 'exact archived roster and targets')
owned, transitions, captured, completed = {}, [], [], []
current_sources = dict(maps['baseline'])
current_binaries = {name: restoration[name] for name in wpt.BINARIES}
source_identities = {name: [(ROOT / name).stat().st_dev, (ROOT / name).stat().st_ino] for name in bodies}
mutation_started = False
failure, recovery_errors = None, []
need(verify('baseline', current_binaries, active=False) == before, 'actual archived epoch')
save('BEFORE.json', before)
save('CONFIG.json', config)
save('PRE-FLIGHT.json', before)
save('baseline-ARCHITECTURE.json', architecture.verify(ROOT, current_binaries))
try:
    for name, item in owned_plan['temporary_fixtures'].items():
        path, source = ROOT / name, ROOT / item['source']
        need(restoration[name] is None and not path.exists() and not path.is_symlink(), 'temporary absence ' + name)
        need(sha(source) == item['sha256'], 'temporary body ' + name)
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
except BaseException as error:
    failure = repr(error)
finally:
    recovery_errors.extend(restore_sources())
    if not recovery_errors:
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
        if not recovery_errors and 'restored' in completed:
            save('ROOT-FINAL-CHECK.json', {'status': 'ORIGINAL_STACK_RESTORED_VERIFIED',
                 'full_roles': 611, 'source_count': 72, 'installed_identities': 23, 'staged_paths': 925, 'native_paths': 43,
                 'completed_phases': completed, 'captured_phases': captured, 'comparison_error': failure,
                 'recovery_errors': [], 'final_pins_sha256': sha(HERE / 'FINAL-PINS.json'), 'native_acceptance': False})
    except BaseException as error:
        recovery_errors.append('final preservation: ' + repr(error))
    save('CLEANUP.json', {'removed': removed, 'errors': recovery_errors, 'comparison_error': failure})
save('RESULT.json', {'completed_phases': completed, 'captured_phases': captured, 'comparison_error': failure,
                     'recovery_errors': recovery_errors, 'source_transitions': transitions,
                     'mutation_started': mutation_started, 'native_acceptance': False})
need(failure is None and not recovery_errors and completed == ['candidate', 'restored'], 'comparison or restoration failed; inspect retained evidence')
