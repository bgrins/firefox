import copy
import json
from pathlib import Path
import sys
import time
import types

assert sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load(name, path):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec', dont_inherit=True), module.__dict__)
    return module


hooks = load('scoped_hooks', HERE / 'hooks.py')
pins = hooks.helper.read(HERE / 'INPUTS.json')
adapter = load('actual_adapter', ROOT / pins['adapter'])
receipt = hooks.helper.read(ROOT / pins['receipt'])
policy = hooks.helper.read(HERE / 'OWNER-POLICY.json')
capture = hooks.helper.read(ROOT / pins['capture'])
original = adapter.validate_refresh
result = {'success': False, 'deployment': False, 'native_or_browser_run': False}
start = time.monotonic()
try:
    stats = {}
    with hooks.refresh_scope(adapter, policy, stats) as native_head:
        retained = adapter.validate_refresh
        actual = native_head(receipt)
    assert adapter.validate_refresh is original
    assert actual['head'] == capture['checkpoint']['commit']
    assert actual['epoch_sha256'] == adapter.binding['current_epoch_sha256']
    assert actual['committed'] and actual['signature_verified']
    assert actual['authority_kind'] == 'internal-observed-head-from-native-receipt-and-raw-refresh'
    assert stats['refresh_hook_calls'] == 1 and stats['hooks_restored']
    negatives = []
    try:
        retained(receipt)
    except AssertionError as error:
        assert str(error) == 'refresh hook escaped its invocation'
        negatives.append('retained outer hook after success')
    else:
        raise AssertionError('escaped hook accepted')
    try:
        with hooks.refresh_scope(adapter, policy, {}) as native_head:
            retained = adapter.validate_refresh
            native_head({})
    except AssertionError:
        negatives.append('actual native head exception')
    else:
        raise AssertionError('invalid native receipt accepted')
    assert adapter.validate_refresh is original
    try:
        retained(receipt)
    except AssertionError as error:
        assert str(error) == 'refresh hook escaped its invocation'
        negatives.append('retained outer hook after exception')
    else:
        raise AssertionError('escaped failed hook accepted')
    clone = types.FunctionType(original.__code__, dict(adapter.__dict__))
    adapter.validate_refresh = clone
    try:
        hooks.native_head_view(adapter, receipt, policy, {})
    except AssertionError:
        negatives.append('wrong original globals')
    else:
        raise AssertionError('detached globals accepted')
    finally:
        adapter.validate_refresh = original
    assert hooks.helper._memo.Session.active_session is None
    result.update(success=True, actual_head_view=actual, stats=stats, negatives=negatives,
                  original_attribute_restored=True, seconds=time.monotonic()-start)
except BaseException as error:
    result.update(error=repr(error), seconds=time.monotonic()-start)
    (HERE / 'RESULT-hook.json').write_text(json.dumps(result,indent=2)+'\n')
    raise
(HERE / 'RESULT-hook.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,sort_keys=True),flush=True)
