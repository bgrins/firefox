import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import socket
import stat
import sys
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OBJ = ROOT / 'objdir-full.noindex'
PROPOSAL = HERE
NATIVE = 'servo/components/style/values/specified/easing.rs'
PYTHON = '/Users/bgrins/venvs/firefox/bin/python'
BINARY_ROLES = {
    'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox',
    'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/XUL',
    'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/gtest/XUL',
    'objdir-full.noindex/dist/bin/gtest/XUL',
}
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
body_sha = lambda b: hashlib.sha256(b).hexdigest()
terminations = 0


def need(condition, message):
    if not condition:
        raise RuntimeError(message)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def save(name, value):
    with (HERE / name).open('x') as f:
        json.dump(value, f, indent=2, sort_keys=True)
        f.write('\n')


def ref(binding):
    path = Path(binding['path'])
    need(not path.is_absolute() and '..' not in path.parts, 'relative binding')
    path = ROOT / path
    need(sha(path) == binding['sha256'], str(path))
    return read(path)


def ports_free(config):
    opened = []
    try:
        for scheme, ports in config['ports'].items():
            for port in ports:
                udp = scheme in ('dns', 'webtransport-h3')
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM if udp else socket.SOCK_STREAM)
                opened.append(s)
                if not udp:
                    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                try:
                    s.bind(('127.0.0.1', port))
                    if not udp:
                        s.listen(1)
                except OSError as error:
                    raise RuntimeError(f'Port preflight {scheme}:{port} UDP={udp}: {error}') from error
    finally:
        for s in opened:
            s.close()


def write_owned(root, item, data):
    path = root / item['path']
    if item['identity'] is None:
        need(not path.exists() and not path.is_symlink(), 'new owned path absent')
        mode = 'x+b'
    else:
        info = path.lstat()
        need(stat.S_ISREG(info.st_mode) and [info.st_dev, info.st_ino] == item['identity']
             and sha(path) == item['owned_sha256'], 'known owned preimage ' + item['path'])
        mode = 'r+b'
    with path.open(mode, buffering=0) as stream:
        info = os.fstat(stream.fileno())
        identity = [info.st_dev, info.st_ino]
        need(item['identity'] in (None, identity), 'opened identity')
        item['identity'] = identity
        stream.truncate(0)
        item['owned_sha256'] = body_sha(b'')
        try:
            written = stream.write(data)
            item['owned_sha256'] = body_sha(data[:written])
            need(written == len(data), 'complete owned write')
        except BaseException:
            stream.seek(0)
            observed = stream.read()
            if data.startswith(observed):
                item['owned_sha256'] = body_sha(observed)
            raise
    need(sha(path) == item['owned_sha256'], 'owned write postimage')


def restore_owned(root, item, original):
    path = root / item['path']
    if item['identity'] is None:
        need(not path.exists() and not path.is_symlink(), 'untouched new input absent')
        return
    info = path.lstat()
    need(stat.S_ISREG(info.st_mode) and [info.st_dev, info.st_ino] == item['identity']
         and sha(path) == item['owned_sha256'], 'unknown edit preserved ' + item['path'])
    if original is None:
        path.unlink()
        item['identity'] = None
        item['owned_sha256'] = None
    else:
        write_owned(root, item, original)


