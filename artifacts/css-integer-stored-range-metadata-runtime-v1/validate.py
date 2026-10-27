import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import stat
import sys
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
COMMON = 'artifacts/css-cubic-bezier-calc-range-comparison-v1/compare.py'
terminated = False
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
digest = lambda b: hashlib.sha256(b).hexdigest()


def need(value, message):
    if not value:
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


def bound(item, parse=True):
    need(isinstance(item, dict), 'missing actual binding')
    p = Path(item['path'])
    need(not p.is_absolute() and '..' not in p.parts, 'relative evidence path')
    p = ROOT / p
    need(sha(p) == item['sha256'], 'evidence digest ' + str(p))
    return read(p) if parse else p


def check_rows(before, after, roster):
    def keyed(rows):
        result = {(r['test'], r['subtest']): r for r in rows}
        need(len(result) == len(rows), 'duplicate rows')
        need(set(result) == {(t, n) for t, names in roster.items() for n in names}, 'exact selected roster')
        return result
    old, new = keyed(before), keyed(after)
    targets = {('/css/css-easing/timing-functions-syntax-computed.html',
                "Property animation-timing-function value 'steps(calc(-10), start)'")}
    need(targets <= set(old), 'exact stored-range target')
    for key, a in old.items():
        b = new[key]
        need(all(a.get(f) == b.get(f) for f in ('status', 'message', 'known_intermittent')), 'raw observation ' + str(key))
        if key in targets:
            need(a['status'] == b['status'] == 'PASS' and not a.get('known_intermittent'), 'target actual PASS')
            need(a.get('expected', a['status']) == 'FAIL' and b.get('expected', b['status']) == 'PASS', 'target expectation FAIL to PASS')
        else:
            need(a.get('expected') == b.get('expected'), 'unchanged control expectation ' + str(key))
    return {'rows': len(old), 'targets': [list(k) for k in sorted(targets)], 'other_observations_exact': True}


def check_baseline(historical, fresh, roster):
    expected = {(t, n) for t, names in roster.items() for n in names}
    def keyed(rows):
        result = {(r['test'], r['subtest']): r for r in rows}
        need(len(result) == len(rows) and set(result) == expected, 'exact fresh roster')
        return result
    old, new = keyed(historical), keyed(fresh)
    for key, row in old.items():
        need(all(row.get(f) == new[key].get(f) for f in
                 ('status', 'message', 'expected', 'known_intermittent')),
             'historical outcome changed before metadata correction ' + str(key))
    return {'rows': len(old), 'historical_outcomes_exact': True}


def archived_baseline(binding, tests, roster):
    result = bound(binding['run'])
    events = [json.loads(line) for line in bound(binding['raw'], False).read_text().splitlines()]
    config = bound(binding['config'])
    rows = [e for e in events if e.get('action') == 'test_status']
    starts = [e for e in events if e.get('action') == 'test_start']
    ends = [e for e in events if e.get('action') == 'test_end']
    need(result['complete'] and result['before'] == result['after'], 'historical installed capture complete/stable')
    need(rows == result['rows'] and starts == result['starts'] and ends == result['ends'], 'raw to RUN join')
    need(not tests.infrastructure_faults(events) and tests.lifecycle(events, config), 'retained lifecycle')
    need(tests.exit_matches_results(result['exit'], rows + ends), 'retained exit semantics')
    need(len(rows) == 113 and len(starts) == len(ends) == 5, 'historical full installed cubic run')
    need(all(e['status'] == e.get('expected', e['status']) == 'OK' and not e.get('known_intermittent') for e in ends), 'retained harness ends')
    for t, names in config['expected_subtests'].items():
        need([r['subtest'] for r in rows if r['test'] == t] == names, 'retained exact roster')
    need(config['expected_subtests'] == roster, 'full historical roster join')
    return rows


def capture_epoch_join(retained, roles, binaries, paths, roster, native):
    capture_roles = set(binaries) | set(paths) | {native} | {
        'testing/web-platform/tests/' + t.lstrip('/') for t in roster}
    need(capture_roles <= set(roles) and capture_roles <= set(retained['after'])
         and all(retained['after'][n] == roles[n] for n in capture_roles),
         'capture to admitted binaries/native/selected WPT/metadata')


