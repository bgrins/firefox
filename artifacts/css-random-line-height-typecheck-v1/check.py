import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('projection', HERE / 'projection.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
sha = lambda b: hashlib.sha256(b).hexdigest()
staging = {'staged_files': ['artifacts/test/' + str(i) for i in range(165)]}
staging['staged_working'] = {n: 'a' * 64 for n in staging['staged_files']}
old_entries = b'100644 ' + b'1' * 40 + b' 0\told\0'
entries = old_entries + b''.join(b'100644 ' + b'2' * 40 + b' 0\t' + n.encode() + b'\0' for n in staging['staged_files'])
epoch = {'semantic_index': {'head': 'head', 'working_diff': 'working', 'entries': sha(old_entries), 'cached_diff': sha(b'')}, 'staged_working': {}, 'raw_index_observation': {'current': 'oldraw'}, 'unchanged': {'binary': 'pin'}}
observed = {'head': 'head', 'working_diff': 'working', 'entries': sha(entries), 'cached_diff': 'staged', 'raw_index': 'newraw'}
result = m.derive(epoch, observed, entries, staging)
assert result['unchanged'] == epoch['unchanged'] and epoch['staged_working'] == {}
assert result['staged_working'] == staging['staged_working']
mutants = []
for field in ('head', 'working_diff', 'entries'):
    v = copy.deepcopy(observed); v[field] = 'wrong'; mutants.append((epoch, v, entries, staging))
v = copy.deepcopy(epoch); v['staged_working'] = {'extra': 'x'}; mutants.append((v, observed, entries, staging))
v = copy.deepcopy(epoch); v['semantic_index']['entries'] = 'wrong'; mutants.append((v, observed, entries, staging))
for token, replacement in [(b'100644 '+b'2'*40, b'100755 '+b'2'*40), (b' 0\tartifacts/test/0', b' 1\tartifacts/test/0')]:
    changed = entries.replace(token, replacement, 1); o = dict(observed, entries=sha(changed)); mutants.append((epoch, o, changed, staging))
changed = entries + b'100644 '+b'3'*40+b' 0\tunrelated\0';mutants.append((epoch, dict(observed, entries=sha(changed)), changed, staging))
v = copy.deepcopy(staging); v['staged_files'].pop(); mutants.append((epoch, observed, entries, v))
v = copy.deepcopy(staging); v['staged_working'].pop(v['staged_files'][0]); mutants.append((epoch, observed, entries, v))
v = copy.deepcopy(staging); old = v['staged_files'][0]; v['staged_files'][0] = 'servo/foreign.rs';v['staged_working']['servo/foreign.rs'] = v['staged_working'].pop(old); mutants.append((epoch, observed, entries, v))
for args in mutants:
    try:
        m.derive(*args)
    except AssertionError:
        pass
    else:
        raise AssertionError('Accepted corrupted projection')
for p in HERE.glob('*.py'):
    ast.parse(p.read_text(), filename=str(p))
print(json.dumps({'projection_positive': 1, 'projection_rejections': len(mutants), 'python_syntax': True, 'main_or_live_checks_executed': False}))
