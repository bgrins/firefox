import ast
import importlib.util
import json
from pathlib import Path
import sys
assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
here = Path(__file__).resolve().parent
root = here.parents[1]
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
assert len(sys.argv) == 2
h = load('check_owner', root / 'artifacts/css-registered-number-source-transition-v4/transition.py')
h.authenticate(here, sys.argv[1])
p = h.read(here / 'POLICY.json')
for name, pin in p['references'].items():
    assert h.digest((root / name).read_bytes()) == pin
for directory, pin in p['packages'].items():
    h.authenticate(root / directory, pin)
for path in here.glob('*.py'):
    ast.parse(path.read_text())
evidence = load('check_evidence', here / 'evidence.py')
epoch = h.read(root / 'artifacts/css-registered-number-native-runtime-v1/CURRENT-EPOCH.json')
print(json.dumps(evidence.verify(root, p, epoch, h), sort_keys=True))
print('Read-only evidence/syntax authentication; no install, build, lint, browser, or canonical mutation.')
