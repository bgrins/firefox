import hashlib
import json
from pathlib import Path
import sys
import types

assert sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
before = (HERE / 'hooks-tested-run1.py').read_text()
after = (HERE / 'hooks.py').read_text()
addition = "    assert adapter.validate_refresh.__code__.co_name == 'validate_refresh'\n"
assert after.count(addition) == 1 and after.replace(addition, '') == before


def load(name, path):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec', dont_inherit=True), module.__dict__)
    return module


hooks = load('name_hooks', HERE / 'hooks.py')
pins = hooks.helper.read(HERE / 'INPUTS.json')
adapter = load('actual_adapter', ROOT / pins['adapter'])
original = adapter.validate_refresh
adapter.validate_refresh = adapter.native_head_view
try:
    hooks.validate_refresh(adapter, None, {}, {})
except AssertionError:
    pass
else:
    raise AssertionError('same-source wrong function accepted')
finally:
    adapter.validate_refresh = original
assert hooks.helper._memo is None
result = {'success': True, 'wrong_same_source_function_rejected_before_session': True,
          'exact_one_assertion_delta': True,
          'hooks_sha256': hashlib.sha256((HERE / 'hooks.py').read_bytes()).hexdigest(),
          'check_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(HERE / 'RESULT-name.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result),flush=True)
