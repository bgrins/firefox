import ast
import copy
import importlib.util
import json
import os
from pathlib import Path
import tempfile

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('rewrite_check', HERE / 'rewrite.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
plan = m.ROOT / 'artifacts/css-integer-stored-range-history-fold-plan-v2'
for name, pin in m.read(HERE / 'REFERENCES.json').items():
    assert m.digest((m.ROOT / name).read_bytes()) == pin
sequence = m.read(HERE / 'SEQUENCE.json')
promoted = m.read(HERE / 'RESEARCH-PROMOTION.json')
assert sequence == m.read(plan / 'SEQUENCE.json') and len(sequence) == 37
assert promoted == m.read(plan / 'RESEARCH-PROMOTION.json') and len(promoted) == 39
for i, entry in enumerate(sequence):
    source = (plan / 'metadata-variants' / (entry['metadata_original_sha256'] + '.original.ini')).read_bytes()
    result = m.transform(source, i == 0)
    assert m.digest(result) == entry['metadata_rewritten_sha256']
    if i:
        expected = (plan / 'metadata-variants' / (entry['metadata_original_sha256'] + '.candidate.ini')).read_bytes()
        assert result == expected
negative = 0
for bad in (b'', m.BLOCK + m.BLOCK, m.BLOCK.replace(b'FAIL', b'PASS')):
    try:
        m.transform(bad, False)
    except RuntimeError:
        negative += 1
    else:
        raise AssertionError('invalid metadata accepted')
extra = {'artifacts/reviewed-new-proof/receipt.json': {'mode': '100644', 'sha256': 'a' * 64}}
m.selection_check(extra, promoted)
for bad in ({}, {next(iter(promoted)): next(iter(promoted.values()))},
            {'layout/base/file.cpp': next(iter(extra.values()))},
            {'artifacts/../bad': next(iter(extra.values()))},
            {'artifacts/bad\nname': next(iter(extra.values()))},
            {'artifacts/link': {'mode': '120000', 'sha256': 'a' * 64}},
            {'artifacts/bad-pin': {'mode': '100644', 'sha256': 'invalid'}}):
    try:
        m.selection_check(bad, promoted)
    except RuntimeError:
        negative += 1
    else:
        raise AssertionError('invalid research selection accepted')

git_attempts = []
def forbid_git(*args, **kwargs):
    git_attempts.append(args)
    raise AssertionError('Git subprocess is forbidden in this check')
m.subprocess.check_output = forbid_git
m.subprocess.run = forbid_git
old_argv = m.sys.argv
old_env = dict(os.environ)
try:
    m.sys.argv = ['rewrite.py', '--run']
    for name in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES'):
        os.environ[name] = '/not-a-real-git-location'
        try:
            m.main()
        except RuntimeError as error:
            assert str(error) == 'ambient ' + name
            negative += 1
        else:
            raise AssertionError('ambient override accepted')
        del os.environ[name]
    try:
        m.main()
    except RuntimeError as error:
        assert str(error) == 'disabled rewrite'
        negative += 1
    else:
        raise AssertionError('disabled runner accepted')
finally:
    m.sys.argv = old_argv
    os.environ.clear()
    os.environ.update(old_env)
assert not git_attempts

tree = ast.parse((HERE / 'rewrite.py').read_text())
main = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'main')
attempt = next(n for n in main.body if isinstance(n, ast.With))
assert ast.unparse(attempt.items[0].context_expr).endswith(".open('x')")
with tempfile.TemporaryDirectory(prefix='fix121-attempt-check-', dir='/private/tmp') as td:
    namespace = dict(HERE=Path(td), carrier='c' * 40, branch='refs/heads/test', json=json)
    code = compile(ast.Module(body=[attempt], type_ignores=[]), '<actual-exclusive-attempt>', 'exec')
    exec(code, namespace)
    before = (Path(td) / 'ATTEMPT.json').read_bytes()
    try:
        exec(code, namespace)
    except FileExistsError:
        negative += 1
    else:
        raise AssertionError('attempt overwrite accepted')
    assert (Path(td) / 'ATTEMPT.json').read_bytes() == before
