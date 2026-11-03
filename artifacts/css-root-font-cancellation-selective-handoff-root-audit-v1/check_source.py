import ast
import difflib
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
binding = json.loads((HERE / 'BINDINGS.json').read_text())
assert binding['execution_enabled'] is False and binding['pending_owner_terminal'] is True
assert all(value is None for key, value in binding.items()
           if key not in ('execution_enabled', 'pending_owner_terminal', 'references'))
origins = json.loads((HERE / 'ORIGINS.json').read_text())
for path, pin in binding['references'].items():
    assert sha(ROOT / path) == pin
for name in ('audit.py', 'archive_audit.py'):
    path = ROOT / origins[name]['path']
    old = path.read_text()
    expected = old.replace('css-root-font-cancellation-normal-handoff-candidate-browser-v2',
                           'css-root-font-cancellation-selective-handoff-candidate-browser-v1')
    expected = expected.replace('css-root-font-cancellation-normal-handoff-candidate-browser-runtime-v2',
                                'css-root-font-cancellation-selective-handoff-candidate-browser-runtime-v1')
    if name == 'audit.py':
        expected = expected.replace("{'servo/components/style/traversal.rs', 'servo/components/style/gecko/traversal.rs', 'servo/ports/geckolib/glue.rs'}",
                                    "{'servo/components/style/data.rs', 'servo/components/style/traversal.rs', 'servo/components/style/gecko/traversal.rs', 'servo/ports/geckolib/glue.rs'}")
    actual = (HERE / name).read_text()
    assert actual == expected
    ast.parse(actual)
    assert (HERE / (name + '.diff')).read_text() == ''.join(difflib.unified_diff(
        old.splitlines(True), actual.splitlines(True), fromfile=str(path.relative_to(ROOT)),
        tofile=str((HERE / name).relative_to(ROOT))))
source = (HERE / 'archive_audit.py').read_text()
join = next(node for node in ast.walk(ast.parse(source))
            if isinstance(node, ast.Assert) and "snapshot['unchanged_source_preimages']" in ast.unparse(node))
code = compile(ast.Module(body=[join], type_ignores=[]), '<actual unchanged-context assertion>', 'exec')
roles = dict.fromkeys(('servo/components/style/data.rs', 'servo/components/style/traversal.rs',
                      'servo/components/style/gecko/traversal.rs', 'servo/ports/geckolib/glue.rs'))
context = {name: str(i) for i, name in enumerate((*roles, 'servo/components/style/matching.rs'))}
unchanged = {name: pin for name, pin in context.items() if name not in roles}
exec(code, dict(snapshot={'unchanged_source_preimages': unchanged},
                policy={'source_context_pins': context}, roles=roles))
rejected = []
for label, value in [('candidate-data-as-unchanged', unchanged | {'servo/components/style/data.rs': context['servo/components/style/data.rs']}),
                     ('missing-original-matching', {})]:
    try:
        exec(code, dict(snapshot={'unchanged_source_preimages': value},
                        policy={'source_context_pins': context}, roles=roles))
    except AssertionError:
        rejected.append(label)
    else:
        raise AssertionError(label)
print(json.dumps({'source_only': True, 'exact_parent_transforms': 2,
                  'projection_positive': True, 'projection_rejections': rejected,
                  'all_future_bindings_null': True, 'live_audit_executed': False,
                  'inherited_suites_rerun': False,
                  'tested_inputs': {name: sha(HERE / name) for name in
                                    ('audit.py', 'archive_audit.py', 'BINDINGS.json', 'check_source.py')}}))