def main():
    inputs = read(HERE / 'INPUTS.json')
    need(sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize, 'isolated interpreter')
    need(sys.argv[1:] == ['--run'] and inputs['ready'] is True, 'Disabled comparison')
    need(inputs['admission'] and inputs['root_review'], 'Actual post-fold admission and root review required')
    for name in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'CC', 'CXX', 'RUSTFLAGS', 'CARGO_TARGET_DIR',
                 'RUSTC', 'RUSTC_WRAPPER', 'MOZ_CONFIGURE_OPTIONS', 'MOZ_ARTIFACT_BUILDS'):
        need(not os.environ.get(name), 'ambient ' + name)
    for name, digest in inputs['local_pins'].items():
        need(sha(HERE / name) == digest, name)
    for name, digest in read(HERE / 'REFERENCES.json').items():
        need(sha(ROOT / name) == digest, name)
    admission = ref(inputs['admission'])
    need(admission['status'] == 'CUBIC_POST_STEPS_METADATA_FOLD_ROOT_VERIFIED' and admission['outer_exit'] == 0, 'post-fold actual admission')
    epoch = ref(admission['epoch'])
    review = ref(inputs['root_review'])
    need(review['status'] == 'CUBIC_FINAL_INSTALL_ROOT_REVIEW_GO' and review['local_pins'] == inputs['local_pins'], 'root source review')
    need(admission['evidence'], 'actual metadata validation and post-fold preservation evidence')
    for item in admission['evidence']:
        ref(item)
    binary_names = set(admission['binaries'])
    need(binary_names == BINARY_ROLES and all(epoch['pins'][n] == v for n, v in admission['binaries'].items()), 'four current original binaries')
    need(all(epoch['pins'][n] == v for n, v in admission['sources'].items()) and NATIVE in admission['sources'], 'current original source provenance')
    h = load('steps_common', ROOT / 'artifacts/css-keyframe-commit-styles-implicit-clean-comparison-v1/compare.py')
    tests = load('steps_tests', HERE / 'tests.py')
    process_control = load('steps_process', HERE / 'process_control.py')
    builder = load('steps_build', HERE / 'build.py')
    policy = load('install_policy', HERE / 'policy.py')
    reference_rows = policy.archived_candidate(ROOT, tests, read(HERE / 'HISTORICAL.json'))
    env = dict(os.environ, GIT_OPTIONAL_LOCKS='0', MOZCONFIG=str(ROOT / 'mozconfig'),
               MOZ_OBJDIR=str(OBJ), MOZ_SKIP_PATH_PERFORMANCE_CHECK='1', MOZ_HEADLESS='1', PYTHONDONTWRITEBYTECODE='1')
    roles = epoch['pins']
    pre, post = read(HERE / 'PREIMAGES.json'), read(HERE / 'POSTIMAGES.json')
    originals = {n: (PROPOSAL / 'original' / n).read_bytes() if pin else None for n, pin in pre.items()}
    candidates = {n: (PROPOSAL / 'candidate' / n).read_bytes() for n in post}
    need(all(roles[n] == (pin['sha256'] if pin else None) for n, pin in pre.items()), 'exact source/test preimages')
    need(all(body_sha(candidates[n]) == post[n]['sha256'] for n in post), 'exact candidate payloads')
    need(all(originals[n] is None if pin is None else body_sha(originals[n]) == pin['sha256'] for n, pin in pre.items()), 'exact original payloads')
    mutable = set(pre)
    excluded = [':(exclude)' + n for n in sorted(mutable)]
    external_diff = body_sha(h.git(ROOT, env, 'diff', '--binary', '--', '.', *excluded))
    state, owned, captures, errors, transitions = {}, {}, {}, [], []
    build_attempted = False
    binaries = dict(admission['binaries'])
    roster = read(HERE / 'CANDIDATE-ROSTER.json')
    historical = read(HERE / 'HISTORICAL.json')
    historical_run = read(ROOT / historical['directory'] / 'wpt-candidate/RUN.json')
    selected_bodies = {NATIVE} | {'testing/web-platform/tests/' + t.lstrip('/') for t in roster}
    need(all(historical_run['after'][n] == (post[n]['sha256'] if n in post else roles[n])
             for n in selected_bodies), 'historical compiled candidate and unchanged selected WPT bodies')
    config = {'tests': [t.lstrip('/') for t in sorted(roster)], 'expected_subtests': roster,
              'baseline_tests': [t.lstrip('/') for t in sorted(roster)], 'baseline_expected_subtests': roster,
              'guard_sources': list(roles), 'reftests': []}
    adapter = types.SimpleNamespace(CONFIG=config, HERE=HERE, ROOT=ROOT, ENV=env,
        PYTHON=PYTHON, BINARY=OBJ / 'dist/Nightly.app/Contents/MacOS/firefox', BINARIES=binary_names,
        WPT_CONFIG=OBJ / '_tests/web-platform/wptrunner.local.ini', PREFS_ROOT=ROOT / 'testing/profiles',
        pins=lambda names: {n: h.fingerprint(ROOT, n) for n in names}, need=need,
        cancelled=lambda: terminations > 0, owned_group=None, process_control=process_control)
    def quiet():
        need(not state and adapter.owned_group is None, 'owned process group must be absent before source changes')
    def verify(label, recover_receipt=False):
        before = h.index_state(ROOT, env)
        expected = roles | binaries | {n: item['owned_sha256'] for n, item in owned.items()}
        need(adapter.pins(expected) == expected, 'all roles/source/binary bodies')
        need(all(before[k] == epoch['semantic_index'][k] for k in ('head', 'entries', 'cached_diff')), 'root semantic staging')
        need(h.semantic_index(h.index_state(ROOT / 'artifacts/css-spec-lean', env)) == epoch['nested_semantic_index'], 'nested library preserved')
        need(body_sha(h.git(ROOT, env, 'diff', '--binary', '--', '.', *excluded)) == external_diff, 'all unrelated working differences preserved')
        for group in ('staged_working', 'committed_research_working_payloads'):
            need(adapter.pins(epoch[group]) == epoch[group], group)
        for n, item in owned.items():
            if item['identity'] is not None:
                info = (ROOT / n).lstat()
                need(stat.S_ISREG(info.st_mode) and [info.st_dev, info.st_ino] == item['identity'], 'owned comparison identity ' + n)
                need(stat.S_IMODE(info.st_mode) == 0o644, 'owned source/test mode ' + n)
        for n, identity in epoch['installed_identities'].items():
            info = (ROOT / n).lstat()
            need([info.st_dev, info.st_ino] == identity and stat.S_ISREG(info.st_mode), 'installed identity ' + n)
        native = set(h.git(ROOT, env, 'diff', '--name-only').decode().splitlines())
        native = {n for n in native if not n.startswith('artifacts/')}
        changed = {n for n, item in owned.items() if pre[n] is not None and item['owned_sha256'] != pre[n]['sha256']}
        need(native == set(epoch['modified_native_paths']) | changed, 'exact native/test modified inventory')
        untracked = set(h.git(ROOT, env, 'ls-files', '--others', '--exclude-standard', '--', 'layout', 'dom', 'servo', 'mfbt').decode().splitlines())
        need(untracked == set(epoch['untracked_native']), 'untracked native inventory')
        after = h.index_state(ROOT, env)
        need(before == after, 'index stable during verification')
        try:
            save(label, {'index': after, 'pins': expected, 'roles': len(expected), 'modified_native_paths': sorted(native)})
        except BaseException as failure:
            if not recover_receipt:
                raise
            errors.append('preservation receipt ' + label + ': ' + repr(failure))
        return expected
    def capture(label):
        quiet()
        resources = verify(label + '-PRE.json', recover_receipt=label == 'restored')
        ports_free(read(ROOT / 'testing/web-platform/tests/config.json'))
        result = tests.run(adapter, label, resources)
        captures[label] = result['rows']
        save('OUTCOME-COMPARISON.json', policy.compare(reference_rows, result['rows'], read(HERE / 'COMPARISON-POLICY.json')))
        verify(label + '-POST.json', recover_receipt=label == 'restored')
    def build(label):
        nonlocal build_attempted
        quiet()
        verify(label + '-BUILD-PRE.json', recover_receipt=label == 'restored')
        directory = HERE / (label + '-build')
        directory.mkdir()
        build_attempted = True
        builder.run(ROOT, OBJ, directory, env, adapter.cancelled, state, process_control)
        quiet()
        binaries.update({n: h.fingerprint(ROOT, n) for n in binary_names})
        need(all(binaries.values()), 'built binaries present')
        verify(label + '-BUILD-POST.json', recover_receipt=label == 'restored')
    mutation_started = False
    success = False
    error = None
    verify('BEFORE.json')
    need(h.semantic_index(h.index_state(ROOT, env)) == epoch['semantic_index'], 'exact post-fold baseline working difference')
    save('CONFIG.json', config)
    save('EPOCH-BINDING.json', {'admission': admission})
    try:
        for n in pre:
            quiet()
            need(not adapter.cancelled(), 'termination requested')
            info = (ROOT / n).lstat() if pre[n] else None
            owned[n] = {'path': n, 'identity': [info.st_dev, info.st_ino] if info else None,
                        'owned_sha256': pre[n]['sha256'] if pre[n] else None}
            mutation_started = True
            write_owned(ROOT, owned[n], candidates[n])
        transitions.append('candidate')
        build('candidate')
        capture('candidate')
        quiet()
        final = verify('FINAL.json')
        need(not adapter.cancelled(), 'termination requested')
        current = copy.deepcopy(epoch)
        current['pins'] = final
        current['semantic_index'] = h.semantic_index(h.index_state(ROOT, env))
        current['modified_native_paths'] = read(HERE / 'FINAL.json')['modified_native_paths']
        for n, item in owned.items():
            if pre[n] is None:
                current['installed_identities'][n] = item['identity']
        current['historical_raw_index_observation'] = current.get('raw_index_observation')
        current['raw_index_observation'] = {'before': read(HERE / 'BEFORE.json')['index']['raw_index'],
            'current': read(HERE / 'FINAL.json')['index']['raw_index'], 'cause_if_changed': 'not established'}
        current['counts'].update(roles=len(final), installed_identities=len(current['installed_identities']),
            native_modified_paths=len(current['modified_native_paths']))
        current['cubic_install_provenance'] = {'admission': inputs['admission'], 'accepted_fix': False,
            'source_sha256': post[NATIVE]['sha256'], 'captured_rows': len(captures['candidate'])}
        save('CURRENT-EPOCH.json', current)
        save('RESULT.json', {'success': True, 'error': None, 'recovery_errors': [],
            'source_transitions': transitions, 'captured_phases': list(captures), 'owned_inputs': owned,
            'outstanding_processes': state, 'wpt_group': adapter.owned_group, 'accepted_fix': False})
        success = True
    except BaseException as failure:
        error = repr(failure)
    finally:
        adapter.cancelled = lambda: False
        if not success:
            restored_all = True
            for n, item in list(owned.items()):
                try:
                    quiet()
                    restore_owned(ROOT, item, originals[n])
                    owned.pop(n)
                except BaseException as failure:
                    restored_all = False
                    errors.append('input recovery ' + n + ': ' + repr(failure))
            if restored_all and build_attempted:
                try:
                    quiet()
                    binaries.update({n: h.fingerprint(ROOT, n) for n in binary_names})
                    try:
                        save('RESTORATION-INPUT-BINARIES.json', {'binaries': binaries, 'successful_build_claim': False})
                    except BaseException as failure:
                        errors.append('restoration binary receipt: ' + repr(failure))
                    transitions.append('restored')
                    build('restored')
                except BaseException as failure:
                    errors.append('original rebuild: ' + repr(failure))
            try:
                quiet()
                verify('RECOVERY-FINAL.json', recover_receipt=True)
                need(h.semantic_index(h.index_state(ROOT, env)) == epoch['semantic_index'], 'complete original source/index restoration')
            except BaseException as failure:
                errors.append('final preservation: ' + repr(failure))
            save('FAILURE.json', {'success': False, 'error': error, 'recovery_errors': errors,
                'source_transitions': transitions, 'captured_phases': list(captures), 'owned_inputs': owned,
                'outstanding_processes': state, 'wpt_group': adapter.owned_group, 'accepted_fix': False})
    need(success, 'installation failed; use outer exit and FAILURE, not partial success publications')


def terminate(signum, frame):
    global terminations
    terminations += 1


if __name__ == '__main__':
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, terminate)
    main()
