import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import time
import types

assert sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda path: json.loads(path.read_bytes())


def load(name, path):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec', dont_inherit=True), module.__dict__)
    return module


pins = read(HERE / 'INPUTS.json')
helper = load('scoped_refresh_helper', HERE / 'helper.py')
adapter = load('actual_root_self_adapter', ROOT / pins['adapter'])
receipt = read(ROOT / pins['receipt'])
policy = read(HERE / 'OWNER-POLICY.json')
capture = read(ROOT / pins['capture'])
result = {'success': False, 'native_or_browser_run': False, 'deployment': False}
started = time.monotonic()
try:
    stats = {}
    snapshot = helper.validate_refresh(adapter, receipt, policy, stats)
    assert snapshot == capture['snapshot']
    assert len(stats['calls']) == 7 and sum(stats['hits'].values()) > 0
    assert all(count == 1 for count in stats['calls'].values())
    result.update(actual_capture_snapshot_equal=True, exact_outer_seconds=time.monotonic()-started,
                  exact_outer_stats=stats)
    print(json.dumps({'actual_outer_complete': result}), flush=True)
    negatives = []
    bad = copy.deepcopy(receipt)
    bad['commit'] = '0' * 40
    failed = {}
    try:
        helper.validate_refresh(adapter, bad, policy, failed)
    except AssertionError:
        negatives.append('changed native receipt rejected by actual outer/parent')
    else:
        raise AssertionError('changed receipt accepted')
    assert failed['hooks_restored'] and failed['fresh_session']
    assert all(count == 1 for count in failed['calls'].values())
    original_binding = adapter.binding
    adapter.binding = copy.deepcopy(original_binding)
    adapter.binding['current_epoch_sha256'] = '0' * 64
    try:
        helper.validate_refresh(adapter, receipt, policy, {})
    except AssertionError:
        negatives.append('changed in-memory outer binding rejected')
    else:
        raise AssertionError('changed binding accepted')
    finally:
        adapter.binding = original_binding
    memo = helper.load_source('boundary_memo', ROOT / pins['memo'])
    registry = read(ROOT / pins['registry'])
    escaped = []
    def retains_validator(throw):
        path = ROOT / next(iter(registry))
        spec = importlib.util.spec_from_file_location('retained_validator', path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        escaped.append((module, module.validate_refresh))
        if throw:
            raise ValueError('retained exception')
        return {'saved': True}
    for throw in (False, True):
        try:
            helper.scoped_call(memo, registry, {'throw': throw}, retains_validator, throw, {})
        except ValueError as error:
            assert throw and str(error) == 'retained exception'
        module, guarded = escaped[-1]
        assert module.validate_refresh is not guarded
        assert Path(module.validate_refresh.__code__.co_filename) == ROOT / next(iter(registry))
        try:
            guarded(None)
        except memo.Rejected as error:
            assert str(error) == 'saved validator escaped its invocation'
            negatives.append('retained validator rejected after ' + ('exception' if throw else 'success'))
        else:
            raise AssertionError('escaped validator accepted')
    calls = []
    with tempfile.TemporaryDirectory(prefix='root-self-memo-boundary-', dir='/private/tmp') as directory:
        scratch = Path(directory)
        file = scratch / 'value'
        file.write_text('one')
        def uncached_outer(value):
            calls.append(value)
            return file.read_text()
        one = helper.scoped_call(memo, registry, {'value': 1}, uncached_outer, 1, {})
        file.write_text('two')
        two = helper.scoped_call(memo, registry, {'value': 2}, uncached_outer, 2, {})
        assert (one, two, calls) == ('one', 'two', [1, 2])
        def throws(value):
            raise ValueError('boundary sentinel')
        boundary_stats = {}
        try:
            helper.scoped_call(memo, registry, {'value': 3}, throws, 3, boundary_stats)
        except ValueError as error:
            assert str(error) == 'boundary sentinel'
            negatives.append('uncached outer exception propagated')
        else:
            raise AssertionError('exception swallowed')
        assert boundary_stats['hooks_restored']
        mutated_scope = {'policy': {'value': 4}}
        def mutates(value):
            mutated_scope['policy']['value'] = 5
        try:
            helper.scoped_call(memo, registry, mutated_scope, mutates, None, {})
        except AssertionError:
            negatives.append('outer policy mutation rejected')
        else:
            raise AssertionError('input mutation accepted')
        with open(file) as stream:
            assert stream.read() == 'two'
    assert not scratch.exists()
    result.update(success=True, negatives=negatives, failed_call_stats=failed,
                  outer_executed_each_time=True, changed_outer_file_observed=True,
                  no_cross_invocation_cache=True, post_exception_io_unchanged=True,
                  scratch_removed=str(scratch), seconds=time.monotonic()-started)
except BaseException as error:
    result.update(error=repr(error), seconds=time.monotonic()-started)
    (HERE / 'RESULT-run1.json').write_text(json.dumps(result,indent=2)+'\n')
    raise
(HERE / 'RESULT-run1.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,sort_keys=True), flush=True)
