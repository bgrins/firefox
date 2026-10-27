import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import signal
import stat
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OBJ = ROOT / 'objdir-full.noindex'
PROPOSAL = ROOT / 'artifacts/css-keyframe-provider-resolution-implementation-v1'
PYTHON = '/Users/bgrins/venvs/firefox/bin/python'
BINARY_ROLES = {
    'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox',
    'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/XUL',
    'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/gtest/XUL',
    'objdir-full.noindex/dist/bin/gtest/XUL',
}
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
stop = False


def need(value, message):
    if not value:
        raise RuntimeError(message)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def referenced(item):
    path = Path(item['path'])
    need(not path.is_absolute() and '..' not in path.parts, 'relative reference')
    need(sha(ROOT / path) == item['sha256'], 'reference ' + str(path))
    return read(ROOT / path)


def gtest_result(log, names):
    events = re.findall(r'TEST_(START|END): ([^\r\n]+)', log)
    need(len(events) == 2 * len(names), 'exact GTest event count')
    actual = []
    for start, end in zip(events[::2], events[1::2]):
        need(start[0] == 'START' and end == ('END', 'PASS'), 'paired passing GTest')
        actual.append(start[1])
    need(sorted(actual) == sorted(names) and len(set(actual)) == len(names), 'exact named GTests')
    summary = f'Ran {len(names)} test(s) from 4 test suite(s) (0 disabled), with 0 failure(s).'
    need(log.count(summary) == 1, 'exact GTest summary')
    return actual


