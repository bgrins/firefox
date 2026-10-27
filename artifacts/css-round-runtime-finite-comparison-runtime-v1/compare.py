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
PLAN = ROOT / 'artifacts/css-round-runtime-finite-comparison-data-v1'
PRIOR = ROOT / 'artifacts/css-counter-additive-install-runtime-v1'
NUMERICAL = ROOT / 'artifacts/css-round-numerical-baseline-runtime-v1'
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def need(ok, message):
    if not ok:
        raise RuntimeError(message)


def save(name, value):
    with (HERE / name).open('x') as stream:
        stream.write(json.dumps(value, indent=2) + '\n')


def authenticate(directory, digest):
    need(sha(directory / 'FILES.json') == digest, 'manifest ' + str(directory))
    for name, value in read(directory / 'FILES.json').items():
        need(not Path(name).is_absolute() and '..' not in Path(name).parts, 'manifest relative path')
        path = directory / name
        need(stat.S_ISREG(path.lstat().st_mode) and sha(path) == value, 'payload ' + name)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


authenticate(PLAN, 'a885b08993116b58f786484fe217b6f0bd62b0705cb516e53f26313243f31c09')
authenticate(ROOT / 'artifacts/css-round-runtime-finite-comparison-data-review-v1',
             '92b63fccc03238197af61c9238cbafe153ed4d36d388fc05b1010ca1a883c7ad')
authenticate(PRIOR, 'dfe49f900d2ba34410520beabc165b0cb40639ca06fcc19ebe8dab1316b51bb5')
authenticate(NUMERICAL, '6488e9596b36cae63c72478be7d533b57812bdd2d680507807160b1d168cbd53')
authenticate(ROOT / 'artifacts/css-round-numerical-baseline-terminal-review-v1',
             '34f469c07bcc45acf493d3e3dc2e9623b2ee34e2f7fd1efdd1b84e8bb93c955c')
prior = load('round_comparison_prior', PRIOR / 'validate.py')
before = prior.verify()
need(before == read(NUMERICAL / 'FINAL.json'), 'actual installed epoch')
save('BEFORE.json', before)
restoration = read(PLAN / 'RESTORATION-PINS.json')
need(restoration == read(NUMERICAL / 'FINAL-PINS.json') and len(restoration) == 605, 'full role inheritance')
sources = read(PLAN / 'SOURCE-MAPS.json')
maps = sources['source_maps']
source_name = sources['path']
source_path = ROOT / source_name
need(before['snapshot']['sources'] == maps['baseline'], 'complete original sources')
need(set(prior.expected['modified_native_paths']) <= set(maps['baseline']), 'guard every modified native path')
owned_plan = read(PLAN / 'OWNERSHIP.json')
need(owned_plan['installed_identities'] == before['installed_tests'], 'installed identities inherited')
roster = read(PLAN / 'ROSTER.json')
config = dict(prior.config)
config.update({key: roster[key] for key in ('tests', 'expected_subtests', 'reftests')})
config['tests'] = ['testing/web-platform/tests' + name for name in roster['tests']]
config.update(expected_total=1484, files_expected_count=43)
need(not set(config['existing_tests']) & set(owned_plan['temporary_fixtures']), 'temporary ownership disjoint')
save('CONFIG.json', config)
wpt = load('round_comparison_wpt', ROOT / config['helpers'] / 'run_wpt.py')
wpt.HERE, wpt.CONFIG = HERE, config
wpt.ENV = dict(prior.wpt.ENV)
architecture = load('round_comparison_architecture', prior.OLD / 'architecture.py')
mandatory = read(PLAN / 'MANDATORY.json')
archived = {(r['test'], r['subtest']): r for r in read(PLAN / 'ARCHIVED-OUTCOMES.json')}
need(len(archived) == 1492, 'unique archived union')
owned = {}
current_phase = 'baseline'
current_binaries = {n: restoration[n] for n in wpt.BINARIES}
source_identity = [source_path.stat().st_dev, source_path.stat().st_ino]
mutation_started = False
baseline_completed = False
completed = []
phase_outcomes = {}


def verify_roles(pins):
    need(wpt.pins(list(pins)) == pins, 'full role contents')
    for name, digest in pins.items():
        path = ROOT / name
        need((not path.exists() and not path.is_symlink()) if digest is None
             else stat.S_ISREG(path.lstat().st_mode), 'role type ' + name)


