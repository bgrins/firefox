import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import stat
import sys
import types

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OBJ = ROOT / 'objdir-full.noindex'
FIXTURE = 'testing/web-platform/tests/css/css-animations/registered-keyframe-invalid-endpoint.html'
SOURCE = ROOT / 'artifacts/css-keyframe-invalid-registered-endpoint-diagnostic-v1/registered-keyframe-invalid-endpoint.html'

read = lambda p: json.loads(p.read_text())
cancelled = False


def need(ok, message):
    if not ok:
        raise RuntimeError(message)


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def save(name, value):
    with (HERE / name).open('x') as stream:
        stream.write(json.dumps(value, indent=2, sort_keys=True) + '\n')


def terminate(signum, frame):
    global cancelled
    cancelled = True


def compare_rows(rows, baseline_rows):
    normalized = lambda r: {k: r.get(k) for k in ('test', 'subtest', 'status', 'message', 'expected', 'known_intermittent')}
    actual = {(r['test'], r['subtest']): normalized(r) for r in rows}
    baseline = {(r['test'], r['subtest']): normalized(r) for r in baseline_rows}
    need(len(actual) == len(rows) and len(baseline) == len(baseline_rows), 'duplicate outcome identity')
    return [dict(identity=list(key), before=baseline.get(key), after=actual.get(key))
            for key in sorted(set(actual) | set(baseline)) if actual.get(key) != baseline.get(key)]


