import ast
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys
import tempfile
import types
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
def need(ok, why):
    if not ok:
        raise RuntimeError(why)
def check():
    c = json.loads((HERE / 'CONFIG.json').read_text())
    assert not c['ready_for_execution'] and all(c[n] is None for n in ('epoch', 'epoch_receipt', 'acceptance', 'acceptance_sha256', 'acceptance_receipt'))
    for n, h in json.loads((HERE / 'REFERENCES.json').read_text()).items():
        assert hashlib.sha256((ROOT / n).read_bytes()).hexdigest() == h, n
    text = (HERE / 'run.py').read_text()
    compile(text, 'run.py', 'exec')
    assert len(c['sources']) == len(c['tests']) == len(c['install']) == 1
    assert len(c['guard_sources']) == 47 and sum(map(len, c['expected_subtests'].values())) == 32
    assert c['candidate_pins']['dom/base/Element.cpp'] == '5770fd0f1134284626ed42152e4b1c1d054cf509ae99e2ebcaf08d5ae00c0913'
    assert hashlib.sha256((HERE / 'fixture.html').read_bytes()).hexdigest() == '18c47e1acbf0a546a975fe5dc92c297a38a71e228a7b6ec576a58bc71c06078b'
    old = (ROOT / 'artifacts/css-cssom-offset-scroll-comparison-v1/run.py').read_text()
    tree = ast.parse(text)
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'replace_source')
    old_function = next(n for n in ast.parse(old).body if isinstance(n, ast.FunctionDef) and n.name == 'replace_source')
    assert ast.dump(function, include_attributes=False) == ast.dump(old_function, include_attributes=False)
    assert "if changed and state['original_source_restored'] and state['all_native_sources_restored']:" in text
    assert "if not succeeded:" in text and text.index('succeeded = True') > text.index("wpt.save('INSTALLATION.json'")
    with tempfile.TemporaryDirectory(prefix='css-install-atomic-check-') as tmp:
        root = Path(tmp)
        name = 'Element.cpp'
        path = root / name
        path.write_bytes(b'original')
        st = path.stat()
        ns = dict(ROOT=root, need=need, stat=stat, hashlib=hashlib, os=types.SimpleNamespace(fstat=os.fstat, fchmod=os.fchmod, replace=os.replace),
            owned_sources={name: {(st.st_dev, st.st_ino, hashlib.sha256(b'original').hexdigest())}})
        exec(compile(ast.Module(body=[function], type_ignores=[]), '<atomic-only>', 'exec'), ns)
        replace = ns['replace_source']
        replace(name, b'candidate')
        replace(name, b'original')
        assert path.read_bytes() == b'original'
        def interrupted(source, target):
            os.replace(source, target)
            raise RuntimeError('simulated post-rename interruption')
        ns['os'].replace = interrupted
        try:
            replace(name, b'candidate')
        except RuntimeError:
            pass
        else:
            raise AssertionError('missing simulated interruption')
        assert path.read_bytes() == b'candidate'
        ns['os'].replace = os.replace
        replace(name, b'original')
        assert path.read_bytes() == b'original'
        path.write_bytes(b'unknown edit')
        try:
            replace(name, b'candidate')
        except RuntimeError:
            pass
        else:
            raise AssertionError('unknown edit accepted')
        assert path.read_bytes() == b'unknown edit'
        assert list(root.iterdir()) == [path]
    path = ROOT / 'artifacts/css-cssom-offset-scroll-comparison-v1/tests.py'
    spec = importlib.util.spec_from_file_location('test_gate', path)
    tests = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tests)
    wpt = types.SimpleNamespace(CONFIG=c, need=need)
    main = c['main_test']
    rows = [{'test':main, 'subtest':n, 'status':'PASS'} for n in c['expected_subtests'][main]]
    tests.require_phase(wpt, 'candidate', {'rows':rows, 'ends':[{'test':main, 'status':'OK'}]})
    bad = copy.deepcopy(rows)
    bad[0]['status'] = 'FAIL'
    try:
        tests.require_phase(wpt, 'candidate', {'rows':bad, 'ends':[]})
    except RuntimeError:
        pass
    else:
        raise AssertionError('candidate failure accepted')
    result = dict(disabled_unbound=True, native_writes_allowed=1, source_guards=47, own_wpt_cases=32,
        atomic_helper_ast_identical=True, scratch_roundtrip=True, post_rename_interrupt_recovery=True,
        unknown_edit_refused=True, candidate_failure_refused=True, full_source_restore_gate_before_build=True,
        no_scratch_residue=True, browser_build_native_index_actions=False)
    (HERE / 'STATIC-CHECK.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result))
if __name__ == '__main__':
    check()