def verify(phase, binaries, active=True):
    pins = {**restoration, **maps[phase], **binaries}
    if active:
        pins.update({n: x['sha256'] for n, x in owned.items()})
    verify_roles(pins)
    snapshot = wpt.snapshot()
    need(snapshot['sources'] == maps[phase], 'source phase')
    for key in ('head', 'index_diff_sha256', 'index_entries_sha256'):
        need(snapshot[key] == before['snapshot'][key], 'preserved ' + key)
    if phase == 'baseline':
        need(snapshot['native_diff_sha256'] == before['snapshot']['native_diff_sha256'], 'exact original native diff')
    native = [n for n in wpt.git('diff', '--name-only').decode().splitlines() if not n.startswith('artifacts/')]
    inventory = set(prior.expected['modified_native_paths'])
    if phase != 'baseline':
        inventory.add(source_name)
    need(set(native) == inventory, 'exact native path inventory')
    need(not wpt.git('ls-files', '--others', '--exclude-standard', '--', 'layout', 'dom', 'servo', 'mfbt'), 'no untracked native')
    identities = dict(before['installed_tests'])
    if active:
        identities.update(owned)
    for name, item in identities.items():
        path = ROOT / name
        info = path.lstat()
        need(stat.S_ISREG(info.st_mode) and [info.st_dev, info.st_ino] == item['identity']
             and sha(path) == item['sha256'], 'test identity ' + name)
    need(not wpt.git('ls-files', '--', *identities), 'owned tests untracked')
    need(wpt.pins(config['existing_tests']) == config['existing_test_pins']
         and wpt.git('ls-files', '--', *config['existing_tests']).decode().splitlines()
         == config['tracked_existing_tests'], 'existing test ownership')
    prior.index.index_state(wpt)
    return {'snapshot': snapshot, 'pins': pins, 'installed_tests': before['installed_tests']}


def write_source(phase, recovery=False):
    global current_phase, mutation_started
    if not recovery:
        verify(current_phase, current_binaries)
    info = source_path.lstat()
    need(stat.S_ISREG(info.st_mode) and [info.st_dev, info.st_ino] == source_identity
         and sha(source_path) == maps[current_phase][source_name], 'source write ownership')
    candidate = PLAN / ('original' if phase == 'baseline' else 'candidate/' + phase) / source_name
    need(sha(candidate) == maps[phase][source_name], 'reviewed source postimage')
    mutation_started = True
    source_path.write_bytes(candidate.read_bytes())
    need(sha(source_path) == maps[phase][source_name], 'source write result')
    current_phase = phase


def build(name):
    global current_binaries
    code = wpt.command(name + '-build', ['./mach', 'build', 'binaries'])
    current_binaries = wpt.pins(wpt.BINARIES)
    save(name + '-BINARIES.json', current_binaries)
    need(code == 0 and all(current_binaries.values()), 'successful build ' + name)
    save(name + '-ARCHITECTURE.json', architecture.verify(ROOT, current_binaries))
    verify(current_phase, current_binaries)


def outcomes(result):
    rows = [(r, r['subtest']) for r in result['rows']]
    rows += [(r, None) for r in result['ends'] if r['test'] in config['reftests']]
    return {(r['test'], sub): {'test': r['test'], 'subtest': sub, 'status': r['status'],
            'message': r.get('message'), 'expected': r.get('expected'),
            'effective_expected': r.get('expected', r['status']),
            'known_intermittent': r.get('known_intermittent', [])} for r, sub in rows}