def main():
    inputs = read(HERE / 'INPUTS.json')
    need(sys.argv[1:] == ['--run'] and inputs['ready'] is True, 'Disabled diagnostic')
    for name, pin in inputs['local_pins'].items():
        need(sha(HERE / name) == pin, 'local body ' + name)
    for name, pin in read(HERE / 'REFERENCES.json').items():
        need(sha(ROOT / name) == pin, 'reference ' + name)
    need(read(HERE / 'ROOT-ACTIVATION.json') == {'inputs_sha256': sha(HERE / 'INPUTS.json'),
         'status': 'COMPACT_OWNER_BROWSER_COMPARISON_ROOT_GO'}, 'root reviewed activation')
    h = load('epoch_helpers', ROOT / 'artifacts/css-keyframe-commit-styles-implicit-clean-comparison-v1/compare.py')
    tests = load('owned_wpt_tests', ROOT / 'artifacts/css-keyframe-commit-styles-clean-wpt-preparation-v4/tests.py')
    ports = load('reviewed_ports', ROOT / 'artifacts/css-keyframe-commit-styles-clean-cost-capture-v3/capture.py')
    parser = load('endpoint_classifier', HERE / 'classify.py')
    ports.V4 = HERE
    binding = inputs['execution_epoch']
    need(isinstance(binding, dict) and sha(ROOT / binding['path']) == binding['sha256'], 'actual execution epoch')
    epoch = read(ROOT / binding['path'])
    owner = load('owner_epoch', HERE / 'owner_epoch.py')
    owner_ref = inputs['owner_runtime_manifest']
    need(isinstance(owner_ref, dict), 'actual completed owner runtime')
    manifest = ROOT / owner_ref['path']
    need(manifest.name == 'FILES.json' and sha(manifest) == owner_ref['sha256'], 'sealed owner runtime')
    source_maps = {}
    for key in ('reviewed_sources', 'expected_applied'):
        ref = inputs[key]
        need(isinstance(ref, dict) and sha(ROOT / ref['path']) == ref['sha256'], 'reviewed source binding ' + key)
        source_maps[key] = read(ROOT / ref['path'])
    need(set(read(HERE / 'REQUIRED-SOURCE-PATHS.json')) <= set(source_maps['reviewed_sources']), 'retained source closure')
    compiled = owner.admit(epoch, manifest, source_maps['reviewed_sources'],
                           read(ROOT / 'artifacts/css-keyframe-animation-rule-owner-host-combined-v2/GTEST-SELECTION.json'),
                           source_maps['expected_applied'], read(HERE / 'OWNER-PRODUCER.json'))
    roles = dict(epoch['pins'])
    need(set(read(HERE / 'REQUIRED-ROLES.json')) <= set(roles), 'retained selected resource closure')
    need(set(epoch['untracked_native']) <= set(roles) and all(roles[n] for n in epoch['untracked_native']), 'pinned allowed native additions')
    need(roles[FIXTURE] is None and roles['testing/web-platform/tests/config.json'] == sha(HERE / 'server-config.json'), 'fixture/config preimages')
    roster = read(ROOT / 'artifacts/css-keyframe-invalid-registered-endpoint-diagnostic-v1/ROSTER.json')
    url = '/' + roster['logical_path']
    config = read(HERE / 'CONFIG.json')
    config['guard_sources'] = list(compiled)
    binaries = {str((OBJ / ('dist/Nightly.app/Contents/MacOS/' + n)).relative_to(ROOT)) for n in ('firefox', 'XUL')}
    need(all(roles[n] for n in binaries), 'installed binary pair')
    env = dict(os.environ, GIT_OPTIONAL_LOCKS='0', MOZ_OBJDIR=str(OBJ), MOZ_SKIP_PATH_PERFORMANCE_CHECK='1')
    for name in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'MOZCONFIG'):
        need(not env.get(name), 'ambient override ' + name)
    owned = None
    wpt = types.SimpleNamespace(HERE=HERE, ROOT=ROOT, ENV=env, CONFIG=config, BINARIES=binaries,
        PYTHON='/Users/bgrins/venvs/firefox/bin/python', BINARY=OBJ / 'dist/Nightly.app/Contents/MacOS/firefox',
        WPT_CONFIG=OBJ / '_tests/web-platform/wptrunner.local.ini', PREFS_ROOT=ROOT / 'testing/profiles',
        need=need, pins=lambda names: {n: h.fingerprint(ROOT, n) for n in names}, cancelled=lambda: cancelled, owned_group=None)
    def verify(active):
        expected = roles | ({FIXTURE: owned['sha256']} if active else {})
        need(wpt.pins(expected) == expected, 'all epoch and resource roles')
        need(h.semantic_index(h.index_state(ROOT, env)) == epoch['semantic_index'], 'semantic index and working diff')
        need(wpt.pins(epoch['staged_working']) == epoch['staged_working'], 'staged working payloads')
        for name, identity in epoch['installed_identities'].items():
            info = (ROOT / name).lstat()
            need(stat.S_ISREG(info.st_mode) and [info.st_dev, info.st_ino] == identity, 'installed identity ' + name)
        native = {n for n in h.git(ROOT, env, 'diff', '--name-only').decode().splitlines() if not n.startswith('artifacts/')}
        need(native == set(epoch['modified_native_paths']), 'exact native inventory')
        untracked = h.git(ROOT, env, 'ls-files', '--others', '--exclude-standard', '--', 'layout', 'dom', 'servo', 'mfbt').decode().splitlines()
        need(set(untracked) == set(epoch['untracked_native']), 'exact pinned native additions')
        nested = h.index_state(ROOT / 'artifacts/css-spec-lean', env)
        need(h.semantic_index(nested) == epoch['nested_semantic_index'], 'nested research index and working diff')
        need(wpt.pins(epoch['committed_research_working_payloads']) == epoch['committed_research_working_payloads'], 'committed research payloads')
        need(not h.git(ROOT, env, 'ls-files', '--', FIXTURE), 'fixture remains untracked')
        if active:
            info = (ROOT / FIXTURE).lstat()
            need(stat.S_ISREG(info.st_mode) and [info.st_dev, info.st_ino] == owned['identity'], 'owned fixture identity')
        return expected
    before_index = h.index_state(ROOT, env)
    need(before_index['raw_index'] == epoch['raw_index_observation']['current'], 'current raw index anchor')
    save('INDEX-BEFORE.json', before_index)
    save('BEFORE.json', verify(False))
    save('ACTIVE-CONFIG.json', config)
    failure, cleanup = None, []
    try:
        need(not cancelled, 'Termination requested')
        save('PORTS.json', ports.ports_free())
        body = SOURCE.read_bytes()
        with (ROOT / FIXTURE).open('xb', buffering=0) as stream:
            info = os.fstat(stream.fileno())
            owned = dict(identity=[info.st_dev, info.st_ino], sha256=hashlib.sha256(b'').hexdigest())
            count = stream.write(body)
            owned['sha256'] = hashlib.sha256(body[:count]).hexdigest()
            need(count == len(body), 'complete fixture write')
        save('OWNED.json', owned)
        active = verify(True)
        run = tests.run(wpt, 'diagnostic', active)
        provider_rows = [r for r in run['rows'] if r['test'] == url]
        save('CLASSIFICATION.json', parser.classify(provider_rows, roster))
        differences = compare_rows(run['rows'], read(HERE / 'BASELINE-ROWS.json'))
        save('COMPARISON.json', dict(exact=not differences, differences=differences, native_acceptance=False))
        need(not differences, 'observed baseline outcomes changed; see comparison')
        save('POST-CAPTURE.json', verify(True))
    except BaseException as error:
        failure = repr(error)
    finally:
        if owned is not None:
            try:
                need(wpt.owned_group is None, 'live owned process prevents fixture cleanup')
                path = ROOT / FIXTURE
                info = path.lstat()
                need(stat.S_ISREG(info.st_mode) and [info.st_dev, info.st_ino] == owned['identity']
                     and sha(path) == owned['sha256'], 'owned unchanged fixture cleanup')
                path.unlink()
            except BaseException as error:
                cleanup.append('fixture: ' + repr(error))
        try:
            save('FINAL.json', verify(False))
            after_index = h.index_state(ROOT, env)
            save('INDEX-AFTER.json', dict(state=after_index,
                 raw_equal_to_before=after_index['raw_index'] == before_index['raw_index'], cause_established=False))
        except BaseException as error:
            cleanup.append('preservation: ' + repr(error))
        save('RESULT.json', dict(error=failure, cleanup_errors=cleanup, owned_group=wpt.owned_group,
             cancelled=cancelled, expected_failure_count=None, native_acceptance=False))
    need(failure is None and not cleanup and not cancelled and wpt.owned_group is None, 'diagnostic incomplete; see retained evidence')


if __name__ == '__main__':
    signal.signal(signal.SIGTERM, terminate)
    signal.signal(signal.SIGINT, terminate)
    main()
