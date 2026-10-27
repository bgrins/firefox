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
FIXTURES = ROOT / 'artifacts/css-name-repeat-context-repair-v3'
PROPOSAL = ROOT / 'artifacts/css-name-repeat-context-repair-v1'
BUILD = ROOT / 'artifacts/css-round-runtime-finite-install-runtime-v1'
INSTALLED = ROOT / 'artifacts/css-round-infinite-value-step-runtime-v1'
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


inputs = read(HERE / 'INPUTS.json')
need(sha(HERE / 'capture.py') == inputs['capture_sha256'], 'bound capture')
authenticate(FIXTURES, '454359c092351c37d751f6fcdb21b75cb7959233dfc05523183d84bb8fbeb259')
authenticate(PROPOSAL, '046289055e5ed4da18d074590ed240513c39378c28f3b73ecb5f7da83ea08308')
authenticate(ROOT / 'artifacts/css-name-repeat-context-repair-review-v1',
             '142d06e2a55683d48c321ad33bd57665234aef4dbe9210b43e54f30b91327180')
authenticate(ROOT / 'artifacts/css-name-repeat-context-repair-review-v3',
             '68913d02e764ccdf32572e2e1755ad61a4e09fc21ac23fb30dc4849515577935')
authenticate(INSTALLED, '736a7240a8105a2e765a93b0d6862ce808e010fb77953869575e9188ba86fc5a')
authenticate(ROOT / 'artifacts/css-round-infinite-value-step-terminal-review-v1',
             '328645f2d9edd5485742cf3503e3f4c1396ae67260993082756fed6bfbd17335')
authenticate(BUILD, 'eae0a81631d0302df59dc71ec0c796ddb7a2c24f5e959a1c5c63b69139225e1d')
authenticate(PRIOR, 'dfe49f900d2ba34410520beabc165b0cb40639ca06fcc19ebe8dab1316b51bb5')
prior = load('name_repeat_prior', PRIOR / 'validate.py')
before = read(INSTALLED / 'FINAL.json')
need(before['pins'] == read(INSTALLED / 'FINAL-PINS.json'), 'installed role join')
test_name = 'testing/web-platform/tests/css/css-grid/subgrid/subgrid-contextual-name-repeat.html'
fixtures = {'subgrid-contextual-name-repeat.html': {
    'future_wpt_path': test_name,
    'sha256': '81e4da216fbf4cd31a500f4b4d8156bd633205000823a4f12057ce0c6cb5d3f3'}}
delta = {'new_roles': [{'path': name, 'proposed_before': None, 'proposed_after': None}
                      for name in [test_name, test_name.replace('/tests/', '/meta/') + '.ini']],
         'temporary_phase_overrides': {test_name: fixtures['subgrid-contextual-name-repeat.html']['sha256']}}
for name, digest in read(PROPOSAL / 'SOURCE-PINS.json').items():
    if name.startswith('original-installed/'):
        need(before['snapshot']['sources'][name.removeprefix('original-installed/')] == digest,
             'current grid source preimage')
baseline_pins = dict(before['pins'])
for role in delta['new_roles']:
    name = role['path']
    need(name not in baseline_pins and role['proposed_before'] is None
         and role['proposed_after'] is None, 'new absent role ' + name)
    baseline_pins[name] = None
need(len(baseline_pins) == 611 and len(before['snapshot']['sources']) == 72
     and len(before['installed_tests']) == 23, 'exact inherited scope')
config = read(INSTALLED / 'CONFIG.json')
config.update(tests=[item['future_wpt_path'] for item in fixtures.values()],
              expected_subtests={'/css/css-grid/subgrid/subgrid-contextual-name-repeat.html': read(FIXTURES / 'ROSTER.json')}, reftests=[], install={},
              expected_total=10, files_expected_count=1)
need(not set(config['tests']) & set(config['existing_tests']), 'new fixture ownership')
save('BEFORE.json', before)
save('BASELINE-PINS.json', baseline_pins)
save('CONFIG.json', config)
wpt = load('name_repeat_wpt', ROOT / config['helpers'] / 'run_wpt.py')
wpt.HERE, wpt.CONFIG, wpt.sha = HERE, config, sha
wpt.ENV = dict(prior.wpt.ENV)
owned = {}


