import copy
import hashlib
import importlib
import json
from pathlib import Path
import sys
import types


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda path: json.loads(path.read_bytes())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
_memo = None


def load_source(name, path):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec', dont_inherit=True), module.__dict__)
    return module


def session_class(memo):
    class ScopedSession(memo.Session):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.wrapped_modules = []

        def wrap_module(self, module, import_ledger):
            original = getattr(module, 'validate_refresh', None)
            super().wrap_module(module, import_ledger)
            wrapped = getattr(module, 'validate_refresh', None)
            if wrapped is original:
                return

            def guarded(*args, **kwargs):
                if not self.active or memo.Session.active_session is not self:
                    raise memo.Rejected('saved validator escaped its invocation')
                return wrapped(*args, **kwargs)

            module.validate_refresh = guarded
            self.wrapped_modules.append((module, original, guarded))

        def __exit__(self, *exception):
            try:
                return super().__exit__(*exception)
            finally:
                for module, original, guarded in reversed(self.wrapped_modules):
                    module.validate_refresh = original

    return ScopedSession


def scoped_call(memo, registry, scope, function, receipt, stats):
    assert memo.Session.active_session is None, 'nested helper invocation'
    before = memo.encoded(scope)
    forbidden = [ROOT / 'artifacts/css-registered-number-native-runtime-v1' / name
                 for name in ('CURRENT-EPOCH.json', 'OWNED.json', 'ROLE.json', 'SOURCE-TRANSITION.lock')]
    session = session_class(memo)(ROOT, registry, scope, [ROOT / 'artifacts'], forbidden)
    try:
        with session:
            result = function(receipt)
            assert memo.encoded(scope) == before, 'outer validation inputs changed'
        return result
    finally:
        assert not session.active and not session.frames
        assert memo.Session.active_session is None
        assert all(getattr(target, name) is original
                   for (target, name), original in session.original.items())
        assert all(module.validate_refresh is original
                   for module, original, guarded in session.wrapped_modules)
        stats.update(calls=copy.deepcopy(session.calls), hits=copy.deepcopy(session.hits),
                     entries=len(session.table), hooks_restored=True, fresh_session=True,
                     outer_result_cached=False, module_functions_restored=True)


def validate_refresh(adapter, receipt, owner_policy, stats):
    global _memo
    assert sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode
    pins = read(HERE / 'INPUTS.json')
    for path, pin in pins['references'].items():
        assert sha(ROOT / path) == pin, path
    adapter_path = ROOT / pins['adapter']
    assert Path(adapter.__file__).resolve() == adapter_path.resolve()
    original = adapter.validate_refresh
    assert Path(original.__code__.co_filename).resolve() == adapter_path.resolve()
    assert adapter.binding == read(adapter_path.parent / 'BINDINGS.json')
    assert adapter.ROOT == ROOT
    if _memo is None:
        _memo = load_source('root_self_saved_memo', ROOT / pins['memo'])
    memo = _memo
    for name in ('argparse', 'configparser', 'copy', 'difflib', 'hashlib', 'importlib.util', 'json', 'os', 'pathlib',
                 're', 'shutil', 'signal', 'stat', 'subprocess', 'sys', 'tempfile', 'urllib.parse'):
        importlib.import_module(name)
    registry = read(ROOT / pins['registry'])
    assert len(registry) == 7
    for path, record in registry.items():
        assert sha(ROOT / path) == record['sha256']
        assert sha(ROOT / record['bindings_path']) == record['bindings_sha256']
        assert record['function'] == 'validate_refresh'
    scope = {'owner_policy': owner_policy, 'outer_binding': adapter.binding,
             'receipt': receipt, 'outer_code_sha256': sha(adapter_path),
             'outer_path': str(adapter_path), 'helper_sha256': sha(Path(__file__))}
    globals_before = {key: id(value) for key, value in adapter.__dict__.items()}
    result = scoped_call(memo, registry, scope, original, receipt, stats)
    assert adapter.validate_refresh is original
    assert {key: id(value) for key, value in adapter.__dict__.items()} == globals_before
    return json.loads(memo.encoded(result))
