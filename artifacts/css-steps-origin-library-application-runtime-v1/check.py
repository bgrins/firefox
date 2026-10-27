import argparse
import ast
import copy
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--output', type=Path, required=True)
out = parser.parse_args().output.resolve()
assert not out.exists() and not out.is_symlink()
source = (HERE / 'apply.py').read_text()
tree = ast.parse(source)
function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'validate_binding')
namespace = {'Path': Path}
exec(compile(ast.Module(body=[function], type_ignores=[]), 'binding-only', 'exec'), namespace)
check = namespace['validate_binding']
actual = json.loads((HERE / 'INPUTS.json').read_text())
assert actual == json.loads((HERE / 'STATIC-INPUTS.json').read_text())
good = copy.deepcopy(actual)
good.update(ready=True, post_capture_epoch={'path': 'artifacts/example/epoch.json', 'sha256': 'a'*64},
            post_capture_receipt={'path': 'artifacts/example/root.json', 'sha256': 'b'*64, 'required_fields': {'status': 'SYNTHETIC_COMPLETED'}},
            protected_binary_paths=copy.deepcopy(actual['protected_binary_paths']))
check(good)
negatives = [actual]
for key, value in [('post_capture_epoch', None), ('post_capture_receipt', None), ('protected_binary_paths', []), ('ready', 1)]:
    item = copy.deepcopy(good); item[key] = value; negatives.append(item)
for field, value in [('path', '/absolute/epoch.json'), ('path', '../epoch.json'), ('sha256', 'z'*64)]:
    item = copy.deepcopy(good); item['post_capture_epoch'][field] = value; negatives.append(item)
for fields in [{}, {'status': ''}]:
    item = copy.deepcopy(good); item['post_capture_receipt']['required_fields'] = fields; negatives.append(item)
for paths in [good['protected_binary_paths'][:-1],
              good['protected_binary_paths'][:-1] + [good['protected_binary_paths'][0]],
              good['protected_binary_paths'][:-1] + ['other/gtest/XUL']]:
    item = copy.deepcopy(good); item['protected_binary_paths'] = paths; negatives.append(item)
for item in negatives:
    try:
        check(item)
    except AssertionError:
        pass
    else:
        raise AssertionError('invalid binding accepted')
before = sorted(x.name for x in HERE.iterdir())
run = subprocess.run([sys.executable, '-I', '-S', '-B', str(HERE / 'apply.py')], capture_output=True, text=True)
assert run.returncode == 1 and 'AssertionError: disabled application plan' in run.stderr
assert before == sorted(x.name for x in HERE.iterdir())
assert '11840' in source and '12438' in source and '2155' in source
assert "report['declaration_axioms'] == expected_axioms" in source
assert "report['executable_cases'] == old['executable_cases'] +" in source
assert "report['source_sha256'] == expected_sources" in source
out.mkdir()
(out / 'disabled.log').write_text(run.stdout + run.stderr)
result = {'status': 'STEPS_ORIGIN_APPLICATION_DRIVER_STATIC_PASS', 'positive_synthetic_binding': 1,
          'rejected_synthetic_bindings': len(negatives), 'actual_disabled_exit': run.returncode,
          'disabled_attempt_writes': False, 'live_preservation_or_git_calls': False,
          'canonical_apply_or_compiler': False, 'future_epoch_binding': None}
(out / 'CHECK.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result))
