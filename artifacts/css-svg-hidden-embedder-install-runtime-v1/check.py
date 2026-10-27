import argparse
import ast
import copy
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
parser = argparse.ArgumentParser()
parser.add_argument('--output', required=True)
args = parser.parse_args()
output = Path(args.output)
assert not output.exists() and not output.is_symlink()
c = read(HERE / 'CONFIG.json')
assert c['ready_for_execution'] is False
assert all(c[k] is None for k in ['epoch', 'epoch_manifest_sha256', 'epoch_receipt',
                                'acceptance', 'acceptance_sha256', 'acceptance_receipt'])
refs = read(HERE / 'REFERENCES.json')
for name, expected in refs.items():
    assert sha(ROOT / name) == expected, name
proposal = ROOT / c['proposal']
for name, expected in read(proposal / 'FILES.json').items():
    assert sha(proposal / name) == expected
pins = read(proposal / 'SOURCE-PINS.json')
assert set(c['sources']) == set(pins) and len(pins) == 5
for name, item in pins.items():
    assert c['source_pins'][name] == c['original_source_pins'][name] == item['installed_sha256']
    assert sha(ROOT / c['candidate_sources'][name]) == c['candidate_pins'][name] == item['installed_candidate_sha256']
assert len(c['guard_sources']) == len(c['source_pins']) == 56
assert len(c['installed_tests']) == 8 and len(c['modified_native_paths']) == 30
for name, item in c['installed_tests'].items():
    assert c['existing_test_pins'][name] == item['sha256']
base = ROOT / 'artifacts/css-svg-hidden-embedder-comparison-runtime-v1'
expected = copy.deepcopy(read(base / 'CONFIG.json')['expected_subtests'])
for directory in ['css-svg-length-readiness-install-runtime-v1',
                  'css-svg-absolute-factor-install-runtime-v1', 'css-hidden-svg-matrix-install-runtime-v1']:
    for test, names in read(ROOT / 'artifacts' / directory / 'CONFIG.json')['expected_subtests'].items():
        assert test not in expected
        expected[test] = names
assert c['expected_subtests'] == expected and len(expected) == 12
assert sum(map(len, expected.values())) == 101
assert len({(test, name) for test, names in expected.items() for name in names}) == 101
resources = read(HERE / 'RESOURCES.json')
assert resources == read(base / 'RESOURCES.json')
for test in expected:
    native = 'testing/web-platform/tests' + test
    assert native in c['install'] or native in resources
    assert 'testing/web-platform/meta' + test + '.ini' in resources
assert len(c['install']) == 1 and (HERE / 'fixture.html').read_bytes() == (base / 'fixture.html').read_bytes()
source = (HERE / 'run.py').read_text()
old = (ROOT / 'artifacts/css-svg-length-readiness-install-runtime-v1/run.py').read_text()
tree = ast.parse(source)
assert source[source.index('finally:\n    if not succeeded:'):] == old[old.index('finally:\n    if not succeeded:'):]
def fn(body, name):
    return ast.dump(next(n for n in ast.parse(body).body if isinstance(n, ast.FunctionDef) and n.name == name), include_attributes=False)
assert fn(source.replace('.svg-hidden-embedder-install.tmp', '.svg-readiness-install.tmp'), 'replace_source') == fn(old, 'replace_source')
assert (HERE / 'tests.py').read_bytes() == (base / 'tests.py').read_bytes()
for path in HERE.glob('*.py'):
    ast.parse(path.read_text())
gate = next(n for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
            and n.func.id == 'need' and len(n.args) > 1 and isinstance(n.args[1], ast.Constant)
            and n.args[1].value == 'all101 integration').args[0]
expression = compile(ast.Expression(gate), '<actual all101 integration gate>', 'eval')
assert eval(expression, {'result': {'rows': [{'status': 'PASS'}] * 101}})
negatives = 0
for rows in [[{'status': 'PASS'}] * 100, [{'status': 'PASS'}] * 102,
             [{'status': 'PASS'}] * 100 + [{'status': 'FAIL'}],
             [{'status': 'PASS'}] * 100 + [{'status': 'TIMEOUT'}]]:
    assert not eval(expression, {'result': {'rows': rows}})
    negatives += 1
output.write_text(json.dumps({'status': 'PASS_DISABLED_UNBOUND', 'references_authenticated': len(refs),
    'cases': 101, 'files': 12, 'source_guards': 56, 'owned_native': 5, 'owned_tests': 1,
    'existing_installed_identities': 8, 'all_pass_gate_negatives': negatives,
    'restoration_tail_identical': True, 'atomic_source_function_identical_except_temp_name': True,
    'live_source_or_binary_pins_read': False, 'executed': False}, indent=2) + '\n')