def verify(active=False):
    pins = dict(baseline_pins)
    if active:
        pins.update({name: item['sha256'] for name, item in owned.items()})
    for name, digest in pins.items():
        path = ROOT / name
        need((not path.exists() and not path.is_symlink()) if digest is None else
             stat.S_ISREG(path.lstat().st_mode) and sha(path) == digest, 'role ' + name)
    snapshot = wpt.snapshot()
    need(snapshot == before['snapshot'], 'exact source/index snapshot')
    native = {name for name in wpt.git('diff', '--name-only').decode().splitlines()
              if not name.startswith('artifacts/')}
    inventory = set(config['modified_native_paths']) | {'servo/components/style/values/generics/calc.rs'}
    need(native == inventory and len(native) == 43, 'exact native inventory')
    need(not wpt.git('ls-files', '--others', '--exclude-standard', '--',
                     'layout', 'dom', 'servo', 'mfbt'), 'no untracked native')
    identities = {**before['installed_tests'], **(owned if active else {})}
    for name, item in identities.items():
        info = (ROOT / name).lstat()
        need(stat.S_ISREG(info.st_mode) and [info.st_dev, info.st_ino] == item['identity']
             and sha(ROOT / name) == item['sha256'], 'test identity ' + name)
    need(not wpt.git('ls-files', '--', *identities, *[r['path'] for r in delta['new_roles']]),
         'installed/temporary tests and new metadata untracked')
    need(wpt.pins(config['existing_tests']) == config['existing_test_pins']
         and wpt.git('ls-files', '--', *config['existing_tests']).decode().splitlines()
         == config['tracked_existing_tests'], 'existing test ownership')
    prior.index.index_state(wpt)
    for name, digest in config['index_expectations']['staged_payload_sha256'].items():
        need(sha(ROOT / name) == digest, 'working staged payload ' + name)
    return {'snapshot': snapshot, 'pins': pins, 'installed_tests': before['installed_tests']}


save('PRE-FLIGHT.json', verify())
architecture = load('name_repeat_architecture', prior.OLD / 'architecture.py')
save('ARCHITECTURE.json', architecture.verify(ROOT, read(BUILD / 'installed-BINARIES.json')))
error = None
try:
    for local, item in fixtures.items():
        name = item['future_wpt_path']
        source, path = FIXTURES / local, ROOT / name
        need(baseline_pins[name] is None and not path.exists() and not path.is_symlink(), 'fixture absence')
        need(sha(source) == item['sha256'] == delta['temporary_phase_overrides'][name], 'fixture body')
        with path.open('xb') as stream:
            info = path.lstat()
            owned[name] = {'identity': [info.st_dev, info.st_ino], 'sha256': item['sha256']}
            stream.write(source.read_bytes())
    save('OWNED-TESTS.json', owned)
    active = verify(active=True)
    need(set(wpt.resource_paths(config['tests'])) <= set(active['pins']), 'resource closure')
    save('PRE-CAPTURE.json', active)
    result = prior.tests.run(wpt, 'diagnostic', active['pins'])
    need(result['before'] == result['after'] == active['pins'], 'capture preservation')
    need(verify(active=True) == active, 'complete active preservation')
    save('CAPTURE.json', {'status': 'COMPLETE_DIAGNOSTIC_CAPTURE', 'subtests': len(result['rows']),
                         'harnesses': len(result['ends']), 'wpt_exit': result['exit'],
                         'native_candidate_applied': False, 'classification_pending': True})
except BaseException as failure:
    error = repr(failure)
    raise
finally:
    removed, cleanup_errors = [], []
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
    final = verify()
    save('FINAL.json', final)
    save('FINAL-PINS.json', final['pins'])
    save('ROOT-FINAL-CHECK.json', {'status': 'NAME_REPEAT_BASELINE_PRESERVATION_PASS',
         'roles': 611, 'sources': 72, 'installed_identities': 23, 'staged_paths': 925,
         'native_paths': 43, 'temporary_tests_removed': len(removed), 'capture_error': error,
         'final_pins_sha256': sha(HERE / 'FINAL-PINS.json'), 'native_acceptance': False})
print(json.dumps(read(HERE / 'CAPTURE.json'), indent=2))