def main():
    inputs = read(HERE / 'INPUTS.json')
    need(sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize, 'isolated interpreter')
    need(sys.argv[1:] == ['--run'] and inputs['ready'] is True, 'disabled validation')
    for p, value in inputs['local_pins'].items():
        need(sha(HERE / p) == value, 'local payload ' + p)
    for p, value in read(HERE / 'REFERENCES.json').items():
        need(sha(ROOT / p) == value, 'helper reference ' + p)
    for n in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'MOZ_CONFIGURE_OPTIONS', 'MOZ_ARTIFACT_BUILDS'):
        need(not os.environ.get(n), 'ambient ' + n)
    review = bound(inputs['root_review'])
    need(review['status'] == 'INTEGER_RANGE_METADATA_VALIDATION_ROOT_REVIEW_GO' and review['local_pins'] == inputs['local_pins'], 'root source review')
    admission = bound(inputs['installed_admission'])
    need(admission['status'] == 'INTEGER_RANGE_METADATA_EPOCH_VERIFIED' and admission['outer_exit'] == 0, 'actual current admission')
    for item in admission['evidence']:
        bound(item, False)
    need(admission['evidence'], 'actual terminal/preservation evidence')
    epoch = bound(admission['epoch'])
    common = load('metadata_common', ROOT / COMMON)
    h = common.load('metadata_guards', ROOT / 'artifacts/css-keyframe-commit-styles-implicit-clean-comparison-v1/compare.py')
    tests = load('metadata_tests', HERE / 'tests.py')
    process = load('metadata_process', HERE / 'process_control.py')
    roster, paths = read(HERE / 'ROSTER.json'), read(HERE / 'PATHS.json')
    historical_rows = archived_baseline(read(HERE / 'HISTORICAL-CAPTURE.json'), tests, roster)
    roles = epoch['pins']
    need(set(admission['binaries']) == common.BINARY_ROLES and all(roles[n] == v for n, v in admission['binaries'].items()), 'exact four current binaries')
    historical_run = bound(read(HERE / 'HISTORICAL-CAPTURE.json')['run'])
    capture_epoch_join(historical_run, roles, set(), paths, roster, common.NATIVE)
    for name in ('servo/components/style/values/specified/number.rs',
                 'testing/web-platform/meta/css/css-easing/timing-functions-syntax-valid.html.ini'):
        need(name in roles and roles[name] == historical_run['after'][name], 'installed easing input ' + name)
    need(set(paths) <= set(roles) and all(roles[n] == v['preimage']['sha256'] for n, v in paths.items()), 'original metadata roles')
    env = dict(os.environ, GIT_OPTIONAL_LOCKS='0', MOZCONFIG=str(ROOT / 'mozconfig'), MOZ_OBJDIR=str(common.OBJ),
               MOZ_SKIP_PATH_PERFORMANCE_CHECK='1', MOZ_HEADLESS='1', PYTHONDONTWRITEBYTECODE='1')
    excluded = [':(exclude)' + n for n in sorted(paths)]
    external = digest(h.git(ROOT, env, 'diff', '--binary', '--', '.', *excluded))
    config = {'tests': [t.lstrip('/') for t in roster], 'expected_subtests': roster,
              'baseline_tests': [t.lstrip('/') for t in roster], 'baseline_expected_subtests': roster,
              'reftests': [], 'guard_sources': list(roles)}
    adapter = types.SimpleNamespace(CONFIG=config, HERE=HERE, ROOT=ROOT, ENV=env, PYTHON=common.PYTHON,
        BINARY=common.OBJ / 'dist/Nightly.app/Contents/MacOS/firefox', BINARIES=common.BINARY_ROLES,
        WPT_CONFIG=common.OBJ / '_tests/web-platform/wptrunner.local.ini', PREFS_ROOT=ROOT / 'testing/profiles',
        pins=lambda names: {n: h.fingerprint(ROOT, n) for n in names}, need=need,
        cancelled=lambda: terminated, owned_group=None, process_control=process)
    owned, errors = {}, []
    def quiet():
        need(adapter.owned_group is None, 'owned process must be absent before metadata changes')
    def verify(label):
        before = h.index_state(ROOT, env)
        expected = roles | {n: item['owned_sha256'] for n, item in owned.items()}
        need(adapter.pins(expected) == expected, 'all roles/source/binaries')
        need(all(before[k] == epoch['semantic_index'][k] for k in ('head', 'entries', 'cached_diff')), 'root semantic staging')
        need(h.semantic_index(h.index_state(ROOT / 'artifacts/css-spec-lean', env)) == epoch['nested_semantic_index'], 'nested state')
        need(digest(h.git(ROOT, env, 'diff', '--binary', '--', '.', *excluded)) == external, 'unrelated working diff')
        for name in ('staged_working', 'committed_research_working_payloads'):
            need(adapter.pins(epoch[name]) == epoch[name], name)
        for n, identity in epoch['installed_identities'].items():
            info = (ROOT / n).lstat()
            need(stat.S_ISREG(info.st_mode) and [info.st_dev, info.st_ino] == identity, 'installed identity ' + n)
        for n, item in owned.items():
            info = (ROOT / n).lstat()
            need(stat.S_ISREG(info.st_mode) and [info.st_dev, info.st_ino] == item['identity'], 'owned metadata identity')
        modified = {n for n in h.git(ROOT, env, 'diff', '--name-only').decode().splitlines() if not n.startswith('artifacts/')}
        changed = {n for n, item in owned.items() if item['owned_sha256'] != paths[n]['preimage']['sha256']}
        need(modified == set(epoch['modified_native_paths']) | changed, 'exact modified inventory')
        untracked = h.git(ROOT, env, 'ls-files', '--others', '--exclude-standard', '--', 'layout', 'dom', 'servo', 'mfbt').decode().splitlines()
        need(set(untracked) == set(epoch['untracked_native']), 'scoped untracked inventory')
        after = h.index_state(ROOT, env)
        need(before == after, 'index stable within guard')
        save(label, {'pins': expected, 'index': after, 'modified_native_paths': sorted(modified)})
        return expected
    originals = {n: (HERE / 'original' / n).read_bytes() for n in paths}
    candidates = {n: (HERE / 'candidate' / n).read_bytes() for n in paths}
    need(all(digest(originals[n]) == v['preimage']['sha256'] and digest(candidates[n]) == v['postimage']['sha256'] for n, v in paths.items()), 'exact metadata bodies')
    verify('BEFORE.json')
    need(h.semantic_index(h.index_state(ROOT, env)) == epoch['semantic_index'], 'full initial working diff')
    save('CONFIG.json', config)
    success, error = False, None
    try:
        resources = verify('BASELINE-BEFORE.json')
        common.ports_free(read(ROOT / 'testing/web-platform/tests/config.json'))
        baseline = tests.run(adapter, 'baseline', resources)
        quiet()
        capture_epoch_join(baseline, roles, common.BINARY_ROLES, paths, roster, common.NATIVE)
        save('BASELINE-COMPARISON.json', check_baseline(historical_rows, baseline['rows'], roster))
        verify('BASELINE-AFTER.json')
        original_rows = baseline['rows']
        for n in paths:
            quiet()
            need(not terminated, 'termination requested')
            info = (ROOT / n).lstat()
            need(stat.S_ISREG(info.st_mode) and sha(ROOT / n) == paths[n]['preimage']['sha256'], 'metadata prewrite')
            owned[n] = {'path': n, 'identity': [info.st_dev, info.st_ino], 'owned_sha256': paths[n]['preimage']['sha256']}
            common.write_owned(ROOT, owned[n], candidates[n])
        resources = verify('CANDIDATE-BEFORE.json')
        common.ports_free(read(ROOT / 'testing/web-platform/tests/config.json'))
        result = tests.run(adapter, 'metadata', resources)
        save('COMPARISON.json', check_rows(original_rows, result['rows'], roster))
        quiet()
        verify('CANDIDATE-AFTER.json')
        need(not terminated, 'termination requested')
        verify('FINAL.json')
        save('RESULT.json', {'success': True, 'error': None, 'cleanup_errors': [],
            'metadata_retained': True, 'owned_inputs': owned, 'owned_group': adapter.owned_group,
            'native_build': False, 'accepted_fix': False, 'fresh_baseline_required': True})
        success = True
    except BaseException as failure:
        error = repr(failure)
    finally:
        if not success:
            for n, item in owned.items():
                try:
                    quiet()
                    common.restore_owned(ROOT, item, originals[n])
                except BaseException as failure:
                    errors.append('metadata restoration ' + n + ': ' + repr(failure))
            try:
                quiet()
                verify('RECOVERY-FINAL.json')
                need(h.semantic_index(h.index_state(ROOT, env)) == epoch['semantic_index'], 'full original restoration')
            except BaseException as failure:
                errors.append('final guard: ' + repr(failure))
            save('FAILURE.json', {'success': False, 'error': error, 'cleanup_errors': errors,
                'metadata_retained': False, 'owned_inputs': owned, 'owned_group': adapter.owned_group,
                'native_build': False, 'accepted_fix': False, 'fresh_baseline_required': True})
    need(success and not errors, 'validation failed; original evidence and recovery retained')


def terminate(signum, frame):
    global terminated
    terminated = True


if __name__ == '__main__':
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, terminate)
    main()
