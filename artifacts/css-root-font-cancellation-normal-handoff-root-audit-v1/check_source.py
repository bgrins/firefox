import ast
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_bytes())
binding = read(HERE / 'BINDINGS.json')
assert binding['execution_enabled'] is False and binding['pending_owner_terminal'] is True
for name in ('owner_manifest_sha256', 'result_sha256', 'terminal_sha256', 'launch', 'session', 'terminal_chunk', 'outer_group', 'archive_records'):
    assert binding[name] is None
for path, pin in binding['references'].items():
    assert sha(ROOT / path) == pin
origins = read(HERE / 'ORIGINS.json')
changes = {'css-root-font-cancellation-trace-candidate-browser-v3': 'css-root-font-cancellation-normal-handoff-candidate-browser-v2',
           'css-root-font-cancellation-trace-candidate-browser-runtime-v1': 'css-root-font-cancellation-normal-handoff-candidate-browser-runtime-v2'}
for name in ('audit.py', 'archive_audit.py'):
    original = (ROOT / origins[name]['path']).read_text()
    for before, after in changes.items():
        original = original.replace(before, after)
    if name == 'audit.py':
        original = original.replace("{'servo/components/style/data.rs', 'servo/components/style/traversal.rs', 'servo/components/style/matching.rs', 'dom/animation/EffectCompositor.cpp', 'layout/style/GeckoBindings.cpp'}", "{'servo/components/style/traversal.rs', 'servo/components/style/gecko/traversal.rs', 'servo/ports/geckolib/glue.rs'}")
    else:
        original = original.replace("{name: policy['source_context_pins'][name] for name in\n                                                       ('servo/ports/geckolib/glue.rs', 'servo/components/style/custom_properties.rs')}", "{name: pin for name, pin in policy['source_context_pins'].items()\n                                                       if name not in roles}")
    assert original == (HERE / name).read_text()
    ast.parse(original)
source = (HERE / 'archive_audit.py').read_text()
join = next(n for n in ast.walk(ast.parse(source)) if isinstance(n, ast.Assert) and "snapshot['unchanged_source_preimages']" in ast.unparse(n))
code = compile(ast.Module(body=[join], type_ignores=[]), '<actual archive context join>', 'exec')
roles = {name: {} for name in ('servo/components/style/traversal.rs', 'servo/components/style/gecko/traversal.rs', 'servo/ports/geckolib/glue.rs')}
context = {name: str(i) for i, name in enumerate((*roles, 'servo/components/style/data.rs', 'servo/components/style/matching.rs', 'dom/animation/EffectCompositor.cpp', 'layout/style/GeckoBindings.cpp', 'servo/components/style/custom_properties.rs'))}
expected = {name: pin for name, pin in context.items() if name not in roles}
exec(code, dict(snapshot={'unchanged_source_preimages': expected}, policy={'source_context_pins': context}, roles=roles))
negatives = []
for label, values in [('candidate-glue-as-unchanged', dict(expected, **{'servo/ports/geckolib/glue.rs': context['servo/ports/geckolib/glue.rs']})),
                      ('missing-original-data', {name: pin for name, pin in expected.items() if name != 'servo/components/style/data.rs'})]:
    try:
        exec(code, dict(snapshot={'unchanged_source_preimages': values}, policy={'source_context_pins': context}, roles=roles))
    except AssertionError:
        negatives.append(label)
    else:
        raise AssertionError(label)
print(json.dumps({'source_only': True, 'exact_parent_transforms': 2, 'projection_positive': True,
 'projection_rejections': negatives, 'all_future_bindings_null': True,
 'live_audit_executed': False, 'inherited_suites_rerun': False,
 'tested_inputs': {n: sha(HERE / n) for n in ('audit.py', 'archive_audit.py', 'BINDINGS.json', 'check_source.py')}}))
