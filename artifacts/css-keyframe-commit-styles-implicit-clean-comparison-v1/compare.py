import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import signal
import stat
import subprocess
import sys
import types

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
HERE = Path(__file__).resolve().parent
MAIN = HERE.parents[1]
ROOT = Path('/private/tmp/firefox-commitstyles-clean-20261024')
OBJ = ROOT / 'obj-commitstyles-native.noindex'
NATIVE = 'dom/animation/EffectCompositor.cpp'
FIXTURE = 'testing/web-platform/tests/web-animations/interfaces/Animation/commit-styles-current-length-dependencies.html'
IMPLICIT = 'testing/web-platform/tests/web-animations/interfaces/Animation/commit-styles-implicit-current-length.html'
IMPLICIT_URL = '/' + IMPLICIT.removeprefix('testing/web-platform/tests/')
IMPLICIT_NAMES = ['commitStyles implicit additive endpoint: variable', 'commitStyles implicit additive endpoint: literal']
COST = MAIN / 'artifacts/css-keyframe-commit-styles-clean-cost-runtime-v2'
COST_PHASE = COST.with_name(COST.name + '-restored')
SERVER_CONFIG = 'testing/web-platform/tests/config.json'
WPT_CONFIG = OBJ / '_tests/web-platform/wptrunner.local.ini'
BASE = '976279105b2e78b8666a959eb3f25c9176cefaf8'
PYTHON = '/Users/bgrins/venvs/firefox/bin/python'
read = lambda path: json.loads(path.read_text())
termination_count = 0


def need(value, message):
    if not value:
        raise RuntimeError(message)


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(name, value):
    with (HERE / name).open('x') as stream:
        stream.write(json.dumps(value, indent=2, sort_keys=True) + '\n')


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def manifest(binding):
    path = MAIN / binding['directory']
    need(sha(path / 'FILES.json') == binding['sha256'], 'manifest ' + str(path))
    for name, expected in read(path / 'FILES.json').items():
        part = Path(name)
        need(not part.is_absolute() and '..' not in part.parts, name)
        need(sha(path / part) == expected, name)
    return path


def fingerprint(root, name):
    path = root / name
    if not path.exists() and not path.is_symlink():
        return None
    need(stat.S_ISREG(path.lstat().st_mode), str(path))
    return sha(path)


def git(root, env, *args):
    return subprocess.check_output(['git', '-c', 'core.fsmonitor=false', *args], cwd=root, env=env)


def index_state(root, env):
    raw_path = Path(git(root, env, 'rev-parse', '--path-format=absolute', '--git-path', 'index').decode().strip())
    return {'head': git(root, env, 'rev-parse', 'HEAD').decode().strip(),
            'entries': hashlib.sha256(git(root, env, 'ls-files', '--stage', '-z')).hexdigest(),
            'cached_diff': hashlib.sha256(git(root, env, 'diff', '--cached', '--binary')).hexdigest(),
            'working_diff': hashlib.sha256(git(root, env, 'diff', '--binary')).hexdigest(),
            'raw_index': sha(raw_path)}


def semantic_index(value):
    return {k: v for k, v in value.items() if k != 'raw_index'}


def verify_main(epoch, env):
    need({name: fingerprint(MAIN, name) for name in epoch['pins']} == epoch['pins'], 'main role preservation')
    need(semantic_index(index_state(MAIN, env)) == epoch['semantic_index'], 'main source/index preservation')
    need(len(epoch['staged_working']) == 925 and all(fingerprint(MAIN, n) == h for n, h in epoch['staged_working'].items()), '925 staged working payloads')
    need(len(epoch['installed_identities']) == 31, '31 installed identities')
    for name, identity in epoch['installed_identities'].items():
        info = (MAIN / name).lstat()
        need(stat.S_ISREG(info.st_mode) and [info.st_dev, info.st_ino] == identity, name)


def policy(baseline, candidate, targets):
    need(set(candidate) == set(baseline), 'exact 76 subtests and two crash results')
    for key, value in candidate.items():
        if key[0] in targets:
            need(value['status'] == 'PASS' and value['message'] in (None, '')
                 and value['expected'] in (None, 'PASS') and not value['known_intermittent'], 'candidate target ' + key[1])
        else:
            need(value == baseline[key], 'upstream control changed: ' + repr(key))


