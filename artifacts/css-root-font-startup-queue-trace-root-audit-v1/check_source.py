import ast
import difflib
import hashlib
import json
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_bytes())
binding = read(HERE / 'BINDINGS.json')
assert binding['execution_enabled'] is False and binding['pending_owner_terminal'] is True
assert all(value is None for key, value in binding.items() if key not in ('execution_enabled', 'pending_owner_terminal', 'references'))
for path, pin in binding['references'].items():
    assert sha(ROOT / path) == pin
roles = read(HERE / 'SOURCE-ROLES.json')['roles']
assert len(roles) == 10
origins = read(HERE / 'ORIGINS.json')
for name in ('audit.py', 'archive_audit.py'):
    path = ROOT / origins[name]['path']
    assert sha(path) == origins[name]['sha256']
    old = path.read_text()
    expected = old.replace('css-root-font-startup-trace-candidate-browser-v1', 'css-root-font-startup-queue-trace-candidate-browser-v1').replace('css-root-font-startup-trace-candidate-browser-runtime-v1', 'css-root-font-startup-queue-trace-candidate-browser-runtime-v1')
    if name == 'audit.py':
        line = next(l for l in old.splitlines() if l.startswith('assert set(roles) =='))
        expected = expected.replace(line, 'assert set(roles) == {' + ', '.join(repr(x) for x in sorted(roles)) + '}')
    actual = (HERE / name).read_text()
    assert actual == expected
    ast.parse(actual)
    assert (HERE / (name + '.diff')).read_text() == ''.join(difflib.unified_diff(old.splitlines(True), actual.splitlines(True), fromfile=str(path.relative_to(ROOT)), tofile=str((HERE / name).relative_to(ROOT))))
source = (HERE / 'archive_audit.py').read_text()
join = next(n for n in ast.walk(ast.parse(source)) if isinstance(n, ast.Assert) and "snapshot['unchanged_source_preimages']" in ast.unparse(n))
code = compile(ast.Module(body=[join], type_ignores=[]), '<actual context projection>', 'exec')
context = {path: value['base_sha256'] for path, value in roles.items()}
context['unchanged-control.cpp'] = 'a' * 64
expected = {name: pin for name, pin in context.items() if name not in roles}
exec(code, dict(snapshot={'unchanged_source_preimages': expected}, policy={'source_context_pins': context}, roles=roles))
rejections = []
for name, projection in [('active-EffectCompositor-as-unchanged', expected | {'dom/animation/EffectCompositor.cpp': context['dom/animation/EffectCompositor.cpp']}), ('active-ServoStyleSet-as-unchanged', expected | {'layout/style/ServoStyleSet.cpp': context['layout/style/ServoStyleSet.cpp']}), ('omitted-unchanged-context', {})]:
    try:
        exec(code, dict(snapshot={'unchanged_source_preimages': projection}, policy={'source_context_pins': context}, roles=roles))
    except AssertionError:
        rejections.append(name)
    else:
        raise AssertionError(name)
print(json.dumps({'exact_parent_transforms': 2, 'role_count': len(roles), 'projection_positive': True, 'projection_rejections': rejections, 'projection_context_scope': 'exact ten base pins plus synthetic unchanged control; future owner policy is not bound', 'references': len(binding['references']), 'future_owner_terminal_result_archive_null': True, 'live_audit_executed': False, 'inherited_suites_rerun': False, 'tested_inputs': {name: sha(HERE / name) for name in ('audit.py', 'archive_audit.py', 'BINDINGS.json', 'SOURCE-ROLES.json', 'ORIGINS.json', 'check_source.py')}}, indent=2))