mapping = m.read(HERE / 'CURRENT-FIX-MAPPING.json')
for fix, fields in ((133, ['research_commit']), (134, ['research_commit', 'shared_prior_research'])):
    row = next(e for e in mapping if e['fix'] == fix)
    assert all(f in row['current_fields'] for f in fields)
assert all(not k.startswith('previous') and 'history' not in k for e in mapping for k in e['current_fields'])
publication_body = next(n.body for n in ast.walk(main) if hasattr(n, 'body') and isinstance(n.body, list)
                        and any(isinstance(x, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'transaction' for t in x.targets) for x in n.body))
transaction_index = next(i for i, n in enumerate(publication_body) if isinstance(n, ast.Assign)
                         and any(isinstance(t, ast.Name) and t.id == 'transaction' for t in n.targets))
publication_code = compile(ast.Module(body=publication_body[transaction_index-1:transaction_index+5], type_ignores=[]), '<actual-publication-guards>', 'exec')
final_gate = next(n for n in publication_body if isinstance(n, ast.Expr) and isinstance(n.value, ast.Call)
                 and any(isinstance(a, ast.Constant) and a.value == 'final published branch and HEAD' for a in n.value.args))
final_code = compile(ast.Module(body=[final_gate], type_ignores=[]), '<actual-final-branch-gate>', 'exec')
publication_cases = []
for fault in ('none', 'before-switch', 'before-detach', 'transaction-switch', 'after-switch', 'after-old-head'):
    state = {'branch': 'refs/heads/expected', 'head': 'c' * 40, 'updates': 0}
    expected_branch = state['branch']
    if fault == 'before-switch':
        state['branch'] = 'refs/heads/other'
    if fault == 'before-detach':
        state['branch'] = None
    def git(*args, data=None):
        if args == ('symbolic-ref', 'HEAD'):
            if state['branch'] is None:
                raise RuntimeError('detached HEAD')
            return (state['branch'] + '\n').encode()
        assert args == ('update-ref', '--stdin')
        lines = data.decode().splitlines()
        assert lines == ['start', 'option no-deref', 'symref-verify HEAD ' + expected_branch,
                         'verify refs/heads/backup ' + 'c' * 40,
                         'update ' + expected_branch + ' ' + 'n' * 40 + ' ' + 'c' * 40,
                         'prepare', 'commit']
        if fault == 'transaction-switch':
            state['branch'] = 'refs/heads/other'
        if state['branch'] != expected_branch:
            raise RuntimeError('simulated atomic symref verification refusal')
        state['updates'] += 1
        state['head'] = 'n' * 40
        if fault == 'after-switch':
            state['branch'] = 'refs/heads/other'
        if fault == 'after-old-head':
            state['head'] = 'c' * 40
        return b''
    class Guards:
        def index_state(self, *args):
            return {'head': state['head']}
    namespace = dict(git=git, branch=expected_branch, backup='refs/heads/backup', carrier='c' * 40,
                     parent='n' * 40, result={}, h=Guards(), ROOT=Path('/not-used'), env={}, need=m.need)
    try:
        exec(publication_code, namespace)
    except RuntimeError:
        assert fault != 'none'
        assert state['updates'] == (1 if fault.startswith('after-') else 0)
    else:
        assert fault == 'none' and state['updates'] == 1
    publication_cases.append(fault)
for branch, head in (('refs/heads/other', 'n' * 40), ('refs/heads/expected', 'c' * 40)):
    namespace = dict(need=m.need, branch='refs/heads/expected', parent='n' * 40,
                     git=lambda *args: (branch if args[0] == 'symbolic-ref' else head).encode())
    try:
        exec(final_code, namespace)
    except RuntimeError:
        negative += 1
    else:
        raise AssertionError('changed final branch/head accepted')
print(json.dumps({'status': 'FIX121_HISTORY_REWRITE_STATIC_PASS', 'transformed_old_trees': 37,
    'negative_controls': negative, 'publication_cases': publication_cases, 'git_subprocesses': len(git_attempts),
    'owned_scratch_removed': True, 'git_objects_refs_indices_signatures_created': False}, indent=2))
