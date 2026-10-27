import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import time
import types

ROOT = Path(__file__).resolve().parents[2]
DRAFT = ROOT / 'artifacts/css-keyframe-provider-resolver-host-preparation-v1'
HERE = Path(__file__).resolve().parent

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

r = load('runner', DRAFT / 'run.py')
owner = load('ownership', ROOT / 'artifacts/css-cubic-bezier-calc-range-comparison-v1/compare.py')
main = next(n for n in ast.parse((DRAFT / 'run.py').read_text()).body if isinstance(n, ast.FunctionDef) and n.name == 'main')
functions = [n for n in main.body if isinstance(n, ast.FunctionDef) and n.name in ('save', 'phase', 'compile_and_test')]
code = compile(ast.fix_missing_locations(ast.Module(body=functions, type_ignores=[])), '<actual-recovery-functions>', 'exec')
names = json.loads((DRAFT / 'GTEST-SELECTION.json').read_text())['original']
log = ''.join(f'TEST_START: {n}\nTEST_END: PASS\n' for n in names) + 'Ran 17 test(s) from 4 test suite(s) (0 disabled), with 0 failure(s).\n'
rows = []
for blocked in ('restored-export-PRE.json', 'restored-export-COMMAND.json', 'restored-export-EXECUTION.json', 'restored-TESTS.json'):
    with tempfile.TemporaryDirectory(prefix='provider-review-') as tmp:
        scratch = Path(tmp)
        (scratch / blocked).mkdir()
        calls, errors = [], []
        def run(*args):
            calls.append(args[2].name)
            (args[2] / 'build.log').write_text(log)
        env = dict(vars(r), HERE=scratch, ROOT=scratch, OBJ=scratch / 'obj', publication_errors=errors, phases=[], env={}, stop=False, state={}, binaries={n:'same' for n in r.BINARY_ROLES}, quiet=lambda:None, builder=types.SimpleNamespace(run=run), control=None, h=types.SimpleNamespace(fingerprint=lambda *a:'same'))
        exec(code, env)
        env['verify'] = lambda label: env['save'](label, {'guards_passed':True})
        env['compile_and_test']('restored', names, True)
        assert calls == ['restored-export', 'restored-binaries', 'restored-gtest']
        assert len(errors) == 1 and errors[0].startswith(blocked + ':')
        rows.append({'blocked_receipt':blocked, 'actual_phase_calls':calls, 'publication_error_retained':True})

pre = json.loads((DRAFT / 'PREIMAGES.json').read_text())
proposal = ROOT / 'artifacts/css-keyframe-provider-resolution-implementation-v1'
for scenario in ('restore-existing-four', 'unknown-endpoint-body', 'unknown-endpoint-inode'):
    with tempfile.TemporaryDirectory(prefix='provider-ownership-review-') as tmp:
        scratch = Path(tmp)
        owned = {}
        originals = {}
        for name in pre:
            path = scratch / name
            path.parent.mkdir(parents=True, exist_ok=True)
            originals[name] = (proposal / 'original' / name).read_bytes()
            path.write_bytes(originals[name])
            info = path.stat()
            owned[name] = {'path':name, 'identity':[info.st_dev,info.st_ino], 'owned_sha256':pre[name]}
            owner.write_owned(scratch, owned[name], (proposal / 'candidate' / name).read_bytes())
        endpoint = 'servo/components/style/keyframe_endpoint.rs'
        if scenario == 'unknown-endpoint-body':
            (scratch / endpoint).write_bytes(b'unknown body')
        elif scenario == 'unknown-endpoint-inode':
            replacement = scratch / 'replacement'
            replacement.write_bytes((scratch / endpoint).read_bytes())
            replacement.replace(scratch / endpoint)
        failed = []
        for name,item in owned.items():
            try:
                owner.restore_owned(scratch,item,originals[name])
            except RuntimeError:
                failed.append(name)
        assert failed == ([] if scenario == 'restore-existing-four' else [endpoint])
        for name,item in owned.items():
            if name not in failed:
                path=scratch/name
                assert path.read_bytes() == originals[name]
                assert [path.stat().st_dev,path.stat().st_ino] == item['identity']
        if scenario == 'unknown-endpoint-body':
            assert (scratch/endpoint).read_bytes() == b'unknown body'
        rows.append({'scenario':scenario, 'restored':len(owned)-len(failed), 'preserved_unknown':failed, 'pre_existing_endpoint_never_deleted':(scratch/endpoint).is_file()})
(HERE / 'SUPPLEMENT.json').write_text(json.dumps(rows,indent=2)+'\n')
print('PASS: four recovery publication faults and three four-source ownership scenarios')
