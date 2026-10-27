import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import types

HERE = Path(__file__).resolve().parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


v = load('metadata_validation', HERE / 'validate.py')
common = load('metadata_common_check', v.ROOT / v.COMMON)
roster = v.read(HERE / 'ROSTER.json')
for name, expected in v.read(HERE / 'REFERENCES.json').items():
    assert v.sha(v.ROOT / name) == expected, name
for name in ('tests.py', 'process_control.py'):
    assert (HERE / name).read_bytes() == (v.ROOT / 'artifacts/css-steps-metadata-validation-v2' / name).read_bytes()
runtime = v.ROOT / 'artifacts/css-cubic-bezier-final-install-runtime-v1'
manifest = v.read(runtime / 'FILES.json')
for name, expected in manifest.items():
    assert v.sha(runtime / name) == expected, name
tests_module = load('archived_tests', HERE / 'tests.py')
before = v.archived_baseline(v.read(HERE / 'HISTORICAL-CAPTURE.json'), tests_module, roster)
targets = [i for i, r in enumerate(before) if r['test'] == '/css/css-easing/timing-functions-syntax-computed.html'
           and r['subtest'] == "Property animation-timing-function value 'steps(calc(-10), start)'"]
assert len(targets) == 1
control = next(i for i, r in enumerate(before) if r['status'] == 'FAIL')
after = copy.deepcopy(before)
for i in targets:
    del after[i]['expected']
assert v.check_rows(before, after, roster)['rows'] == 113
assert v.check_baseline(before, copy.deepcopy(before), roster)['rows'] == 113
baseline_negatives = 0
for field, value in [('status', 'PASS'), ('message', 'changed'), ('expected', 'PASS'), ('known_intermittent', ['PASS'])]:
    changed = copy.deepcopy(before)
    changed[control][field] = value
    try:
        v.check_baseline(before, changed, roster)
    except RuntimeError:
        baseline_negatives += 1
    else:
        raise AssertionError('changed fresh baseline admitted')
negative_count = 0
for mutate in (
    lambda a: a.pop(),
    lambda a: a.append(copy.deepcopy(a[0])),
    lambda a: a[targets[0]].update(status='FAIL'),
    lambda a: a[targets[0]].update(expected='FAIL'),
    lambda a: a[targets[0]].update(message='changed'),
    lambda a: a[targets[0]].update(known_intermittent=['PASS']),
    lambda a: a[control].update(expected='PASS'),
    lambda a: a[0].update(status='FAIL'),
    lambda a: a[0].update(message='changed'),
    lambda a: a[0].update(known_intermittent=['FAIL']),
):
    changed = copy.deepcopy(after)
    mutate(changed)
    try:
        v.check_rows(before, changed, roster)
    except RuntimeError:
        negative_count += 1
    else:
        raise AssertionError('bad rows accepted')

tree = ast.parse((HERE / 'validate.py').read_text())
metadata_paths = v.read(HERE / 'PATHS.json')
joined = common.BINARY_ROLES | set(metadata_paths) | {common.NATIVE} | {
    'testing/web-platform/tests/' + t.lstrip('/') for t in roster}
roles = {name: 'a' * 64 for name in joined}
retained = {'after': dict(roles)}
v.capture_epoch_join(retained, roles, common.BINARY_ROLES, metadata_paths, roster, common.NATIVE)
join_negatives = 0
for name in sorted(joined):
    altered = copy.deepcopy(retained)
    altered['after'][name] = 'b' * 64
    try:
        v.capture_epoch_join(altered, roles, common.BINARY_ROLES, metadata_paths, roster, common.NATIVE)
    except RuntimeError:
        join_negatives += 1
    else:
        raise AssertionError('stale capture role admitted')
altered = copy.deepcopy(retained)
del altered['after'][common.NATIVE]
try:
    v.capture_epoch_join(altered, roles, common.BINARY_ROLES, metadata_paths, roster, common.NATIVE)
except RuntimeError:
    join_negatives += 1
else:
    raise AssertionError('missing capture source admitted')
main = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'main')
tail = next(n for n in main.body if isinstance(n, ast.Try))
code = compile(ast.Module(body=[tail], type_ignores=[]), '<actual-validation-tail>', 'exec')
tail_cases = []
for fault in ('none', 'baseline_capture', 'baseline_policy', 'capture', 'compare', 'post_guard', 'final_guard', 'publication', 'partial_write', 'unknown_edit', 'live_group'):
    with tempfile.TemporaryDirectory(prefix='integer-metadata-control-', dir='/private/tmp') as td:
        root = Path(td)
        originals = {'one.ini': b'old one'}
        candidates = {n: b'new ' + b for n, b in originals.items()}
        for n, b in originals.items():
            (root / n).write_bytes(b)
        paths = {n: {'preimage': {'sha256': hashlib.sha256(b).hexdigest()}} for n, b in originals.items()}
        adapter = types.SimpleNamespace(owned_group=None)
        records = {}
        def quiet():
            v.need(adapter.owned_group is None, 'live group')
        def verify(label):
            if (fault, label) in (('post_guard', 'CANDIDATE-AFTER.json'), ('final_guard', 'FINAL.json')):
                raise RuntimeError(fault)
            records[label] = True
            return {}
        def save(name, value):
            if fault == 'publication' and name == 'RESULT.json':
                raise OSError('publication')
            records[name] = value
        def run(*args):
            if args[1] == 'baseline':
                if fault == 'baseline_capture':
                    raise RuntimeError(fault)
                return {'rows': before}
            if fault == 'live_group':
                adapter.owned_group = 123
                raise RuntimeError('cleanup rejected')
            if fault == 'unknown_edit':
                (root / 'one.ini').write_bytes(b'unknown')
                raise RuntimeError('unknown edit')
            if fault == 'capture':
                raise RuntimeError(fault)
            return {'rows': after}
        def compare(*args):
            if fault == 'compare':
                raise RuntimeError(fault)
            return v.check_rows(*args)
        def write(root, item, body):
            if fault == 'partial_write' and item['path'] == 'one.ini':
                common.write_owned(root, item, body[:2])
                raise OSError('partial write')
            common.write_owned(root, item, body)
        ns = dict(v.__dict__, ROOT=root, paths=paths, candidates=candidates, originals=originals,
            owned={}, errors=[], success=False, error=None, terminated=False, adapter=adapter,
            historical_rows=before, roster=roster, read=lambda p: {}, quiet=quiet, verify=verify, save=save,
            roles={}, capture_epoch_join=lambda *args: None,
            check_baseline=lambda *args: v.need(fault != 'baseline_policy', 'baseline policy'),
            check_rows=compare, tests=types.SimpleNamespace(run=run),
            common=types.SimpleNamespace(write_owned=write, restore_owned=common.restore_owned, ports_free=lambda c: None, BINARY_ROLES=common.BINARY_ROLES, NATIVE=common.NATIVE),
            epoch={'semantic_index': {}}, env={},
            h=types.SimpleNamespace(index_state=lambda *args: {}, semantic_index=lambda x: x))
        exec(code, ns)
        assert ns['success'] == (fault == 'none')
        if fault == 'none':
            assert all((root / n).read_bytes() == b for n, b in candidates.items())
        elif fault == 'live_group':
            assert all((root / n).read_bytes() == b for n, b in candidates.items()) and ns['errors']
        elif fault == 'unknown_edit':
            assert (root / 'one.ini').read_bytes() == b'unknown' and ns['errors']
        else:
            assert all((root / n).read_bytes() == b for n, b in originals.items()) and not ns['errors']
        tail_cases.append(fault)
config_node = next(n for n in main.body if isinstance(n, ast.Assign)
                   and any(isinstance(t, ast.Name) and t.id == 'config' for t in n.targets))
config_ns = {'roster': roster, 'roles': {}}
exec(compile(ast.Module(body=[config_node], type_ignores=[]), '<actual-config>', 'exec'), config_ns)
config = config_ns['config']
raw_path = v.bound(v.read(HERE / 'HISTORICAL-CAPTURE.json')['raw'], False)
archived_events = [json.loads(line) for line in raw_path.read_text().splitlines()]
dispatch_checks = []
with tempfile.TemporaryDirectory(prefix='integer-metadata-dispatch-', dir='/private/tmp') as td:
    scratch = Path(td)
    calls = []
    phase_events = {}
    for phase in ('baseline', 'metadata'):
        events = copy.deepcopy(archived_events)
        if phase == 'metadata':
            for e in events:
                if e.get('action') == 'test_status' and (e['test'], e['subtest']) == (
                        before[targets[0]]['test'], before[targets[0]]['subtest']):
                    del e['expected']
        phase_events[phase] = events
    class FakeProcess:
        pid = 123456
        def __init__(self, command, **kwargs):
            calls.append(command)
            log = Path(next(a.removeprefix('--log-raw=') for a in command if a.startswith('--log-raw=')))
            phase = log.parent.name.removeprefix('wpt-')
            events = phase_events[phase]
            log.write_text(''.join(json.dumps(e) + '\n' for e in events))
            terminal = [e for e in events if e.get('action') in ('test_status', 'test_end')]
            self.code = 0 if tests_module.exit_matches_results(0, terminal) else 1
        def wait(self, timeout):
            return self.code
    actual_subprocess = tests_module.subprocess
    tests_module.subprocess = types.SimpleNamespace(Popen=FakeProcess, STDOUT=-2,
        TimeoutExpired=actual_subprocess.TimeoutExpired)
    adapter = types.SimpleNamespace(CONFIG=config, HERE=scratch, ROOT=scratch, ENV={},
        PYTHON='not-executed', BINARY=scratch/'not-executed', WPT_CONFIG=scratch/'config.ini',
        PREFS_ROOT=scratch, BINARIES=set(), pins=lambda names: {}, need=v.need,
        cancelled=lambda: False, owned_group=None,
        process_control=types.SimpleNamespace(terminate=lambda p: {'owned_group_absent': True}))
    try:
        results = {}
        for phase in ('baseline', 'metadata'):
            results[phase] = tests_module.run(adapter, phase, {})
            assert results[phase]['complete'] and len(results[phase]['rows']) == 113
            assert calls[-1][-5:] == config['tests'] and adapter.owned_group is None
            assert (scratch/('wpt-'+phase)/'PROCESS-CLEANUP.json').is_file()
            dispatch_checks.append(phase)
        v.check_rows(results['baseline']['rows'], results['metadata']['rows'], roster)
        for key in ('baseline_tests', 'baseline_expected_subtests'):
            bad = dict(config)
            del bad[key]
            adapter.CONFIG = bad
            count = len(calls)
            try:
                tests_module.run(adapter, 'baseline', {})
            except KeyError as error:
                assert error.args == (key,) and len(calls) == count
            else:
                raise AssertionError('missing baseline key accepted')
            dispatch_checks.append('missing-'+key+'-rejected-before-process')
    finally:
        tests_module.subprocess = actual_subprocess
print(json.dumps({'status': 'INTEGER_RANGE_METADATA_STATIC_CHECKS_PASS', 'fresh_baseline_negatives': baseline_negatives, 'row_negatives': negative_count,
    'capture_epoch_join_negatives': join_negatives,
    'actual_tail_cases': tail_cases, 'actual_helper_dispatch': dispatch_checks, 'scratch_removed': True, 'browser_or_live_mutation': False}, indent=2))
