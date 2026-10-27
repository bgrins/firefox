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
PLAN = ROOT / 'artifacts/css-round-numerical-baseline-plan-v2'
PRIOR = ROOT / 'artifacts/css-counter-additive-install-runtime-v1'
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
        need(not Path(name).is_absolute() and '..' not in Path(name).parts,
             'relative manifest member')
        path = directory / name
        need(stat.S_ISREG(path.lstat().st_mode) and sha(path) == value, 'payload ' + name)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_roles(wpt, pins):
    need(wpt.pins(list(pins)) == pins, 'full role contents')
    for name, digest in pins.items():
        path = ROOT / name
        need((not path.exists() and not path.is_symlink()) if digest is None
             else stat.S_ISREG(path.lstat().st_mode), 'role type ' + name)


authenticate(PLAN, '11a466f65680865176806642ef363bc211e451ee6c52b6256c2c170534f6de9a')
authenticate(PRIOR, 'dfe49f900d2ba34410520beabc165b0cb40639ca06fcc19ebe8dab1316b51bb5')
authenticate(ROOT / 'artifacts/css-counter-additive-install-results-review-v1',
             '2dff296aece7b2031e6934fe959eba3705f362ce8c12ad0beb0386defc4c932e')
prior = load('numerical_prior', PRIOR / 'validate.py')
before = prior.verify()
need(before == read(PRIOR / 'INSTALLATION.json')['after'], 'latest installed epoch')
save('BEFORE.json', before)
fixtures = read(PLAN / 'FIXTURES.json')
roles = read(PLAN / 'OWNERSHIP-PLAN.json')['roles']
baseline_pins = dict(before['pins'])
for role in roles:
    name = role['path']
    need((name in baseline_pins) == role['archived_role_present'], 'absence role membership')
    need(baseline_pins.get(name) is None, 'absence role value')
    path = ROOT / name
    need(not path.exists() and not path.is_symlink(), 'live absence ' + name)
    baseline_pins[name] = None
need(len(baseline_pins) == 605, 'complete extended baseline roles')
save('BASELINE-PINS.json', baseline_pins)
config = dict(prior.config)
config.update(tests=['testing/web-platform/tests/' + f['wpt_relative'] for f in fixtures],
              expected_subtests=read(PLAN / 'ROSTER.json'), reftests=[], install={},
              expected_total=42, files_expected_count=4)
save('CONFIG.json', config)
wpt = load('numerical_wpt', ROOT / config['helpers'] / 'run_wpt.py')
wpt.HERE, wpt.CONFIG = HERE, config
wpt.ENV = dict(prior.wpt.ENV)
owned = {}
active_pins = dict(baseline_pins)
error = None
try:
    for fixture in fixtures:
        name = 'testing/web-platform/tests/' + fixture['wpt_relative']
        path = ROOT / name
        source = PLAN / fixture['local']
        need(sha(source) == fixture['sha256'], 'fixture body')
        with path.open('xb') as stream:
            info = path.lstat()
            owned[name] = {'identity': [info.st_dev, info.st_ino], 'sha256': fixture['sha256']}
            stream.write(source.read_bytes())
        active_pins[name] = fixture['sha256']
    save('OWNED-TESTS.json', owned)
    verify_roles(wpt, active_pins)
    need(set(wpt.resource_paths(config['tests'])) <= set(active_pins), 'resource closure')
    need(wpt.snapshot() == before['snapshot'], 'source/index snapshot')
    prior.index.index_state(wpt)
    need(not wpt.git('ls-files', '--', *owned), 'owned fixtures untracked')
    architecture = load('numerical_architecture', prior.OLD / 'architecture.py')
    save('ARCHITECTURE.json', architecture.verify(ROOT, read(PRIOR / 'BUILT-BINARIES.json')))
    save('PRE-CAPTURE.json', {'pins': active_pins, 'snapshot': before['snapshot'],
                             'installed_tests': before['installed_tests']})
    result = prior.tests.run(wpt, 'diagnostic', active_pins)
    need(result['before'] == result['after'] == active_pins, 'exact active preservation')
    verify_roles(wpt, active_pins)
    save('CAPTURE.json', {'status': 'COMPLETE_DIAGNOSTIC_CAPTURE',
                         'subtests': len(result['rows']), 'harnesses': len(result['ends']),
                         'wpt_exit': result['exit'], 'native_candidate_applied': False,
                         'classification_pending': True})
except BaseException as failure:
    error = repr(failure)
    raise
finally:
    removed = []
    cleanup_errors = []
    for name, item in owned.items():
        try:
            path = ROOT / name
            info = path.lstat()
            need(stat.S_ISREG(info.st_mode) and [info.st_dev, info.st_ino] == item['identity']
                 and sha(path) == item['sha256'], 'cleanup ownership ' + name)
            path.unlink()
            removed.append(name)
        except BaseException as failure:
            cleanup_errors.append(repr(failure))
    save('CLEANUP.json', {'removed': removed, 'errors': cleanup_errors, 'capture_error': error})
    need(not cleanup_errors, 'fixture cleanup')
    final = prior.verify()
    need(final == before, 'full final preservation')
    verify_roles(wpt, baseline_pins)
    save('FINAL.json', final)
    save('FINAL-PINS.json', baseline_pins)
    save('ROOT-FINAL-CHECK.json', {'status': 'NUMERICAL_BASELINE_PRESERVATION_PASS',
         'roles': 605, 'sources': 72, 'installed_identities': 21, 'staged_paths': 925,
         'native_paths': 42, 'temporary_tests_removed': len(removed), 'capture_error': error,
         'final_pins_sha256': sha(HERE / 'FINAL-PINS.json')})
print(json.dumps(read(HERE / 'CAPTURE.json'), indent=2))
