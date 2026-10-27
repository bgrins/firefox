import ast
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
def read(p):
    return json.loads(p.read_text())
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
c = read(HERE / 'CONFIG.json')
assert c['ready_for_execution'] is False
acceptance = ROOT / c['acceptance']
assert sha(acceptance) == c['acceptance_sha256'] and read(acceptance) == c['acceptance_receipt']
a = c['acceptance_receipt']
assert a['status'] == 'SCOPED_ACCEPTED' and a['fix'] == 113
assert a['runtime'] == c['epoch'] and a['runtime_files_sha256'] == c['epoch_manifest_sha256']
assert a['native_paths'] == c['sources'] + list(c['install'])
assert a['patch']['sha256'] == sha(ROOT / a['patch']['path']) == sha(ROOT / c['proposal'] / 'gecko-wpt.patch')
for n, h in read(HERE / 'REFERENCES.json').items():
    assert sha(ROOT / n) == h, n
proposal = ROOT / c['proposal']
for n, h in read(proposal / 'FILES.json').items():
    assert sha(proposal / n) == h, n
assert c['sources'] == ['dom/svg/SVGGraphicsElement.cpp']
assert len(c['guard_sources']) == len(c['source_pins']) == 50
assert len(c['modified_native_paths']) == 26
assert len(c['tests']) == len(c['install']) == len(c['expected_subtests']) == 1
assert sum(map(len, c['expected_subtests'].values())) == 8
assert len(c['installed_tests']) == 2
assert (HERE / 'fixture.html').read_bytes() == (proposal / 'hidden-svg-matrix-viewport-resize.html').read_bytes()
comparison = ROOT / 'artifacts/css-hidden-svg-matrix-comparison-v1'
assert read(HERE / 'RESOURCES.json') == read(comparison / 'RESOURCES.json')
assert c['source_pins'] == read(comparison / 'CONFIG.json')['source_pins']
for n, item in c['installed_tests'].items():
    assert c['existing_test_pins'][n] == item['sha256']
    assert n not in c['install']
s = (HERE / 'run.py').read_text()
ast.parse(s)
base = (ROOT / 'artifacts/css-cssom-client-install-v1/run.py').read_text()
def function(text, name):
    return ast.dump(next(n for n in ast.parse(text).body if isinstance(n, ast.FunctionDef) and n.name == name), include_attributes=False)
assert function(s.replace('.svg-install.tmp', '.rounding-comparison.tmp'), 'replace_source') == function(base, 'replace_source')
assert s[s.index('finally:\n    if not succeeded:'):].replace('restore SVGGraphicsElement.cpp', 'restore Element.h') == base[base.index('finally:\n    if not succeeded:'):]
module = ast.parse((comparison / 'tests.py').read_text())
require = next(n for n in module.body if isinstance(n, ast.FunctionDef) and n.name == 'require_phase')
namespace = {}
exec(compile(ast.Module(body=[require], type_ignores=[]), '<isolated require_phase>', 'exec'), namespace)
class Wpt:
    CONFIG = c
    @staticmethod
    def need(ok, message):
        if not ok:
            raise RuntimeError(message)
rows = [{'test': test, 'subtest': name, 'status': 'PASS'} for test, names in c['expected_subtests'].items() for name in names]
namespace['require_phase'](Wpt, 'candidate', {'rows': rows, 'ends': []})
for index in range(8):
    altered = [dict(r) for r in rows]
    altered[index]['status'] = 'FAIL'
    try:
        namespace['require_phase'](Wpt, 'candidate', {'rows': altered, 'ends': []})
    except RuntimeError:
        pass
    else:
        raise AssertionError(index)
epoch = ROOT / c['epoch']
assert sha(epoch / 'FILES.json') == c['epoch_manifest_sha256']
for n, h in read(epoch / 'FILES.json').items():
    assert sha(epoch / n) == h, n
state = read(epoch / 'STATE.json')
receipt = read(epoch / 'ROOT-FINAL-CHECK.json')
final = read(epoch / 'FINAL.json')
assert state['status'] == 'terminal' and state['restored'] and state['restore_build_exit'] == 0
assert state['recovery_errors'] == [] and 'failure' not in state and state['paired_preservation_passed']
assert set(state['phases']) == {'baseline', 'candidate'} and all(p['build_exit'] == 0 for p in state['phases'].values())
assert receipt == c['epoch_receipt'] and receipt['status'] == 'RESTORED_VERIFIED' and receipt['exit'] == 0
assert receipt['state_sha256'] == sha(epoch / 'STATE.json') and receipt['final_sha256'] == sha(epoch / 'FINAL.json')
assert receipt['restored_binary_pins'] == state['restored_binary_pins']
assert read(epoch / 'BEFORE.json') == final and final['sources'] == c['source_pins']
assert read(epoch / 'FINAL-PINS.json') == {**read(epoch / 'RESOURCES.json'), **final['sources'], **state['restored_binary_pins']}
assert read(epoch / 'RESOURCES.json') == read(HERE / 'RESOURCES.json')
assert (HERE / 'run.py').read_bytes() == (ROOT / 'artifacts/css-hidden-svg-matrix-install-v1/run.py').read_bytes()
result = {'status': 'PASS', 'native_execution': False, 'epoch_authenticated': c['epoch_manifest_sha256'], 'acceptance_authenticated': c['acceptance_sha256'],
          'source_guards': 50, 'preserved_native_differences': 26, 'owned_sources': 1,
          'owned_tests': 1, 'preserved_installed_tests': 2, 'subtests': 8,
          'resource_pins': len(read(HERE / 'RESOURCES.json')), 'negative_outcomes_rejected': 8,
          'atomic_helper_identical_modulo_temp_suffix': True, 'rollback_tail_identical_modulo_operation_label': True}
(HERE / 'STATIC-CHECK.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result))
