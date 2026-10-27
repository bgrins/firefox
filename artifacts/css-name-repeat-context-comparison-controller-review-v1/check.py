import ast
import copy
import hashlib
import json
import os
from pathlib import Path
import stat
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUNTIME = ROOT / 'artifacts/css-name-repeat-context-comparison-runtime-v1'
DATA = ROOT / 'artifacts/css-name-repeat-context-comparison-data-v1/data'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text())
inputs = read(RUNTIME / 'INPUTS.json')
assert inputs['compare_sha256'] == sha(RUNTIME / 'compare.py') == '303e3bd29f5e4acbd033d616ee83e8a33fa46b9bfe6dc1c2759afc230d61617d'
assert inputs['ready_for_execution'] is False
assert all(inputs[k] is None for k in ('controller_review', 'actual_session', 'actual_exit'))
refs = {str((RUNTIME / n).relative_to(ROOT)): sha(RUNTIME / n) for n in ('compare.py', 'INPUTS.json')}
for name, expected in inputs['manifests'].items():
    path = ROOT / name / 'FILES.json'
    assert sha(path) == expected
    refs[str(path.relative_to(ROOT))] = expected
    for member, digest in read(path).items():
        assert not Path(member).is_absolute() and '..' not in Path(member).parts
        item = path.parent / member
        assert stat.S_ISREG(item.lstat().st_mode) and sha(item) == digest
for name, expected in inputs['helper_pins'].items():
    assert sha(ROOT / name) == expected
    refs[name] = expected
tree = ast.parse((RUNTIME / 'compare.py').read_text())
compile(tree, str(RUNTIME / 'compare.py'), 'exec')
functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)
             and node.name in ('need', 'assess', 'write_source', 'restore_sources', 'cleanup_fixtures')]
assert len(functions) == 5
policy = read(DATA / 'EXPERIMENT-POLICY.json')
archived = {(x['test'], x['subtest']): x for x in read(DATA / 'ARCHIVED-OUTCOMES.json')}
landing = {(x['test'], x['subtest']) for x in policy['candidate_required_PASS']}
repairs = {(x['test'], x['subtest']) for x in policy['observed_repair_witnesses']}
env = {'archived': archived, 'landing_keys': landing, 'repair_keys': repairs,
       'stat': stat, 'sha': sha, 'save': lambda *args: None}
exec(compile(ast.Module(body=functions, type_ignores=[]), '<selected controller functions>', 'exec'), env)
assess = env['assess']
assert not assess(archived, 'restored')[2]
candidate = copy.deepcopy(archived)
for key in repairs:
    candidate[key].update(status='PASS', message=None, expected=None)
assert not assess(candidate, 'candidate')[2]
assert len(assess(candidate, 'candidate')[1]) == 8
checks = 2
for key in landing:
    bad = copy.deepcopy(candidate)
    bad[key]['status'] = 'FAIL'
    assert assess(bad, 'candidate')[2]
    checks += 1
old_pass = next(k for k, v in archived.items() if v['status'] == 'PASS' and k not in landing)
old_fail = next(k for k, v in archived.items() if v['status'] == 'FAIL' and k not in repairs)
for key, field, value in [(old_pass, 'status', 'FAIL'), (old_pass, 'effective_expected', 'FAIL'),
                          (old_pass, 'known_intermittent', ['FAIL']), (old_fail, 'message', 'changed'),
                          (old_fail, 'expected', 'FAIL'), (old_fail, 'known_intermittent', ['FAIL']),
                          (next(iter(repairs)), 'effective_expected', 'FAIL')]:
    bad = copy.deepcopy(candidate)
    bad[key][field] = value
    assert assess(bad, 'candidate')[2]
    checks += 1
extra = copy.deepcopy(candidate)
extra[old_fail].update(status='PASS', message=None, expected=None)
diff, improvements, errors = assess(extra, 'candidate')
assert not errors and len(improvements) == 9 and sum(not x['required_landing'] for x in improvements) == 1
assert assess(candidate, 'restored')[2]
checks += 2
bad = copy.deepcopy(candidate)
bad.pop(old_pass)
try:
    assess(bad, 'candidate')
