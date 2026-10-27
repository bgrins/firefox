import argparse
import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--output', type=Path, required=True)
out = parser.parse_args().output.resolve()
out.mkdir()
spec = importlib.util.spec_from_file_location('runner', HERE / 'run.py')
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)
inputs = r.read(HERE / 'INPUTS.json')
assert inputs['ready'] is False and inputs['epoch'] is None and inputs['expected_head'] is None
for n, pin in inputs['local_pins'].items():
    assert r.sha(HERE / n) == pin
for n, pin in r.read(HERE / 'REFERENCES.json').items():
    assert r.sha(ROOT / n) == pin
selection = r.read(HERE / 'GTEST-SELECTION.json')
assert selection['candidate'][:17] == selection['original'] and len(set(selection['candidate'])) == 19
log = ''.join(f'TEST_START: {n}\nTEST_END: PASS\n' for n in selection['candidate'])
log += 'Ran 19 test(s) from 4 test suite(s) (0 disabled), with 0 failure(s).\n'
assert r.gtest_result(log, selection['candidate']) == selection['candidate']
negatives = [log.replace('TEST_END: PASS', 'TEST_END: FAIL', 1), log.replace(selection['candidate'][0], 'Unknown.Test'), log.replace('19 test(s)', '0 test(s)'), log + 'TEST_START: Extra.Test\nTEST_END: PASS\n', log.replace('TEST_START:', 'BAD_START:', 1)]
for bad in negatives:
    try:
        r.gtest_result(bad, selection['candidate'])
    except RuntimeError:
        pass
    else:
        raise AssertionError('bad GTest log accepted')
refusal = subprocess.run(['python3', '-I', '-S', '-B', str(HERE / 'run.py'), '--run'], capture_output=True, text=True)
assert refusal.returncode == 1 and 'Disabled provider host experiment' in refusal.stderr
(out / 'disabled.log').write_text(refusal.stdout + refusal.stderr)
owner = r.load('ownership', ROOT / 'artifacts/css-cubic-bezier-calc-range-comparison-v1/compare.py')
main = next(n for n in ast.parse((HERE / 'run.py').read_text()).body if isinstance(n, ast.FunctionDef) and n.name == 'main')
tail = next(n for n in main.body if isinstance(n, ast.Try) and n.finalbody)
code = compile(ast.fix_missing_locations(ast.Module(body=ast.parse('error=None\npassed=False\n').body+[tail], type_ignores=[])), '<actual-provider-tail>', 'exec')
results = []
for case in ['success', 'metadata-failure', 'candidate-build-failure', 'second-write-failure', 'first-restore-failure', 'final-receipt-failure', 'terminal-receipt-failure', 'live-group']:
    with tempfile.TemporaryDirectory(prefix='provider-tail-') as tmp:
        root = Path(tmp)
        originals = {'first': b'one', 'second': b'two'}
        candidates = {n: b'candidate-' + b for n,b in originals.items()}
        for n,b in originals.items(): (root / n).write_bytes(b)
        pre = {n: hashlib.sha256(b).hexdigest() for n,b in originals.items()}
        owned, calls, receipts, publication, recovery = {}, [], {}, [], []
        def quiet():
            if case == 'live-group' and 'metadata' in calls:
                raise RuntimeError('owned group remains')
        def write(root, item, data):
            owner.write_owned(root,item,data)
            if case == 'second-write-failure' and item['path']=='second':
                raise OSError('after second write')
        def restore(root,item,data):
            calls.append('restore-'+item['path'])
            if case == 'first-restore-failure' and item['path']=='first':
                raise RuntimeError('unknown first source')
            owner.restore_owned(root,item,data)
        def phase(*args, **kwargs):
            calls.append('metadata')
            if case in ['metadata-failure','first-restore-failure','live-group']:
                raise RuntimeError('metadata failure')
        def compile_and_test(prefix,*args):
            calls.append(prefix+'-compile-test')
            if case == 'candidate-build-failure' and prefix=='candidate':
                raise RuntimeError('candidate build failed')
        def verify(label):
            quiet()
            return ({n:hashlib.sha256((root/n).read_bytes()).hexdigest() for n in pre}, {}, [])
        def publish(label,*args):
            if case=='final-receipt-failure' and label=='CURRENT-EPOCH.json':
                publication.append('injected final receipt')
        def result(*args): return {'args':args}
        def save(label,value):
            if case=='terminal-receipt-failure' and label=='RESULT.json':
                publication.append('injected terminal receipt')
            else: receipts[label]=copy.deepcopy(value)
        env=dict(vars(r),ROOT=root,OBJ=root/'obj',pre=pre,post={},owned=owned,originals=originals,candidates=candidates,quiet=quiet,ownership=types.SimpleNamespace(write_owned=write,restore_owned=restore),verify=verify,phase=phase,compile_and_test=compile_and_test,selection=selection,publication_errors=publication,recovery_errors=recovery,save=save,publish_epoch=publish,result=result,epoch={'semantic_index':{}},h=types.SimpleNamespace(semantic_index=lambda i:i))
        exec(code,env)
        assert env['passed'] == (case=='success')
        if case=='success':
            assert all((root/n).read_bytes()==b for n,b in candidates.items())
        elif case not in ['first-restore-failure','live-group']:
            assert all((root/n).read_bytes()==b for n,b in originals.items())
            assert 'restored-compile-test' in calls
        if case=='first-restore-failure':
            assert 'restore-second' in calls and (root/'second').read_bytes()==originals['second']
            assert 'restored-compile-test' not in calls
        if case=='live-group':
            assert all((root/n).read_bytes()==b for n,b in candidates.items())
        results.append({'case':case,'passed':env['passed'],'calls':calls,'publication_errors':publication,'recovery_errors':recovery})
(out/'TAIL.json').write_text(json.dumps(results,indent=2)+'\n')
(out/'CHECK.json').write_text(json.dumps({'status':'PROVIDER_RESOLVER_HOST_PREPARATION_STATIC_PASS','gtest_parser_negatives':len(negatives),'actual_tail_scenarios':len(results),'disabled_refusal':True,'native_or_compiler_execution':False},indent=2)+'\n')
print('PASS: disabled gate, exact GTest parser and eight actual-tail scenarios')
