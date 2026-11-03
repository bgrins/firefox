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
           if key in ('result_sha256', 'terminal_sha256', 'terminal_chunk', 'archive_records'))
assert binding['owner_manifest_sha256'] == '0eef6144415a2e0cb278cb285bd8f93c82ebff53e4b410f840588636307b7645'
assert (binding['launch'],binding['session'],binding['outer_group']) == ('03008b',62755,43798)
origins = json.loads((HERE / 'ORIGINS.json').read_text())
for path, pin in binding['references'].items():
    assert sha(ROOT / path) == pin
for name in ('audit.py', 'archive_audit.py'):
    path = ROOT / origins[name]['path']
    old = path.read_text()
    expected = old.replace('css-root-font-cancellation-selective-handoff-candidate-browser-v1',
                           'css-root-font-startup-trace-candidate-browser-v1')
    expected = expected.replace('css-root-font-cancellation-selective-handoff-candidate-browser-runtime-v1',
                                'css-root-font-startup-trace-candidate-browser-runtime-v1')
    if name == 'audit.py':
        expected = expected.replace("{'servo/components/style/data.rs', 'servo/components/style/traversal.rs', 'servo/components/style/gecko/traversal.rs', 'servo/ports/geckolib/glue.rs'}","{'dom/animation/KeyframeEffect.cpp', 'layout/style/GeckoBindings.cpp', 'servo/components/style/data.rs', 'servo/components/style/gecko/traversal.rs', 'servo/components/style/matching.rs', 'servo/components/style/traversal.rs', 'servo/components/style/values/specified/length.rs', 'servo/ports/geckolib/glue.rs'}")
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
owner = ROOT / 'artifacts/css-root-font-startup-trace-candidate-browser-v1'
roles = json.loads((owner/'SOURCE-ROLES.json').read_text())
context = json.loads((owner/'POLICY.json').read_text())['source_context_pins']
assert len(roles) == 8
unchanged = {name: pin for name, pin in context.items() if name not in roles}
exec(code, dict(snapshot={'unchanged_source_preimages': unchanged},
                policy={'source_context_pins': context}, roles=roles))
rejected = []
for label, value in [('candidate-KeyframeEffect-as-unchanged', unchanged | {'dom/animation/KeyframeEffect.cpp': context['dom/animation/KeyframeEffect.cpp']}),
                     ('missing-original-EffectCompositor', {name:pin for name,pin in unchanged.items() if name != 'dom/animation/EffectCompositor.cpp'})]:
    try:
        exec(code, dict(snapshot={'unchanged_source_preimages': value},
                        policy={'source_context_pins': context}, roles=roles))
    except AssertionError:
        rejected.append(label)
    else:
        raise AssertionError(label)
print(json.dumps({'source_only': True, 'exact_parent_transforms': 2,
                  'projection_positive': True, 'projection_rejections': rejected,
                  'actual_launch_and_active_owner_bound': True, 'future_terminal_result_archive_null': True, 'live_audit_executed': False,
                  'inherited_suites_rerun': False,
                  'tested_inputs': {name: sha(HERE / name) for name in
                                    ('audit.py', 'archive_audit.py', 'BINDINGS.json', 'check_source.py')}}))
