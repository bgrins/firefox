import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

refs = read(HERE / 'REFERENCES.json')
for path, pin in refs.items():
    assert sha(ROOT / path) == pin
module = load('comparison', HERE / 'compare.py')
binding = read(HERE / 'BINDINGS.json')
assert not binding['execution_enabled']
assert all(binding[k] is None for k in ('owner_manifest','runtime_manifest','owner_terminal','owner_result','build_result','restoration'))
module.authenticate(ROOT / binding['baseline']['directory'], binding['baseline']['manifest_sha256'])
assert sha(ROOT / binding['baseline']['path']) == binding['baseline']['sha256']
raw = read(ROOT / binding['baseline']['path'])
assert raw['counts'] == {'PASS': 5, 'FAIL': 2}
assert sha(ROOT / binding['source_roles']['path']) == binding['source_roles']['sha256']
assert {r['subtest'] for r in raw['subtests'] if r['status'] == 'FAIL'} == {f'SMIL root font-size {unit} uses the actual document-root identity' for unit in ('rem', 'rlh')}
assessor = load('signature', ROOT / 'artifacts/css-keyframe-font-unit-candidate-browser-v3/assess.py')
baseline = {'rows': [assessor.signature(r) for r in raw['subtests']], 'ends': [assessor.signature(r) for r in raw['endings']]}
rows, ends = copy.deepcopy((baseline['rows'], baseline['ends']))
for row in rows:
    if row['status'] == 'FAIL':
        row.update(status='PASS', expected='PASS', expected_field_present=False, message=None, message_field_present=False)
positive = module.compare_signatures(baseline, rows, ends)
assert positive['fail_to_pass'] == 2 and positive['preserved_pass_signatures'] == 5
rejects = []
def reject(label, callback):
    try:
        callback()
    except (AssertionError, KeyError, TypeError):
        rejects.append(label)
    else:
        raise AssertionError(label)
reject('disabled main before runtime access', module.main)
old_pass = next(i for i,r in enumerate(baseline['rows']) if r['status'] == 'PASS')
old_fail = next(i for i,r in enumerate(baseline['rows']) if r['status'] == 'FAIL')
mutations = [
 ('missing callback', lambda r,e:r.pop()),
 ('duplicate callback', lambda r,e:r.__setitem__(0,r[1])),
 ('unexpected callback identity', lambda r,e:r[0].update(subtest='unexpected')),
 ('unfixed target', lambda r,e:r[old_fail].update(status='FAIL')),
 ('old PASS regressed', lambda r,e:r[old_pass].update(status='FAIL')),
 ('old PASS message changed', lambda r,e:r[old_pass].update(message='new')),
 ('old PASS expected-field changed', lambda r,e:r[old_pass].update(expected_field_present=not r[old_pass]['expected_field_present'])),
 ('old PASS intermittent metadata changed', lambda r,e:r[old_pass].update(known_intermittent=['FAIL'])),
 ('missing ending', lambda r,e:e.pop()),
 ('duplicate ending', lambda r,e:e.append(copy.deepcopy(e[0]))),
 ('ending status changed', lambda r,e:e[0].update(status='CRASH')),
 ('ending metadata changed', lambda r,e:e[0].update(message='new'))]
for label, mutation in mutations:
    r,e=copy.deepcopy((rows,ends)); mutation(r,e)
    reject(label, lambda:module.compare_signatures(baseline,r,e))
source = (HERE/'compare.py').read_text()
main_node = next(n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name == 'main')
join = next(n for n in ast.walk(main_node) if isinstance(n, ast.Assert) and "terminal['result_sha256']" in ast.get_source_segment(source, n))
join_code = compile(ast.Module(body=[join], type_ignores=[]), 'actual-terminal-result-join', 'exec')
join_binding = {'owner_result': {'sha256': 'a'*64}}
exec(join_code, {'terminal': {'result_sha256': 'a'*64}, 'bindings': join_binding})
reject('terminal result digest mismatch', lambda: exec(join_code, {'terminal': {'result_sha256': 'b'*64}, 'bindings': join_binding}))
reject('terminal result digest absent', lambda: exec(join_code, {'terminal': {}, 'bindings': join_binding}))
original_events = [json.loads(line) for line in (ROOT / binding['baseline']['directory'] / 'raw.jsonl').read_text().splitlines()]
assert [r for r in original_events if r.get('action') == 'test_status'] == raw['subtests']
assert [r for r in original_events if r.get('action') == 'test_end'] == raw['endings']
assert not (HERE/'RESULT.json').exists()
print(json.dumps({'saved_only':True,'actual_baseline':{'PASS':5,'FAIL':2,'endings':1},'synthetic_candidate_positive':{'PASS':7,'improvements':2,'preserved_PASS':5,'preserved_endings':1},'negative_controls':rejects,'references':len(refs),'candidate_outcome_pending':True,'no_live_operations':True}))