def baseline_policy(archived, fresh):
    new_keys = {(IMPLICIT_URL, name) for name in IMPLICIT_NAMES}
    need(set(fresh) == set(archived) | new_keys, 'fresh 74+2 historical and two implicit identities')
    need(all(fresh[key] == value for key, value in archived.items()), 'historical original outcomes changed')
    for key in new_keys:
        value = fresh[key]
        need(value['expected'] in (None, 'PASS') and not value['known_intermittent'], 'implicit expected status')
        if value['status'] == 'PASS':
            need(value['message'] in (None, ''), 'implicit PASS message')
        else:
            need(key[1] == IMPLICIT_NAMES[0] and value['status'] == 'FAIL', 'literal control must PASS')
            labels = ('Inline implicit-endpoint snapshot immediately after commitStyles',
                      'Inline snapshot after cancellation and provider change',
                      'Computed snapshot after cancellation and provider change')
            pattern = r'assert_equals: (?:' + '|'.join(re.escape(x) for x in labels) + r') expected "280px" but got "-?[0-9]+(?:\.[0-9]+)?px"'
            need(re.fullmatch(pattern, value['message'] or '') is not None, 'implicit calibration failure')


def main():
    inputs = read(HERE / 'INPUTS.json')
    need(sys.argv[1:] == ['--run'] and inputs['ready'] is True, 'Disabled comparison')
    need(all(inputs.get(n) for n in ['baseline', 'baseline_review', 'clean_epoch', 'main_epoch', 'controller_review', 'root_binding']), 'Actual baseline and root bindings required')
    need(sha(HERE / 'REFERENCES.json') == inputs['references_sha256'], 'references')
    for name, expected in inputs['local_pins'].items():
        need(sha(HERE / name) == expected, name)
    for name, expected in read(HERE / 'REFERENCES.json').items():
        need(sha(MAIN / name) == expected, name)
    for name in ['baseline_review', 'controller_review']:
        manifest(inputs[name])
    need(sha(MAIN / inputs['root_binding']['path']) == inputs['root_binding']['sha256'], 'root activation binding')
    baseline_dir = manifest(inputs['baseline'])
    epoch_path = MAIN / inputs['main_epoch']['path']
    need(sha(epoch_path) == inputs['main_epoch']['sha256'], 'main preservation epoch')
    epoch = read(epoch_path)
    tests = load('clean_comparison_tests', MAIN / 'artifacts/css-keyframe-commit-styles-clean-wpt-preparation-v4/tests.py')
    builder = load('clean_comparison_build', HERE / 'build.py')
    env = dict(os.environ, MOZCONFIG=str(ROOT / '.mozconfig-commitstyles'), MOZ_SKIP_PATH_PERFORMANCE_CHECK='1', GIT_OPTIONAL_LOCKS='0')
    for key in ['CC', 'CXX', 'RUSTFLAGS', 'CARGO_TARGET_DIR', 'MOZ_CONFIGURE_OPTIONS', 'MOZ_ARTIFACT_BUILDS', 'MOZ_OBJDIR', 'GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE']:
        need(not env.get(key), key)
    final = read(baseline_dir / 'FINAL.json')
    need(final['error'] is None and not final['cleanup_errors'] and final['fixture_absent'] and final['server_config_absent'], 'successful baseline cleanup')
    archived = read(baseline_dir / 'wpt-baseline/RUN.json')
    config = read(baseline_dir / 'CONFIG.json')
    events = [json.loads(line) for line in (baseline_dir / 'wpt-baseline/raw.json').read_text().splitlines()]
    need(archived['complete'] and archived['before'] == archived['after'], 'baseline complete/stable')
    need(archived['rows'] == [e for e in events if e.get('action') == 'test_status'] and archived['ends'] == [e for e in events if e.get('action') == 'test_end'], 'baseline raw join')
    need(tests.lifecycle(events, config) and not tests.infrastructure_faults(events)
         and tests.exit_matches_results(archived['exit'], archived['rows'] + archived['ends']), 'baseline lifecycle/exit')
    expected_config = read(MAIN / 'artifacts/css-keyframe-commit-styles-clean-base-validation-plan-v1/WPT-INPUTS.json')['selection']
    need(all(config[k] == v for k, v in expected_config.items()), 'same roster')
    need(len(archived['rows']) == 74 and len(archived['ends']) == 5, '74 subtests/three harnesses/two crash tests')
    need(archived['starts'] == [e for e in events if e.get('action') == 'test_start'], 'baseline starts join')
    for test, names in config['expected_subtests'].items():
        need([r['subtest'] for r in archived['rows'] if r['test'] == test] == names, 'baseline exact ordered names ' + test)
    need(all(e['status'] == e.get('expected', e['status']) == ('PASS' if e['test'] in config['reftests'] else 'OK') and not e.get('known_intermittent') for e in archived['ends']), 'baseline harness/crash statuses')
    need(read(baseline_dir / 'wpt-baseline/CLEANUP.json') == {'owned_group_absent': True, 'errors': []}, 'baseline process cleanup')
    baseline = tests.values(archived)
    target = '/' + FIXTURE.removeprefix('testing/web-platform/tests/')
    need(len(baseline) == 76 and sum(k[0] == target for k in baseline) == 15, 'baseline identities')
    for key, value in baseline.items():
        if value['status'] == 'FAIL' and key[0] == target:
            need(re.fullmatch(r'assert_equals: Inline value immediately after commitStyles expected "-?[0-9]+(?:\.[0-9]+)?px" but got "-?[0-9]+(?:\.[0-9]+)?px"', value['message'] or '') is not None, 'baseline target calibration failure')
    archived_baseline = baseline
    clean_epoch_path = MAIN / inputs['clean_epoch']['path']
    need(sha(clean_epoch_path) == inputs['clean_epoch']['sha256'], 'fresh clean epoch')
    clean_epoch = read(clean_epoch_path)
    roles = read(COST_PHASE / 'FINAL-PINS.json')
    need(len(roles) == 53 and clean_epoch['roles'] == roles, 'all latest restored cost roles')
    cost_final = read(COST / 'FINAL-PINS.json')
    need(all(roles[n] == v for n, v in cost_final.items()), 'cost owner/phase final join')
    build_binding = read(COST / 'restored-SOURCE-BUILD.json')
    need(build_binding['phase'] == 'restored' and build_binding['source_sha256'] == roles[NATIVE], 'latest restored source/build')
    need(read(COST / 'RESULT.json')['completed'] == ['original', 'candidate', 'restored'], 'completed cost restoration')
    binding = read(baseline_dir / 'BUILD-BINDING.json')
    binaries = set(binding['binaries'])
    need(len(binaries) == 2 and all(n.startswith('obj-commitstyles-native.noindex/dist/Nightly.app/Contents/MacOS/') for n in binaries), 'binary pair')
    original = (MAIN / 'artifacts/css-keyframe-commit-styles-precompose-refresh-proposal-v1/original/EffectCompositor.cpp').read_bytes()
    candidate = (MAIN / 'artifacts/css-keyframe-commit-styles-precompose-refresh-proposal-v1/candidate/EffectCompositor.cpp').read_bytes()
    body = (MAIN / 'artifacts/css-keyframe-commit-styles-ordinary-landing-wpt-v1/commit-styles-current-length-dependencies.html').read_bytes()
    server_body = (MAIN / 'artifacts/css-keyframe-commit-styles-clean-wpt-preparation-v4/server-config.json').read_bytes()
    implicit_body = (MAIN / 'artifacts/css-keyframe-commit-styles-implicit-endpoint-wpt-v1/commit-styles-implicit-current-length.html').read_bytes()
    payloads = {FIXTURE: body, IMPLICIT: implicit_body, SERVER_CONFIG: server_body}
    need(IMPLICIT not in roles and IMPLICIT + '.headers' not in roles, 'new implicit guards')
    roles.update({IMPLICIT: None, IMPLICIT + '.headers': None, IMPLICIT.replace('testing/web-platform/tests/', 'testing/web-platform/meta/') + '.ini': None})
    need(len(roles) == 56, '53 prior plus three implicit guards')
    config['tests'].append(IMPLICIT.removeprefix('testing/web-platform/tests/'))
    config['expected_subtests'][IMPLICIT_URL] = IMPLICIT_NAMES
    config['baseline_tests'] = config['tests']
    config['baseline_expected_subtests'] = config['expected_subtests']
    need(sum(map(len, config['expected_subtests'].values())) == 76 and len(config['tests']) == 6, '76 rows/six files')
    targets = (target, IMPLICIT_URL)
    need(binding['wpt_config'] == str(WPT_CONFIG) and binding['prefs_root'] == str(ROOT / 'testing/profiles'), 'same objdir metadata and preference inputs')
    source_hash = lambda data: hashlib.sha256(data).hexdigest()
    need(roles[NATIVE] == source_hash(original) and all(roles[n] is None for n in payloads), 'baseline source/owned-input preimages')
    owned_checkout = read(MAIN / 'artifacts/css-keyframe-commit-styles-clean-build-recovery-v1/OWNERSHIP.json')
    info = ROOT.lstat()
    need(stat.S_ISDIR(info.st_mode) and [info.st_dev, info.st_ino] == owned_checkout['identity'] and not OBJ.is_symlink(), 'owned checkout/object directory')
    for name, pin in read(MAIN / 'artifacts/css-keyframe-commit-styles-clean-build-recovery-v1/PREFLIGHT.json')['tools'].items():
        path = Path(name).resolve(strict=True)
        info = path.stat()
        need(str(path) == pin['resolved'] and [info.st_dev, info.st_ino] == pin['identity'] and sha(path) == pin['sha256'], 'tool ' + name)
    need(Path(git(ROOT, env, 'rev-parse', '--show-toplevel').decode().strip()).resolve() == ROOT.resolve(), 'clean source root')
    clean_index = index_state(ROOT, env)
    need(clean_index == clean_epoch['index'], 'fresh current clean raw/semantic epoch')
    need(clean_index['head'] == BASE and not git(ROOT, env, 'diff', '--name-only') and not git(ROOT, env, 'diff', '--cached', '--name-only'), 'pristine tracked baseline')
    need({n: fingerprint(ROOT, n) for n in roles} == roles, 'fresh baseline source/config/input/binary pair')
    verify_main(epoch, env)
    save('BEFORE.json', roles)
    save('MAIN-BEFORE.json', index_state(MAIN, env))
    save('CLEAN-INDEX-BEFORE.json', clean_index)
    save('CONFIG.json', config)
    state, errors, failure, captures = {}, [], None, []
    binary_pins = {n: roles[n] for n in binaries}
    need(binary_pins == build_binding['binaries'], 'latest actual restored binary pair')
    ports = load('implicit_ports', MAIN / 'artifacts/css-keyframe-commit-styles-clean-cost-capture-v3/capture.py')
    source_identity = None
    source_owned = None
    owned = []
    adapter = types.SimpleNamespace(CONFIG=config, HERE=HERE, ROOT=ROOT, ENV=env, BINARIES=binaries,
        pins=lambda names: {n: fingerprint(ROOT, n) for n in names}, need=need, PYTHON=PYTHON,
        BINARY=OBJ / 'dist/Nightly.app/Contents/MacOS/firefox', WPT_CONFIG=WPT_CONFIG,
        PREFS_ROOT=ROOT / 'testing/profiles', cancelled=lambda: termination_count > 0, owned_group=None)
    def quiet():
        need(not state and adapter.owned_group is None, 'outstanding owned process group prevents mutation')
    def verify_phase(data, fixture_present):
        expected = roles | {NATIVE: source_hash(data)} | {n: source_hash(b) if fixture_present else None for n, b in payloads.items()}
        expected.update(binary_pins)
        need(adapter.pins(expected) == expected, 'phase source/config/resources')
        index = index_state(ROOT, env)
        need(all(index[k] == clean_index[k] for k in ['head', 'entries', 'cached_diff']), 'clean index preserved')
        changed = set(git(ROOT, env, 'diff', '--name-only').decode().splitlines())
        need(changed == ({NATIVE} if data == candidate else set()), 'only candidate tracked change')
        untracked = set(git(ROOT, env, 'ls-files', '--others', '--exclude-standard').decode().splitlines())
        need(untracked <= {'.mozconfig-commitstyles', *(set(payloads) if fixture_present else set())}, 'clean untracked ownership')
        verify_main(epoch, env)
        return expected
    def write_source(data, expected):
        nonlocal source_owned
        quiet()
        path = ROOT / NATIVE
        info = path.lstat()
        need(stat.S_ISREG(info.st_mode) and [info.st_dev, info.st_ino] == source_identity and sha(path) == expected, 'owned source preimage')
        with path.open('r+b', buffering=0) as stream:
            check = os.fstat(stream.fileno())
            need([check.st_dev, check.st_ino] == source_identity, 'source identity before write')
            source_owned = expected
            try:
                stream.truncate(0)
                source_owned = source_hash(b'')
                written = stream.write(data)
                source_owned = source_hash(data[:written])
                need(written == len(data), 'complete native write')
            except BaseException:
                stream.seek(0)
                observed = stream.read()
                if data.startswith(observed):
                    source_owned = source_hash(observed)
                raise
        need(sha(path) == source_owned, 'native postimage')
    def build(phase, cancelled):
        nonlocal binary_pins
        quiet()
        directory = HERE / (phase + '-build')
        directory.mkdir()
        before_build = adapter.pins(roles)
        save(phase + '-BUILD-BEFORE.json', before_build)
        builder.run(ROOT, OBJ, directory, env, cancelled, state)
        quiet()
        binary_pins = adapter.pins(binaries)
        need(all(binary_pins.values()), 'built binary pair')
        after_build = adapter.pins(roles)
        need(after_build == before_build | binary_pins, 'only binary pair changed during build')
        save(phase + '-BUILD-AFTER.json', after_build)
    def capture(phase, body):
        quiet()
        active = verify_phase(body, True)
        save(phase + '-PORTS.json', ports.ports_free())
        run = tests.run(adapter, phase, active)
        captures.append(phase)
        return run
    try:
        need(not termination_count, 'Termination requested')
        info = (ROOT / NATIVE).lstat()
        source_identity = [info.st_dev, info.st_ino]
        for name, payload in payloads.items():
            with (ROOT / name).open('xb', buffering=0) as stream:
                info = os.fstat(stream.fileno())
                item = {'path': name, 'identity': [info.st_dev, info.st_ino], 'sha256': source_hash(b'')}
                owned.append(item)
                written = stream.write(payload)
                item['sha256'] = source_hash(payload[:written])
                need(written == len(payload), 'complete owned input write')
            need(sha(ROOT / name) == item['sha256'], 'owned input body')
        save('OWNED.json', owned)
        run = capture('baseline_capture', original)
        baseline = tests.values(run)
        baseline_policy(archived_baseline, baseline)
        save('BASELINE-POLICY.json', dict(historical_74_plus_2_exact=True, literal_control_pass=True, implicit_failure_count_required=None))
        write_source(candidate, source_hash(original))
        save('CANDIDATE-SOURCE.json', {'path': NATIVE, 'identity': source_identity, 'sha256': source_owned})
        build('candidate', lambda: termination_count > 0)
        run = capture('candidate', candidate)
        policy(baseline, tests.values(run), targets)
        save('CANDIDATE-POLICY.json', {'all_17_targets_pass': True, 'other_59_subtests_and_2_crashes_exact': True})
    except BaseException as error:
        failure = repr(error)
    finally:
        if source_owned is not None:
            recovery_count = termination_count
            try:
                write_source(original, source_owned)
                save('RESTORED-SOURCE.json', {'path': NATIVE, 'identity': source_identity, 'sha256': source_owned})
            except BaseException as error:
                errors.append('source restoration: ' + repr(error))
            try:
                info = (ROOT / NATIVE).lstat()
                need(stat.S_ISREG(info.st_mode) and [info.st_dev, info.st_ino] == source_identity
                     and sha(ROOT / NATIVE) == source_hash(original), 'original body before restoration build')
                build('restored', lambda: termination_count > recovery_count)
                adapter.cancelled = lambda: termination_count > recovery_count
                run = capture('restored', original)
                need(tests.values(run) == baseline, 'restored exact fresh baseline 76+2')
            except BaseException as error:
                errors.append('restoration: ' + repr(error))
        for item in reversed(owned):
            try:
                quiet()
                path = ROOT / item['path']
                info = path.lstat()
                need(stat.S_ISREG(info.st_mode) and [info.st_dev, info.st_ino] == item['identity'] and sha(path) == item['sha256'], 'owned input cleanup')
                path.unlink()
            except BaseException as error:
                errors.append('input cleanup: ' + repr(error))
        try:
            quiet()
            final_roles = verify_phase(original, False)
            if source_owned is None:
                need(final_roles == roles, 'unmutated baseline binaries preserved')
            save('FINAL-PINS.json', final_roles)
            save('MAIN-AFTER.json', index_state(MAIN, env))
            save('CLEAN-INDEX-AFTER.json', index_state(ROOT, env))
        except BaseException as error:
            errors.append('final preservation: ' + repr(error))
        result = {'error': failure, 'recovery_errors': errors, 'captures': captures,
                  'source_mutation_attempted': source_owned is not None, 'outstanding_groups': state,
                  'wpt_group': adapter.owned_group, 'termination_count': termination_count,
                  'native_acceptance': False, 'performance_measured': False}
        save('RESULT.json', result)
    need(failure is None and not errors and captures == ['baseline_capture', 'candidate', 'restored'] and not termination_count, 'comparison rejected; see RESULT.json')


def terminate(signum, frame):
    global termination_count
    termination_count += 1


if __name__ == '__main__':
    signal.signal(signal.SIGTERM, terminate)
    signal.signal(signal.SIGINT, terminate)
    main()
