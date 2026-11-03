import importlib.util
import json
from contextlib import contextmanager
from pathlib import Path


HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('scoped_saved_refresh_helper', HERE / 'helper.py')
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)


@contextmanager
def refresh_scope(adapter, owner_policy, stats):
    pins = helper.read(HERE / 'INPUTS.json')
    source = helper.ROOT / pins['adapter']
    assert helper.sha(source) == pins['references'][pins['adapter']]
    original = adapter.validate_refresh
    native_head = adapter.native_head_view
    for function, name in ((original, 'validate_refresh'), (native_head, 'native_head_view')):
        assert function.__globals__ is adapter.__dict__
        assert function.__code__.co_name == name
        assert Path(function.__code__.co_filename).resolve() == source.resolve()
    assert adapter.binding == json.loads((source.parent / 'BINDINGS.json').read_bytes())
    active = True
    calls = 0

    def refresh(receipt):
        nonlocal calls
        assert active, 'refresh hook escaped its invocation'
        assert adapter.validate_refresh is refresh
        calls += 1
        assert calls == 1, 'native head invoked refresh more than once'
        adapter.validate_refresh = original
        try:
            return helper.validate_refresh(adapter, receipt, owner_policy, stats)
        finally:
            adapter.validate_refresh = refresh

    adapter.validate_refresh = refresh
    try:
        yield native_head
        assert calls == 1
    finally:
        active = False
        adapter.validate_refresh = original
        stats.update(refresh_hook_calls=calls, outer_attribute_restored=True)


def native_head_view(adapter, receipt, owner_policy, stats):
    with refresh_scope(adapter, owner_policy, stats) as original:
        return original(receipt)


def validate_refresh(adapter, receipt, owner_policy, stats):
    assert adapter.validate_refresh.__globals__ is adapter.__dict__
    return helper.validate_refresh(adapter, receipt, owner_policy, stats)