except RuntimeError:
    checks += 1
else:
    raise AssertionError('missing outcome accepted')

recovery_checks = 0
with tempfile.TemporaryDirectory(prefix='name-repeat-controller-review-') as name:
    scratch = Path(name)
    for key in ('a', 'b'):
        (scratch / key).write_bytes(('original ' + key).encode())
        (scratch / (key + '.original')).write_bytes(('original ' + key).encode())
        (scratch / (key + '.candidate')).write_bytes(('candidate ' + key).encode())
    original = {key: sha(scratch / key) for key in ('a', 'b')}
    proposed = {key: sha(scratch / (key + '.candidate')) for key in ('a', 'b')}
    env.update(ROOT=scratch, bodies={key: {'original': key + '.original', 'candidate': key + '.candidate'}
                                    for key in ('a', 'b')},
               maps={'baseline': original, 'candidate': proposed}, current_sources=dict(original),
               source_identities={key: [(scratch / key).stat().st_dev, (scratch / key).stat().st_ino]
                                  for key in ('a', 'b')},
               mutation_started=False, transitions=[])
    env['write_source']('a', 'candidate')
    assert not env['restore_sources']()
    assert all(sha(scratch / key) == original[key] for key in original)
    recovery_checks += 1
    env['write_source']('a', 'candidate')
    env['write_source']('b', 'candidate')
    (scratch / 'a').write_bytes(b'unknown edit')
    errors = env['restore_sources']()
    assert len(errors) == 1 and (scratch / 'a').read_bytes() == b'unknown edit' and sha(scratch / 'b') == original['b']
    recovery_checks += 1
    (scratch / 'a').write_bytes((scratch / 'a.original').read_bytes())
    (scratch / 'replacement').write_bytes((scratch / 'a.original').read_bytes())
    os.replace(scratch / 'replacement', scratch / 'a')
    assert len(env['restore_sources']()) == 1
    recovery_checks += 1
    for key in ('owned', 'edited', 'replaced'):
        (scratch / key).write_bytes(b'fixture')
    env['owned'] = {key: {'identity': [(scratch / key).stat().st_dev, (scratch / key).stat().st_ino],
                          'sha256': sha(scratch / key)} for key in ('owned', 'edited', 'replaced')}
    (scratch / 'edited').write_bytes(b'unknown fixture')
    (scratch / 'newfixture').write_bytes(b'fixture')
    os.replace(scratch / 'newfixture', scratch / 'replaced')
    removed, errors = env['cleanup_fixtures']()
    assert removed == ['owned'] and len(errors) == 2
    assert (scratch / 'edited').read_bytes() == b'unknown fixture' and (scratch / 'replaced').read_bytes() == b'fixture'
    recovery_checks += 1
check = {'status': 'NAME_REPEAT_COMPARISON_CONTROLLER_SOURCE_GO',
         'controller_sha256': inputs['compare_sha256'], 'decision_checks': checks,
         'scratch_recovery_checks': recovery_checks, 'manifests_authenticated': len(inputs['manifests']),
         'fixture_count': 7, 'roles': 611, 'sources': 72, 'installed_identities': 23,
         'staged_payloads': 925, 'native_paths': 43, 'source_changes': 2,
         'subtests': 1532, 'reftests': 8, 'required_new_passes': 10,
         'source_review_only': True, 'ready_for_execution': False,
         'live_inputs_read': False, 'live_actions': False, 'native_acceptance': False}
for name, value in [('CHECK.json', check), ('REFERENCES.json', refs), ('REVIEWED-INPUTS.json', inputs)]:
    with (HERE / name).open('x') as stream:
        stream.write(json.dumps(value, indent=2) + '\n')
print(json.dumps(check, indent=2))
