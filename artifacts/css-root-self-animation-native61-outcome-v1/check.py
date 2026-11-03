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
assert raw['counts'] == {'PASS': 54, 'FAIL': 7}
for path, pin in raw['input_runtime_manifests'].items():
    module.authenticate((ROOT / path).parent, pin)
assessor = load('signature', ROOT / 'artifacts/css-keyframe-font-unit-candidate-browser-v3/assess.py')
baseline = {'rows': [assessor.signature(r) for r in raw['rows']], 'ends': [assessor.signature(r) for r in raw['endings']]}
rows, ends = copy.deepcopy((baseline['rows'], baseline['ends']))
for row in rows:
    if row['status'] == 'FAIL':
        row.update(status='PASS', expected='PASS', expected_field_present=False, message=None, message_field_present=False)
positive = module.compare_signatures(baseline, rows, ends)
assert positive['fail_to_pass'] == 7 and positive['preserved_pass_signatures'] == 54
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
 ('duplicate ending', lambda r,e:e.__setitem__(0,e[1])),
 ('ending status changed', lambda r,e:e[0].update(status='CRASH')),
 ('ending metadata changed', lambda r,e:e[0].update(message='new'))]
for label, mutation in mutations:
    r,e=copy.deepcopy((rows,ends)); mutation(r,e)
    reject(label, lambda:module.compare_signatures(baseline,r,e))
assert not (HERE/'RESULT.json').exists()
print(json.dumps({'saved_only':True,'actual_baseline':{'PASS':54,'FAIL':7,'endings':5},'synthetic_candidate_positive':{'PASS':61,'improvements':7,'preserved_PASS':54,'preserved_endings':5},'negative_controls':rejects,'references':len(refs),'candidate_outcome_pending':True,'no_live_operations':True}))
