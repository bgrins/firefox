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
PROPOSAL = ROOT / 'artifacts/css-quote-scope-append-coc-inputs-v1'
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


def index_flags(h, root, env):
    return body_sha(h.git(root, env, 'ls-files', '-v', '-z'))


def index_interval(h, before, after, flags_before, flags_after, expected_flags):
    need(h.semantic_index(before) == h.semantic_index(after), 'semantic index stable during verification')
    need(flags_before == flags_after == expected_flags, 'index flags preserved')
    return {'raw_before': before['raw_index'], 'raw_after': after['raw_index'],
            'raw_changed': before['raw_index'] != after['raw_index'],
            'flags_before': flags_before, 'flags_after': flags_after,
            'semantic_equal': True, 'cause_established': False}


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
    need(inputs['admission'] and inputs['root_review'], 'Actual candidate epoch and root review required')
    for name in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'CC', 'CXX', 'RUSTFLAGS', 'CARGO_TARGET_DIR',
                 'RUSTC', 'RUSTC_WRAPPER', 'MOZ_CONFIGURE_OPTIONS', 'MOZ_ARTIFACT_BUILDS'):
        need(not os.environ.get(name), 'ambient ' + name)
    for name, digest in inputs['local_pins'].items():
        need(sha(HERE / name) == digest, name)
    for name, digest in read(HERE / 'REFERENCES.json').items():
        need(sha(ROOT / name) == digest, name)
    for name, item in read(PROPOSAL / 'FILES.json').items():
        need(sha(PROPOSAL / name) == (item['sha256'] if isinstance(item, dict) else item), 'proposal ' + name)
    admission = ref(inputs['admission'])
    need(admission['status'] == 'QUOTE_COC_EPOCH_VERIFIED' and admission['exit'] == 0, 'actual candidate epoch')
    epoch = ref(admission['epoch'])
    review = ref(inputs['root_review'])
    need(review['status'] == 'QUOTE_COC_ROOT_REVIEW_GO' and review['local_pins'] == inputs['local_pins'], 'root source review')
    need(admission['evidence'], 'actual candidate build and preservation evidence')
    for item in admission['evidence']:
        ref(item)
    binary_names = set(admission['binaries'])
    need(binary_names == BINARY_ROLES and all(epoch['pins'][n] == v for n, v in admission['binaries'].items()), 'four admitted binary roles')
    source_pins = read(HERE / 'SOURCE-PINS.json')
    need(admission['sources'] == {n: v['candidate_sha256'] for n, v in source_pins.items()}, 'compiled candidate quote sources')
    need(all(epoch['pins'][n] == v for n, v in admission['sources'].items()), 'candidate source epoch')
    h = load('steps_common', ROOT / 'artifacts/css-keyframe-commit-styles-implicit-clean-comparison-v1/compare.py')
    tests = load('steps_tests', HERE / 'tests.py')
    process_control = load('steps_process', HERE / 'process_control.py')
    builder = load('steps_build', HERE / 'build.py')
    policy = load('steps_policy', HERE / 'policy.py')
    env = dict(os.environ, GIT_OPTIONAL_LOCKS='0', MOZCONFIG=str(ROOT / 'mozconfig'),
               MOZ_OBJDIR=str(OBJ), MOZ_SKIP_PATH_PERFORMANCE_CHECK='1', MOZ_HEADLESS='1', PYTHONDONTWRITEBYTECODE='1')
    extra = admission['additional_roles']
    need(all(n not in epoch['pins'] or epoch['pins'][n] == v for n, v in extra.items()), 'nonconflicting role extension')
    roles = epoch['pins'] | extra
    required = set(read(HERE / 'GUARD-PATHS.json')['paths']) | {
        'objdir-full.noindex/_tests/web-platform/wptrunner.local.ini',
        'testing/web-platform/tests/config.json'}
    for name in list(required):
        if name.startswith('testing/web-platform/tests/') and name.endswith('.html'):
            required.add(name + '.headers')
            parent = Path(name).parent
            while str(parent).startswith('testing/web-platform/tests'):
                required.add(str(parent / '__dir__.headers'))
                parent = parent.parent
    need(required <= set(roles), 'complete quote resource and response guard closure')
    pre = {n: {'sha256': v['candidate_sha256']} for n, v in source_pins.items()}
    originals = {n: (PROPOSAL / 'candidate' / n).read_bytes() for n in pre}
    candidates = {n: (PROPOSAL / 'scoped-original' / n).read_bytes() for n in pre}
    need(all(body_sha(originals[n]) == pre[n]['sha256'] == roles[n]
             and body_sha(candidates[n]) == source_pins[n]['scoped_original_sha256'] for n in pre), 'exact C/O/C bodies')
    mutable = set(pre)
    excluded = [':(exclude)' + n for n in sorted(mutable)]
    external_diff = body_sha(h.git(ROOT, env, 'diff', '--binary', '--', '.', *excluded))
    state, owned, captures, errors, transitions = {}, {}, {}, [], []
    build_attempted = False
    binaries = dict(admission['binaries'])
    config = read(HERE / 'CONFIG.json')
    config['reftests'] = list(config['expected_end_only'])
    config['guard_sources'] = list(roles)
    committed = {n: body_sha(h.git(ROOT, env, 'show', 'HEAD:' + n)) for n in pre}
    initial_index = h.index_state(ROOT, env)
    initial_nested = h.index_state(ROOT / 'artifacts/css-spec-lean', env)
    expected_flags = admission['index_flags']
    need(set(expected_flags) == {'root', 'nested'}, 'root and nested index flag baselines')
    need(all(isinstance(v, str) and len(v) == 64 and all(c in '0123456789abcdef' for c in v)
             for v in expected_flags.values()), 'index flag SHA256')
    need(index_flags(h, ROOT, env) == expected_flags['root']
         and index_flags(h, ROOT / 'artifacts/css-spec-lean', env) == expected_flags['nested'], 'admitted index flags')
    need(initial_index['raw_index'] == epoch['raw_index_observation']['current'], 'admitted raw index')
    adapter = types.SimpleNamespace(CONFIG=config, HERE=HERE, ROOT=ROOT, ENV=env,
        PYTHON=PYTHON, BINARY=OBJ / 'dist/Nightly.app/Contents/MacOS/firefox', BINARIES=binary_names,
        WPT_CONFIG=OBJ / '_tests/web-platform/wptrunner.local.ini', PREFS_ROOT=ROOT / 'testing/profiles',
        pins=lambda names: {n: h.fingerprint(ROOT, n) for n in names}, need=need,
        cancelled=lambda: terminations > 0, owned_group=None, process_control=process_control)
    def quiet():
        need(not state and adapter.owned_group is None, 'owned process group must be absent before source changes')
    def verify(label, recover_receipt=False):
        before = h.index_state(ROOT, env)
        flags_before = index_flags(h, ROOT, env)
        expected = roles | binaries | {n: item['owned_sha256'] for n, item in owned.items()}
        need(adapter.pins(expected) == expected, 'all roles/source/binary bodies')
        need(all(before[k] == epoch['semantic_index'][k] for k in ('head', 'entries', 'cached_diff')), 'root semantic staging')
        nested = h.index_state(ROOT / 'artifacts/css-spec-lean', env)
        nested_flags_before = index_flags(h, ROOT / 'artifacts/css-spec-lean', env)
        need(h.semantic_index(nested) == epoch['nested_semantic_index'], 'nested library semantic staging preserved')
        need(flags_before == expected_flags['root'] and nested_flags_before == expected_flags['nested'], 'root and nested index flags preserved')
        need(body_sha(h.git(ROOT, env, 'diff', '--binary', '--', '.', *excluded)) == external_diff, 'all unrelated working differences preserved')
        for group in ('staged_working', 'committed_research_working_payloads'):
            need(adapter.pins(epoch[group]) == epoch[group], group)
        for n, item in owned.items():
            if item['identity'] is not None:
                info = (ROOT / n).lstat()
                need(stat.S_ISREG(info.st_mode) and [info.st_dev, info.st_ino] == item['identity'], 'owned comparison identity ' + n)
        for n, identity in epoch['installed_identities'].items():
            info = (ROOT / n).lstat()
            need([info.st_dev, info.st_ino] == identity and stat.S_ISREG(info.st_mode), 'installed identity ' + n)
        native = set(h.git(ROOT, env, 'diff', '--name-only').decode().splitlines())
        native = {n for n in native if not n.startswith('artifacts/')}
        changed = {n for n in mutable if expected[n] != committed[n]}
        need(native == (set(epoch['modified_native_paths']) - mutable) | changed, 'exact native/test modified inventory')
        untracked = set(h.git(ROOT, env, 'ls-files', '--others', '--exclude-standard', '--', 'layout', 'dom', 'servo', 'mfbt').decode().splitlines())
        need(untracked == set(epoch['untracked_native']), 'untracked native inventory')
        after = h.index_state(ROOT, env)
        flags_after = index_flags(h, ROOT, env)
        nested_after = h.index_state(ROOT / 'artifacts/css-spec-lean', env)
        nested_flags_after = index_flags(h, ROOT / 'artifacts/css-spec-lean', env)
        observations = {
            'root': index_interval(h, before, after, flags_before, flags_after, expected_flags['root']),
            'nested': index_interval(h, nested, nested_after, nested_flags_before, nested_flags_after, expected_flags['nested'])}
        for key, initial in [('root', initial_index), ('nested', initial_nested)]:
            observations[key]['raw_initial'] = initial['raw_index']
            observations[key]['raw_changed_from_initial'] = observations[key]['raw_after'] != initial['raw_index']
        try:
            save(label, {'index': after, 'pins': expected, 'roles': len(expected), 'modified_native_paths': sorted(native), 'index_observations': observations})
        except BaseException as failure:
            if not recover_receipt:
                raise
            errors.append('preservation receipt ' + label + ': ' + repr(failure))
        return expected
    def capture(label):
        quiet()
        resources = verify(label + '-PRE.json', recover_receipt=label == 'candidate-restored')
        ports_free(read(ROOT / 'testing/web-platform/tests/config.json'))
        result = tests.run(adapter, label, resources)
        policy.check(result, config, label, captures.get('candidate-initial'))
        captures[label] = policy.values(result)
        verify(label + '-POST.json', recover_receipt=label == 'candidate-restored')
    def build(label):
        nonlocal build_attempted
        quiet()
        verify(label + '-BUILD-PRE.json', recover_receipt=label == 'candidate-restored')
        directory = HERE / (label + '-build')
        directory.mkdir()
        build_attempted = True
        builder.run(ROOT, OBJ, directory, env, adapter.cancelled, state, process_control)
        quiet()
        binaries.update({n: h.fingerprint(ROOT, n) for n in binary_names})
        need(all(binaries.values()), 'built binaries present')
        verify(label + '-BUILD-POST.json', recover_receipt=label == 'candidate-restored')
    baseline = None
    mutation_started = False
    error = None
    verify('BEFORE.json')
    need(h.semantic_index(h.index_state(ROOT, env)) == epoch['semantic_index'], 'exact initial candidate working difference')
    save('ACTUAL-CONFIG.json', config)
    save('EPOCH-BINDING.json', {'admission': admission, 'additional_roles': extra})
    try:
        capture('candidate-initial')
        baseline = captures['candidate-initial']
        quiet()
        for n in pre:
            info = (ROOT / n).lstat()
            owned[n] = {'path': n, 'identity': [info.st_dev, info.st_ino], 'owned_sha256': pre[n]['sha256']}
        mutation_started = True
        for n in pre:
            quiet()
            write_owned(ROOT, owned[n], candidates[n])
            transitions.append({'path': n, 'variant': 'scoped-original'})
        build('scoped-original')
        capture('scoped-original')
    except BaseException as failure:
        error = repr(failure)
    finally:
        adapter.cancelled = lambda: False
        if mutation_started:
            restored = True
            for n, item in owned.items():
                try:
                    quiet()
                    restore_owned(ROOT, item, originals[n])
                    transitions.append({'path': n, 'variant': 'candidate-restored'})
                except BaseException as failure:
                    restored = False
                    errors.append('source recovery ' + n + ': ' + repr(failure))
            if restored:
                try:
                    quiet()
                    binaries.update({n: h.fingerprint(ROOT, n) for n in binary_names})
                    try:
                        save('RESTORATION-INPUT-BINARIES.json', {'binaries': binaries, 'successful_build_claim': False})
                    except BaseException as failure:
                        errors.append('restoration binary receipt: ' + repr(failure))
                    build('candidate-restored')
                    if baseline is not None:
                        capture('candidate-restored')
                except BaseException as failure:
                    errors.append('candidate rebuild/capture: ' + repr(failure))
        try:
            quiet()
            verify('FINAL.json')
            need(h.semantic_index(h.index_state(ROOT, env)) == epoch['semantic_index'], 'complete initial source/index restoration')
        except BaseException as failure:
            errors.append('final preservation: ' + repr(failure))
        save('RESULT.json', {'error': error, 'recovery_errors': errors, 'mutation_started': mutation_started,
             'source_transitions': transitions, 'captured_phases': list(captures), 'owned_inputs': owned,
             'outstanding_processes': state, 'wpt_group': adapter.owned_group, 'phase_order': config['phases'],
             'accepted_fix': False, 'success': error is None and not errors and list(captures) == config['phases']})
    need(error is None and not errors and list(captures) == config['phases'], 'comparison failed; observations and recovery retained')


def terminate(signum, frame):
    global terminations
    terminations += 1


if __name__ == '__main__':
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, terminate)
    main()
