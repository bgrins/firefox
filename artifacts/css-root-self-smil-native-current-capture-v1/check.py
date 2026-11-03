import builtins
import copy
import hashlib
import importlib.machinery
import json
from pathlib import Path
import sys
import time
import types

assert sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
read = lambda path: json.loads(path.read_bytes())


def load(name, path):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec', dont_inherit=True), module.__dict__)
    return module


adapter = load('new_saved_adapter', HERE / 'baseline.py')
binding = adapter.binding
for name, pin in binding['references'].items():
    assert sha(ROOT / name) == pin
parent = ROOT / binding['refresh_validator']['directory']
assert (HERE / 'capture_current.py').read_bytes() == (parent / 'capture_current.py').read_bytes()
assert binding['additional_sources'] == {}
assert binding['saved_parent_refresh'] == {
    'directory': 'artifacts/css-root-self-saved-refresh-memo-v1',
    'manifest_sha256': '9e486e64eedf15412c018fc15b99f984cb0a22621846bbecbb6cc80593a621b0'}
assert "previous = memo.validate_refresh(parent, receipt, binding, {})" in (HERE / 'baseline.py').read_text()
receipt = read(ROOT / binding['native_receipt'])
runtime = ROOT / binding['refresh_binding']['directory']
observed = (builtins.open, Path.read_bytes, Path.read_text, Path.stat,
            importlib.machinery.SourceFileLoader.exec_module)
result = {'success': False, 'native_or_live_capture': False, 'memo_registry_extended': False}
start = time.monotonic()
try:
    snapshot = adapter.validate_refresh(receipt)
    assert snapshot == read(runtime / 'POST.json') == read(runtime / 'PRE.json')
    assert observed == (builtins.open, Path.read_bytes, Path.read_text, Path.stat,
                        importlib.machinery.SourceFileLoader.exec_module)
    result['actual_saved_seconds'] = time.monotonic() - start
    negatives = []
    for label, mutate in [
        ('wrong parent source hash', lambda b: b['refresh_validator'].update(driver_sha256='0' * 64)),
        ('wrong helper manifest', lambda b: b['saved_parent_refresh'].update(manifest_sha256='0' * 64)),
        ('wrong parent bindings hash', lambda b: b['refresh_validator'].update(bindings_sha256='0' * 64)),
    ]:
        adapter.binding = copy.deepcopy(binding)
        mutate(adapter.binding)
        try:
            adapter.validate_refresh(receipt)
        except (AssertionError, RuntimeError) as error:
            if isinstance(error, RuntimeError):
                assert label == 'wrong helper manifest' and str(error).startswith('manifest digest: ')
            negatives.append(label)
        else:
            raise AssertionError('mutation accepted: ' + label)
    adapter.binding = copy.deepcopy(binding)
    wrong = ROOT / 'artifacts/css-keyframe-font-unit-native-current-capture-v2'
    adapter.binding['refresh_validator'] = {
        'directory': str(wrong.relative_to(ROOT)),
        'driver_sha256': sha(wrong / 'baseline.py'),
        'bindings_sha256': sha(wrong / 'BINDINGS.json')}
    try:
        adapter.validate_refresh(receipt)
    except AssertionError:
        negatives.append('different authentic parent rejected by fixed helper identity')
    else:
        raise AssertionError('different parent accepted')
    adapter.binding = binding
    assert observed == (builtins.open, Path.read_bytes, Path.read_text, Path.stat,
                        importlib.machinery.SourceFileLoader.exec_module)
    result.update(success=True, negatives=negatives, saved_snapshot_equal=True,
                  global_hooks_restored=True, new_outer_uncached=True,
                  known_parent_only=True, references=len(binding['references']),
                  seconds=time.monotonic()-start)
except BaseException as error:
    result.update(error=repr(error), seconds=time.monotonic()-start)
    (HERE / 'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    raise
(HERE / 'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,sort_keys=True),flush=True)