def main():
    inputs = read(HERE / 'INPUTS.json')
    need(sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize, 'isolated interpreter')
    need(sys.argv[1:] == ['--run'] and inputs['ready'] is True, 'Disabled provider host experiment')
    need(inputs['epoch'] and inputs['expected_head'] and inputs['controller_review'], 'future terminal epoch and review required')
    for name, pin in inputs['local_pins'].items():
        need(sha(HERE / name) == pin, 'local pin ' + name)
    for name, pin in read(HERE / 'REFERENCES.json').items():
        need(sha(ROOT / name) == pin, 'external pin ' + name)
    for name, pin in read(PROPOSAL / 'FILES.json').items():
        need(sha(PROPOSAL / name) == pin, 'proposal payload ' + name)
    review = referenced(inputs['controller_review'])
    need(review['status'] == 'PROVIDER_RESOLVER_HOST_ROOT_REVIEW_GO' and review['local_pins'] == inputs['local_pins'], 'controller source approval')
    source_review = read(ROOT / 'artifacts/css-keyframe-provider-resolution-root-review-v1/CHECK.json')
    need(source_review['status'] == 'READY_FOR_ISOLATED_COMPILE_AND_HOST_TESTS', 'source admission')
    for name in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'CC', 'CXX', 'RUSTFLAGS', 'CARGO_TARGET_DIR', 'RUSTC', 'RUSTC_WRAPPER', 'MOZ_CONFIGURE_OPTIONS', 'MOZ_ARTIFACT_BUILDS'):
        need(not os.environ.get(name), 'ambient ' + name)
    env = dict(os.environ, GIT_OPTIONAL_LOCKS='0', MOZCONFIG=str(ROOT / 'mozconfig'),
               MOZ_OBJDIR=str(OBJ), MOZ_HEADLESS='1', MOZ_SKIP_PATH_PERFORMANCE_CHECK='1', PYTHONDONTWRITEBYTECODE='1')
    h = load('preserve', ROOT / 'artifacts/css-keyframe-commit-styles-implicit-clean-comparison-v1/compare.py')
    a = load('epoch', ROOT / 'artifacts/css-keyframe-operation-descriptor-post-signing-proposal-v2/epoch.py')
    ownership = load('ownership', ROOT / 'artifacts/css-cubic-bezier-calc-range-comparison-v1/compare.py')
    builder = load('phase', HERE / 'phase.py')
    control = load('control', HERE / 'process_control.py')
    epoch = referenced(inputs['epoch'])
    need(epoch['semantic_index']['head'] == inputs['expected_head'], 'bound future HEAD')
    pre, post = read(HERE / 'PREIMAGES.json'), read(HERE / 'POSTIMAGES.json')
    need(len(pre) == len(post) == 4 and set(pre) == set(post), 'four existing owned source paths')
    need(all(epoch['pins'][n] == pin for n, pin in pre.items()), 'original source epoch join')
    need(BINARY_ROLES <= set(epoch['pins']), 'four binary roles')
    originals = {n: (PROPOSAL / 'original' / n).read_bytes() for n in pre}
    candidates = {n: (PROPOSAL / 'candidate' / n).read_bytes() for n in post}
    need(all(hashlib.sha256(originals[n]).hexdigest() == pre[n] and hashlib.sha256(candidates[n]).hexdigest() == post[n] for n in pre), 'selected source bodies')
    selection = read(HERE / 'GTEST-SELECTION.json')
    need(len(selection['original']) == 17 and len(selection['candidate']) == 19 and selection['candidate'][:17] == selection['original'], '17 plus two tests')
    publication_errors, recovery_errors, phases = [], [], []
    owned, state = {}, {}
    binaries = {n: epoch['pins'][n] for n in BINARY_ROLES}
    def save(name, value):
        try:
            with (HERE / name).open('x') as stream:
                stream.write(json.dumps(value, indent=2, sort_keys=True) + '\n')
        except BaseException as error:
            publication_errors.append(name + ': ' + repr(error))
    before = a.verify_current(h, ROOT, env, epoch)
    save('BEFORE.json', before)
    need(not publication_errors, 'pre-application receipt')
    excluded = [':(exclude)' + n for n in pre]
    external = h.git(ROOT, env, 'diff', '--binary', '--', '.', *excluded)
    def quiet():
        need(not state, 'owned process groups must be absent')
    def verify(label):
        quiet()
        first = h.index_state(ROOT, env)
        expected = epoch['pins'] | binaries | {n: item['owned_sha256'] for n, item in owned.items()}
        need({n: h.fingerprint(ROOT, n) for n in expected} == expected, 'source/binary/resource roles')
        need(all(first[k] == epoch['semantic_index'][k] for k in ('head', 'entries', 'cached_diff')), 'main HEAD/staging')
        need(h.semantic_index(h.index_state(ROOT / 'artifacts/css-spec-lean', env)) == epoch['nested_semantic_index'], 'nested semantic index')
        need(h.git(ROOT, env, 'diff', '--binary', '--', '.', *excluded) == external, 'unrelated working changes')
        for group in ('staged_working', 'committed_research_working_payloads'):
            need({n: h.fingerprint(ROOT, n) for n in epoch[group]} == epoch[group], group)
        for n, identity in epoch['installed_identities'].items():
            info = (ROOT / n).lstat()
            need(stat.S_ISREG(info.st_mode) and [info.st_dev, info.st_ino] == identity, 'installed identity')
        for n, item in owned.items():
            info = (ROOT / n).lstat()
            need(stat.S_ISREG(info.st_mode) and [info.st_dev, info.st_ino] == item['identity'], 'owned source identity')
        native = {n for n in h.git(ROOT, env, 'diff', '--name-only').decode().splitlines() if not n.startswith('artifacts/')}
        changed = {n for n, item in owned.items() if item['owned_sha256'] != pre[n] and n not in epoch['untracked_native']}
        need(native == set(epoch['modified_native_paths']) | changed, 'native inventory')
        additions = set(h.git(ROOT, env, 'ls-files', '--others', '--exclude-standard', '--', 'layout', 'dom', 'servo', 'mfbt').decode().splitlines())
        need(additions == set(epoch['untracked_native']), 'native additions')
        need(h.index_state(ROOT, env) == first, 'stable check interval')
        save(label, {'index': first, 'pins': expected, 'modified_native_paths': sorted(native)})
        return expected, first, native
    def phase(label, command, recovering=False, timeout=None):
        verify(label + '-PRE.json')
        directory = HERE / label
        directory.mkdir()
        save(label + '-COMMAND.json', {'command': command, 'started': time.time()})
        deadline = time.monotonic() + timeout if timeout else None
        cancelled = lambda: (stop and not recovering) or (deadline is not None and time.monotonic() >= deadline)
        try:
            builder.run(ROOT, OBJ, directory, env, cancelled, state, control, command, publication_errors)
        finally:
            quiet()
            binaries.update({n: h.fingerprint(ROOT, n) for n in BINARY_ROLES})
        verify(label + '-POST.json')
        phases.append(label)
        save(label + '-EXECUTION.json', {'exit': 0, 'command': command, 'finished': time.time(), 'log_sha256': sha(directory / 'build.log')})
        if not recovering:
            need(not publication_errors, 'phase receipt publication')
        return directory / 'build.log'
    def compile_and_test(prefix, names, recovering=False):
        phase(prefix + '-export', [PYTHON, './mach', 'build', 'export', '-j2'], recovering)
        phase(prefix + '-binaries', [PYTHON, './mach', 'build', 'binaries', '-j2'], recovering)
        need(all(binaries.values()), 'compiled binary roles present')
        log = phase(prefix + '-gtest', [PYTHON, './mach', 'gtest', ':'.join(names), '--jobs=1'], recovering, 600)
        actual = gtest_result(log.read_text(errors='replace'), names)
        need(binaries['objdir-full.noindex/dist/bin/gtest/XUL'] == binaries['objdir-full.noindex/dist/Nightly.app/Contents/MacOS/gtest/XUL'], 'packaged GTest pair')
        save(prefix + '-TESTS.json', {'names': actual, 'passed': len(actual), 'log_sha256': sha(log)})
    def publish_epoch(label, pins, index, native):
        current = copy.deepcopy(epoch)
        current['pins'] = pins
        current['semantic_index'] = h.semantic_index(index)
        current['modified_native_paths'] = sorted(native)
        current['counts']['native_modified_paths'] = len(native)
        current['raw_index_observation'] = {'current': index['raw_index'], 'before': before['index']['raw_index'], 'bytes_equal': index['raw_index'] == before['index']['raw_index'], 'cause_if_changed': 'not established'}
        save(label, current)
    def result(status, error, retained):
        return {'status': status, 'error': error, 'recovery_errors': recovery_errors.copy(), 'publication_errors': publication_errors.copy(), 'phases': phases.copy(), 'candidate_retained': retained, 'owned_sources': copy.deepcopy(owned), 'outstanding_processes': state.copy(), 'normal_producer_enabled': False, 'browser_execution': False, 'accepted_bug_increment': 0}
    error = None
    passed = False
    try:
        for n in pre:
            quiet()
            info = (ROOT / n).lstat()
            owned[n] = {'path': n, 'identity': [info.st_dev, info.st_ino], 'owned_sha256': pre[n]}
            ownership.write_owned(ROOT, owned[n], candidates[n])
        pins, index, native = verify('APPLIED.json')
        publish_epoch('SOURCE-EPOCH.json', pins, index, native)
        need(not publication_errors, 'application receipt')
        phase('candidate-metadata', ['/Users/bgrins/.rustup/toolchains/stable-aarch64-apple-darwin/bin/cargo', '--config', str(OBJ / '.cargo/config.toml'), 'metadata', '--format-version', '1', '--frozen', '--manifest-path', str(ROOT / 'toolkit/library/gtest/rust/Cargo.toml')], timeout=600)
        compile_and_test('candidate', selection['candidate'])
        need(not publication_errors and not stop, 'complete recorded candidate experiment')
        pins, index, native = verify('FINAL.json')
        publish_epoch('CURRENT-EPOCH.json', pins, index, native)
        need(not publication_errors, 'candidate final receipts')
        save('RESULT.json', result('PROVIDER_RESOLVER_BUILD_AND_19_TESTS_PASS', None, True))
        need(not publication_errors and not stop, 'candidate terminal receipt')
        passed = True
    except BaseException as failure:
        error = repr(failure)
    finally:
        if not passed:
            for n, item in owned.items():
                try:
                    quiet()
                    ownership.restore_owned(ROOT, item, originals[n])
                except BaseException as failure:
                    recovery_errors.append('restore ' + n + ': ' + repr(failure))
            if owned and not recovery_errors:
                try:
                    compile_and_test('restored', selection['original'], True)
                except BaseException as failure:
                    recovery_errors.append('restored compilation/tests: ' + repr(failure))
            try:
                pins, index, native = verify('RESTORED-FINAL.json')
                need(all(pins[n] == pre[n] for n in pre), 'original source restoration')
                need(h.semantic_index(index) == epoch['semantic_index'], 'full original semantic restoration')
                if not recovery_errors:
                    publish_epoch('RESTORED-EPOCH.json', pins, index, native)
            except BaseException as failure:
                recovery_errors.append('final preservation: ' + repr(failure))
            save('RECOVERY-RESULT.json', result('INCOMPLETE_OR_FAILED', error, None))
    need(passed and not recovery_errors and not publication_errors, 'host experiment incomplete; inspect retained recovery evidence')


def terminate(signum, frame):
    global stop
    stop = True


if __name__ == '__main__':
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, terminate)
    main()
