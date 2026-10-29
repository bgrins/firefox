import ast
import hashlib
import json
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
root = Path(__file__).resolve().parents[2]
here = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
policy = json.loads((here / 'POLICY.json').read_bytes())
assert policy['install_enabled'] is False and policy['activation_pending']
assert policy['head'] is policy['epoch_sha256'] is policy['owned_sha256'] is None
assert policy['accepted_fix_id'] is None and policy['acceptance'] is False
for name, pin in policy['references'].items():
    assert sha(root / name) == pin, name
for name, pin in policy['packages'].items():
    directory = root / name
    assert sha(directory / 'FILES.json') == pin
    for path, row in json.loads((directory / 'FILES.json').read_bytes()).items():
        assert sha(directory / path) == (row['sha256'] if isinstance(row, dict) else row)
for path in here.glob('*.py'):
    ast.parse(path.read_text(), filename=str(path))
assert len(policy['preserved_accepted_payload']) == 27
assert policy['supersedes_source_pin']['fix'] == 145
assert 'round_context_quotient_transition' in policy['accepted_transitions']
assert len(policy['tests']) == 1
print('Disabled installer syntax, references, source overlap and preservation bindings verified; no install/build/browser/signing execution.')
