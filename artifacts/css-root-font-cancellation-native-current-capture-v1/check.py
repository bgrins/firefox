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
assert binding['additional_sources'] == read(ROOT/'artifacts/css-keyframe-font-unit-native-current-capture-v2/BINDINGS.json')['additional_sources']
assert 'saved_parent_refresh' not in binding
assert 'previous = parent.validate_refresh(receipt)' in (HERE/'baseline.py').read_text()
assert (parent/'baseline.py').read_bytes() == (ROOT/'artifacts/css-root-self-smil-native-current-capture-v1/baseline.py').read_bytes()
import ast
current_source = (HERE/'baseline.py').read_text()
old_source = (ROOT/'artifacts/css-keyframe-font-unit-native-current-capture-v2/baseline.py').read_text()
def claim_body(source):
    return ast.get_source_segment(source, next(node for node in ast.parse(source).body if isinstance(node, ast.FunctionDef) and node.name == 'claim_additional_sources'))
assert claim_body(current_source) == claim_body(old_source)
assert binding['source_preimages']['servo/ports/geckolib/glue.rs'] == '83cc1e6f6d27aa92d34377564aa6969dbdda838dd880b401e35de08f250d5027'
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
        ('pending refresh', lambda b: b.update(pending_pair_refresh=True)),
        ('wrong parent bindings hash', lambda b: b['refresh_validator'].update(bindings_sha256='0' * 64)),
    ]:
        adapter.binding = copy.deepcopy(binding)
        mutate(adapter.binding)
        try:
            adapter.validate_refresh(receipt)
        except (AssertionError, RuntimeError) as error:
            if isinstance(error, RuntimeError):
                raise
            negatives.append(label)
        else:
            raise AssertionError('mutation accepted: ' + label)
    adapter.binding = binding
    wrong_receipt = dict(receipt, signature_verified=False)
    try:
        adapter.native_head_view(wrong_receipt)
    except AssertionError:
        negatives.append('modified native receipt rejected before saved bridge')
    else:
        raise AssertionError('modified native receipt accepted')
    adapter.binding = binding
    assert observed == (builtins.open, Path.read_bytes, Path.read_text, Path.stat,
                        importlib.machinery.SourceFileLoader.exec_module)
    result.update(success=True, negatives=negatives, saved_snapshot_equal=True,
                  global_hooks_restored=True, new_outer_uncached=True,
                  known_parent_memo_remains_nested=True, references=len(binding['references']),
                  seconds=time.monotonic()-start)
except BaseException as error:
    result.update(error=repr(error), seconds=time.monotonic()-start)
    (HERE / 'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    raise
(HERE / 'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,sort_keys=True),flush=True)