def capture(label, policy_phase):
    verified = verify(current_phase, current_binaries)
    need(set(wpt.resource_paths(config['tests'])) <= set(verified['pins']), 'complete resource closure')
    result = prior.tests.run(wpt, label, verified['pins'])
    need(result['before'] == result['after'] == verified['pins'], 'phase map joins')
    need(verify(current_phase, current_binaries) == verified, 'full phase preservation')
    actual = outcomes(result)
    need(set(actual) == set(archived), 'exact outcome keys')
    differences = [{'baseline': archived[key], 'actual': value}
                   for key, value in actual.items() if value != archived[key]]
    save(label + '-DIFFERENCES.json', differences)
    repairs = set()
    if policy_phase != 'baseline':
        rules = mandatory['candidate_families'][policy_phase]
        repairs = {(r['test'], r['subtest']) for r in rules['required_repairs']}
        for test, names in rules['required_pass'].items():
            need(all(actual[test, n]['status'] == 'PASS' for n in names), 'all candidate landing cases')
    for key, expected in archived.items():
        value = actual[key]
        if key in repairs:
            need(expected['status'] == 'FAIL' and value['status'] == 'PASS'
                 and value['effective_expected'] == 'PASS' and value['known_intermittent'] == [],
                 'target repair ' + str(key))
        else:
            need(value == expected, 'changed non-target outcome ' + str(key))
    for test, names in mandatory['installed_mandatory']['subtests'].items():
        need(all(actual[test, name]['status'] == 'PASS' for name in names), 'installed mandatory cases')
    need(all(actual[test, None]['status'] == 'PASS' for test in config['reftests']), 'all references')
    if policy_phase == 'combined_optional':
        for single in ('runtime_nan_only', 'finite_zero_only'):
            single_repairs = {(r['test'], r['subtest'])
                              for r in mandatory['candidate_families'][single]['required_repairs']}
            remaining = repairs - single_repairs
            for key, previous in phase_outcomes[single].items():
                if key in remaining:
                    need(previous['status'] == 'FAIL' and actual[key]['status'] == 'PASS', 'remaining combined repair')
                else:
                    need(actual[key] == previous, 'combined preservation against ' + single + ': ' + str(key))
    summary = {'status': 'PHASE_COMPARISON_PASS', 'subtests': len(result['rows']),
               'harnesses_ok': sum(e['status'] == 'OK' for e in result['ends']),
               'reference_passes': len(config['reftests']), 'required_repairs': len(repairs),
               'counts': {s: sum(r['status'] == s for r in result['rows']) for s in ('PASS', 'FAIL')},
               'all_other_outcomes_exact': True, 'wpt_exit': result['exit']}
    save(label + '-SUMMARY.json', summary)
    phase_outcomes[label] = actual
    completed.append(label)
    print(label + ': ' + json.dumps(summary), flush=True)


verify_roles(restoration)
save('PRE-FLIGHT.json', {'preservation': before, 'pins': restoration})
failure = None
recovery_errors = []
try:
    for name, item in owned_plan['temporary_fixtures'].items():
        path = ROOT / name
        need(restoration[name] is None and not path.exists() and not path.is_symlink(), 'temporary absence')
        source = ROOT / item['source']
        need(sha(source) == item['sha256'], 'temporary body')
        with path.open('xb') as stream:
            info = path.lstat()
            owned[name] = {'identity': [info.st_dev, info.st_ino], 'sha256': item['sha256']}
            stream.write(source.read_bytes())
    save('OWNED-TESTS.json', owned)
    verify('baseline', current_binaries)
    capture('baseline_capture', 'baseline')
    baseline_completed = True
    for phase in ('runtime_nan_only', 'finite_zero_only', 'combined'):
        write_source(phase)
        build(phase)
        capture(phase, 'combined_optional' if phase == 'combined' else phase)
except BaseException as error:
    failure = repr(error)
finally:
    try:
        if mutation_started:
            write_source('baseline', recovery=True)
            build('restored')
            if baseline_completed:
                capture('restored', 'baseline')
    except BaseException as error:
        recovery_errors.append(repr(error))
    removed = []
    for name, item in owned.items():
        try:
            path = ROOT / name
            info = path.lstat()
            need(stat.S_ISREG(info.st_mode) and [info.st_dev, info.st_ino] == item['identity']
                 and sha(path) == item['sha256'], 'cleanup identity ' + name)
            path.unlink()
            removed.append(name)
        except BaseException as error:
            recovery_errors.append(repr(error))
    if not recovery_errors:
        try:
            final = verify('baseline', current_binaries, active=False)
            save('FINAL.json', final)
            save('FINAL-PINS.json', final['pins'])
            save('ROOT-FINAL-CHECK.json', {'status': 'ORIGINAL_STACK_RESTORED_VERIFIED',
                 'full_roles': 605, 'source_count': 72, 'installed_identities': 21,
                 'staged_paths': 925, 'native_paths': 42, 'completed_phases': completed,
                 'comparison_error': failure, 'recovery_errors': [],
                 'final_pins_sha256': sha(HERE / 'FINAL-PINS.json'), 'new_acceptance': False})
        except BaseException as error:
            recovery_errors.append('final preservation: ' + repr(error))
    save('CLEANUP.json', {'removed': removed, 'errors': recovery_errors, 'comparison_error': failure})
save('RESULT.json', {'completed_phases': completed, 'comparison_error': failure,
                     'recovery_errors': recovery_errors, 'native_acceptance': False})
need(failure is None and not recovery_errors, 'comparison or restoration failed; inspect retained evidence')
